"""End-to-end auth flow against PostgreSQL and a recording mail service."""

import asyncio
import time

import pytest
from app.api.deps import get_email_service
from app.main import app
from app.services.email_service import EmailService


class RecordingMail(EmailService):
    def __init__(self):
        self.sent: list[tuple[str, str]] = []

    async def send_verification_email(self, to_email: str, raw_token: str) -> None:
        self.sent.append((to_email, raw_token))


@pytest.fixture(autouse=True)
def _fresh_limiters():
    from app.core.rate_limit import (
        login_failures,
        login_requests,
        registration_attempts,
        resend_attempts,
    )

    for limiter in (
        login_failures,
        login_requests,
        registration_attempts,
        resend_attempts,
    ):
        limiter._events.clear()
    yield


@pytest.fixture
def mail():
    service = RecordingMail()
    app.dependency_overrides[get_email_service] = lambda: service
    yield service
    app.dependency_overrides.pop(get_email_service, None)


async def _register(client, email, password="correct horse"):
    return await client.post(
        "/api/v1/auth/register", json={"email": email, "password": password}
    )


async def _login(client, email, password="correct horse"):
    return await client.post(
        "/api/v1/auth/login", data={"username": email, "password": password}
    )


@pytest.mark.asyncio
async def test_register_verify_login_roundtrip(async_client, mail):
    assert (await _register(async_client, "Ann@Example.com")).status_code == 201
    assert (await _login(async_client, "ann@example.com")).status_code == 403
    token = mail.sent[-1][1]
    verified = await async_client.post(
        "/api/v1/auth/verify-email", json={"token": token}
    )
    assert verified.status_code == 200
    login = await _login(async_client, " ANN@example.com ")
    assert login.status_code == 200
    me = await async_client.get(
        "/api/v1/me",
        headers={"Authorization": f"Bearer {login.json()['access_token']}"},
    )
    assert me.status_code == 200


@pytest.mark.asyncio
async def test_resend_is_throttled_then_sends_after_cooldown(
    async_client, mail, monkeypatch
):
    from app.core.config import settings

    await _register(async_client, "bo@example.com")
    first_token = mail.sent[0][1]
    again = await async_client.post(
        "/api/v1/auth/resend-verification", json={"email": "bo@example.com"}
    )
    assert again.status_code == 200 and len(mail.sent) == 1

    monkeypatch.setattr(settings, "EMAIL_VERIFICATION_RESEND_COOLDOWN_SECONDS", 0)
    await async_client.post(
        "/api/v1/auth/resend-verification", json={"email": "bo@example.com"}
    )
    assert len(mail.sent) == 2
    stale = await async_client.post(
        "/api/v1/auth/verify-email", json={"token": first_token}
    )
    assert stale.status_code == 400


@pytest.mark.xfail(
    strict=True,
    reason="Design gap: mailbox verification accepts a password chosen by the registrant.",
)
@pytest.mark.asyncio
async def test_unverified_email_cannot_be_claimed_with_someone_elses_password(
    async_client, mail
):
    await _register(async_client, "victim@example.com", "attacker-password")
    token = mail.sent[-1][1]
    await async_client.post("/api/v1/auth/verify-email", json={"token": token})
    attacker_login = await _login(
        async_client, "victim@example.com", "attacker-password"
    )
    assert attacker_login.status_code != 200


@pytest.mark.asyncio
async def test_password_hashing_does_not_block_event_loop(async_client, mail):
    ticks = 0

    async def heartbeat():
        nonlocal ticks
        while True:
            await asyncio.sleep(0.01)
            ticks += 1

    task = asyncio.create_task(heartbeat())
    started = time.perf_counter()
    await _register(async_client, "cy@example.com")
    elapsed = time.perf_counter() - started
    task.cancel()
    assert ticks >= elapsed / 0.01 * 0.5, (
        f"event loop stalled: {ticks} ticks in {elapsed:.2f}s"
    )


@pytest.mark.asyncio
async def test_repeated_bad_logins_are_throttled(async_client, mail):
    await _register(async_client, "di@example.com")
    codes = [
        (await _login(async_client, "di@example.com", "wrong-pass")).status_code
        for _ in range(12)
    ]
    assert codes[:10] == [401] * 10 and codes[10:] == [429, 429]
    locked = await _login(async_client, "di@example.com")
    assert locked.status_code == 429 and "Retry-After" in locked.headers


@pytest.mark.asyncio
async def test_unverified_login_is_protected_by_request_throttling(async_client, mail):
    await _register(async_client, "ed@example.com")
    codes = [
        (await _login(async_client, "ed@example.com")).status_code for _ in range(32)
    ]
    assert codes[:30] == [403] * 30
    assert codes[30:] == [429, 429]


@pytest.mark.asyncio
async def test_signup_attempts_are_capped(async_client, mail):
    codes = [
        (await _register(async_client, f"u{i}@example.com")).status_code
        for i in range(22)
    ]
    assert codes.count(201) == 20 and codes[-2:] == [429, 429]


@pytest.mark.asyncio
async def test_resend_attempts_are_capped_separately(async_client, mail):
    await _register(async_client, "resend@example.com")
    codes = [
        (
            await async_client.post(
                "/api/v1/auth/resend-verification",
                json={"email": "resend@example.com"},
            )
        ).status_code
        for _ in range(22)
    ]
    assert codes[:20] == [200] * 20
    assert codes[20:] == [429, 429]
