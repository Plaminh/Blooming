import os
from unittest.mock import patch
from app.core.config import Settings
import pytest

# Database credentials are required settings; every scenario needs them so a
# test fails only for the rule it names.
DB_ENV = {"POSTGRES_DB": "blooming", "POSTGRES_USER": "blooming", "POSTGRES_PASSWORD": "secret"}


def test_config_development_defaults():
    # When no overrides are provided, dev defaults apply
    with patch.dict(os.environ, DB_ENV, clear=True):
        settings = Settings(_env_file=None, SECRET_KEY="your-super-secret-key-that-is-at-least-32-bytes-long-test")
        assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 30
        assert settings.EMAIL_VERIFICATION_FRONTEND_URL == "http://localhost:1420/verify-email"
        assert "http://localhost:1420" in settings.FRONTEND_URLS

def test_config_staging_overrides():
    # When staging env vars are provided, they override the defaults
    env_vars = {
        "SECRET_KEY": "your-super-secret-key-that-is-at-least-32-bytes-long-test",
        "ENVIRONMENT": "staging",
        "ACCESS_TOKEN_EXPIRE_MINUTES": "1440",
        "EMAIL_VERIFICATION_FRONTEND_URL": "https://staging.blooming.com/verify-email",
        "FRONTEND_URLS": '["http://tauri.localhost", "tauri://localhost", "https://staging.blooming.com"]',
        "BREVO_API_KEY": "test-key",
        "BREVO_SENDER_EMAIL": "test@test.com",
        **DB_ENV,
    }
    with patch.dict(os.environ, env_vars, clear=True):
        settings = Settings(_env_file=None)
        assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 1440
        assert settings.EMAIL_VERIFICATION_FRONTEND_URL == "https://staging.blooming.com/verify-email"
        assert "http://tauri.localhost" in settings.FRONTEND_URLS
        assert "tauri://localhost" in settings.FRONTEND_URLS
        assert "http://localhost:1420" not in settings.FRONTEND_URLS

@pytest.mark.parametrize("override", [
    {"ACCESS_TOKEN_EXPIRE_MINUTES": "30"},
    {"EMAIL_VERIFICATION_FRONTEND_URL": "http://staging.example/verify-email"},
])
def test_staging_rejects_unsafe_session_or_verification_configuration(override):
    env_vars = {
        "SECRET_KEY": "your-super-secret-key-that-is-at-least-32-bytes-long-test",
        "ENVIRONMENT": "staging",
        "ACCESS_TOKEN_EXPIRE_MINUTES": "1440",
        "EMAIL_VERIFICATION_FRONTEND_URL": "https://staging.example/verify-email",
        "BREVO_API_KEY": "test-key",
        "BREVO_SENDER_EMAIL": "test@example.com",
        **DB_ENV,
        **override,
    }
    with patch.dict(os.environ, env_vars, clear=True), pytest.raises(ValueError, match="Staging"):
        Settings(_env_file=None)
