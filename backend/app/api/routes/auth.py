from fastapi import APIRouter, status

from app.db.deps import DatabaseSession
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
)
from app.schemas.user import (
    UserRegistrationRequest,
    UserResponse,
)
from app.services.auth_service import AuthService


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a user",
)
def register_user(
    request: UserRegistrationRequest,
    session: DatabaseSession,
) -> UserResponse:
    """Register a regular Platform Launchpad user."""

    return AuthService(session).register_user(request)


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="Authenticate a user",
)
def login_user(
    request: LoginRequest,
    session: DatabaseSession,
) -> LoginResponse:
    """Authenticate a user and issue an access token."""

    return AuthService(session).authenticate(request)