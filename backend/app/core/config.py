from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL

# Resolve .env locations from this file so settings load identically no matter
# which working directory uvicorn, alembic, or pytest is started from.
_BACKEND_DIR = Path(__file__).resolve().parents[2]
_REPO_ROOT = _BACKEND_DIR.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(_REPO_ROOT / ".env", _BACKEND_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    PROJECT_NAME: str = "Blooming API"
    API_V1_PREFIX: str = "/api/v1"
    ENVIRONMENT: str = "development"

    # Credentials come from the repository .env shared with docker-compose.
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: SecretStr
    POSTGRES_HOST: str = "127.0.0.1"
    POSTGRES_PORT: int = 5432

    DB_ECHO: bool = False
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    # Bounded so an unreachable database fails fast instead of hanging a request.
    DB_CONNECT_TIMEOUT: int = 5

    @property
    def database_url(self) -> URL:
        """Async SQLAlchemy URL. ``str()`` on it masks the password."""
        return URL.create(
            drivername="postgresql+psycopg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD.get_secret_value(),
            host=self.POSTGRES_HOST,
            port=self.POSTGRES_PORT,
            database=self.POSTGRES_DB,
        )


settings = Settings()
