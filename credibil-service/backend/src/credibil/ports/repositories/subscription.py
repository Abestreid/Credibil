from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from uuid import UUID

    from credibil.domain.subscription.entities import Subscription


class SubscriptionRepository(ABC):
    """Abstract interface for subscription data access."""

    @abstractmethod
    async def find_by_id(self, subscription_id: UUID) -> Subscription | None: ...

    @abstractmethod
    async def find_by_tenant_id(self, tenant_id: UUID) -> Subscription | None: ...

    @abstractmethod
    async def save(self, subscription: Subscription) -> Subscription: ...

    @abstractmethod
    async def delete(self, subscription_id: UUID) -> None: ...
