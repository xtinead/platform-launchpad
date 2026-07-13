from typing import Literal

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.core.config import settings
from app.db.health import check_database_connection


router = APIRouter(prefix="/health", tags=["Health"])


class LivenessResponse(BaseModel):
    status: Literal["ok"]
    service: str
    version: str
    environment: str


class ReadinessChecks(BaseModel):
    database: Literal["ok", "unavailable"]


class ReadinessResponse(BaseModel):
    status: Literal["ready"]
    checks: ReadinessChecks


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


@router.get(
    "/ready",
    response_model=ReadinessResponse,
    responses={
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            "description": "A required dependency is unavailable",
        }
    },
    summary="Check API readiness",
)
def readiness_check() -> ReadinessResponse | JSONResponse:
    """Confirm that required dependencies are available."""

    if not check_database_connection():
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "error": {
                    "code": "service_unavailable",
                    "message": "The service is not ready to receive traffic.",
                    "details": {
                        "database": "unavailable",
                    },
                    "request_id": "not-yet-implemented",
                }
            },
        )

    return ReadinessResponse(
        status="ready",
        checks=ReadinessChecks(database="ok"),
    )