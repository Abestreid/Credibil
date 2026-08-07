from __future__ import annotations

import uuid

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID

from credibil.infrastructure.database.base import Base


class MonitoredCompanyModel(Base):
    __tablename__ = "monitored_companies"
    __table_args__ = (
        UniqueConstraint("user_id", "idno", name="uq_monitored_user_idno"),
        Index("ix_monitored_user", "user_id"),
        Index("ix_monitored_idno", "idno"),
        Index("ix_monitored_active", "is_active"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    idno = Column(String(13), nullable=False)
    company_id = Column(UUID(as_uuid=True), nullable=True)
    company_name = Column(String(500), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    last_checked_at = Column(DateTime(timezone=True), nullable=True)
    last_change_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )


class CompanySnapshotModel(Base):
    """Rolling two-slot snapshot of a monitored company's canonical state.

    Only companies watched by at least one user get a snapshot. Keyed by IDNO
    (shared across watchers).
    """

    __tablename__ = "company_snapshots"

    idno = Column(String(13), primary_key=True)
    snapshot_hash = Column(String(64), nullable=False)
    snapshot_json = Column(JSONB, nullable=False, default=dict)
    snapshot_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    prev_snapshot_json = Column(JSONB, nullable=True)
    prev_snapshot_at = Column(DateTime(timezone=True), nullable=True)


class CompanyChangeEventModel(Base):
    __tablename__ = "company_change_events"
    __table_args__ = (
        Index("ix_change_event_idno", "idno"),
        Index("ix_change_event_detected", "detected_at"),
        Index("ix_change_event_batch", "batch_id"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    idno = Column(String(13), nullable=False)
    category = Column(String(30), nullable=False, default="general")
    field = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    batch_id = Column(String(40), nullable=True)
    detected_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())


class MonitoringNotificationModel(Base):
    __tablename__ = "monitoring_notifications"
    __table_args__ = (
        Index("ix_notification_user", "user_id"),
        Index("ix_notification_user_unread", "user_id", "is_read"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    idno = Column(String(13), nullable=False)
    company_name = Column(String(500), nullable=True)
    change_count = Column(Integer, nullable=False, default=0)
    summary = Column(Text, nullable=True)
    metadata_ = Column("metadata", JSONB, nullable=False, default=dict)
    is_read = Column(Boolean, nullable=False, default=False)
    email_sent = Column(Boolean, nullable=False, default=False)
    read_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
