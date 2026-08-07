from __future__ import annotations

from credibil.core.exceptions import NotFoundError


class APIKeyNotFoundError(NotFoundError):
    code = "API_KEY_NOT_FOUND"
    message = "API key not found"

    def __init__(self, identifier: str | None = None) -> None:
        details = {"identifier": identifier} if identifier else {}
        super().__init__(details=details)


class APIKeyValidationError(NotFoundError):
    code = "API_KEY_VALIDATION_ERROR"
    message = "API key validation failed"
    status_code = 422
