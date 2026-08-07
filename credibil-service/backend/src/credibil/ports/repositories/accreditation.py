from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from uuid import UUID

    from credibil.domain.accreditation.entities import (
        Accreditation,
        AccreditationCategory,
        AccreditationStatus,
    )


class AccreditationRepository(ABC):
    """Repository for accreditation records from MOLDAC."""

    @abstractmethod
    async def find_by_id(self, accreditation_id: UUID) -> Accreditation | None: ...

    @abstractmethod
    async def find_by_certificate_number(self, cert_number: str) -> Accreditation | None: ...

    @abstractmethod
    async def find_by_category(
        self, category: AccreditationCategory, limit: int = 100, offset: int = 0
    ) -> list[Accreditation]: ...

    @abstractmethod
    async def find_by_status(
        self, status: AccreditationStatus, limit: int = 100, offset: int = 0
    ) -> list[Accreditation]: ...

    @abstractmethod
    async def find_by_organization(
        self, organization_name: str, limit: int = 100, offset: int = 0
    ) -> list[Accreditation]: ...

    @abstractmethod
    async def save(self, accreditation: Accreditation) -> Accreditation: ...

    @abstractmethod
    async def delete(self, accreditation_id: UUID) -> None: ...

    @abstractmethod
    async def list_accreditations(
        self, limit: int = 100, offset: int = 0, filters: dict[str, Any] | None = None
    ) -> list[Accreditation]: ...

    @abstractmethod
    async def count_by_category(self, category: AccreditationCategory) -> int: ...

    @abstractmethod
    async def count_by_status(self, status: AccreditationStatus) -> int: ...

    @abstractmethod
    async def search_by_keyword(self, keyword: str, limit: int = 100) -> list[Accreditation]: ...
