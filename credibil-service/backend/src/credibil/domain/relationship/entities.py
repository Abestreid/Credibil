from __future__ import annotations

from datetime import date, datetime
from enum import StrEnum
from typing import TYPE_CHECKING, Any

from credibil.core.id import new_id

if TYPE_CHECKING:
    from uuid import UUID


class PersonType(StrEnum):
    NATURAL = "natural"
    LEGAL = "legal"


class Person:
    """A natural or legal person — can be founder, director, or owner of companies."""

    def __init__(
        self,
        *,
        person_id: UUID | None = None,
        idnp: str | None = None,
        full_name: str,
        person_type: PersonType = PersonType.NATURAL,
        date_of_birth: date | None = None,
        nationality: str | None = None,
        metadata: dict[str, Any] | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        self.id = person_id or new_id()
        self.idnp = idnp
        self.full_name = full_name
        self.person_type = person_type
        self.date_of_birth = date_of_birth
        self.nationality = nationality
        self.metadata = metadata or {}
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    def update(self, **kwargs: Any) -> None:
        allowed = {"idnp", "full_name", "person_type", "date_of_birth", "nationality", "metadata"}
        for key, value in kwargs.items():
            if key in allowed:
                setattr(self, key, value)
        self.updated_at = datetime.utcnow()

    def __repr__(self) -> str:
        return f"<Person id={self.id} name={self.full_name!r}>"


class RelationshipType(StrEnum):
    FOUNDER = "founder"
    DIRECTOR = "director"
    BENEFICIAL_OWNER = "beneficial_owner"
    LEGAL_REPRESENTATIVE = "legal_representative"


class CompanyRelationship:
    """Links a Person to a Company with a role and date range."""

    def __init__(
        self,
        *,
        relationship_id: UUID | None = None,
        person_id: UUID,
        company_idno: str,
        relationship_type: RelationshipType,
        start_date: date | None = None,
        end_date: date | None = None,
        ownership_percentage: float | None = None,
        is_active: bool = True,
        metadata: dict[str, Any] | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        self.id = relationship_id or new_id()
        self.person_id = person_id
        self.company_idno = company_idno
        self.relationship_type = relationship_type
        self.start_date = start_date
        self.end_date = end_date
        self.ownership_percentage = ownership_percentage
        self.is_active = is_active
        self.metadata = metadata or {}
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    def deactivate(self) -> None:
        self.is_active = False
        self.end_date = date.today()
        self.updated_at = datetime.utcnow()

    def __repr__(self) -> str:
        return (
            f"<CompanyRelationship person={self.person_id} "
            f"company={self.company_idno} type={self.relationship_type}>"
        )
