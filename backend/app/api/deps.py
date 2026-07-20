import uuid
from typing import Annotated

from fastapi import Depends
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from sqlalchemy.orm import Session

from app.core.exceptions import (
    AccountDisabledError,
    AuthenticationRequiredError,
    InvalidTokenError,
    PermissionDeniedError,
)
from app.core.security import decode_access_token
from app.db.deps import get_db
from app.models.enums import UserRole
from app.models.user import User
from app.repositories.user_repository import UserRepository


bearer_scheme = HTTPBearer(
    auto_error=False,
    scheme_name="BearerAuth",
)


def get_current_user(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(bearer_scheme),
    ],
    session: Annotated[Session, Depends(get_db)],
) -> User:
    """Resolve and validate the authenticated application user."""

    if credentials is None:
        raise AuthenticationRequiredError()

    if credentials.scheme.lower() != "bearer":
        raise InvalidTokenError()

    payload = decode_access_token(credentials.credentials)

    try:
        user_id = uuid.UUID(payload.sub)
    except ValueError as exc:
        raise InvalidTokenError() from exc

    user = UserRepository(session).get_by_id(user_id)

    if user is None:
        raise InvalidTokenError()

    if not user.is_active:
        raise AccountDisabledError()

    return user


def require_admin(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Require the authenticated user to have administrator access."""

    if current_user.role != UserRole.ADMIN:
        raise PermissionDeniedError()

    return current_user


CurrentUser = Annotated[User, Depends(get_current_user)]
AdminUser = Annotated[User, Depends(require_admin)]