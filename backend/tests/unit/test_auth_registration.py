from unittest.mock import AsyncMock, Mock

import pytest
from fastapi import HTTPException

from app.schemas.user import UserCreate
from app.services import auth_service
from app.services.email_service import EmailConfigurationError, EmailDeliveryError


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("email_error", "expected_status"),
    [
        (EmailConfigurationError("missing configuration"), 503),
        (EmailDeliveryError("provider rejected request"), 502),
    ],
)
async def test_failed_registration_email_removes_unsent_token(
    monkeypatch, email_error, expected_status
):
    db = AsyncMock()
    db.add = Mock()
    email_service = AsyncMock()
    email_service.send_verification_email.side_effect = email_error
    monkeypatch.setattr(auth_service, "get_user_by_email", AsyncMock(return_value=None))
    monkeypatch.setattr(auth_service, "get_password_hash", lambda _: "hashed")

    with pytest.raises(HTTPException) as exc:
        await auth_service.register_user(
            db,
            UserCreate(email="test@example.com", password="password123"),
            email_service,
        )

    assert exc.value.status_code == expected_status
    assert db.commit.await_count == 2
    assert db.execute.await_count == 1
    assert "DELETE FROM email_verification_tokens" in str(db.execute.await_args.args[0])
