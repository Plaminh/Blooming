from unittest.mock import Mock

import pytest
from app.core.config import settings
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from tests.conftest import check_safe_db_url


@pytest.mark.unit
def test_safe_db_url_exact_dev_url_rejected():
    with pytest.raises(
        RuntimeError, match="matches the development database precisely"
    ):
        check_safe_db_url(str(settings.database_url))


@pytest.mark.unit
def test_safe_db_url_exact_dev_db_rejected():
    url = f"postgresql+psycopg://user:pass@127.0.0.1:5432/{settings.POSTGRES_DB}"
    with pytest.raises(
        RuntimeError, match="matches the development database precisely"
    ):
        check_safe_db_url(url)


@pytest.mark.unit
def test_safe_db_url_contains_dev_name_but_ends_in_test():
    # Example: if dev is 'blooming', 'blooming_test' is valid
    url = f"postgresql+psycopg://user:pass@127.0.0.1:5432/{settings.POSTGRES_DB}_test"
    # Should not raise
    safe_url = check_safe_db_url(url)
    assert safe_url.endswith("_test")


@pytest.mark.unit
def test_safe_db_url_test_only_in_credentials():
    url = "postgresql+psycopg://testuser:testpass@test.com:5432/my_database"
    with pytest.raises(RuntimeError, match="must end with '_test'"):
        check_safe_db_url(url)


@pytest.mark.unit
def test_safe_db_url_missing_db_name():
    url = "postgresql+psycopg://user:pass@127.0.0.1:5432/"
    with pytest.raises(RuntimeError, match="must contain a database name"):
        check_safe_db_url(url)


@pytest.mark.unit
def test_safe_db_url_valid_local_test_db():
    url = "postgresql+psycopg://user:pass@127.0.0.1:5432/my_app_test"
    result = check_safe_db_url(url)
    assert "my_app_test" in result


@pytest.mark.unit
def test_safe_db_url_has_no_caller_controlled_trust_bypass():
    url = "postgresql+psycopg://user:pass@some-random-host:12345/random_db"
    with pytest.raises(TypeError):
        check_safe_db_url(url, is_testcontainers=True)


@pytest.mark.unit
@pytest.mark.parametrize(
    "url",
    [
        "postgresql+psycopg://user:pass@remote.example:5432/app_test",
        "postgresql+psycopg://user:pass@/app_test",
        "postgresql+psycopg://user:pass@localhost/app_test?host=remote.example",
        "postgresql+psycopg://user:pass@localhost/app_test?dbname=production",
        "sqlite:///app_test",
        "not-a-url-secret",
    ],
)
def test_unsafe_connection_targets_rejected(url):
    with pytest.raises(RuntimeError, match="SAFETY VIOLATION") as exc:
        check_safe_db_url(url)
    assert url not in str(exc.value)


@pytest.mark.unit
def test_safe_url_preserves_password():
    from sqlalchemy.engine import make_url

    url = "postgresql+psycopg://user:s%40fe%3Apass@localhost/app_test"
    assert make_url(check_safe_db_url(url)).password == "s@fe:pass"


@pytest.mark.unit
def test_safe_db_url_credential_redaction():
    url = f"postgresql+psycopg://secret_user:super_secret_password@127.0.0.1:5432/{settings.POSTGRES_DB}"
    with pytest.raises(RuntimeError) as exc_info:
        check_safe_db_url(url)

    error_msg = str(exc_info.value)
    # Ensure credentials are not in the error message
    assert "super_secret_password" not in error_msg
    assert "secret_user" not in error_msg


@pytest.mark.unit
async def test_unsafe_url_rejected_before_any_engine_creation(monkeypatch):
    from tests import conftest

    monkeypatch.setenv(
        "TEST_DATABASE_URL", settings.database_url.render_as_string(hide_password=False)
    )
    create_engine = Mock(
        side_effect=AssertionError("Engine creation must not be reached")
    )
    monkeypatch.setattr(conftest, "create_async_engine", create_engine)
    fixture = conftest.engine_and_template.__wrapped__()
    with pytest.raises(RuntimeError, match="SAFETY VIOLATION"):
        await anext(fixture)
    create_engine.assert_not_called()


@pytest.mark.integration
async def test_database_is_safely_isolated(db_session: AsyncSession):
    """
    Verify that the test session is connected to a generated ephemeral test database.
    This guarantees that modifications during the test do not affect the development
    or production databases, as all writes are confined to this temporary clone.
    """
    result = await db_session.execute(text("SELECT current_database()"))
    current_db = result.scalar()

    assert current_db != settings.POSTGRES_DB
    assert current_db.startswith("test_db_")
