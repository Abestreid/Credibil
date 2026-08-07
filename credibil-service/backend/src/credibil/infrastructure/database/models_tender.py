from __future__ import annotations

import uuid

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Float,
    Index,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID

from credibil.infrastructure.database.base import Base


class TenderModel(Base):
    __tablename__ = "tenders"
    __table_args__ = (
        Index("ix_tender_ocid", "ocid", unique=True),
        Index("ix_tender_buyer_idno", "buyer_idno"),
        Index("ix_tender_status", "status"),
        Index("ix_tender_cpv", "cpv_code"),
        Index("ix_tender_category", "main_category"),
        Index("ix_tender_published", "published_date"),
        Index("ix_tender_value", "value_amount"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ocid = Column(String(200), nullable=False)
    title = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), nullable=False, default="planning")
    status_details = Column(String(100), nullable=True)
    procurement_method = Column(String(50), nullable=True)
    procurement_method_details = Column(String(200), nullable=True)
    main_category = Column(String(50), nullable=True)
    cpv_code = Column(String(50), nullable=True)
    cpv_description = Column(Text, nullable=True)
    buyer_idno = Column(String(13), nullable=True)
    buyer_name = Column(String(500), nullable=True)
    value_amount = Column(Float, nullable=True)
    value_currency = Column(String(10), nullable=True)
    budget_amount = Column(Float, nullable=True)
    budget_currency = Column(String(10), nullable=True)
    is_eu_funded = Column(Boolean, nullable=False, default=False)
    tender_start_date = Column(Date, nullable=True)
    tender_end_date = Column(Date, nullable=True)
    contract_start_date = Column(Date, nullable=True)
    contract_end_date = Column(Date, nullable=True)
    published_date = Column(DateTime(timezone=True), nullable=True)
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
        return f"<TenderModel ocid={self.ocid!r} title={self.title[:50]!r}>"


class TenderAwardModel(Base):
    __tablename__ = "tender_awards"
    __table_args__ = (
        Index("ix_award_tender_ocid", "tender_ocid"),
        Index("ix_award_supplier_idno", "supplier_idno"),
        Index("ix_award_status", "status"),
        Index("ix_award_date", "award_date"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tender_id = Column(UUID(as_uuid=True), nullable=True)
    tender_ocid = Column(String(200), nullable=False)
    ocds_award_id = Column(String(200), nullable=True)
    status = Column(String(50), nullable=False, default="pending")
    status_details = Column(String(100), nullable=True)
    award_date = Column(Date, nullable=True)
    value_amount = Column(Float, nullable=True)
    value_currency = Column(String(10), nullable=True)
    supplier_idno = Column(String(13), nullable=True)
    supplier_name = Column(String(500), nullable=True)
    related_lots = Column(JSONB, nullable=False, default=list)
    related_bid_id = Column(String(200), nullable=True)
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
        return f"<TenderAwardModel tender={self.tender_ocid!r} supplier={self.supplier_name!r}>"


class TenderBidModel(Base):
    __tablename__ = "tender_bids"
    __table_args__ = (
        Index("ix_bid_tender_ocid", "tender_ocid"),
        Index("ix_bid_tenderer_idno", "tenderer_idno"),
        Index("ix_bid_status", "status"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tender_id = Column(UUID(as_uuid=True), nullable=True)
    tender_ocid = Column(String(200), nullable=False)
    ocds_bid_id = Column(String(200), nullable=True)
    status = Column(String(50), nullable=False, default="pending")
    bid_date = Column(Date, nullable=True)
    value_amount = Column(Float, nullable=True)
    value_currency = Column(String(10), nullable=True)
    tenderer_idno = Column(String(13), nullable=True)
    tenderer_name = Column(String(500), nullable=True)
    related_lots = Column(JSONB, nullable=False, default=list)
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
        return f"<TenderBidModel tender={self.tender_ocid!r} tenderer={self.tenderer_name!r}>"
