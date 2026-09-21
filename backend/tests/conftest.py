import asyncio
import importlib
import logging
import os
import sys
import uuid
from collections.abc import AsyncGenerator
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
import pytest_asyncio
from app.core.config import settings
from httpx import ASGITransport, AsyncClient
from sqlalchemy import event, text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import ArgumentError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from testcontainers.postgres import PostgresContainer

logger = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def event_loop_policy():
    # Psycopg async connections require SelectorEventLoop on Windows.
    if sys.platform == "win32":
        return asyncio.WindowsSelectorEventLoopPolicy()
    return asyncio.DefaultEventLoopPolicy()


@pytest.fixture
def clock(monkeypatch):
    """Control only domain clocks; authentication tokens keep their real expiry."""

    class Clock(datetime):
        instant = datetime(2026, 1, 1, 9, tzinfo=timezone.utc)

        @classmethod
        def now(cls, tz=None):
            return (
                cls.instant.astimezone(tz) if tz else cls.instant.replace(tzinfo=None)
            )

        @classmethod
        def advance(cls, seconds):
            cls.instant += timedelta(seconds=seconds)

    for name in (
        "focus_service",
        "reminders_service",
        "garden_service",
        "today_service",
    ):
        monkeypatch.setattr(
            importlib.import_module(f"app.services.{name}"), "datetime", Clock
        )
    monkeypatch.setattr(importlib.import_module("app.core.economy"), "datetime", Clock)
    return Clock


# Constants
DATABASE_DIR = Path(__file__).resolve().parents[2] / "database"


def check_safe_db_url(url: str) -> str:
    """Ensure we never connect to the normal dev database or a production-like host."""
    try:
        parsed_url = make_url(url)
    except (ArgumentError, ValueError):
        raise RuntimeError("SAFETY VIOLATION: Invalid test database URL.") from None
    if parsed_url.drivername != "postgresql+psycopg":
        raise RuntimeError("SAFETY VIOLATION: Use postgresql+psycopg.")
    if parsed_url.query:
        raise RuntimeError(
            "SAFETY VIOLATION: Connection query overrides are not allowed."
        )

    db_name = parsed_url.database
    if not db_name:
        raise RuntimeError(
            "SAFETY VIOLATION: Test database URL must contain a database name."
        )

    if db_name == settings.POSTGRES_DB:
        raise RuntimeError(
            "SAFETY VIOLATION: Test database name matches the development database precisely!"
        )

    if str(parsed_url.set(password="***")) == str(
        settings.database_url.set(password="***")
    ):
        raise RuntimeError(
            "SAFETY VIOLATION: Test database URL matches the development database precisely!"
        )

    if not db_name.endswith("_test"):
        raise RuntimeError(
            f"SAFETY VIOLATION: Test database name must end with '_test'. Got: {db_name}"
        )

    # Check for obvious production hosts
    if parsed_url.host not in ("127.0.0.1", "localhost", "::1"):
        raise RuntimeError(
            "SAFETY VIOLATION: Only explicit loopback database hosts are allowed."
        )

    return parsed_url.render_as_string(hide_password=False)


@pytest_asyncio.fixture(scope="session")
async def engine_and_template():
    """
    Starts an ephemeral PostgreSQL container (or uses TEST_DATABASE_URL).
    Creates a unique template database and initializes the schema on it.
    """
    if not DATABASE_DIR.exists() or not any((DATABASE_DIR / "tables").iterdir()):
        raise RuntimeError(f"Database tables directory is missing or empty.")

    test_db_url = os.getenv("TEST_DATABASE_URL")
    container = None

    # Generate unique template name for this test session
    template_name = f"blooming_template_{uuid.uuid4().hex}"

    try:
        if test_db_url:
            root_url = check_safe_db_url(test_db_url)
        else:
            container = PostgresContainer("postgres:17-alpine", dbname="blooming_test")
            container.start()
            raw_url = container.get_connection_url().replace(
                "postgresql+psycopg2://", "postgresql+psycopg://"
            )
            root_url = check_safe_db_url(raw_url)

        root_engine = create_async_engine(root_url, isolation_level="AUTOCOMMIT")

        try:
            async with root_engine.connect() as conn:
                try:
                    await conn.execute(text(f'CREATE DATABASE "{template_name}"'))
                except Exception as e:
                    if (
                        "permission denied" in str(e).lower()
                        or "privilege" in str(e).lower()
                    ):
                        raise RuntimeError(
                            "The user provided in TEST_DATABASE_URL lacks the CREATEDB privilege. "
                            "This is required to run isolated tests using the template database strategy."
                        ) from e
                    raise
        finally:
            await root_engine.dispose()

        # Connect to the template database to initialize schema
        template_url = (
            make_url(root_url)
            .set(database=template_name)
            .render_as_string(hide_password=False)
        )
        template_engine = create_async_engine(template_url)

        try:
            async with template_engine.begin() as conn:
                # Read install.sql to get the exact order of tables
                install_sql_path = DATABASE_DIR / "install.sql"
                install_lines = install_sql_path.read_text(encoding="utf-8").splitlines()
                
                for line in install_lines:
                    line = line.strip()
                    if line.startswith(r'\ir '):
                        rel_path = line.split(' ')[1]
                        sql_path = DATABASE_DIR / rel_path
                        sql = sql_path.read_text(encoding="utf-8")
                        
                        raw_conn = await conn.get_raw_connection()
                        await raw_conn.driver_connection.execute(sql)
        finally:
            await template_engine.dispose()

        yield root_url, template_name

    finally:
        # Teardown logic
        try:
            # We must create a new connection to the root DB to drop the template
            # because the template DB cannot be dropped while we are connected to it.
            if "root_url" in locals() and "template_name" in locals():
                cleanup_engine = create_async_engine(
                    root_url, isolation_level="AUTOCOMMIT"
                )
                try:
                    async with cleanup_engine.connect() as conn:
                        await conn.execute(
                            text(f"""
                            SELECT pg_terminate_backend(pg_stat_activity.pid)
                            FROM pg_stat_activity
                            WHERE pg_stat_activity.datname = '{template_name}'
                            AND pid <> pg_backend_pid()
                        """)
                        )
                        await conn.execute(
                            text(f'DROP DATABASE IF EXISTS "{template_name}"')
                        )
                finally:
                    await cleanup_engine.dispose()
        finally:
            if container:
                container.stop()


@pytest_asyncio.fixture
async def db_session(engine_and_template) -> AsyncGenerator[AsyncSession, None]:
    """
    Function-scoped fixture that clones the template database.
    Provides 100% isolation per test.
    """
    root_url, template_name = engine_and_template
    test_db_name = f"test_db_{uuid.uuid4().hex}"

    root_engine = create_async_engine(root_url, isolation_level="AUTOCOMMIT")
    try:
        async with root_engine.connect() as conn:
            await conn.execute(
                text(f'CREATE DATABASE "{test_db_name}" TEMPLATE "{template_name}"')
            )
    finally:
        await root_engine.dispose()

    test_url = (
        make_url(root_url)
        .set(database=test_db_name)
        .render_as_string(hide_password=False)
    )
    test_engine = create_async_engine(test_url)

    SessionLocal = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )

    try:
        async with SessionLocal() as session:
            yield session
    finally:
        await test_engine.dispose()

        # Drop test DB
        cleanup_engine = create_async_engine(root_url, isolation_level="AUTOCOMMIT")
        try:
            async with cleanup_engine.connect() as conn:
                await conn.execute(
                    text(f"""
                    SELECT pg_terminate_backend(pg_stat_activity.pid)
                    FROM pg_stat_activity
                    WHERE pg_stat_activity.datname = '{test_db_name}'
                    AND pid <> pg_backend_pid()
                """)
                )
                await conn.execute(text(f'DROP DATABASE IF EXISTS "{test_db_name}"'))
        finally:
            await cleanup_engine.dispose()


@pytest_asyncio.fixture
async def async_client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    FastAPI test client with the database session overridden to use our isolated test DB.
    """
    # Lazily import FastAPI app to avoid side-effects during test collection
    from app.api.deps import get_db_session
    from app.db.session import engine as application_engine
    from app.main import app

    connection_attempts = []

    def reject_application_connection(*args):
        connection_attempts.append(True)
        raise AssertionError(
            "API test attempted to connect to the application database"
        )

    event.listen(
        application_engine.sync_engine, "do_connect", reject_application_connection
    )

    async def override_get_db_session():
        try:
            yield db_session
        except Exception:
            await db_session.rollback()
            raise

    original_overrides = dict(app.dependency_overrides)
    app.dependency_overrides[get_db_session] = override_get_db_session

    try:
        async with AsyncClient(
            transport=ASGITransport(app=app, raise_app_exceptions=False),
            base_url="http://test",
        ) as client:
            yield client
    finally:
        app.dependency_overrides = original_overrides
        event.remove(
            application_engine.sync_engine, "do_connect", reject_application_connection
        )
        assert connection_attempts == [], "Database dependency override was bypassed"


pytest_plugins = [
    "tests.fixtures.users",
    "tests.fixtures.tasks",
    "tests.fixtures.planning",
    "tests.fixtures.goals",
    "tests.fixtures.garden",
    "tests.fixtures.focus",
    "tests.fixtures.reminders",
]
