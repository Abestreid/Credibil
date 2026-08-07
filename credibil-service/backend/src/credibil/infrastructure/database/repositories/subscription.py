from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import select

from credibil.domain.subscription.entities import (
    Subscription,
    SubscriptionInterval,
    SubscriptionStatus,
)
from credibil.infrastructure.database.models_organization import SubscriptionModel
from credibil.ports.repositories.subscription import SubscriptionRepository

if TYPE_CHECKING:
    from uuid import UUID

    from sqlalchemy.ext.asyncio import AsyncSession


class SQLAlchemySubscriptionRepository(SubscriptionRepository):
    """PostgreSQL subscription repository via SQLAlchemy."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_id(self, subscription_id: UUID) -> Subscription | None:
        stmt = select(SubscriptionModel).where(SubscriptionModel.id == subscription_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def find_by_tenant_id(self, tenant_id: UUID) -> Subscription | None:
        stmt = select(SubscriptionModel).where(SubscriptionModel.tenant_id == tenant_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def save(self, subscription: Subscription) -> Subscription:
        model = self._to_model(subscription)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_domain(model)

    async def delete(self, subscription_id: UUID) -> None:
        stmt = select(SubscriptionModel).where(SubscriptionModel.id == subscription_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model:
            await self._session.delete(model)

    def _to_domain(self, model: SubscriptionModel) -> Subscription:
        return Subscription(
            subscription_id=model.id,
            tenant_id=model.tenant_id,
            stripe_subscription_id=model.stripe_subscription_id,
            stripe_customer_id=model.stripe_customer_id,
            status=SubscriptionStatus(model.status),
            interval=SubscriptionInterval(model.interval),
            current_period_start=model.current_period_start,
            current_period_end=model.current_period_end,
            cancel_at_period_end=model.cancel_at_period_end,
            metadata=model.metadata_ if model.metadata_ else {},
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_model(self, sub: Subscription) -> SubscriptionModel:
        return SubscriptionModel(
            id=sub.id,
            tenant_id=sub.tenant_id,
            stripe_subscription_id=sub.stripe_subscription_id,
            stripe_customer_id=sub.stripe_customer_id,
            status=sub.status.value,
            interval=sub.interval.value,
            current_period_start=sub.current_period_start,
            current_period_end=sub.current_period_end,
            cancel_at_period_end=sub.cancel_at_period_end,
            metadata_=sub.metadata,
            created_at=sub.created_at,
            updated_at=sub.updated_at,
        )
