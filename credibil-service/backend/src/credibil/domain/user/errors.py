from __future__ import annotations

from credibil.core.exceptions import AppError, ConflictError, NotFoundError


class UserNotFoundError(NotFoundError):
    code = "USER_NOT_FOUND"
    message = "User not found"

    def __init__(self, identifier: str | None = None) -> None:
        details = {"identifier": identifier} if identifier else {}
        super().__init__(details=details)


class UserAlreadyExistsError(ConflictError):
    code = "USER_ALREADY_EXISTS"
    message = "User with this email already exists"

    def __init__(self, email: str) -> None:
        super().__init__(details={"email": email})


class InvalidCredentialsError(AppError):
    status_code = 401
    code = "INVALID_CREDENTIALS"
    message = "Invalid email or password"


class AccountSuspendedError(AppError):
    status_code = 403
    code = "ACCOUNT_SUSPENDED"
    message = "Account has been suspended"


class UserValidationError(AppError):
    code = "USER_VALIDATION_ERROR"
    message = "User validation failed"
    status_code = 422
