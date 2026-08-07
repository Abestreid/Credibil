from __future__ import annotations

from credibil.core.exceptions import AppError, ConflictError, NotFoundError


class CompanyNotFoundError(NotFoundError):
    code = "COMPANY_NOT_FOUND"
    message = "Company not found"

    def __init__(self, identifier: str | None = None) -> None:
        details = {"identifier": identifier} if identifier else {}
        super().__init__(details=details)


class CompanyAlreadyExistsError(ConflictError):
    code = "COMPANY_ALREADY_EXISTS"
    message = "Company with this IDNO already exists"

    def __init__(self, idno: str) -> None:
        super().__init__(details={"idno": idno})


class CompanyValidationError(AppError):
    code = "COMPANY_VALIDATION_ERROR"
    message = "Company validation failed"
    status_code = 422
