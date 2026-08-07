from __future__ import annotations

from sqlalchemy import DateTime, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import mapped_column

from credibil.infrastructure.database.base import Base


class UserModel(Base):
    __tablename__ = "users"

    id = mapped_column(UUID(as_uuid=True), primary_key=True)
    email = mapped_column(String(255), nullable=False, unique=True, index=True)
    hashed_password = mapped_column(String(255), nullable=False)
    full_name = mapped_column(String(255), nullable=False, default="")
    role = mapped_column(String(50), nullable=False, default="user", index=True)
    status = mapped_column(String(50), nullable=False, default="active", index=True)
    tenant_id = mapped_column(UUID(as_uuid=True), nullable=True, index=True)
    last_login_at = mapped_column(DateTime(timezone=True), nullable=True)
    metadata_ = mapped_column("metadata", JSONB, nullable=False, default=dict)
    created_at = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    def __repr__(self) -> str:
        return f"<UserModel id={self.id} email={self.email!r}>"
