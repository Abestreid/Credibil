from __future__ import annotations

import time
import uuid
from typing import TYPE_CHECKING

import structlog
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

if TYPE_CHECKING:
    from fastapi import Request, Response

logger = structlog.get_logger("audit")


class AuditLogMiddleware(BaseHTTPMiddleware):
    """Logs every request/response for audit trail."""

    SKIP_PATHS = {"/health", "/health/ready", "/health/live", "/docs", "/redoc", "/openapi.json"}

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.url.path in self.SKIP_PATHS:
            return await call_next(request)

        request_id = str(uuid.uuid4())
        start = time.perf_counter()

        forwarded = request.headers.get("X-Forwarded-For")
        client_ip = (
            forwarded.split(",")[0].strip()
            if forwarded
            else (request.client.host if request.client else "unknown")
        )

        response = await call_next(request)
        duration_ms = round((time.perf_counter() - start) * 1000, 2)

        log_data = {
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": duration_ms,
            "client_ip": client_ip,
            "user_agent": request.headers.get("User-Agent", "")[:200],
        }

        if response.status_code >= 500:
            logger.error("audit.request", **log_data)
        elif response.status_code >= 400:
            logger.warning("audit.request", **log_data)
        else:
            logger.info("audit.request", **log_data)

        response.headers["X-Request-ID"] = request_id
        return response
