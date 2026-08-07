from __future__ import annotations

import uuid

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Index,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID

from credibil.infrastructure.database.base import Base


class PersonModel(Base):
    __tablename__ = "persons"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    idnp = Column(String(13), nullable=True, unique=True, index=True)
    full_name = Column(String(500), nullable=False)
    person_type = Column(String(50), nullable=False, default="natural")
    date_of_birth = Column(Date, nullable=True)
    nationality = Column(String(10), nullable=True)
    metadata_ = Column("metadata", JSONB, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    def __repr__(self) -> str:
        return f"<PersonModel id={self.id} name={self.full_name!r}>"


class CompanyRelationshipModel(Base):
    __tablename__ = "company_relationships"
    __table_args__ = (
        Index(
            "ix_relationship_person_company",
            "person_id",
            "company_idno",
            unique=False,
        ),
        Index(
            "ix_relationship_company_type",
            "company_idno",
            "relationship_type",
        ),
        Index(
            "ix_relationship_person_type",
            "person_id",
            "relationship_type",
        ),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    person_id = Column(
        UUID(as_uuid=True),
        ForeignKey("persons.id", ondelete="CASCADE"),
        nullable=False,
    )
    company_idno = Column(String(13), nullable=False, index=True)
    relationship_type = Column(String(50), nullable=False)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    ownership_percentage = Column(Float, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    metadata_ = Column("metadata", JSONB, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    def __repr__(self) -> str:
        return f"<CompanyRelationshipModel person={self.person_id} company={self.company_idno}>"
