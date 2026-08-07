from __future__ import annotations

from typing import TYPE_CHECKING, Any

from fastapi.responses import JSONResponse

if TYPE_CHECKING:
    from fastapi import FastAPI


class AppError(Exception):
    """Base application error."""

    status_code: int = 500
    code: str = "INTERNAL_ERROR"
    message: str = "An unexpected error occurred"

    def __init__(self, message: str | None = None, details: dict[str, Any] | None = None):
        self.message = message or self.__class__.message
        self.details = details or {}
        super().__init__(self.message)


class NotFoundError(AppError):
    status_code = 404
    code = "NOT_FOUND"
    message = "Resource not found"


class ConflictError(AppError):
    status_code = 409
    code = "CONFLICT"
    message = "Resource already exists"


class ValidationError(AppError):
    status_code = 422
    code = "VALIDATION_ERROR"
    message = "Validation failed"


class UnauthorizedError(AppError):
    status_code = 401
    code = "UNAUTHORIZED"
    message = "Authentication required"


class ForbiddenError(AppError):
    status_code = 403
    code = "FORBIDDEN"
    message = "Insufficient permissions"


class RateLimitError(AppError):
    status_code = 429
    code = "RATE_LIMITED"
    message = "Rate limit exceeded"


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def app_error_handler(request: Any, exc: AppError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "details": exc.details,
                },
                "request_id": getattr(request.state, "request_id", None),
            },
        )
