from __future__ import annotations

import uuid

from sqlalchemy import BigInteger, Column, Date, DateTime, Float, Index, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID

from credibil.infrastructure.database.base import Base


class EnforcementProceedingModel(Base):
    __tablename__ = "enforcement_proceedings"
    __table_args__ = (
        Index("ix_enforcement_somation_id", "somation_id", unique=True),
        Index("ix_enforcement_debtor_idno", "debtor_idno"),
        Index("ix_enforcement_creditor_idno", "creditor_idno"),
        Index("ix_enforcement_state", "state"),
        Index("ix_enforcement_publication_date", "publication_date"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    somation_id = Column(BigInteger, nullable=False)
    debtor_name = Column(String(500), nullable=True)
    debtor_idno = Column(String(13), nullable=True)
    debtor_idno_masked = Column(String(20), nullable=True)
    creditor_name = Column(String(500), nullable=True)
    creditor_idno = Column(String(13), nullable=True)
    executory_doc_number = Column(String(200), nullable=True)
    court_name = Column(String(300), nullable=True)
    case_number = Column(String(100), nullable=True)
    amount = Column(Float, nullable=True)
    currency = Column(String(10), nullable=False, default="MDL")
    publication_date = Column(Date, nullable=True)
    state = Column(String(20), nullable=False, default="active")
    source_url = Column(Text, nullable=True)
    raw_data = Column(JSONB, nullable=False, default=dict)
    metadata_ = Column("metadata", JSONB, nullable=False, default=dict)
    first_seen_at = Column(DateTime(timezone=True), nullable=True)
    last_seen_at = Column(DateTime(timezone=True), nullable=True)
    fetched_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    def __repr__(self) -> str:
        return (
            f"<EnforcementProceedingModel somation_id={self.somation_id} "
            f"state={self.state!r}>"
        )
