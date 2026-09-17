from pydantic import BaseModel, EmailStr, Field

class RegisterResponse(BaseModel):
    email: EmailStr
    verification_required: bool

class VerifyEmailRequest(BaseModel):
    token: str = Field(min_length=32, max_length=128)

class ResendVerificationRequest(BaseModel):
    email: EmailStr
