from __future__ import annotations

from credibil.core.exceptions import ConflictError, NotFoundError


class OrganizationNotFoundError(NotFoundError):
    code = "ORGANIZATION_NOT_FOUND"
    message = "Organization not found"

    def __init__(self, identifier: str | None = None) -> None:
        details = {"identifier": identifier} if identifier else {}
        super().__init__(details=details)


class OrganizationAlreadyExistsError(ConflictError):
    code = "ORGANIZATION_ALREADY_EXISTS"
    message = "Organization with this slug already exists"

    def __init__(self, slug: str) -> None:
        super().__init__(details={"slug": slug})


class OrganizationValidationError(NotFoundError):
    code = "ORGANIZATION_VALIDATION_ERROR"
    message = "Organization validation failed"
    status_code = 422
