from fastapi import APIRouter

from app.api.deps import CurrentUser
from app.schemas.user import UserResponse


router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get the current user",
)
def get_current_user_profile(
    current_user: CurrentUser,
) -> UserResponse:
    """Return the authenticated user's profile."""

    return UserResponse.model_validate(current_user)