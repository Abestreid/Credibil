from __future__ import annotations

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from credibil.infrastructure.database.base import Base


class OrganizationModel(Base):
    __tablename__ = "organizations"

    id = mapped_column(UUID(as_uuid=True), primary_key=True)
    name = mapped_column(String(255), nullable=False)
    slug = mapped_column(String(255), nullable=False, unique=True, index=True)
    plan = mapped_column(String(50), nullable=False, default="free", index=True)
    status = mapped_column(String(50), nullable=False, default="active", index=True)
    max_users = mapped_column(Integer, nullable=False, default=5)
    max_api_calls = mapped_column(Integer, nullable=False, default=1000)
    settings_ = mapped_column("settings", JSONB, nullable=False, default=dict)
    created_at = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    def __repr__(self) -> str:
        return f"<OrganizationModel id={self.id} name={self.name!r}>"


class SubscriptionModel(Base):
    __tablename__ = "subscriptions"

    id = mapped_column(UUID(as_uuid=True), primary_key=True)
    tenant_id = mapped_column(UUID(as_uuid=True), nullable=False, unique=True, index=True)
    stripe_subscription_id = mapped_column(String(255), nullable=True, unique=True)
    stripe_customer_id = mapped_column(String(255), nullable=True)
    status = mapped_column(String(50), nullable=False, default="active", index=True)
    interval = mapped_column(String(50), nullable=False, default="monthly")
    current_period_start = mapped_column(DateTime(timezone=True), nullable=True)
    current_period_end = mapped_column(DateTime(timezone=True), nullable=True)
    cancel_at_period_end: Mapped[bool] = mapped_column(nullable=False, default=False)
    metadata_ = mapped_column("metadata", JSONB, nullable=False, default=dict)
    created_at = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    def __repr__(self) -> str:
        return f"<SubscriptionModel id={self.id} tenant_id={self.tenant_id}>"


class APIKeyModel(Base):
    __tablename__ = "api_keys"

    id = mapped_column(UUID(as_uuid=True), primary_key=True)
    tenant_id = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    name = mapped_column(String(255), nullable=False)
    key_prefix = mapped_column(String(20), nullable=False, index=True)
    key_hash = mapped_column(String(255), nullable=False, unique=True)
    scopes_ = mapped_column("scopes", JSONB, nullable=False, default=list)
    rate_limit = mapped_column(Integer, nullable=False, default=1000)
    status = mapped_column(String(50), nullable=False, default="active", index=True)
    expires_at = mapped_column(DateTime(timezone=True), nullable=True)
    last_used_at = mapped_column(DateTime(timezone=True), nullable=True)
    metadata_ = mapped_column("metadata", JSONB, nullable=False, default=dict)
    created_at = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    def __repr__(self) -> str:
        return f"<APIKeyModel id={self.id} name={self.name!r}>"
