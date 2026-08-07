from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sqlalchemy import select

from credibil.domain.court.entities import (
    CaseStatus,
    CaseType,
    CourtCase,
    CourtHearing,
    CourtType,
)
from credibil.infrastructure.database.models_court import CourtCaseModel, CourtHearingModel
from credibil.ports.repositories.court_case import CourtCaseRepository, CourtHearingRepository

if TYPE_CHECKING:
    from datetime import date
    from uuid import UUID

    from sqlalchemy.ext.asyncio import AsyncSession


def _case_to_entity(model: CourtCaseModel) -> CourtCase:
    return CourtCase(
        case_id=model.id,
        case_number=model.case_number,
        case_type=CaseType(model.case_type),
        court_name=model.court_name,
        court_type=CourtType(model.court_type),
        court_slug=model.court_slug,
        registration_date=model.registration_date,
        decision_date=model.decision_date,
        status=CaseStatus(model.status),
        plaintiff_name=model.plaintiff_name,
        plaintiff_idno=model.plaintiff_idno,
        defendant_name=model.defendant_name,
        defendant_idno=model.defendant_idno,
        judge_name=model.judge_name,
        subject_matter=model.subject_matter,
        decision_summary=model.decision_summary,
        source_url=model.source_url,
        raw_data=model.raw_data,
        metadata=model.metadata_,
        fetched_at=model.fetched_at,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def _case_to_model(entity: CourtCase) -> CourtCaseModel:
    return CourtCaseModel(
        id=entity.id,
        case_number=entity.case_number,
        case_type=entity.case_type,
        court_name=entity.court_name,
        court_type=entity.court_type,
        court_slug=entity.court_slug,
        registration_date=entity.registration_date,
        decision_date=entity.decision_date,
        status=entity.status,
        plaintiff_name=entity.plaintiff_name,
        plaintiff_idno=entity.plaintiff_idno,
        defendant_name=entity.defendant_name,
        defendant_idno=entity.defendant_idno,
        judge_name=entity.judge_name,
        subject_matter=entity.subject_matter,
        decision_summary=entity.decision_summary,
        source_url=entity.source_url,
        raw_data=entity.raw_data,
        metadata_=entity.metadata,
        fetched_at=entity.fetched_at,
        created_at=entity.created_at,
        updated_at=entity.updated_at,
    )


def _hearing_to_entity(model: CourtHearingModel) -> CourtHearing:
    return CourtHearing(
        hearing_id=model.id,
        case_id=model.case_id,
        case_number=model.case_number,
        hearing_date=model.hearing_date,
        hearing_time=model.hearing_time,
        court_name=model.court_name,
        department=model.department,
        room=model.room,
        judge_name=model.judge_name,
        hearing_type=model.hearing_type,
        outcome=model.outcome,
        source_url=model.source_url,
        raw_data=model.raw_data,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def _hearing_to_model(entity: CourtHearing) -> CourtHearingModel:
    return CourtHearingModel(
        id=entity.id,
        case_id=entity.case_id,
        case_number=entity.case_number,
        hearing_date=entity.hearing_date,
        hearing_time=entity.hearing_time,
        court_name=entity.court_name,
        department=entity.department,
        room=entity.room,
        judge_name=entity.judge_name,
        hearing_type=entity.hearing_type,
        outcome=entity.outcome,
        source_url=entity.source_url,
        raw_data=entity.raw_data,
        created_at=entity.created_at,
        updated_at=entity.updated_at,
    )


class SQLAlchemyCourtCaseRepository(CourtCaseRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_id(self, case_id: UUID) -> CourtCase | None:
        result = await self._session.execute(
            select(CourtCaseModel).where(CourtCaseModel.id == case_id)
        )
        model = result.scalar_one_or_none()
        return _case_to_entity(model) if model else None

    async def find_by_case_number(self, case_number: str) -> CourtCase | None:
        result = await self._session.execute(
            select(CourtCaseModel).where(CourtCaseModel.case_number == case_number)
        )
        model = result.scalar_one_or_none()
        return _case_to_entity(model) if model else None

    async def find_by_idno(
        self, idno: str, role: str | None = None, limit: int = 100, offset: int = 0
    ) -> list[CourtCase]:
        stmt = select(CourtCaseModel)
        if role == "plaintiff":
            stmt = stmt.where(CourtCaseModel.plaintiff_idno == idno)
        elif role == "defendant":
            stmt = stmt.where(CourtCaseModel.defendant_idno == idno)
        else:
            stmt = stmt.where(
                (CourtCaseModel.plaintiff_idno == idno) | (CourtCaseModel.defendant_idno == idno)
            )
        stmt = stmt.order_by(CourtCaseModel.registration_date.desc()).offset(offset).limit(limit)
        result = await self._session.execute(stmt)
        return [_case_to_entity(m) for m in result.scalars().all()]

    async def save(self, case: CourtCase) -> CourtCase:
        existing = await self._session.get(CourtCaseModel, case.id)
        if existing:
            for attr in [
                "case_type",
                "court_name",
                "court_type",
                "court_slug",
                "registration_date",
                "decision_date",
                "status",
                "plaintiff_name",
                "plaintiff_idno",
                "defendant_name",
                "defendant_idno",
                "judge_name",
                "subject_matter",
                "decision_summary",
                "source_url",
                "raw_data",
                "fetched_at",
            ]:
                setattr(existing, attr, getattr(case, attr))
            existing.metadata_ = case.metadata
            existing.updated_at = case.updated_at
            await self._session.flush()
            return _case_to_entity(existing)

        model = _case_to_model(case)
        self._session.add(model)
        await self._session.flush()
        return _case_to_entity(model)

    async def delete(self, case_id: UUID) -> None:
        model = await self._session.get(CourtCaseModel, case_id)
        if model:
            await self._session.delete(model)
            await self._session.flush()

    async def list_cases(
        self, limit: int = 100, offset: int = 0, filters: dict[str, Any] | None = None
    ) -> list[CourtCase]:
        stmt = select(CourtCaseModel)
        if filters:
            for key, value in filters.items():
                if hasattr(CourtCaseModel, key):
                    stmt = stmt.where(getattr(CourtCaseModel, key) == value)
        stmt = stmt.order_by(CourtCaseModel.registration_date.desc()).offset(offset).limit(limit)
        result = await self._session.execute(stmt)
        return [_case_to_entity(m) for m in result.scalars().all()]

    async def count_by_idno(self, idno: str) -> int:
        from sqlalchemy import func

        result = await self._session.execute(
            select(func.count())
            .select_from(CourtCaseModel)
            .where(
                (CourtCaseModel.plaintiff_idno == idno) | (CourtCaseModel.defendant_idno == idno)
            )
        )
        return result.scalar_one()

    async def find_by_court(
        self, court_slug: str, limit: int = 100, offset: int = 0
    ) -> list[CourtCase]:
        result = await self._session.execute(
            select(CourtCaseModel)
            .where(CourtCaseModel.court_slug == court_slug)
            .order_by(CourtCaseModel.registration_date.desc())
            .offset(offset)
            .limit(limit)
        )
        return [_case_to_entity(m) for m in result.scalars().all()]

    async def find_by_date_range(
        self,
        start_date: date,
        end_date: date,
        court_slug: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[CourtCase]:
        stmt = select(CourtCaseModel).where(
            CourtCaseModel.registration_date >= start_date,
            CourtCaseModel.registration_date <= end_date,
        )
        if court_slug:
            stmt = stmt.where(CourtCaseModel.court_slug == court_slug)
        stmt = stmt.order_by(CourtCaseModel.registration_date.desc()).offset(offset).limit(limit)
        result = await self._session.execute(stmt)
        return [_case_to_entity(m) for m in result.scalars().all()]

    async def count_active_by_idno(self, idno: str) -> int:
        from sqlalchemy import func

        result = await self._session.execute(
            select(func.count())
            .select_from(CourtCaseModel)
            .where(
                ((CourtCaseModel.plaintiff_idno == idno) | (CourtCaseModel.defendant_idno == idno)),
                CourtCaseModel.status.in_(["open", "in_progress", "pending"]),
            )
        )
        return result.scalar_one()

    async def find_open_cases_by_idno(self, idno: str) -> list[CourtCase]:
        result = await self._session.execute(
            select(CourtCaseModel).where(
                (CourtCaseModel.plaintiff_idno == idno) | (CourtCaseModel.defendant_idno == idno),
                CourtCaseModel.status.in_(["open", "in_progress", "pending"]),
            )
        )
        return [_case_to_entity(m) for m in result.scalars().all()]


class SQLAlchemyCourtHearingRepository(CourtHearingRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_id(self, hearing_id: UUID) -> CourtHearing | None:
        result = await self._session.execute(
            select(CourtHearingModel).where(CourtHearingModel.id == hearing_id)
        )
        model = result.scalar_one_or_none()
        return _hearing_to_entity(model) if model else None

    async def find_by_case_number(
        self, case_number: str, limit: int = 100, offset: int = 0
    ) -> list[CourtHearing]:
        result = await self._session.execute(
            select(CourtHearingModel)
            .where(CourtHearingModel.case_number == case_number)
            .order_by(CourtHearingModel.hearing_date.desc())
            .offset(offset)
            .limit(limit)
        )
        return [_hearing_to_entity(m) for m in result.scalars().all()]

    async def save(self, hearing: CourtHearing) -> CourtHearing:
        existing = await self._session.get(CourtHearingModel, hearing.id)
        if existing:
            for attr in [
                "case_id",
                "case_number",
                "hearing_date",
                "hearing_time",
                "court_name",
                "department",
                "room",
                "judge_name",
                "hearing_type",
                "outcome",
                "source_url",
                "raw_data",
            ]:
                setattr(existing, attr, getattr(hearing, attr))
            existing.updated_at = hearing.updated_at
            await self._session.flush()
            return _hearing_to_entity(existing)

        model = _hearing_to_model(hearing)
        self._session.add(model)
        await self._session.flush()
        return _hearing_to_entity(model)

    async def delete(self, hearing_id: UUID) -> None:
        model = await self._session.get(CourtHearingModel, hearing_id)
        if model:
            await self._session.delete(model)
            await self._session.flush()

    async def find_upcoming_by_idno(self, idno: str, limit: int = 50) -> list[CourtHearing]:
        from datetime import date as date_type

        result = await self._session.execute(
            select(CourtHearingModel)
            .join(CourtCaseModel, CourtHearingModel.case_number == CourtCaseModel.case_number)
            .where(
                (CourtCaseModel.plaintiff_idno == idno) | (CourtCaseModel.defendant_idno == idno),
                CourtHearingModel.hearing_date >= date_type.today(),
            )
            .order_by(CourtHearingModel.hearing_date.asc())
            .limit(limit)
        )
        return [_hearing_to_entity(m) for m in result.scalars().all()]

    async def find_by_date_range(
        self,
        start_date: date,
        end_date: date,
        court_slug: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[CourtHearing]:
        stmt = select(CourtHearingModel).where(
            CourtHearingModel.hearing_date >= start_date,
            CourtHearingModel.hearing_date <= end_date,
        )
        if court_slug:
            stmt = stmt.where(CourtHearingModel.court_name == court_slug)
        stmt = stmt.order_by(CourtHearingModel.hearing_date.asc()).offset(offset).limit(limit)
        result = await self._session.execute(stmt)
        return [_hearing_to_entity(m) for m in result.scalars().all()]

    async def count_by_case(self, case_number: str) -> int:
        from sqlalchemy import func

        result = await self._session.execute(
            select(func.count())
            .select_from(CourtHearingModel)
            .where(CourtHearingModel.case_number == case_number)
        )
        return result.scalar_one()
