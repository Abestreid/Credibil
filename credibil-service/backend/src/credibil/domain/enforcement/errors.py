from __future__ import annotations

from credibil.core.exceptions import AppError, NotFoundError


class EnforcementProceedingNotFoundError(NotFoundError):
    code = "ENFORCEMENT_PROCEEDING_NOT_FOUND"
    message = "Enforcement proceeding not found"

    def __init__(self, identifier: str | None = None) -> None:
        details = {"identifier": identifier} if identifier else {}
        super().__init__(details=details)


class EnforcementFetchError(AppError):
    code = "ENFORCEMENT_FETCH_ERROR"
    message = "Failed to fetch enforcement data from unej.md"
    status_code = 502

    def __init__(self, target: str, reason: str | None = None) -> None:
        details: dict[str, str | None] = {"target": target}
        if reason:
            details["reason"] = reason
        super().__init__(details=details)
