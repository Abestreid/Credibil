from __future__ import annotations

from credibil.core.exceptions import NotFoundError


class SubscriptionNotFoundError(NotFoundError):
    code = "SUBSCRIPTION_NOT_FOUND"
    message = "Subscription not found"

    def __init__(self, identifier: str | None = None) -> None:
        details = {"identifier": identifier} if identifier else {}
        super().__init__(details=details)


class SubscriptionValidationError(NotFoundError):
    code = "SUBSCRIPTION_VALIDATION_ERROR"
    message = "Subscription validation failed"
    status_code = 422
