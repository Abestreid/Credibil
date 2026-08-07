from __future__ import annotations

from credibil.core.exceptions import AppError, NotFoundError


class FinancialReportNotFoundError(NotFoundError):
    code = "FINANCIAL_REPORT_NOT_FOUND"
    message = "Financial report not found"

    def __init__(self, identifier: str | None = None) -> None:
        details = {"identifier": identifier} if identifier else {}
        super().__init__(details=details)


class FinancialReportFetchError(AppError):
    code = "FINANCIAL_REPORT_FETCH_ERROR"
    message = "Failed to fetch financial report from statistica.md"
    status_code = 502

    def __init__(self, idno: str, reason: str | None = None) -> None:
        details: dict[str, str | None] = {"idno": idno}
        if reason:
            details["reason"] = reason
        super().__init__(details=details)


class FinancialReportValidationError(AppError):
    code = "FINANCIAL_REPORT_VALIDATION_ERROR"
    message = "Financial report validation failed"
    status_code = 422
