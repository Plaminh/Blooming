import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException, Request

from app.api.routes import auth
from app.core.rate_limit import (
    login_failures,
    login_requests,
    registration_attempts,
    resend_attempts,
)


def request_from(ip: str, forwarded_for: str | None = None) -> Request:
    headers = []
    if forwarded_for:
        headers.append((b"x-forwarded-for", forwarded_for.encode()))
    return Request(
        {
            "type": "http",
            "method": "POST",
            "path": "/api/v1/auth/login",
            "headers": headers,
            "client": (ip, 12345),
            "server": ("test", 80),
            "scheme": "http",
        }
    )


def form(email: str = "user@example.com", password: str = "wrong"):
    return SimpleNamespace(username=email, password=password)


@pytest.fixture(autouse=True)
def clear_limiters():
    for limiter in (
        login_failures,
        login_requests,
        registration_attempts,
        resend_attempts,
    ):
        limiter._events.clear()
    yield


@pytest.mark.asyncio
async def test_attack_from_one_ip_does_not_lock_account_for_another(monkeypatch):
    rejected = HTTPException(status_code=401, detail="Incorrect email or password")
    authenticate = AsyncMock(side_effect=rejected)
    monkeypatch.setattr(auth.auth_service, "authenticate", authenticate)

    attacker = request_from("198.51.100.10")
    for _ in range(10):
        with pytest.raises(HTTPException) as caught:
            await auth.login(attacker, AsyncMock(), form())
        assert caught.value.status_code == 401
    with pytest.raises(HTTPException) as limited:
        await auth.login(attacker, AsyncMock(), form())
    assert limited.value.status_code == 429
    assert "Retry-After" in limited.value.headers

    authenticate.side_effect = None
    authenticate.return_value = SimpleNamespace(id=uuid.uuid4())
    response = await auth.login(request_from("203.0.113.20"), AsyncMock(), form(password="right"))
    assert response.access_token

    # The successful login clears only the successful source/account pair.
    with pytest.raises(HTTPException) as still_limited:
        await auth.login(attacker, AsyncMock(), form(password="right"))
    assert still_limited.value.status_code == 429


@pytest.mark.asyncio
async def test_unverified_password_checks_are_request_limited(monkeypatch):
    monkeypatch.setattr(
        auth.auth_service,
        "authenticate",
        AsyncMock(side_effect=HTTPException(status_code=403, detail="EMAIL_NOT_VERIFIED")),
    )
    request = request_from("198.51.100.30")

    for _ in range(30):
        with pytest.raises(HTTPException) as caught:
            await auth.login(request, AsyncMock(), form(password="right"))
        assert caught.value.status_code == 403
    with pytest.raises(HTTPException) as limited:
        await auth.login(request, AsyncMock(), form(password="right"))
    assert limited.value.status_code == 429


def test_client_supplied_forwarded_header_is_not_parsed_by_auth_routes():
    request = request_from("198.51.100.40", forwarded_for="203.0.113.99")
    assert auth._client_host(request) == "198.51.100.40"
