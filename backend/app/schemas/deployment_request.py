import uuid
from datetime import datetime
from typing import Any

from pydantic import Field

from app.models.enums import (
    DeploymentOperation,
    DeploymentRequestStatus,
)
from app.schemas.common import APIModel, PaginatedResponse


class DeploymentRequestCreateRequest(APIModel):
    """Request body for queuing an environment lifecycle operation."""

    operation: DeploymentOperation
    request_payload: dict[str, Any] = Field(default_factory=dict)


class DeploymentRequestResponse(APIModel):
    id: uuid.UUID
    environment_id: uuid.UUID
    requested_by_id: uuid.UUID
    operation: DeploymentOperation
    status: DeploymentRequestStatus
    attempt_count: int
    error_message: str | None = None
    request_payload: dict[str, Any]
    requested_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None
    updated_at: datetime


class DeploymentRequestListResponse(
    PaginatedResponse[DeploymentRequestResponse]
):
    pass