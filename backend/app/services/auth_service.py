from datetime import UTC, datetime

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import (
    AccountDisabledError,
    EmailAlreadyRegisteredError,
    InvalidCredentialsError,
)
from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.models.enums import UserRole
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginRequest, LoginResponse
from app.schemas.user import (
    UserRegistrationRequest,
    UserResponse,
    UserSummary,
)


class AuthService:
    """User registration and authentication business logic."""

    def __init__(self, session: Session) -> None:
        self.session = session
        self.users = UserRepository(session)

    def register_user(
        self,
        request: UserRegistrationRequest,
    ) -> UserResponse:
        existing_user = self.users.get_by_email(str(request.email))

        if existing_user is not None:
            raise EmailAlreadyRegisteredError()

        user = User(
            email=str(request.email).lower(),
            password_hash=hash_password(
                request.password.get_secret_value(),
            ),
            full_name=request.full_name,
            role=UserRole.USER,
            is_active=True,
        )

        try:
            self.users.add(user)
            self.session.commit()
            self.session.refresh(user)
        except IntegrityError as exc:
            self.session.rollback()
            raise EmailAlreadyRegisteredError() from exc
        except Exception:
            self.session.rollback()
            raise

        return UserResponse.model_validate(user)

    def authenticate(
        self,
        request: LoginRequest,
    ) -> LoginResponse:
        user = self.users.get_by_email(str(request.email))

        if user is None:
            raise InvalidCredentialsError()

        if not verify_password(
            request.password.get_secret_value(),
            user.password_hash,
        ):
            raise InvalidCredentialsError()

        if not user.is_active:
            raise AccountDisabledError()

        user.last_login_at = datetime.now(UTC)

        try:
            self.session.commit()
            self.session.refresh(user)
        except Exception:
            self.session.rollback()
            raise

        access_token, expires_in = create_access_token(
            subject=str(user.id),
            role=user.role,
        )

        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=expires_in,
            user=UserSummary.model_validate(user),
        )