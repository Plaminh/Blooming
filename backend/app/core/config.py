from pathlib import Path
from pydantic import SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL
import warnings

# Resolve .env locations from this file so settings load identically no matter
# which working directory uvicorn or pytest is started from.
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
    LOG_LEVEL: str = "INFO"
    GIT_SHA: str = "development"

    SECRET_KEY: SecretStr
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    FRONTEND_URLS: list[str] = [
        "http://localhost:1420",
        "http://127.0.0.1:1420",
    ]

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

    BREVO_API_KEY: SecretStr | None = None
    BREVO_SENDER_EMAIL: str | None = None
    BREVO_SENDER_NAME: str | None = None
    EMAIL_VERIFICATION_FRONTEND_URL: str = "http://localhost:1420/verify-email"
    EMAIL_VERIFICATION_EXPIRE_MINUTES: int = 30
    EMAIL_VERIFICATION_RESEND_COOLDOWN_SECONDS: int = 60

    GROQ_API_KEY: SecretStr | None = None
    GROQ_BASE_URL: str = "https://api.groq.com/openai/v1"
    OLLAMA_BASE_URL: str = "http://localhost:11434/v1"
    AI_ROUTE_ROUTER: str = "groq:llama-3.1-8b-instant"
    AI_ROUTE_CHITCHAT: str = "groq:llama-3.1-8b-instant"
    AI_ROUTE_PLANNER_LITE: str = "groq:openai/gpt-oss-20b"
    AI_ROUTE_PLANNER: str = "groq:openai/gpt-oss-120b"
    AI_ROUTE_EDITOR: str = "groq:openai/gpt-oss-20b,groq:openai/gpt-oss-120b"
    AI_STRICT_MODELS: list[str] = ["openai/gpt-oss-20b", "openai/gpt-oss-120b"]
    AI_TOKEN_BUDGET_24H: dict[str, int] = {
        "openai/gpt-oss-20b": 1_600_000,
        "openai/gpt-oss-120b": 1_600_000,
        "llama-3.1-8b-instant": 4_000_000,
    }
    # Planning is intentionally unlimited per user. Model-level rolling token
    # budgets still protect provider capacity and trigger graceful degradation.
    AI_USER_CALLS_PER_DAY: dict[str, int] = {
        "EDITOR": 100,
        "CHITCHAT": 150,
        "ROUTER": 400,
    }
    AI_TIMEOUT_SECONDS: float = 20.0
    # Total provider time for one chat turn, across router, cascade and repair.
    # The desktop client aborts chat requests after 75s, so keep this well below.
    AI_REQUEST_BUDGET_SECONDS: float = 45.0
    AI_CHAT_RATE_LIMIT_PER_MIN: int = 120
    AI_BUDGET_LEAN_THRESHOLD: float = 0.70
    AI_BUDGET_RULES_ONLY_THRESHOLD: float = 0.85
    AI_NUDGE_COOLDOWN_MINUTES: int = 30

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

    @model_validator(mode="after")
    def validate_environment_and_secrets(self) -> "Settings":
        secret_val = self.SECRET_KEY.get_secret_value()
        if (
            len(secret_val) < 32
            or secret_val == "your-super-secret-key-that-is-at-least-32-bytes-long"
        ):
            raise ValueError(
                "SECRET_KEY must be at least 32 characters long and not a weak default"
            )

        if self.ENVIRONMENT in ("production", "staging"):
            if not self.BREVO_API_KEY or not self.BREVO_SENDER_EMAIL:
                raise ValueError(
                    "BREVO_API_KEY and BREVO_SENDER_EMAIL are required in production/staging"
                )
            if self.ENVIRONMENT == "staging":
                if self.ACCESS_TOKEN_EXPIRE_MINUTES != 1440:
                    raise ValueError("Staging ACCESS_TOKEN_EXPIRE_MINUTES must be 1440")
                if not self.EMAIL_VERIFICATION_FRONTEND_URL.startswith("https://"):
                    raise ValueError("Staging email verification URL must use HTTPS")
        else:
            if not self.BREVO_API_KEY or not self.BREVO_SENDER_EMAIL:
                warnings.warn(
                    "Starting in development without BREVO_API_KEY or BREVO_SENDER_EMAIL. Email features will return safe errors."
                )

        return self


settings = Settings()  # type: ignore[call-arg]  # Required fields come from the environment.
