from __future__ import annotations

import uuid

from sqlalchemy import Column, Date, DateTime, Index, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID

from credibil.infrastructure.database.base import Base


class CourtCaseModel(Base):
    __tablename__ = "court_cases"
    __table_args__ = (
        Index("ix_court_case_number", "case_number", unique=True),
        Index("ix_court_case_idno", "plaintiff_idno"),
        Index("ix_court_case_defendant_idno", "defendant_idno"),
        Index("ix_court_case_court", "court_slug"),
        Index("ix_court_case_status", "status"),
        Index("ix_court_case_dates", "registration_date", "decision_date"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_number = Column(String(100), nullable=False)
    case_type = Column(String(50), nullable=False, default="other")
    court_name = Column(String(300), nullable=False)
    court_type = Column(String(50), nullable=False, default="judecatorie")
    court_slug = Column(String(50), nullable=True)
    registration_date = Column(Date, nullable=True)
    decision_date = Column(Date, nullable=True)
    status = Column(String(50), nullable=False, default="open")
    plaintiff_name = Column(String(500), nullable=True)
    plaintiff_idno = Column(String(13), nullable=True)
    defendant_name = Column(String(500), nullable=True)
    defendant_idno = Column(String(13), nullable=True)
    judge_name = Column(String(300), nullable=True)
    subject_matter = Column(Text, nullable=True)
    decision_summary = Column(Text, nullable=True)
    source_url = Column(Text, nullable=True)
    raw_data = Column(JSONB, nullable=False, default=dict)
    metadata_ = Column("metadata", JSONB, nullable=False, default=dict)
    fetched_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    def __repr__(self) -> str:
        return f"<CourtCaseModel case_number={self.case_number!r} court={self.court_name!r}>"


class CourtHearingModel(Base):
    __tablename__ = "court_hearings"
    __table_args__ = (
        Index("ix_hearing_case_number", "case_number"),
        Index("ix_hearing_date", "hearing_date"),
        Index("ix_hearing_court_date", "court_name", "hearing_date"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id = Column(UUID(as_uuid=True), nullable=True)
    case_number = Column(String(100), nullable=False)
    hearing_date = Column(Date, nullable=False)
    hearing_time = Column(String(20), nullable=True)
    court_name = Column(String(300), nullable=True)
    department = Column(String(200), nullable=True)
    room = Column(String(50), nullable=True)
    judge_name = Column(String(300), nullable=True)
    hearing_type = Column(String(100), nullable=True)
    outcome = Column(Text, nullable=True)
    source_url = Column(Text, nullable=True)
    raw_data = Column(JSONB, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    def __repr__(self) -> str:
        return f"<CourtHearingModel case={self.case_number!r} date={self.hearing_date}>"
