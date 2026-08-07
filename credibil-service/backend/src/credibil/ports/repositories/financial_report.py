from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from uuid import UUID

    from credibil.domain.financial import FinancialReport


class FinancialReportRepository(ABC):
    """Repository for financial reports."""

    @abstractmethod
    async def find_by_id(self, report_id: UUID) -> FinancialReport | None: ...

    @abstractmethod
    async def find_by_idno_and_year(self, idno: str, year: int) -> FinancialReport | None: ...

    @abstractmethod
    async def find_by_idno(
        self,
        idno: str,
        limit: int = 100,
        offset: int = 0,
    ) -> list[FinancialReport]: ...

    @abstractmethod
    async def save(self, report: FinancialReport) -> FinancialReport: ...

    @abstractmethod
    async def delete(self, report_id: UUID) -> None: ...

    @abstractmethod
    async def list_reports(
        self,
        limit: int = 100,
        offset: int = 0,
        filters: dict[str, Any] | None = None,
    ) -> list[FinancialReport]: ...

    @abstractmethod
    async def count_by_idno(self, idno: str) -> int: ...

    @abstractmethod
    async def find_years_for_idno(self, idno: str) -> list[int]: ...

    @abstractmethod
    async def find_latest_by_idno(self, idno: str) -> FinancialReport | None: ...
