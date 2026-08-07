from __future__ import annotations

from credibil.core.exceptions import AppError, NotFoundError


class CourtCaseNotFoundError(NotFoundError):
    code = "COURT_CASE_NOT_FOUND"
    message = "Court case not found"

    def __init__(self, identifier: str | None = None) -> None:
        details = {"identifier": identifier} if identifier else {}
        super().__init__(details=details)


class CourtCaseFetchError(AppError):
    code = "COURT_CASE_FETCH_ERROR"
    message = "Failed to fetch court case from instente.justice.md"
    status_code = 502

    def __init__(self, case_number: str, reason: str | None = None) -> None:
        details: dict[str, str | None] = {"case_number": case_number}
        if reason:
            details["reason"] = reason
        super().__init__(details=details)


class CourtSearchError(AppError):
    code = "COURT_SEARCH_ERROR"
    message = "Failed to search court cases on instente.justice.md"
    status_code = 502

    def __init__(self, query: str, reason: str | None = None) -> None:
        details: dict[str, str | None] = {"query": query}
        if reason:
            details["reason"] = reason
        super().__init__(details=details)
