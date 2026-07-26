import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser
from app.db.deps import get_db
from app.models.enums import EnvironmentStatus
from app.schemas.environment import (
    EnvironmentCreateRequest,
    EnvironmentListResponse,
    EnvironmentResponse,
    EnvironmentUpdateRequest,
)
from app.services.environment_service import EnvironmentService


router = APIRouter(
    prefix="/environments",
    tags=["Environments"],
)


@router.post(
    "",
    response_model=EnvironmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create an environment",
    description=(
        "Create a new environment owned by the authenticated user. "
        "New environments begin in the pending state."
    ),
)
def create_environment(
    request: EnvironmentCreateRequest,
    current_user: CurrentUser,
    session: Annotated[Session, Depends(get_db)],
) -> EnvironmentResponse:
    """Create an environment for the authenticated user."""

    return EnvironmentService(session).create_environment(
        current_user=current_user,
        request=request,
    )


@router.get(
    "",
    response_model=EnvironmentListResponse,
    status_code=status.HTTP_200_OK,
    summary="List environments",
    description=(
        "Return a paginated list of environments owned by the "
        "authenticated user. Results may be filtered by status."
    ),
)
def list_environments(
    current_user: CurrentUser,
    session: Annotated[Session, Depends(get_db)],
    page: Annotated[
        int,
        Query(
            ge=1,
            description="Page number to return.",
        ),
    ] = 1,
    page_size: Annotated[
        int,
        Query(
            ge=1,
            le=100,
            description="Maximum number of environments per page.",
        ),
    ] = 20,
    status_filter: Annotated[
        EnvironmentStatus | None,
        Query(
            alias="status",
            description="Filter environments by lifecycle status.",
        ),
    ] = None,
) -> EnvironmentListResponse:
    """List environments owned by the authenticated user."""

    return EnvironmentService(session).list_environments(
        current_user=current_user,
        page=page,
        page_size=page_size,
        status=status_filter,
    )


@router.get(
    "/{environment_id}",
    response_model=EnvironmentResponse,
    status_code=status.HTTP_200_OK,
    summary="Get an environment",
    description=(
        "Return an environment visible to the authenticated user. "
        "Environment owners and administrators may access the resource."
    ),
)
def get_environment(
    environment_id: uuid.UUID,
    current_user: CurrentUser,
    session: Annotated[Session, Depends(get_db)],
) -> EnvironmentResponse:
    """Return an accessible environment by ID."""

    return EnvironmentService(session).get_environment(
        current_user=current_user,
        environment_id=environment_id,
    )


@router.patch(
    "/{environment_id}",
    response_model=EnvironmentResponse,
    status_code=status.HTTP_200_OK,
    summary="Update an environment",
    description=(
        "Update editable fields on an environment. At least one "
        "editable field must be included in the request."
    ),
)
def update_environment(
    environment_id: uuid.UUID,
    request: EnvironmentUpdateRequest,
    current_user: CurrentUser,
    session: Annotated[Session, Depends(get_db)],
) -> EnvironmentResponse:
    """Update an accessible environment."""

    return EnvironmentService(session).update_environment(
        current_user=current_user,
        environment_id=environment_id,
        request=request,
    )