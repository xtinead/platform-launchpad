from typing import Any


class ApplicationError(Exception):
    """Base exception for expected application failures."""

    status_code: int = 500
    code: str = "internal_server_error"
    message: str = "An unexpected error occurred."

    def __init__(
        self,
        *,
        message: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.message = message or self.message
        self.details = details or {}
        super().__init__(self.message)


class EmailAlreadyRegisteredError(ApplicationError):
    status_code = 409
    code = "email_already_registered"
    message = "An account with this email address already exists."


class InvalidCredentialsError(ApplicationError):
    status_code = 401
    code = "invalid_credentials"
    message = "The email or password is incorrect."


class AccountDisabledError(ApplicationError):
    status_code = 403
    code = "account_disabled"
    message = "This account is disabled."


class AuthenticationRequiredError(ApplicationError):
    status_code = 401
    code = "authentication_required"
    message = "Authentication is required."


class InvalidTokenError(ApplicationError):
    status_code = 401
    code = "invalid_token"
    message = "The access token is invalid."


class TokenExpiredError(ApplicationError):
    status_code = 401
    code = "token_expired"
    message = "The access token has expired."


class PermissionDeniedError(ApplicationError):
    status_code = 403
    code = "permission_denied"
    message = "You do not have permission to perform this operation."