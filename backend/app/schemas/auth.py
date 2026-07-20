from pydantic import EmailStr, SecretStr, field_validator

from app.schemas.common import APIModel
from app.schemas.user import UserSummary


class LoginRequest(APIModel):
    email: EmailStr
    password: SecretStr

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr) -> str:
        return str(value).strip().lower()


class TokenPayload(APIModel):
    sub: str
    role: str
    type: str
    iat: int
    exp: int


class LoginResponse(APIModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserSummary