from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import TYPE_CHECKING, Any

from credibil.core.id import new_id

if TYPE_CHECKING:
    from uuid import UUID


class UserRole(StrEnum):
    ADMIN = "admin"
    ANALYST = "analyst"
    USER = "user"
    API_CLIENT = "api_client"


class UserStatus(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"


class User:
    """Core user entity."""

    def __init__(
        self,
        *,
        user_id: UUID | None = None,
        email: str,
        hashed_password: str,
        full_name: str = "",
        role: UserRole = UserRole.USER,
        status: UserStatus = UserStatus.ACTIVE,
        tenant_id: UUID | None = None,
        last_login_at: datetime | None = None,
        metadata: dict[str, Any] | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        self.id = user_id or new_id()
        self.email = email.lower().strip()
        self.hashed_password = hashed_password
        self.full_name = full_name
        self.role = role
        self.status = status
        self.tenant_id = tenant_id
        self.last_login_at = last_login_at
        self.metadata = metadata or {}
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    def update(self, **kwargs: Any) -> None:
        allowed = {
            "email",
            "full_name",
            "role",
            "status",
            "hashed_password",
            "last_login_at",
            "metadata",
        }
        for key, value in kwargs.items():
            if key in allowed:
                setattr(self, key, value)
        self.updated_at = datetime.utcnow()

    def deactivate(self) -> None:
        self.status = UserStatus.INACTIVE
        self.updated_at = datetime.utcnow()

    def suspend(self) -> None:
        self.status = UserStatus.SUSPENDED
        self.updated_at = datetime.utcnow()

    def record_login(self) -> None:
        self.last_login_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email!r} role={self.role.value}>"
