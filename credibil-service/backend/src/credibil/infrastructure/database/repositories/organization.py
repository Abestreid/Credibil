from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import func, select

from credibil.domain.organization.entities import Organization, OrganizationPlan, OrganizationStatus
from credibil.infrastructure.database.models_organization import OrganizationModel
from credibil.ports.repositories.organization import OrganizationRepository

if TYPE_CHECKING:
    from uuid import UUID

    from sqlalchemy.ext.asyncio import AsyncSession


class SQLOrganizationRepository(OrganizationRepository):
    """PostgreSQL organization repository via SQLAlchemy."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_id(self, org_id: UUID) -> Organization | None:
        stmt = select(OrganizationModel).where(OrganizationModel.id == org_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def find_by_slug(self, slug: str) -> Organization | None:
        stmt = select(OrganizationModel).where(OrganizationModel.slug == slug.lower())
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def save(self, organization: Organization) -> Organization:
        model = self._to_model(organization)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_domain(model)

    async def delete(self, org_id: UUID) -> None:
        stmt = select(OrganizationModel).where(OrganizationModel.id == org_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model:
            await self._session.delete(model)

    async def list_organizations(
        self,
        offset: int = 0,
        limit: int = 25,
    ) -> tuple[list[Organization], int]:
        base = select(OrganizationModel)
        count_q = select(func.count()).select_from(OrganizationModel)

        total_result = await self._session.execute(count_q)
        total = total_result.scalar_one()

        base = base.order_by(OrganizationModel.created_at.desc()).offset(offset).limit(limit)
        result = await self._session.execute(base)
        models = list(result.scalars().all())
        return [self._to_domain(m) for m in models], total

    async def count_by_slug(self, slug: str) -> int:
        stmt = (
            select(func.count())
            .select_from(OrganizationModel)
            .where(OrganizationModel.slug == slug.lower())
        )
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def exists(self, org_id: UUID) -> bool:
        stmt = (
            select(func.count())
            .select_from(OrganizationModel)
            .where(OrganizationModel.id == org_id)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one() > 0

    def _to_domain(self, model: OrganizationModel) -> Organization:
        return Organization(
            org_id=model.id,
            name=model.name,
            slug=model.slug,
            plan=OrganizationPlan(model.plan),
            status=OrganizationStatus(model.status),
            max_users=model.max_users,
            max_api_calls=model.max_api_calls,
            settings=model.settings_ if model.settings_ else {},
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_model(self, org: Organization) -> OrganizationModel:
        return OrganizationModel(
            id=org.id,
            name=org.name,
            slug=org.slug,
            plan=org.plan.value,
            status=org.status.value,
            max_users=org.max_users,
            max_api_calls=org.max_api_calls,
            settings_=org.settings,
            created_at=org.created_at,
            updated_at=org.updated_at,
        )
