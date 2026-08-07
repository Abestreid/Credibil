from __future__ import annotations

import time
import uuid
from typing import TYPE_CHECKING

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from credibil.api.middleware.audit import AuditLogMiddleware
from credibil.api.middleware.rate_limit import RateLimitMiddleware
from credibil.api.middleware.security import SecurityHeadersMiddleware

if TYPE_CHECKING:
    from fastapi import Request
    from starlette.responses import Response


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


class TimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        response.headers["X-Response-Time"] = f"{duration_ms}ms"
        return response


__all__ = [
    "AuditLogMiddleware",
    "RateLimitMiddleware",
    "RequestIDMiddleware",
    "SecurityHeadersMiddleware",
    "TimingMiddleware",
]
