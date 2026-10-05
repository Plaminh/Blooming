import uuid
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
import jwt
from fastapi import HTTPException

from app.core.config import settings
from app.core.security import (
    ALGORITHM,
    create_access_token,
    decode_access_token,
    get_password_hash,
)
from app.services import auth_service


def login_form(email: str, password: str):
    return SimpleNamespace(username=email, password=password)


@pytest.mark.asyncio
async def test_verified_active_user_can_login(monkeypatch):
    user = SimpleNamespace(
        id=uuid.uuid4(),
        password_hash=get_password_hash('Password123!'),
        email_verified_at=datetime.now(timezone.utc),
        account_status='ACTIVE',
        last_login_at=None,
    )
    monkeypatch.setattr(auth_service, 'get_user_by_email', AsyncMock(return_value=user))
    db = AsyncMock()

    authenticated = await auth_service.authenticate(
        db, login_form('  USER@Example.COM ', 'Password123!')
    )

    assert authenticated is user
    auth_service.get_user_by_email.assert_awaited_once_with(db, 'user@example.com')
    assert user.last_login_at is not None
    db.commit.assert_awaited_once()
    db.refresh.assert_awaited_once_with(user)


@pytest.mark.asyncio
@pytest.mark.parametrize('user,password', [(None, 'Password123!'), ('known', 'wrong')])
async def test_unknown_user_and_wrong_password_share_generic_401(monkeypatch, user, password):
    stored_user = None if user is None else SimpleNamespace(
        password_hash=get_password_hash('Password123!')
    )
    monkeypatch.setattr(auth_service, 'get_user_by_email', AsyncMock(return_value=stored_user))

    with pytest.raises(HTTPException) as caught:
        await auth_service.authenticate(AsyncMock(), login_form('user@example.com', password))

    assert caught.value.status_code == 401
    assert caught.value.detail == 'Incorrect email or password'


@pytest.mark.asyncio
async def test_unverified_user_is_rejected_without_issuing_a_session(monkeypatch):
    user = SimpleNamespace(
        password_hash=get_password_hash('Password123!'),
        email_verified_at=None,
        account_status='ACTIVE',
    )
    monkeypatch.setattr(auth_service, 'get_user_by_email', AsyncMock(return_value=user))

    with pytest.raises(HTTPException) as caught:
        await auth_service.authenticate(
            AsyncMock(), login_form('user@example.com', 'Password123!')
        )

    assert caught.value.status_code == 403
    assert caught.value.detail == 'EMAIL_NOT_VERIFIED'


def test_access_token_round_trip_and_invalid_token_rejection():
    user_id = uuid.uuid4()
    payload = decode_access_token(create_access_token(user_id))
    assert payload is not None
    assert payload['sub'] == str(user_id)
    assert payload['type'] == 'access'
    assert decode_access_token('not-a-jwt') is None

    expired = jwt.encode(
        {
            "sub": str(user_id),
            "type": "access",
            "exp": datetime.now(timezone.utc) - timedelta(seconds=1),
        },
        settings.SECRET_KEY.get_secret_value(),
        algorithm=ALGORITHM,
    )
    assert decode_access_token(expired) is None


@pytest.mark.asyncio
async def test_password_worker_exceptions_are_not_swallowed(monkeypatch):
    user = SimpleNamespace(password_hash="broken")
    monkeypatch.setattr(auth_service, "get_user_by_email", AsyncMock(return_value=user))

    def fail_verify(_password, _hash):
        raise RuntimeError("password worker failed")

    monkeypatch.setattr(auth_service, "verify_password", fail_verify)
    with pytest.raises(RuntimeError, match="password worker failed"):
        await auth_service.authenticate(
            AsyncMock(), login_form("user@example.com", "Password123!")
        )
