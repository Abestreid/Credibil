from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from uuid import UUID

    from credibil.domain.organization.entities import Organization


class OrganizationRepository(ABC):
    """Abstract interface for organization data access."""

    @abstractmethod
    async def find_by_id(self, org_id: UUID) -> Organization | None: ...

    @abstractmethod
    async def find_by_slug(self, slug: str) -> Organization | None: ...

    @abstractmethod
    async def save(self, organization: Organization) -> Organization: ...

    @abstractmethod
    async def delete(self, org_id: UUID) -> None: ...

    @abstractmethod
    async def list_organizations(
        self,
        offset: int = 0,
        limit: int = 25,
    ) -> tuple[list[Organization], int]: ...

    @abstractmethod
    async def count_by_slug(self, slug: str) -> int: ...

    @abstractmethod
    async def exists(self, org_id: UUID) -> bool: ...
