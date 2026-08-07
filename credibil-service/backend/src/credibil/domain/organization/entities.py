from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import TYPE_CHECKING, Any

from credibil.core.id import new_id

if TYPE_CHECKING:
    from uuid import UUID


class OrganizationPlan(StrEnum):
    FREE = "free"
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class OrganizationStatus(StrEnum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    CANCELLED = "cancelled"
    PENDING = "pending"


class Organization:
    """Tenant organization entity — represents a company/workspace on the platform."""

    def __init__(
        self,
        *,
        org_id: UUID | None = None,
        name: str,
        slug: str,
        plan: OrganizationPlan = OrganizationPlan.FREE,
        status: OrganizationStatus = OrganizationStatus.ACTIVE,
        max_users: int = 5,
        max_api_calls: int = 1000,
        settings: dict[str, Any] | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        self.id = org_id or new_id()
        self.name = name
        self.slug = slug.lower().strip()
        self.plan = plan
        self.status = status
        self.max_users = max_users
        self.max_api_calls = max_api_calls
        self.settings = settings or {}
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    def update(self, **kwargs: Any) -> None:
        allowed = {"name", "slug", "plan", "status", "max_users", "max_api_calls", "settings"}
        for key, value in kwargs.items():
            if key in allowed:
                setattr(self, key, value)
        self.updated_at = datetime.utcnow()

    def suspend(self) -> None:
        self.status = OrganizationStatus.SUSPENDED
        self.updated_at = datetime.utcnow()

    def activate(self) -> None:
        self.status = OrganizationStatus.ACTIVE
        self.updated_at = datetime.utcnow()

    def upgrade_plan(
        self,
        plan: OrganizationPlan,
        max_users: int,
        max_api_calls: int,
    ) -> None:
        self.plan = plan
        self.max_users = max_users
        self.max_api_calls = max_api_calls
        self.updated_at = datetime.utcnow()

    def __repr__(self) -> str:
        return f"<Organization id={self.id} name={self.name!r} plan={self.plan.value}>"
