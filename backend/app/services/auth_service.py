import secrets
import hashlib
import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete, select, update
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.config import settings
from app.core.security import verify_password, dummy_verify, get_password_hash
from app.db.models.users import User, EmailVerificationToken, UserSettings
from app.schemas.user import UserCreate
from app.services.user_service import get_user_by_email
from app.services.email_service import (
    EmailService,
    EmailConfigurationError,
    EmailDeliveryError,
)

logger = logging.getLogger(__name__)


async def authenticate(db: AsyncSession, form_data: OAuth2PasswordRequestForm) -> User:
    generic_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect email or password",
        headers={"WWW-Authenticate": "Bearer"},
    )

    email = form_data.username.strip().casefold()
    user = await get_user_by_email(db, email)
    if not user:
        dummy_verify()
        raise generic_error

    if not verify_password(form_data.password, user.password_hash):
        raise generic_error

    if not user.email_verified_at:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="EMAIL_NOT_VERIFIED",
        )

    if user.account_status != "ACTIVE":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is not active",
        )

    user.last_login_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(user)
    return user


async def register_user(
    db: AsyncSession, user_in: UserCreate, email_service: EmailService
) -> User:
    email = user_in.email.strip().casefold()
    existing_user = await get_user_by_email(db, email)
    if existing_user and existing_user.email_verified_at is None:
        # A retry after a lost or failed verification email must lead the
        # user to "resend", not to a dead end. The password is not changed:
        # only whoever controls the mailbox can finish the original account.
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "EMAIL_NOT_VERIFIED",
                "message": "This email is registered but not verified yet. Check your inbox or resend the verification email.",
            },
        )
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email already registered."
        )

    hashed_password = get_password_hash(user_in.password)

    db_user = User(
        email=email, password_hash=hashed_password, display_name=user_in.display_name
    )
    try:
        db.add(db_user)
        await db.flush()

        db_settings = UserSettings(user_id=db_user.id)
        db.add(db_settings)

        raw_token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
        expires_at = datetime.now(timezone.utc) + timedelta(
            minutes=settings.EMAIL_VERIFICATION_EXPIRE_MINUTES
        )

        db_token = EmailVerificationToken(
            user_id=db_user.id, token_hash=token_hash, expires_at=expires_at
        )
        db.add(db_token)
        await db.commit()
        await db.refresh(db_user)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Could not register user due to a conflict.",
        )

    try:
        await email_service.send_verification_email(email, raw_token)
    except EmailConfigurationError as e:
        logger.error(f"Email configuration error for user {db_user.id}: {str(e)}")
        await db.execute(
            delete(EmailVerificationToken).where(
                EmailVerificationToken.id == db_token.id
            )
        )
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Email service configuration is invalid. Please contact the administrator.",
        )
    except EmailDeliveryError as e:
        logger.error(
            f"Failed to send verification email for user {db_user.id}: {str(e)}"
        )
        await db.execute(
            delete(EmailVerificationToken).where(
                EmailVerificationToken.id == db_token.id
            )
        )
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Account created, but verification email failed to send. Please use resend verification.",
        )
    return db_user


async def verify_email(db: AsyncSession, raw_token: str) -> User:
    token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
    now = datetime.now(timezone.utc)

    # Conditional update for atomicity
    result = await db.execute(
        update(EmailVerificationToken)
        .where(EmailVerificationToken.token_hash == token_hash)
        .where(EmailVerificationToken.used_at.is_(None))
        .where(EmailVerificationToken.expires_at > now)
        .values(used_at=now)
        .returning(EmailVerificationToken.user_id)
    )
    user_id = result.scalars().first()

    if not user_id:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    user_result = await db.execute(select(User).where(User.id == user_id))
    user = user_result.scalars().first()
    if not user:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    user.email_verified_at = now

    await db.execute(
        update(EmailVerificationToken)
        .where(EmailVerificationToken.user_id == user.id)
        .where(EmailVerificationToken.used_at.is_(None))
        .values(used_at=now)
    )

    await db.commit()
    await db.refresh(user)
    return user


async def resend_verification(
    db: AsyncSession, email: str, email_service: EmailService
) -> None:
    email = email.strip().casefold()

    # Lock the user row for update to prevent concurrent resends
    user_result = await db.execute(
        select(User).where(User.email == email).with_for_update()
    )
    user = user_result.scalars().first()

    if not user or user.email_verified_at:
        await db.rollback()
        return

    result = await db.execute(
        select(EmailVerificationToken)
        .where(EmailVerificationToken.user_id == user.id)
        .order_by(EmailVerificationToken.created_at.desc())
    )
    last_token = result.scalars().first()

    now = datetime.now(timezone.utc)
    if last_token:
        elapsed = (now - last_token.created_at).total_seconds()
        if elapsed < settings.EMAIL_VERIFICATION_RESEND_COOLDOWN_SECONDS:
            await db.rollback()
            return

    raw_token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
    expires_at = now + timedelta(minutes=settings.EMAIL_VERIFICATION_EXPIRE_MINUTES)

    try:
        await email_service.send_verification_email(user.email, raw_token)
    except EmailConfigurationError as e:
        logger.error(f"Email configuration error for resend user {user.id}: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Email service configuration is invalid. Please contact the administrator.",
        )
    except EmailDeliveryError as e:
        logger.error(
            f"Failed to resend verification email for user {user.id}: {str(e)}"
        )
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to resend verification email.",
        )

    # Email sent successfully, invalidate old tokens
    await db.execute(
        update(EmailVerificationToken)
        .where(EmailVerificationToken.user_id == user.id)
        .where(EmailVerificationToken.used_at.is_(None))
        .values(used_at=now)
    )

    new_token = EmailVerificationToken(
        user_id=user.id, token_hash=token_hash, expires_at=expires_at
    )
    db.add(new_token)

    await db.commit()
