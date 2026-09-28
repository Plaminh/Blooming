from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr, ConfigDict, Field, field_validator


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    display_name: str | None = Field(default=None, max_length=100)

    @field_validator("password")
    @classmethod
    def password_max_length(cls, v: str) -> str:
        if len(v.encode("utf-8")) > 72:
            raise ValueError("Password must not exceed 72 bytes")
        return v


class UserUpdate(BaseModel):
    display_name: str | None = Field(default=None, max_length=100)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: EmailStr
    display_name: str | None
    email_verified_at: datetime | None = None
    created_at: datetime
