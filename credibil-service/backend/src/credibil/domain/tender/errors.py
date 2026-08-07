from __future__ import annotations

from credibil.core.exceptions import AppError, NotFoundError


class TenderNotFoundError(NotFoundError):
    code = "TENDER_NOT_FOUND"
    message = "Tender not found"

    def __init__(self, identifier: str | None = None) -> None:
        details = {"identifier": identifier} if identifier else {}
        super().__init__(details=details)


class TenderFetchError(AppError):
    code = "TENDER_FETCH_ERROR"
    message = "Failed to fetch tender from mtender.gov.md"
    status_code = 502

    def __init__(self, ocid: str, reason: str | None = None) -> None:
        details: dict[str, str | None] = {"ocid": ocid}
        if reason:
            details["reason"] = reason
        super().__init__(details=details)


class TenderSyncError(AppError):
    code = "TENDER_SYNC_ERROR"
    message = "Failed to sync tenders from mtender.gov.md"
    status_code = 502

    def __init__(self, reason: str | None = None) -> None:
        details: dict[str, str | None] = {}
        if reason:
            details["reason"] = reason
        super().__init__(details=details)
