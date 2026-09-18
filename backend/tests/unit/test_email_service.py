from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest
from pydantic import SecretStr

from app.services import email_service


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("status_code", "expected_error"),
    [
        (401, email_service.EmailConfigurationError),
        (400, email_service.EmailDeliveryError),
    ],
)
async def test_brevo_http_errors_are_classified(
    monkeypatch, status_code, expected_error
):
    monkeypatch.setattr(email_service.settings, "BREVO_API_KEY", SecretStr("test-key"))
    monkeypatch.setattr(
        email_service.settings, "BREVO_SENDER_EMAIL", "sender@example.com"
    )
    response = httpx.Response(
        status_code,
        request=httpx.Request("POST", "https://api.brevo.com/v3/smtp/email"),
        json={"code": "unauthorized"},
    )
    client = MagicMock()
    client.post = AsyncMock(return_value=response)
    context = AsyncMock()
    context.__aenter__.return_value = client
    monkeypatch.setattr(email_service.httpx, "AsyncClient", lambda **_: context)

    with pytest.raises(expected_error):
        await email_service.BrevoEmailService().send_verification_email(
            "recipient@example.com", "token"
        )
