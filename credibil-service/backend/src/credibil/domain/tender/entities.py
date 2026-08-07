from __future__ import annotations

from datetime import date, datetime
from enum import StrEnum
from typing import TYPE_CHECKING, Any

from credibil.core.id import new_id

if TYPE_CHECKING:
    from uuid import UUID


class TenderStatus(StrEnum):
    PLANNING = "planning"
    PLANNING_NOTICE = "planning_notice"
    ACTIVE = "active"
    CANCELLED = "cancelled"
    COMPLETE = "complete"
    UNSUCCESSFUL = "unsuccessful"


class ProcurementMethod(StrEnum):
    OPEN = "open"
    LIMITED = "limited"
    DIRECT = "direct"
    NEGOTIATED = "negotiated"


class ProcurementCategory(StrEnum):
    GOODS = "goods"
    SERVICES = "services"
    WORKS = "works"


class AwardStatus(StrEnum):
    PENDING = "pending"
    ACTIVE = "active"
    CANCELLED = "cancelled"
    UNSUCCESSFUL = "unsuccessful"
    COMPLETE = "complete"


class BidStatus(StrEnum):
    PENDING = "pending"
    VALID = "valid"
    DISQUALIFIED = "disqualified"
    WITHDRAWN = "withdrawn"


class Tender:
    """A public procurement tender from mtender.gov.md (OCDS format)."""

    def __init__(
        self,
        *,
        tender_id: UUID | None = None,
        ocid: str,
        title: str,
        description: str | None = None,
        status: TenderStatus = TenderStatus.PLANNING,
        status_details: str | None = None,
        procurement_method: ProcurementMethod | None = None,
        procurement_method_details: str | None = None,
        main_category: ProcurementCategory | None = None,
        cpv_code: str | None = None,
        cpv_description: str | None = None,
        buyer_idno: str | None = None,
        buyer_name: str | None = None,
        value_amount: float | None = None,
        value_currency: str | None = None,
        budget_amount: float | None = None,
        budget_currency: str | None = None,
        is_eu_funded: bool = False,
        tender_start_date: date | None = None,
        tender_end_date: date | None = None,
        contract_start_date: date | None = None,
        contract_end_date: date | None = None,
        published_date: datetime | None = None,
        source_url: str | None = None,
        raw_data: dict[str, Any] | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        self.id = tender_id or new_id()
        self.ocid = ocid
        self.title = title
        self.description = description
        self.status = status
        self.status_details = status_details
        self.procurement_method = procurement_method
        self.procurement_method_details = procurement_method_details
        self.main_category = main_category
        self.cpv_code = cpv_code
        self.cpv_description = cpv_description
        self.buyer_idno = buyer_idno
        self.buyer_name = buyer_name
        self.value_amount = value_amount
        self.value_currency = value_currency
        self.budget_amount = budget_amount
        self.budget_currency = budget_currency
        self.is_eu_funded = is_eu_funded
        self.tender_start_date = tender_start_date
        self.tender_end_date = tender_end_date
        self.contract_start_date = contract_start_date
        self.contract_end_date = contract_end_date
        self.published_date = published_date
        self.source_url = source_url
        self.raw_data = raw_data or {}
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    def update(self, **kwargs: Any) -> None:
        allowed = {
            "title",
            "description",
            "status",
            "status_details",
            "procurement_method",
            "procurement_method_details",
            "main_category",
            "cpv_code",
            "cpv_description",
            "buyer_idno",
            "buyer_name",
            "value_amount",
            "value_currency",
            "budget_amount",
            "budget_currency",
            "is_eu_funded",
            "tender_start_date",
            "tender_end_date",
            "contract_start_date",
            "contract_end_date",
            "published_date",
            "source_url",
            "raw_data",
        }
        for key, value in kwargs.items():
            if key in allowed:
                setattr(self, key, value)
        self.updated_at = datetime.utcnow()

    @property
    def is_active(self) -> bool:
        return self.status in (
            TenderStatus.ACTIVE,
            TenderStatus.PLANNING,
            TenderStatus.PLANNING_NOTICE,
        )

    def __repr__(self) -> str:
        return f"<Tender ocid={self.ocid!r} title={self.title[:50]!r} status={self.status}>"


class TenderAward:
    """An award decision for a tender."""

    def __init__(
        self,
        *,
        award_id: UUID | None = None,
        tender_id: UUID | None = None,
        tender_ocid: str,
        ocds_award_id: str | None = None,
        status: AwardStatus = AwardStatus.PENDING,
        status_details: str | None = None,
        award_date: date | None = None,
        value_amount: float | None = None,
        value_currency: str | None = None,
        supplier_idno: str | None = None,
        supplier_name: str | None = None,
        related_lots: list[str] | None = None,
        related_bid_id: str | None = None,
        source_url: str | None = None,
        raw_data: dict[str, Any] | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        self.id = award_id or new_id()
        self.tender_id = tender_id
        self.tender_ocid = tender_ocid
        self.ocds_award_id = ocds_award_id
        self.status = status
        self.status_details = status_details
        self.award_date = award_date
        self.value_amount = value_amount
        self.value_currency = value_currency
        self.supplier_idno = supplier_idno
        self.supplier_name = supplier_name
        self.related_lots = related_lots or []
        self.related_bid_id = related_bid_id
        self.source_url = source_url
        self.raw_data = raw_data or {}
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    @property
    def is_successful(self) -> bool:
        return self.status in (AwardStatus.ACTIVE, AwardStatus.COMPLETE)

    def __repr__(self) -> str:
        return (
            f"<TenderAward tender={self.tender_ocid!r} "
            f"supplier={self.supplier_name!r} status={self.status}>"
        )


class TenderBid:
    """A bid/proposal submitted for a tender."""

    def __init__(
        self,
        *,
        bid_id: UUID | None = None,
        tender_id: UUID | None = None,
        tender_ocid: str,
        ocds_bid_id: str | None = None,
        status: BidStatus = BidStatus.PENDING,
        bid_date: date | None = None,
        value_amount: float | None = None,
        value_currency: str | None = None,
        tenderer_idno: str | None = None,
        tenderer_name: str | None = None,
        related_lots: list[str] | None = None,
        source_url: str | None = None,
        raw_data: dict[str, Any] | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        self.id = bid_id or new_id()
        self.tender_id = tender_id
        self.tender_ocid = tender_ocid
        self.ocds_bid_id = ocds_bid_id
        self.status = status
        self.bid_date = bid_date
        self.value_amount = value_amount
        self.value_currency = value_currency
        self.tenderer_idno = tenderer_idno
        self.tenderer_name = tenderer_name
        self.related_lots = related_lots or []
        self.source_url = source_url
        self.raw_data = raw_data or {}
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    def __repr__(self) -> str:
        return (
            f"<TenderBid tender={self.tender_ocid!r} "
            f"tenderer={self.tenderer_name!r} status={self.status}>"
        )
