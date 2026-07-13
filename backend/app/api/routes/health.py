from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel

from app.core.config import settings


router = APIRouter(prefix="/health", tags=["Health"])


class LivenessResponse(BaseModel):
    status: Literal["ok"]
    service: str
    version: str
    environment: str


@router.get(
    "/live",
    response_model=LivenessResponse,
    summary="Check API process liveness",
)
def liveness_check() -> LivenessResponse:
    """Confirm that the FastAPI process is running."""

    return LivenessResponse(
        status="ok",
        service=settings.app_name,
        version=settings.app_version,
        environment=settings.app_environment,
    )