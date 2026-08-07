from __future__ import annotations

from credibil.core.exceptions import AppError, NotFoundError


class AccreditationNotFoundError(NotFoundError):
    code = "ACCREDITATION_NOT_FOUND"
    message = "Accreditation not found"

    def __init__(self, identifier: str | None = None) -> None:
        details = {"identifier": identifier} if identifier else {}
        super().__init__(details=details)


class AccreditationFetchError(AppError):
    code = "ACCREDITATION_FETCH_ERROR"
    message = "Failed to fetch accreditation data from acreditare.md"
    status_code = 502

    def __init__(self, reason: str | None = None) -> None:
        details: dict[str, str | None] = {}
        if reason:
            details["reason"] = reason
        super().__init__(details=details)
