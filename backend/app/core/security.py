import uuid
from datetime import datetime, timedelta, timezone
from typing import Any
import jwt
import bcrypt

from app.core.config import settings

ALGORITHM = "HS256"


def get_password_hash(password: str) -> str:
    """Hash a password securely using bcrypt."""
    pwd_bytes = password.encode("utf-8")
    if len(pwd_bytes) > 72:
        raise ValueError("Password must not exceed 72 bytes")
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hash."""
    pwd_bytes = plain_password.encode("utf-8")
    hash_bytes = hashed_password.encode("utf-8")
    try:
        return bcrypt.checkpw(pwd_bytes, hash_bytes)
    except ValueError:
        return False


def dummy_verify() -> None:
    """Perform a dummy verify to reduce timing differences for unknown users."""
    verify_password(
        "dummy", "$2b$12$2l48uQDbUelET6BV7HFzre82gYRoQu0nfxq8ka9rSpb9x5mkZVtDG"
    )


def create_access_token(subject: str | uuid.UUID) -> str:
    """Create a JWT access token for the given subject (user ID)."""
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"exp": expire, "iat": now, "sub": str(subject), "type": "access"}
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY.get_secret_value(), algorithm=ALGORITHM
    )
    return encoded_jwt


def decode_access_token(token: str) -> dict[str, Any] | None:
    """Decode a JWT token, returning the payload if valid."""
    try:
        decoded = jwt.decode(
            token, settings.SECRET_KEY.get_secret_value(), algorithms=[ALGORITHM]
        )
        if decoded.get("type") != "access":
            return None
        # Verify sub is UUID
        sub = decoded.get("sub")
        if not sub:
            return None
        try:
            uuid.UUID(sub)
        except ValueError:
            return None
        return decoded
    except jwt.PyJWTError:
        return None
