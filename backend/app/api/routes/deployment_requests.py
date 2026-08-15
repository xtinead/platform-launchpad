import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser
from app.db.deps import get_db
from app.models.enums import (
    DeploymentOperation,
    DeploymentRequestStatus,
)
from app.schemas.deployment_request import (
    DeploymentRequestListResponse,
    DeploymentRequestResponse,
)
from app.services.deployment_request_service import (
    DeploymentRequestService,
)


router = APIRouter(
    prefix="/deployment-requests",
    tags=["Deployment Requests"],
)


@router.get(
    "",
    response_model=DeploymentRequestListResponse,
    status_code=status.HTTP_200_OK,
    summary="List deployment requests",
    description=(
        "Return deployment requests for environments owned by the "
        "authenticated user. Results may be filtered by deployment "
        "status and operation."
    ),
)
def list_deployment_requests(
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
            description="Maximum number of requests per page.",
        ),
    ] = 20,
    status_filter: Annotated[
        DeploymentRequestStatus | None,
        Query(
            alias="status",
            description="Filter by deployment-request status.",
        ),
    ] = None,
    operation_filter: Annotated[
        DeploymentOperation | None,
        Query(
            alias="operation",
            description="Filter by deployment operation.",
        ),
    ] = None,
) -> DeploymentRequestListResponse:
    """List deployment requests visible to the current user."""

    return DeploymentRequestService(session).list_requests(
        current_user=current_user,
        page=page,
        page_size=page_size,
        status=status_filter,
        operation=operation_filter,
    )


@router.get(
    "/{deployment_request_id}",
    response_model=DeploymentRequestResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a deployment request",
    description=(
        "Return a deployment request visible to the authenticated "
        "environment owner or an administrator."
    ),
)
def get_deployment_request(
    deployment_request_id: uuid.UUID,
    current_user: CurrentUser,
    session: Annotated[Session, Depends(get_db)],
) -> DeploymentRequestResponse:
    """Return an accessible deployment request by ID."""

    return DeploymentRequestService(session).get_request(
        current_user=current_user,
        deployment_request_id=deployment_request_id,
    )