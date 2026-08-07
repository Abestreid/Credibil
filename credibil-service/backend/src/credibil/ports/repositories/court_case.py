from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from datetime import date
    from uuid import UUID

    from credibil.domain.court.entities import CourtCase, CourtHearing


class CourtCaseRepository(ABC):
    """Repository for court cases."""

    @abstractmethod
    async def find_by_id(self, case_id: UUID) -> CourtCase | None: ...

    @abstractmethod
    async def find_by_case_number(self, case_number: str) -> CourtCase | None: ...

    @abstractmethod
    async def find_by_idno(
        self,
        idno: str,
        role: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[CourtCase]: ...

    @abstractmethod
    async def save(self, case: CourtCase) -> CourtCase: ...

    @abstractmethod
    async def delete(self, case_id: UUID) -> None: ...

    @abstractmethod
    async def list_cases(
        self,
        limit: int = 100,
        offset: int = 0,
        filters: dict[str, Any] | None = None,
    ) -> list[CourtCase]: ...

    @abstractmethod
    async def count_by_idno(self, idno: str) -> int: ...

    @abstractmethod
    async def find_by_court(
        self,
        court_slug: str,
        limit: int = 100,
        offset: int = 0,
    ) -> list[CourtCase]: ...

    @abstractmethod
    async def find_by_date_range(
        self,
        start_date: date,
        end_date: date,
        court_slug: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[CourtCase]: ...

    @abstractmethod
    async def count_active_by_idno(self, idno: str) -> int: ...

    @abstractmethod
    async def find_open_cases_by_idno(self, idno: str) -> list[CourtCase]: ...


class CourtHearingRepository(ABC):
    """Repository for court hearings/agenda entries."""

    @abstractmethod
    async def find_by_id(self, hearing_id: UUID) -> CourtHearing | None: ...

    @abstractmethod
    async def find_by_case_number(
        self, case_number: str, limit: int = 100, offset: int = 0
    ) -> list[CourtHearing]: ...

    @abstractmethod
    async def save(self, hearing: CourtHearing) -> CourtHearing: ...

    @abstractmethod
    async def delete(self, hearing_id: UUID) -> None: ...

    @abstractmethod
    async def find_upcoming_by_idno(self, idno: str, limit: int = 50) -> list[CourtHearing]: ...

    @abstractmethod
    async def find_by_date_range(
        self,
        start_date: date,
        end_date: date,
        court_slug: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[CourtHearing]: ...

    @abstractmethod
    async def count_by_case(self, case_number: str) -> int: ...
