from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sqlalchemy import func, select, update

from credibil.domain.enforcement.entities import (
    EnforcementProceeding,
    EnforcementState,
)
from credibil.infrastructure.database.models_enforcement import EnforcementProceedingModel
from credibil.ports.repositories.enforcement import EnforcementRepository

if TYPE_CHECKING:
    from uuid import UUID

    from sqlalchemy.ext.asyncio import AsyncSession


def _to_entity(model: EnforcementProceedingModel) -> EnforcementProceeding:
    return EnforcementProceeding(
        proceeding_id=model.id,
        somation_id=model.somation_id,
        debtor_name=model.debtor_name,
        debtor_idno=model.debtor_idno,
        debtor_idno_masked=model.debtor_idno_masked,
        creditor_name=model.creditor_name,
        creditor_idno=model.creditor_idno,
        executory_doc_number=model.executory_doc_number,
        court_name=model.court_name,
        case_number=model.case_number,
        amount=model.amount,
        currency=model.currency,
        publication_date=model.publication_date,
        state=EnforcementState(model.state),
        source_url=model.source_url,
        raw_data=model.raw_data,
        metadata=model.metadata_,
        first_seen_at=model.first_seen_at,
        last_seen_at=model.last_seen_at,
        fetched_at=model.fetched_at,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def _to_model(entity: EnforcementProceeding) -> EnforcementProceedingModel:
    return EnforcementProceedingModel(
        id=entity.id,
        somation_id=entity.somation_id,
        debtor_name=entity.debtor_name,
        debtor_idno=entity.debtor_idno,
        debtor_idno_masked=entity.debtor_idno_masked,
        creditor_name=entity.creditor_name,
        creditor_idno=entity.creditor_idno,
        executory_doc_number=entity.executory_doc_number,
        court_name=entity.court_name,
        case_number=entity.case_number,
        amount=entity.amount,
        currency=entity.currency,
        publication_date=entity.publication_date,
        state=entity.state,
        source_url=entity.source_url,
        raw_data=entity.raw_data,
        metadata_=entity.metadata,
        first_seen_at=entity.first_seen_at,
        last_seen_at=entity.last_seen_at,
        fetched_at=entity.fetched_at,
        created_at=entity.created_at,
        updated_at=entity.updated_at,
    )


_UPDATABLE = (
    "somation_id",
    "debtor_name",
    "debtor_idno",
    "debtor_idno_masked",
    "creditor_name",
    "creditor_idno",
    "executory_doc_number",
    "court_name",
    "case_number",
    "amount",
    "currency",
    "publication_date",
    "state",
    "source_url",
    "raw_data",
    "first_seen_at",
    "last_seen_at",
    "fetched_at",
)


class SQLAlchemyEnforcementRepository(EnforcementRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_id(self, proceeding_id: UUID) -> EnforcementProceeding | None:
        model = await self._session.get(EnforcementProceedingModel, proceeding_id)
        return _to_entity(model) if model else None

    async def find_by_somation_id(self, somation_id: int) -> EnforcementProceeding | None:
        result = await self._session.execute(
            select(EnforcementProceedingModel).where(
                EnforcementProceedingModel.somation_id == somation_id
            )
        )
        model = result.scalar_one_or_none()
        return _to_entity(model) if model else None

    def _idno_clause(self, idno: str, role: str | None):
        if role == "debtor":
            return EnforcementProceedingModel.debtor_idno == idno
        if role == "creditor":
            return EnforcementProceedingModel.creditor_idno == idno
        return (EnforcementProceedingModel.debtor_idno == idno) | (
            EnforcementProceedingModel.creditor_idno == idno
        )

    async def find_by_idno(
        self,
        idno: str,
        role: str | None = None,
        state: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[EnforcementProceeding]:
        stmt = select(EnforcementProceedingModel).where(self._idno_clause(idno, role))
        if state:
            stmt = stmt.where(EnforcementProceedingModel.state == state)
        stmt = (
            stmt.order_by(EnforcementProceedingModel.publication_date.desc().nullslast())
            .offset(offset)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return [_to_entity(m) for m in result.scalars().all()]

    async def save(self, proceeding: EnforcementProceeding) -> EnforcementProceeding:
        existing = await self._session.get(EnforcementProceedingModel, proceeding.id)
        if existing:
            for attr in _UPDATABLE:
                setattr(existing, attr, getattr(proceeding, attr))
            existing.metadata_ = proceeding.metadata
            existing.updated_at = proceeding.updated_at
            await self._session.flush()
            return _to_entity(existing)

        model = _to_model(proceeding)
        self._session.add(model)
        await self._session.flush()
        return _to_entity(model)

    async def delete(self, proceeding_id: UUID) -> None:
        model = await self._session.get(EnforcementProceedingModel, proceeding_id)
        if model:
            await self._session.delete(model)
            await self._session.flush()

    async def list_proceedings(
        self,
        limit: int = 100,
        offset: int = 0,
        filters: dict[str, Any] | None = None,
    ) -> list[EnforcementProceeding]:
        stmt = select(EnforcementProceedingModel)
        if filters:
            for key, value in filters.items():
                if hasattr(EnforcementProceedingModel, key):
                    stmt = stmt.where(getattr(EnforcementProceedingModel, key) == value)
        stmt = (
            stmt.order_by(EnforcementProceedingModel.publication_date.desc().nullslast())
            .offset(offset)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return [_to_entity(m) for m in result.scalars().all()]

    async def count_by_idno(
        self, idno: str, role: str | None = None, state: str | None = None
    ) -> int:
        stmt = (
            select(func.count())
            .select_from(EnforcementProceedingModel)
            .where(self._idno_clause(idno, role))
        )
        if state:
            stmt = stmt.where(EnforcementProceedingModel.state == state)
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def all_somation_ids(self) -> set[int]:
        result = await self._session.execute(select(EnforcementProceedingModel.somation_id))
        return {row for (row,) in result.all()}

    async def mark_archived(self, somation_ids: list[int]) -> int:
        if not somation_ids:
            return 0
        result = await self._session.execute(
            update(EnforcementProceedingModel)
            .where(
                EnforcementProceedingModel.somation_id.in_(somation_ids),
                EnforcementProceedingModel.state != EnforcementState.ARCHIVED.value,
            )
            .values(state=EnforcementState.ARCHIVED.value)
        )
        await self._session.flush()
        return result.rowcount or 0
