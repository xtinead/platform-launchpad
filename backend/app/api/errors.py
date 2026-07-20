from fastapi import Request
from fastapi.responses import JSONResponse

from app.core.exceptions import ApplicationError


async def application_error_handler(
    request: Request,
    exc: ApplicationError,
) -> JSONResponse:
    """Convert an application exception into the API error envelope."""

    request_id = getattr(
        request.state,
        "request_id",
        "unavailable",
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
        headers={
            "X-Request-ID": request_id,
        },
    )