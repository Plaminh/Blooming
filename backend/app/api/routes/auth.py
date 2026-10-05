from typing import Annotated
from fastapi import APIRouter, HTTPException, Request, status, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import SessionDep, EmailServiceDep
from app.schemas.user import UserCreate
from app.schemas.auth import (
    RegisterResponse,
    VerifyEmailRequest,
    ResendVerificationRequest,
)
from app.schemas.token import TokenResponse
from app.services import auth_service
from app.core.rate_limit import (
    login_failures,
    login_requests,
    registration_attempts,
    resend_attempts,
)
from app.core.security import create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])


def _client_host(request: Request) -> str:
    """Use ASGI's peer address; never parse a client-supplied forwarding header."""
    return request.client.host if request.client else "unknown"


@router.post(
    "/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED
)
async def register(
    request: Request,
    user_in: UserCreate,
    db: SessionDep,
    email_service: EmailServiceDep,
):
    """
    Register a new user, auto-provision default settings, and send verification email.
    """
    client = _client_host(request)
    key = f"register:{client}"
    registration_attempts.enforce(key)
    registration_attempts.record(key)
    user = await auth_service.register_user(db, user_in, email_service)
    return RegisterResponse(email=user.email, verification_required=True)


@router.post("/verify-email", response_model=TokenResponse)
async def verify_email(request: VerifyEmailRequest, db: SessionDep):
    user = await auth_service.verify_email(db, request.token)
    access_token = create_access_token(subject=user.id)
    return TokenResponse(access_token=access_token, token_type="bearer")


@router.post("/resend-verification", status_code=status.HTTP_200_OK)
async def resend_verification(
    http_request: Request,
    request: ResendVerificationRequest,
    db: SessionDep,
    email_service: EmailServiceDep,
):
    client = _client_host(http_request)
    key = f"resend:{client}"
    resend_attempts.enforce(key)
    resend_attempts.record(key)
    await auth_service.resend_verification(db, request.email, email_service)
    return {"message": "If the account exists, a verification email has been resent."}


@router.post("/login", response_model=TokenResponse)
async def login(
    request: Request,
    db: SessionDep,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
):
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    client = _client_host(request)
    email = form_data.username.strip().casefold()
    request_key = f"login-request:{client}"
    failure_key = f"login-failure:{client}:{email}"
    login_requests.enforce(request_key)
    login_failures.enforce(failure_key)
    login_requests.record(request_key)
    try:
        user = await auth_service.authenticate(db, form_data)
    except HTTPException as exc:
        if exc.status_code == status.HTTP_401_UNAUTHORIZED:
            login_failures.record(failure_key)
        raise
    login_failures.reset(failure_key)
    access_token = create_access_token(subject=user.id)
    return TokenResponse(access_token=access_token, token_type="bearer")
