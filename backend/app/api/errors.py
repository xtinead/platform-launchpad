from fastapi import Request
from fastapi.responses import JSONResponse

from app.core.exceptions import ApplicationError


async def application_error_handler(
    request: Request,
    exc: ApplicationError,
) -> JSONResponse:
    """Convert expected application exceptions to the API error envelope."""

    request_id = getattr(
        request.state,
        "request_id",
        "not-yet-implemented",
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
                "request_id": request_id,
            }
        },
    )