from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from uuid import UUID

    from credibil.domain.relationship.entities import (
        CompanyRelationship,
        Person,
        RelationshipType,
    )


class PersonRepository(ABC):
    """Repository for person entities."""

    @abstractmethod
    async def find_by_id(self, person_id: UUID) -> Person | None: ...

    @abstractmethod
    async def find_by_idnp(self, idnp: str) -> Person | None: ...

    @abstractmethod
    async def save(self, person: Person) -> Person: ...

    @abstractmethod
    async def delete(self, person_id: UUID) -> None: ...

    @abstractmethod
    async def list_persons(
        self,
        limit: int = 100,
        offset: int = 0,
        filters: dict[str, Any] | None = None,
        search: str | None = None,
    ) -> list[Person]: ...

    @abstractmethod
    async def count_all(self) -> int: ...

    @abstractmethod
    async def exists(self, person_id: UUID) -> bool: ...


class RelationshipRepository(ABC):
    """Repository for company-person relationships (the graph)."""

    @abstractmethod
    async def find_by_id(self, relationship_id: UUID) -> CompanyRelationship | None: ...

    @abstractmethod
    async def save(self, relationship: CompanyRelationship) -> CompanyRelationship: ...

    @abstractmethod
    async def delete(self, relationship_id: UUID) -> None: ...

    @abstractmethod
    async def find_by_company_idno(
        self,
        idno: str,
        relationship_type: RelationshipType | None = None,
        active_only: bool = True,
    ) -> list[CompanyRelationship]: ...

    @abstractmethod
    async def find_by_person_id(
        self,
        person_id: UUID,
        relationship_type: RelationshipType | None = None,
        active_only: bool = True,
    ) -> list[CompanyRelationship]: ...

    @abstractmethod
    async def find_by_person_idnp(
        self,
        idnp: str,
        relationship_type: RelationshipType | None = None,
        active_only: bool = True,
    ) -> list[CompanyRelationship]: ...

    @abstractmethod
    async def find_related_companies(
        self,
        idno: str,
        active_only: bool = True,
    ) -> list[CompanyRelationship]: ...

    @abstractmethod
    async def find_shared_directors(
        self,
        idno_a: str,
        idno_b: str,
    ) -> list[CompanyRelationship]: ...

    @abstractmethod
    async def find_shared_founders(
        self,
        idno_a: str,
        idno_b: str,
    ) -> list[CompanyRelationship]: ...

    @abstractmethod
    async def count_by_company(self, idno: str) -> int: ...

    @abstractmethod
    async def count_by_person(self, person_id: UUID) -> int: ...

    @abstractmethod
    async def find_existing(
        self,
        person_id: UUID,
        company_idno: str,
        relationship_type: RelationshipType,
    ) -> CompanyRelationship | None: ...
