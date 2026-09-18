import uuid
from datetime import datetime, timezone

import pytest
import pytest_asyncio
from app.core.security import create_access_token
from app.db.models.users import User, UserSettings
from sqlalchemy.ext.asyncio import AsyncSession


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Creates a basic active user with a verified email."""
    user = User(
        id=uuid.uuid4(),
        email=f"test_{uuid.uuid4().hex}@example.com",
        password_hash="fakehash",
        account_status="ACTIVE",
        email_verified_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_user_two(db_session: AsyncSession) -> User:
    """Creates a second active user for cross-user tests."""
    user = User(
        id=uuid.uuid4(),
        email=f"test_{uuid.uuid4().hex}@example.com",
        password_hash="fakehash",
        account_status="ACTIVE",
        email_verified_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_user_settings(db_session: AsyncSession, test_user: User) -> UserSettings:
    """Creates default settings for the test user."""
    settings = UserSettings(
        user_id=test_user.id,
        timezone="UTC",
        default_focus_minutes=25,
        default_break_minutes=5,
        reminders_enabled=True,
    )
    db_session.add(settings)
    await db_session.commit()
    await db_session.refresh(settings)
    return settings


@pytest.fixture
def auth_headers(test_user: User) -> dict[str, str]:
    """Generates valid JWT auth headers for the test user."""
    token = create_access_token(str(test_user.id))
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_headers_two(test_user_two: User) -> dict[str, str]:
    """Generates valid JWT auth headers for the second test user."""
    token = create_access_token(str(test_user_two.id))
    return {"Authorization": f"Bearer {token}"}
