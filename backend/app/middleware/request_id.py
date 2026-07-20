import uuid
from collections.abc import Awaitable, Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


REQUEST_ID_HEADER = "X-Request-ID"


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Attach a correlation identifier to every HTTP request."""

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        """Resolve a request ID and add it to request and response state."""

        request_id = self._resolve_request_id(
            request.headers.get(REQUEST_ID_HEADER)
        )

        request.state.request_id = request_id

        response = await call_next(request)
        response.headers[REQUEST_ID_HEADER] = request_id

        return response

    @staticmethod
    def _resolve_request_id(candidate: str | None) -> str:
        """Accept a valid UUID request ID or generate a new one."""

        if candidate is not None:
            try:
                return str(uuid.UUID(candidate))
            except ValueError:
                pass

        return str(uuid.uuid4())