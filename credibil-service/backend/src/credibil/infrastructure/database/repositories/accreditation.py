from __future__ import annotations

import contextlib
from datetime import date
from typing import TYPE_CHECKING, Any

from sqlalchemy import func, select

from credibil.domain.accreditation.entities import (
    Accreditation,
    AccreditationCategory,
    AccreditationStatus,
)
from credibil.infrastructure.database.models_accreditation import AccreditationModel
from credibil.ports.repositories.accreditation import AccreditationRepository

if TYPE_CHECKING:
    from uuid import UUID

    from sqlalchemy.ext.asyncio import AsyncSession


def _to_entity(model: AccreditationModel) -> Accreditation:
    issue_date = None
    expiry_date = None
    if model.issue_date:
        with contextlib.suppress(ValueError):
            issue_date = date.strptime(model.issue_date, "%d.%m.%Y")
    if model.expiry_date:
        with contextlib.suppress(ValueError):
            expiry_date = date.strptime(model.expiry_date, "%d.%m.%Y")

    return Accreditation(
        accreditation_id=model.id,
        organization_name=model.organization_name,
        director_name=model.director_name,
        address=model.address,
        phone=model.phone,
        fax=model.fax,
        email=model.email,
        certificate_number=model.certificate_number,
        category=AccreditationCategory(model.category),
        standard=model.standard,
        status=AccreditationStatus(model.status),
        issue_date=issue_date,
        expiry_date=expiry_date,
        scope=model.scope,
        certificate_url=model.certificate_url,
        annex_urls=model.annex_urls or [],
        remarks=model.remarks,
        country_code=model.country_code,
        source_url=model.source_url,
        raw_data=model.raw_data,
        last_synced=model.last_synced,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def _to_model(entity: Accreditation) -> AccreditationModel:
    return AccreditationModel(
        id=entity.id,
        organization_name=entity.organization_name,
        director_name=entity.director_name,
        address=entity.address,
        phone=entity.phone,
        fax=entity.fax,
        email=entity.email,
        certificate_number=entity.certificate_number,
        category=entity.category,
        standard=entity.standard,
        status=entity.status,
        issue_date=entity.issue_date.strftime("%d.%m.%Y") if entity.issue_date else None,
        expiry_date=entity.expiry_date.strftime("%d.%m.%Y") if entity.expiry_date else None,
        scope=entity.scope,
        certificate_url=entity.certificate_url,
        annex_urls=entity.annex_urls,
        remarks=entity.remarks,
        country_code=entity.country_code,
        source_url=entity.source_url,
        raw_data=entity.raw_data,
        last_synced=entity.last_synced,
        created_at=entity.created_at,
        updated_at=entity.updated_at,
    )


class SQLAlchemyAccreditationRepository(AccreditationRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_id(self, accreditation_id: UUID) -> Accreditation | None:
        result = await self._session.execute(
            select(AccreditationModel).where(AccreditationModel.id == accreditation_id)
        )
        model = result.scalar_one_or_none()
        return _to_entity(model) if model else None

    async def find_by_certificate_number(self, cert_number: str) -> Accreditation | None:
        result = await self._session.execute(
            select(AccreditationModel).where(AccreditationModel.certificate_number == cert_number)
        )
        model = result.scalar_one_or_none()
        return _to_entity(model) if model else None

    async def find_by_category(
        self, category: AccreditationCategory, limit: int = 100, offset: int = 0
    ) -> list[Accreditation]:
        result = await self._session.execute(
            select(AccreditationModel)
            .where(AccreditationModel.category == category)
            .order_by(AccreditationModel.organization_name)
            .limit(limit)
            .offset(offset)
        )
        return [_to_entity(m) for m in result.scalars().all()]

    async def find_by_status(
        self, status: AccreditationStatus, limit: int = 100, offset: int = 0
    ) -> list[Accreditation]:
        result = await self._session.execute(
            select(AccreditationModel)
            .where(AccreditationModel.status == status)
            .order_by(AccreditationModel.organization_name)
            .limit(limit)
            .offset(offset)
        )
        return [_to_entity(m) for m in result.scalars().all()]

    async def find_by_organization(
        self, organization_name: str, limit: int = 100, offset: int = 0
    ) -> list[Accreditation]:
        result = await self._session.execute(
            select(AccreditationModel)
            .where(AccreditationModel.organization_name.ilike(f"%{organization_name}%"))
            .order_by(AccreditationModel.organization_name)
            .limit(limit)
            .offset(offset)
        )
        return [_to_entity(m) for m in result.scalars().all()]

    async def save(self, accreditation: Accreditation) -> Accreditation:
        model = _to_model(accreditation)
        await self._session.merge(model)
        await self._session.flush()
        return accreditation

    async def delete(self, accreditation_id: UUID) -> None:
        result = await self._session.execute(
            select(AccreditationModel).where(AccreditationModel.id == accreditation_id)
        )
        model = result.scalar_one_or_none()
        if model:
            await self._session.delete(model)
            await self._session.flush()

    async def list_accreditations(
        self, limit: int = 100, offset: int = 0, filters: dict[str, Any] | None = None
    ) -> list[Accreditation]:
        query = select(AccreditationModel)

        if filters:
            if "category" in filters:
                query = query.where(AccreditationModel.category == filters["category"])
            if "status" in filters:
                query = query.where(AccreditationModel.status == filters["status"])
            if "country_code" in filters:
                query = query.where(AccreditationModel.country_code == filters["country_code"])
            if "keyword" in filters:
                keyword = f"%{filters['keyword']}%"
                query = query.where(
                    AccreditationModel.organization_name.ilike(keyword)
                    | AccreditationModel.certificate_number.ilike(keyword)
                    | AccreditationModel.scope.ilike(keyword)
                )

        query = query.order_by(AccreditationModel.organization_name)
        query = query.limit(limit).offset(offset)

        result = await self._session.execute(query)
        return [_to_entity(m) for m in result.scalars().all()]

    async def count_by_category(self, category: AccreditationCategory) -> int:
        result = await self._session.execute(
            select(func.count())
            .select_from(AccreditationModel)
            .where(AccreditationModel.category == category)
        )
        return result.scalar() or 0

    async def count_by_status(self, status: AccreditationStatus) -> int:
        result = await self._session.execute(
            select(func.count())
            .select_from(AccreditationModel)
            .where(AccreditationModel.status == status)
        )
        return result.scalar() or 0

    async def search_by_keyword(self, keyword: str, limit: int = 100) -> list[Accreditation]:
        pattern = f"%{keyword}%"
        result = await self._session.execute(
            select(AccreditationModel)
            .where(
                AccreditationModel.organization_name.ilike(pattern)
                | AccreditationModel.certificate_number.ilike(pattern)
                | AccreditationModel.scope.ilike(pattern)
                | AccreditationModel.director_name.ilike(pattern)
            )
            .order_by(AccreditationModel.organization_name)
            .limit(limit)
        )
        return [_to_entity(m) for m in result.scalars().all()]
