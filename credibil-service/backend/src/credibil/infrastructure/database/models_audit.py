from __future__ import annotations

from sqlalchemy import Column, DateTime, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from credibil.infrastructure.database.base import Base


class AuditLogModel(Base):
    __tablename__ = "audit_logs"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=None)
    request_id = Column(String(36), unique=True, nullable=False, index=True)
    method = Column(String(10), nullable=False, index=True)
    path = Column(String(500), nullable=False, index=True)
    status_code = Column(Integer, nullable=False, index=True)
    client_ip = Column(String(45), nullable=False, index=True)
    user_id = Column(String(36), nullable=True, index=True)
    api_key_prefix = Column(String(16), nullable=True)
    user_agent = Column(String(500), nullable=True)
    request_body = Column(Text, nullable=True)
    duration_ms = Column(Integer, nullable=False)
    error_message = Column(Text, nullable=True)
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), index=True
    )
