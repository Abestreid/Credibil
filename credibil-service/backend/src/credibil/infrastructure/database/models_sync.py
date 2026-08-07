from __future__ import annotations

import uuid

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID

from credibil.infrastructure.database.base import Base


class SyncHistoryModel(Base):
    __tablename__ = "sync_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    provider_id = Column(String(100), nullable=False, index=True)
    sync_type = Column(String(50), nullable=False)
    country_code = Column(String(10), nullable=False, index=True)
    status = Column(String(50), nullable=False, default="pending", index=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    finished_at = Column(DateTime(timezone=True), nullable=True)
    records_total = Column(Integer, nullable=False, default=0)
    records_created = Column(Integer, nullable=False, default=0)
    records_updated = Column(Integer, nullable=False, default=0)
    records_unchanged = Column(Integer, nullable=False, default=0)
    records_failed = Column(Integer, nullable=False, default=0)
    error_message = Column(Text, nullable=True)
    file_checksum = Column(String(64), nullable=True)
    file_path = Column(Text, nullable=True)
    duration_seconds = Column(Float, nullable=True)
    metadata_ = Column("metadata", JSONB, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    def __repr__(self) -> str:
        return f"<SyncHistoryModel id={self.id} provider={self.provider_id} status={self.status}>"
