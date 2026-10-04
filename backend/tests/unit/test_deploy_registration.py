"""Registration from a deployed desktop app.

An installed Tauri app calls the API from its own webview origin, not from the
dev server. These tests cover the CORS contract that registration depends on,
the secret-store friendly FRONTEND_URLS format, and the unverified re-register
path.
"""

import os
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.core.config import DESKTOP_APP_ORIGINS, Settings

DB_ENV = {"POSTGRES_DB": "blooming", "POSTGRES_USER": "blooming", "POSTGRES_PASSWORD": "secret"}
SECRET = "a-test-secret-key-that-is-longer-than-32-characters"


def _settings(**env) -> Settings:
    with patch.dict(os.environ, {"SECRET_KEY": SECRET, **DB_ENV, **env}, clear=True):
        return Settings(_env_file=None)


def _preflight(origin: str):
    from app.main import app

    return TestClient(app).options(
        "/api/v1/auth/register",
        headers={
            "Origin": origin,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )


@pytest.mark.parametrize("origin", [*DESKTOP_APP_ORIGINS, "http://localhost:1420"])
def test_installed_app_and_dev_server_pass_the_register_preflight(origin):
    response = _preflight(origin)
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == origin


def test_other_websites_are_still_refused():
    response = _preflight("https://evil.example")
    assert response.status_code == 400
    assert "access-control-allow-origin" not in response.headers


def test_desktop_origins_are_added_to_any_configured_list():
    settings = _settings(FRONTEND_URLS='["https://verify.staging.example"]')
    assert settings.FRONTEND_URLS == ["https://verify.staging.example"]
    assert settings.cors_origins[0] == "https://verify.staging.example"
    assert set(DESKTOP_APP_ORIGINS) <= set(settings.cors_origins)


@pytest.mark.parametrize(
    "raw",
    [
        "https://verify.staging.example, http://localhost:1420",
        '["https://verify.staging.example", "http://localhost:1420"]',
    ],
)
def test_frontend_urls_accept_json_or_comma_separated_values(raw):
    assert _settings(FRONTEND_URLS=raw).FRONTEND_URLS == [
        "https://verify.staging.example",
        "http://localhost:1420",
    ]


def test_trailing_slashes_do_not_break_origin_matching():
    settings = _settings(FRONTEND_URLS="https://verify.staging.example/")
    assert "https://verify.staging.example" in settings.cors_origins


class _User:
    def __init__(self, verified: bool):
        self.email_verified_at = object() if verified else None


@pytest.mark.asyncio
async def test_re_registering_an_unverified_email_points_to_verification(monkeypatch):
    from app.schemas.user import UserCreate
    from app.services import auth_service

    monkeypatch.setattr(auth_service, "get_user_by_email", AsyncMock(return_value=_User(verified=False)))
    with pytest.raises(HTTPException) as caught:
        await auth_service.register_user(
            AsyncMock(), UserCreate(email="new@blooming.app", password="Password123!"), AsyncMock()
        )
    assert caught.value.status_code == 409
    assert caught.value.detail["code"] == "EMAIL_NOT_VERIFIED"


@pytest.mark.asyncio
async def test_re_registering_a_verified_email_is_a_plain_conflict(monkeypatch):
    from app.schemas.user import UserCreate
    from app.services import auth_service

    monkeypatch.setattr(auth_service, "get_user_by_email", AsyncMock(return_value=_User(verified=True)))
    with pytest.raises(HTTPException) as caught:
        await auth_service.register_user(
            AsyncMock(), UserCreate(email="new@blooming.app", password="Password123!"), AsyncMock()
        )
    assert caught.value.status_code == 409
    assert caught.value.detail == "Email already registered."
