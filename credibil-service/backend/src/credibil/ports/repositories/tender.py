from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from datetime import date
    from uuid import UUID

    from credibil.domain.tender.entities import Tender, TenderAward, TenderBid


class TenderRepository(ABC):
    """Repository for tenders."""

    @abstractmethod
    async def find_by_id(self, tender_id: UUID) -> Tender | None: ...

    @abstractmethod
    async def find_by_ocid(self, ocid: str) -> Tender | None: ...

    @abstractmethod
    async def find_by_buyer_idno(
        self, idno: str, limit: int = 100, offset: int = 0
    ) -> list[Tender]: ...

    @abstractmethod
    async def find_by_supplier_idno(
        self, idno: str, limit: int = 100, offset: int = 0
    ) -> list[Tender]: ...

    @abstractmethod
    async def save(self, tender: Tender) -> Tender: ...

    @abstractmethod
    async def delete(self, tender_id: UUID) -> None: ...

    @abstractmethod
    async def list_tenders(
        self, limit: int = 100, offset: int = 0, filters: dict[str, Any] | None = None
    ) -> list[Tender]: ...

    @abstractmethod
    async def count_by_buyer_idno(self, idno: str) -> int: ...

    @abstractmethod
    async def find_by_date_range(
        self, start_date: date, end_date: date, limit: int = 100, offset: int = 0
    ) -> list[Tender]: ...

    @abstractmethod
    async def find_by_status(
        self, status: str, limit: int = 100, offset: int = 0
    ) -> list[Tender]: ...

    @abstractmethod
    async def find_active_by_buyer_idno(self, idno: str) -> list[Tender]: ...

    @abstractmethod
    async def find_by_cpv_code(
        self, cpv_code: str, limit: int = 100, offset: int = 0
    ) -> list[Tender]: ...


class TenderAwardRepository(ABC):
    """Repository for tender awards."""

    @abstractmethod
    async def find_by_id(self, award_id: UUID) -> TenderAward | None: ...

    @abstractmethod
    async def find_by_tender_ocid(
        self, tender_ocid: str, limit: int = 100, offset: int = 0
    ) -> list[TenderAward]: ...

    @abstractmethod
    async def find_by_supplier_idno(
        self, idno: str, limit: int = 100, offset: int = 0
    ) -> list[TenderAward]: ...

    @abstractmethod
    async def save(self, award: TenderAward) -> TenderAward: ...

    @abstractmethod
    async def delete(self, award_id: UUID) -> None: ...

    @abstractmethod
    async def count_by_supplier_idno(self, idno: str) -> int: ...

    @abstractmethod
    async def find_successful_by_supplier_idno(self, idno: str) -> list[TenderAward]: ...

    @abstractmethod
    async def find_by_date_range(
        self, start_date: date, end_date: date, limit: int = 100, offset: int = 0
    ) -> list[TenderAward]: ...


class TenderBidRepository(ABC):
    """Repository for tender bids."""

    @abstractmethod
    async def find_by_id(self, bid_id: UUID) -> TenderBid | None: ...

    @abstractmethod
    async def find_by_tender_ocid(
        self, tender_ocid: str, limit: int = 100, offset: int = 0
    ) -> list[TenderBid]: ...

    @abstractmethod
    async def find_by_tenderer_idno(
        self, idno: str, limit: int = 100, offset: int = 0
    ) -> list[TenderBid]: ...

    @abstractmethod
    async def save(self, bid: TenderBid) -> TenderBid: ...

    @abstractmethod
    async def delete(self, bid_id: UUID) -> None: ...
