"""Shared FastAPI dependencies."""

import logging
import uuid
from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_access_token
from app.db.models.users import User
from app.db.session import AsyncSessionLocal
from app.services.email_service import BrevoEmailService, EmailService


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield one session per request, rolling back and closing on the way out."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as exc:
            await session.rollback()
            if not isinstance(exc, HTTPException):
                logging.getLogger(__name__).error("transaction_failed", extra={"error_type": type(exc).__name__})
            raise

SessionDep = Annotated[AsyncSession, Depends(get_db_session)]

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login"
)

TokenDep = Annotated[str, Depends(reusable_oauth2)]

async def get_current_user(session: SessionDep, token: TokenDep) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
        
    user_id_str: str | None = payload.get("sub")
    if user_id_str is None:
        raise credentials_exception
        
    try:
        user_id = uuid.UUID(user_id_str)
    except ValueError:
        raise credentials_exception
        
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if user is None:
        raise credentials_exception
        
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
        
    return user

CurrentUser = Annotated[User, Depends(get_current_user)]

def get_email_service() -> EmailService:
    return BrevoEmailService()

EmailServiceDep = Annotated[EmailService, Depends(get_email_service)]
