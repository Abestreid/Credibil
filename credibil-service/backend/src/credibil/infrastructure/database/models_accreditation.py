from __future__ import annotations

import uuid

from sqlalchemy import (
    Column,
    DateTime,
    Index,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID

from credibil.infrastructure.database.base import Base


class AccreditationModel(Base):
    __tablename__ = "accreditations"
    __table_args__ = (
        Index("ix_accreditation_cert_number", "certificate_number", unique=True),
        Index("ix_accreditation_category", "category"),
        Index("ix_accreditation_status", "status"),
        Index("ix_accreditation_org_name", "organization_name"),
        Index("ix_accreditation_country", "country_code"),
        Index("ix_accreditation_standard", "standard"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_name = Column(String(500), nullable=False)
    director_name = Column(String(300), nullable=True)
    address = Column(Text, nullable=True)
    phone = Column(String(100), nullable=True)
    fax = Column(String(100), nullable=True)
    email = Column(String(200), nullable=True)
    certificate_number = Column(String(50), nullable=False)
    category = Column(String(50), nullable=False)
    standard = Column(String(200), nullable=False)
    status = Column(String(50), nullable=False, default="active")
    issue_date = Column(String(10), nullable=True)  # DD.MM.YYYY
    expiry_date = Column(String(10), nullable=True)  # DD.MM.YYYY
    scope = Column(Text, nullable=True)
    certificate_url = Column(Text, nullable=True)
    annex_urls = Column(JSONB, nullable=False, default=list)
    remarks = Column(Text, nullable=True)
    country_code = Column(String(2), nullable=False, default="MD")
    source_url = Column(Text, nullable=True)
    raw_data = Column(JSONB, nullable=False, default=dict)
    last_synced = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    def __repr__(self) -> str:
        return (
            f"<AccreditationModel cert={self.certificate_number!r} "
            f"org={self.organization_name[:50]!r}>"
        )
