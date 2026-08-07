from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import TYPE_CHECKING, Any

from credibil.core.id import new_id

if TYPE_CHECKING:
    from uuid import UUID


class SubscriptionStatus(StrEnum):
    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELLED = "cancelled"
    TRIALING = "trialing"
    UNPAID = "unpaid"


class SubscriptionInterval(StrEnum):
    MONTHLY = "monthly"
    YEARLY = "yearly"


class Subscription:
    """Subscription entity linking an organization to a billing plan."""

    def __init__(
        self,
        *,
        subscription_id: UUID | None = None,
        tenant_id: UUID,
        stripe_subscription_id: str | None = None,
        stripe_customer_id: str | None = None,
        status: SubscriptionStatus = SubscriptionStatus.ACTIVE,
        interval: SubscriptionInterval = SubscriptionInterval.MONTHLY,
        current_period_start: datetime | None = None,
        current_period_end: datetime | None = None,
        cancel_at_period_end: bool = False,
        metadata: dict[str, Any] | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        self.id = subscription_id or new_id()
        self.tenant_id = tenant_id
        self.stripe_subscription_id = stripe_subscription_id
        self.stripe_customer_id = stripe_customer_id
        self.status = status
        self.interval = interval
        self.current_period_start = current_period_start
        self.current_period_end = current_period_end
        self.cancel_at_period_end = cancel_at_period_end
        self.metadata = metadata or {}
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    def update(self, **kwargs: Any) -> None:
        allowed = {
            "status",
            "interval",
            "current_period_start",
            "current_period_end",
            "cancel_at_period_end",
            "stripe_subscription_id",
            "stripe_customer_id",
            "metadata",
        }
        for key, value in kwargs.items():
            if key in allowed:
                setattr(self, key, value)
        self.updated_at = datetime.utcnow()

    def cancel(self) -> None:
        self.cancel_at_period_end = True
        self.updated_at = datetime.utcnow()

    @property
    def is_active(self) -> bool:
        return self.status in (SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIALING)

    def __repr__(self) -> str:
        return f"<Subscription id={self.id} tenant_id={self.tenant_id} status={self.status.value}>"
