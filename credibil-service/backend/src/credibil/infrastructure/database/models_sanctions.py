from __future__ import annotations

import uuid

from sqlalchemy import Column, DateTime, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from credibil.infrastructure.database.base import Base


class SanctionsEntryModel(Base):
    __tablename__ = "sanctions_entries"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    target_name = Column(String(500), nullable=False, index=True)
    target_idno = Column(String(13), index=True, nullable=True)
    target_idnp = Column(String(13), index=True, nullable=True)
    sanction_type = Column(String(50), nullable=False, index=True)
    status = Column(String(50), nullable=False, default="active", index=True)
    list_name = Column(String(200), nullable=True)
    list_url = Column(Text, nullable=True)
    country_code = Column(String(3), nullable=True, index=True)
    reason = Column(Text, nullable=True)
    program = Column(String(200), nullable=True)
    listed_date = Column(String(10), nullable=True)
    last_updated = Column(String(10), nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)


class RiskAssessmentModel(Base):
    __tablename__ = "risk_assessments"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    target_idno = Column(String(13), index=True, nullable=True)
    target_idnp = Column(String(13), index=True, nullable=True)
    target_name = Column(String(500), nullable=True)
    overall_risk = Column(String(20), nullable=False, default="unknown")
    sanctions_risk = Column(String(20), nullable=False, default="unknown")
    litigation_risk = Column(String(20), nullable=False, default="unknown")
    financial_risk = Column(String(20), nullable=False, default="unknown")
    sanctions_count = Column(Integer, default=0)
    active_cases_count = Column(Integer, default=0)
    total_cases_count = Column(Integer, default=0)
    risk_factors = Column(Text, nullable=True)
    assessed_at = Column(DateTime, server_default=func.now(), nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
