import httpx

from app.core.config import settings


class EmailConfigurationError(Exception):
    pass


class EmailDeliveryError(Exception):
    pass


class EmailService:
    async def send_verification_email(self, to_email: str, raw_token: str) -> None:
        raise NotImplementedError


class BrevoEmailService(EmailService):
    async def send_verification_email(self, to_email: str, raw_token: str) -> None:
        if not settings.BREVO_API_KEY or not settings.BREVO_SENDER_EMAIL:
            raise EmailConfigurationError("Email service is not properly configured.")

        link = f"{settings.EMAIL_VERIFICATION_FRONTEND_URL}?token={raw_token}"

        url = "https://api.brevo.com/v3/smtp/email"
        headers = {
            "api-key": settings.BREVO_API_KEY.get_secret_value(),
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        sender = {"email": settings.BREVO_SENDER_EMAIL}
        if settings.BREVO_SENDER_NAME:
            sender["name"] = settings.BREVO_SENDER_NAME

        payload = {
            "sender": sender,
            "to": [{"email": to_email}],
            "subject": "Verify your Blooming account",
            "textContent": f"Please verify your email by clicking the following link:\n\n{link}",
            "htmlContent": f'<p>Please verify your email by clicking the following link:</p><p><a href="{link}">{link}</a></p>',
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(url, headers=headers, json=payload)
                response.raise_for_status()
        except httpx.HTTPError as e:
            raise EmailDeliveryError("Failed to send email via Brevo API") from e
