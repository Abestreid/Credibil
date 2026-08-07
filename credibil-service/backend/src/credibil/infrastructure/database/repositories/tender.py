from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sqlalchemy import func, select

from credibil.domain.tender.entities import (
    AwardStatus,
    BidStatus,
    ProcurementCategory,
    ProcurementMethod,
    Tender,
    TenderAward,
    TenderBid,
    TenderStatus,
)
from credibil.infrastructure.database.models_tender import (
    TenderAwardModel,
    TenderBidModel,
    TenderModel,
)
from credibil.ports.repositories.tender import (
    TenderAwardRepository,
    TenderBidRepository,
    TenderRepository,
)

if TYPE_CHECKING:
    from datetime import date
    from uuid import UUID

    from sqlalchemy.ext.asyncio import AsyncSession


def _tender_to_entity(model: TenderModel) -> Tender:
    return Tender(
        tender_id=model.id,
        ocid=model.ocid,
        title=model.title,
        description=model.description,
        status=TenderStatus(model.status),
        status_details=model.status_details,
        procurement_method=ProcurementMethod(model.procurement_method)
        if model.procurement_method
        else None,
        procurement_method_details=model.procurement_method_details,
        main_category=ProcurementCategory(model.main_category) if model.main_category else None,
        cpv_code=model.cpv_code,
        cpv_description=model.cpv_description,
        buyer_idno=model.buyer_idno,
        buyer_name=model.buyer_name,
        value_amount=model.value_amount,
        value_currency=model.value_currency,
        budget_amount=model.budget_amount,
        budget_currency=model.budget_currency,
        is_eu_funded=model.is_eu_funded,
        tender_start_date=model.tender_start_date,
        tender_end_date=model.tender_end_date,
        contract_start_date=model.contract_start_date,
        contract_end_date=model.contract_end_date,
        published_date=model.published_date,
        source_url=model.source_url,
        raw_data=model.raw_data,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def _tender_to_model(entity: Tender) -> TenderModel:
    return TenderModel(
        id=entity.id,
        ocid=entity.ocid,
        title=entity.title,
        description=entity.description,
        status=entity.status,
        status_details=entity.status_details,
        procurement_method=entity.procurement_method,
        procurement_method_details=entity.procurement_method_details,
        main_category=entity.main_category,
        cpv_code=entity.cpv_code,
        cpv_description=entity.cpv_description,
        buyer_idno=entity.buyer_idno,
        buyer_name=entity.buyer_name,
        value_amount=entity.value_amount,
        value_currency=entity.value_currency,
        budget_amount=entity.budget_amount,
        budget_currency=entity.budget_currency,
        is_eu_funded=entity.is_eu_funded,
        tender_start_date=entity.tender_start_date,
        tender_end_date=entity.tender_end_date,
        contract_start_date=entity.contract_start_date,
        contract_end_date=entity.contract_end_date,
        published_date=entity.published_date,
        source_url=entity.source_url,
        raw_data=entity.raw_data,
        created_at=entity.created_at,
        updated_at=entity.updated_at,
    )


def _award_to_entity(model: TenderAwardModel) -> TenderAward:
    return TenderAward(
        award_id=model.id,
        tender_id=model.tender_id,
        tender_ocid=model.tender_ocid,
        ocds_award_id=model.ocds_award_id,
        status=AwardStatus(model.status),
        status_details=model.status_details,
        award_date=model.award_date,
        value_amount=model.value_amount,
        value_currency=model.value_currency,
        supplier_idno=model.supplier_idno,
        supplier_name=model.supplier_name,
        related_lots=model.related_lots,
        related_bid_id=model.related_bid_id,
        source_url=model.source_url,
        raw_data=model.raw_data,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def _award_to_model(entity: TenderAward) -> TenderAwardModel:
    return TenderAwardModel(
        id=entity.id,
        tender_id=entity.tender_id,
        tender_ocid=entity.tender_ocid,
        ocds_award_id=entity.ocds_award_id,
        status=entity.status,
        status_details=entity.status_details,
        award_date=entity.award_date,
        value_amount=entity.value_amount,
        value_currency=entity.value_currency,
        supplier_idno=entity.supplier_idno,
        supplier_name=entity.supplier_name,
        related_lots=entity.related_lots,
        related_bid_id=entity.related_bid_id,
        source_url=entity.source_url,
        raw_data=entity.raw_data,
        created_at=entity.created_at,
        updated_at=entity.updated_at,
    )


def _bid_to_entity(model: TenderBidModel) -> TenderBid:
    return TenderBid(
        bid_id=model.id,
        tender_id=model.tender_id,
        tender_ocid=model.tender_ocid,
        ocds_bid_id=model.ocds_bid_id,
        status=BidStatus(model.status),
        bid_date=model.bid_date,
        value_amount=model.value_amount,
        value_currency=model.value_currency,
        tenderer_idno=model.tenderer_idno,
        tenderer_name=model.tenderer_name,
        related_lots=model.related_lots,
        source_url=model.source_url,
        raw_data=model.raw_data,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def _bid_to_model(entity: TenderBid) -> TenderBidModel:
    return TenderBidModel(
        id=entity.id,
        tender_id=entity.tender_id,
        tender_ocid=entity.tender_ocid,
        ocds_bid_id=entity.ocds_bid_id,
        status=entity.status,
        bid_date=entity.bid_date,
        value_amount=entity.value_amount,
        value_currency=entity.value_currency,
        tenderer_idno=entity.tenderer_idno,
        tenderer_name=entity.tenderer_name,
        related_lots=entity.related_lots,
        source_url=entity.source_url,
        raw_data=entity.raw_data,
        created_at=entity.created_at,
        updated_at=entity.updated_at,
    )


class SQLAlchemyTenderRepository(TenderRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_id(self, tender_id: UUID) -> Tender | None:
        result = await self._session.execute(select(TenderModel).where(TenderModel.id == tender_id))
        model = result.scalar_one_or_none()
        return _tender_to_entity(model) if model else None

    async def find_by_ocid(self, ocid: str) -> Tender | None:
        result = await self._session.execute(select(TenderModel).where(TenderModel.ocid == ocid))
        model = result.scalar_one_or_none()
        return _tender_to_entity(model) if model else None

    async def find_by_buyer_idno(
        self, idno: str, limit: int = 100, offset: int = 0
    ) -> list[Tender]:
        result = await self._session.execute(
            select(TenderModel)
            .where(TenderModel.buyer_idno == idno)
            .order_by(TenderModel.published_date.desc())
            .offset(offset)
            .limit(limit)
        )
        return [_tender_to_entity(m) for m in result.scalars().all()]

    async def find_by_supplier_idno(
        self, idno: str, limit: int = 100, offset: int = 0
    ) -> list[Tender]:
        """Find tenders where a company appeared as a supplier via awards."""
        subq = (
            select(TenderAwardModel.tender_ocid)
            .where(TenderAwardModel.supplier_idno == idno)
            .distinct()
        )
        result = await self._session.execute(
            select(TenderModel)
            .where(TenderModel.ocid.in_(subq))
            .order_by(TenderModel.published_date.desc())
            .offset(offset)
            .limit(limit)
        )
        return [_tender_to_entity(m) for m in result.scalars().all()]

    async def save(self, tender: Tender) -> Tender:
        existing = await self._session.execute(
            select(TenderModel).where(TenderModel.ocid == tender.ocid)
        )
        existing_model = existing.scalar_one_or_none()

        if existing_model:
            for attr in [
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
            ]:
                setattr(existing_model, attr, getattr(tender, attr))
            existing_model.updated_at = tender.updated_at
            await self._session.flush()
            return _tender_to_entity(existing_model)

        model = _tender_to_model(tender)
        self._session.add(model)
        await self._session.flush()
        return _tender_to_entity(model)

    async def delete(self, tender_id: UUID) -> None:
        model = await self._session.get(TenderModel, tender_id)
        if model:
            await self._session.delete(model)
            await self._session.flush()

    async def list_tenders(
        self, limit: int = 100, offset: int = 0, filters: dict[str, Any] | None = None
    ) -> list[Tender]:
        stmt = select(TenderModel)
        if filters:
            for key, value in filters.items():
                if hasattr(TenderModel, key):
                    stmt = stmt.where(getattr(TenderModel, key) == value)
        stmt = stmt.order_by(TenderModel.published_date.desc()).offset(offset).limit(limit)
        result = await self._session.execute(stmt)
        return [_tender_to_entity(m) for m in result.scalars().all()]

    async def count_by_buyer_idno(self, idno: str) -> int:
        result = await self._session.execute(
            select(func.count()).select_from(TenderModel).where(TenderModel.buyer_idno == idno)
        )
        return result.scalar_one()

    async def find_by_date_range(
        self, start_date: date, end_date: date, limit: int = 100, offset: int = 0
    ) -> list[Tender]:
        result = await self._session.execute(
            select(TenderModel)
            .where(
                TenderModel.published_date >= start_date,
                TenderModel.published_date <= end_date,
            )
            .order_by(TenderModel.published_date.desc())
            .offset(offset)
            .limit(limit)
        )
        return [_tender_to_entity(m) for m in result.scalars().all()]

    async def find_by_status(self, status: str, limit: int = 100, offset: int = 0) -> list[Tender]:
        result = await self._session.execute(
            select(TenderModel)
            .where(TenderModel.status == status)
            .order_by(TenderModel.published_date.desc())
            .offset(offset)
            .limit(limit)
        )
        return [_tender_to_entity(m) for m in result.scalars().all()]

    async def find_active_by_buyer_idno(self, idno: str) -> list[Tender]:
        result = await self._session.execute(
            select(TenderModel).where(
                TenderModel.buyer_idno == idno,
                TenderModel.status.in_(["active", "planning", "planning_notice"]),
            )
        )
        return [_tender_to_entity(m) for m in result.scalars().all()]

    async def find_by_cpv_code(
        self, cpv_code: str, limit: int = 100, offset: int = 0
    ) -> list[Tender]:
        result = await self._session.execute(
            select(TenderModel)
            .where(TenderModel.cpv_code == cpv_code)
            .order_by(TenderModel.published_date.desc())
            .offset(offset)
            .limit(limit)
        )
        return [_tender_to_entity(m) for m in result.scalars().all()]


class SQLAlchemyTenderAwardRepository(TenderAwardRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_id(self, award_id: UUID) -> TenderAward | None:
        result = await self._session.execute(
            select(TenderAwardModel).where(TenderAwardModel.id == award_id)
        )
        model = result.scalar_one_or_none()
        return _award_to_entity(model) if model else None

    async def find_by_tender_ocid(
        self, tender_ocid: str, limit: int = 100, offset: int = 0
    ) -> list[TenderAward]:
        result = await self._session.execute(
            select(TenderAwardModel)
            .where(TenderAwardModel.tender_ocid == tender_ocid)
            .order_by(TenderAwardModel.award_date.desc())
            .offset(offset)
            .limit(limit)
        )
        return [_award_to_entity(m) for m in result.scalars().all()]

    async def find_by_supplier_idno(
        self, idno: str, limit: int = 100, offset: int = 0
    ) -> list[TenderAward]:
        result = await self._session.execute(
            select(TenderAwardModel)
            .where(TenderAwardModel.supplier_idno == idno)
            .order_by(TenderAwardModel.award_date.desc())
            .offset(offset)
            .limit(limit)
        )
        return [_award_to_entity(m) for m in result.scalars().all()]

    async def save(self, award: TenderAward) -> TenderAward:
        existing = await self._session.execute(
            select(TenderAwardModel).where(
                TenderAwardModel.tender_ocid == award.tender_ocid,
                TenderAwardModel.ocds_award_id == award.ocds_award_id,
            )
        )
        existing_model = existing.scalar_one_or_none()

        if existing_model:
            for attr in [
                "tender_id",
                "status",
                "status_details",
                "award_date",
                "value_amount",
                "value_currency",
                "supplier_idno",
                "supplier_name",
                "related_lots",
                "related_bid_id",
                "source_url",
                "raw_data",
            ]:
                setattr(existing_model, attr, getattr(award, attr))
            existing_model.updated_at = award.updated_at
            await self._session.flush()
            return _award_to_entity(existing_model)

        model = _award_to_model(award)
        self._session.add(model)
        await self._session.flush()
        return _award_to_entity(model)

    async def delete(self, award_id: UUID) -> None:
        model = await self._session.get(TenderAwardModel, award_id)
        if model:
            await self._session.delete(model)
            await self._session.flush()

    async def count_by_supplier_idno(self, idno: str) -> int:
        result = await self._session.execute(
            select(func.count())
            .select_from(TenderAwardModel)
            .where(TenderAwardModel.supplier_idno == idno)
        )
        return result.scalar_one()

    async def find_successful_by_supplier_idno(self, idno: str) -> list[TenderAward]:
        result = await self._session.execute(
            select(TenderAwardModel).where(
                TenderAwardModel.supplier_idno == idno,
                TenderAwardModel.status.in_(["active", "complete"]),
            )
        )
        return [_award_to_entity(m) for m in result.scalars().all()]

    async def find_by_date_range(
        self, start_date: date, end_date: date, limit: int = 100, offset: int = 0
    ) -> list[TenderAward]:
        result = await self._session.execute(
            select(TenderAwardModel)
            .where(
                TenderAwardModel.award_date >= start_date,
                TenderAwardModel.award_date <= end_date,
            )
            .order_by(TenderAwardModel.award_date.desc())
            .offset(offset)
            .limit(limit)
        )
        return [_award_to_entity(m) for m in result.scalars().all()]


class SQLAlchemyTenderBidRepository(TenderBidRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_id(self, bid_id: UUID) -> TenderBid | None:
        result = await self._session.execute(
            select(TenderBidModel).where(TenderBidModel.id == bid_id)
        )
        model = result.scalar_one_or_none()
        return _bid_to_entity(model) if model else None

    async def find_by_tender_ocid(
        self, tender_ocid: str, limit: int = 100, offset: int = 0
    ) -> list[TenderBid]:
        result = await self._session.execute(
            select(TenderBidModel)
            .where(TenderBidModel.tender_ocid == tender_ocid)
            .order_by(TenderBidModel.bid_date.desc())
            .offset(offset)
            .limit(limit)
        )
        return [_bid_to_entity(m) for m in result.scalars().all()]

    async def find_by_tenderer_idno(
        self, idno: str, limit: int = 100, offset: int = 0
    ) -> list[TenderBid]:
        result = await self._session.execute(
            select(TenderBidModel)
            .where(TenderBidModel.tenderer_idno == idno)
            .order_by(TenderBidModel.bid_date.desc())
            .offset(offset)
            .limit(limit)
        )
        return [_bid_to_entity(m) for m in result.scalars().all()]

    async def save(self, bid: TenderBid) -> TenderBid:
        existing = await self._session.execute(
            select(TenderBidModel).where(
                TenderBidModel.tender_ocid == bid.tender_ocid,
                TenderBidModel.ocds_bid_id == bid.ocds_bid_id,
            )
        )
        existing_model = existing.scalar_one_or_none()

        if existing_model:
            for attr in [
                "tender_id",
                "status",
                "bid_date",
                "value_amount",
                "value_currency",
                "tenderer_idno",
                "tenderer_name",
                "related_lots",
                "source_url",
                "raw_data",
            ]:
                setattr(existing_model, attr, getattr(bid, attr))
            existing_model.updated_at = bid.updated_at
            await self._session.flush()
            return _bid_to_entity(existing_model)

        model = _bid_to_model(bid)
        self._session.add(model)
        await self._session.flush()
        return _bid_to_entity(model)

    async def delete(self, bid_id: UUID) -> None:
        model = await self._session.get(TenderBidModel, bid_id)
        if model:
            await self._session.delete(model)
            await self._session.flush()
