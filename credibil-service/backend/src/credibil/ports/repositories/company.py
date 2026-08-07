from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from uuid import UUID

    from credibil.core.pagination import PageParams, PaginatedResult
    from credibil.domain.company.entities import Company


class CompanyRepository(ABC):
    """Abstract interface for company data access."""

    @abstractmethod
    async def find_by_id(self, company_id: UUID) -> Company | None: ...

    @abstractmethod
    async def find_by_idno(self, idno: str) -> Company | None: ...

    @abstractmethod
    async def save(self, company: Company) -> Company: ...

    @abstractmethod
    async def delete(self, company_id: UUID) -> None: ...

    @abstractmethod
    async def list_companies(
        self,
        page_params: PageParams,
        filters: dict[str, Any] | None = None,
        search: str | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> PaginatedResult[Company]: ...

    @abstractmethod
    async def count_by_idno(self, idno: str) -> int: ...

    @abstractmethod
    async def exists(self, company_id: UUID) -> bool: ...
