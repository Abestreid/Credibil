from __future__ import annotations

import uuid

from sqlalchemy import Column, Date, DateTime, Float, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID

from credibil.infrastructure.database.base import Base


class CompanyModel(Base):
    __tablename__ = "companies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    idno = Column(String(13), nullable=False, unique=True, index=True)
    name_ro = Column(String(500), nullable=False)
    name_ru = Column(String(500), nullable=False, default="")
    registration_date = Column(Date, nullable=True)
    status = Column(String(50), nullable=False, default="active", index=True)
    legal_form = Column(String(50), nullable=False, default="OTHER")
    legal_address = Column(Text, nullable=True)
    postal_code = Column(String(10), nullable=True)
    caem = Column(String(10), nullable=True)
    caem_description = Column(Text, nullable=True)
    cuatm = Column(String(20), nullable=True)
    cuiio = Column(String(50), nullable=True)
    cfp = Column(String(50), nullable=True)
    cfoj = Column(String(50), nullable=True)
    business_category = Column(String(20), nullable=True)  # micro, small, medium, large
    tax_debt = Column(Float, nullable=True)
    tax_debt_fetched_at = Column(DateTime(timezone=True), nullable=True)
    founder_count = Column(Integer, nullable=False, default=0)
    director_count = Column(Integer, nullable=False, default=0)
    metadata_ = Column("metadata", JSONB, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    def __repr__(self) -> str:
        return f"<CompanyModel id={self.id} idno={self.idno}>"
