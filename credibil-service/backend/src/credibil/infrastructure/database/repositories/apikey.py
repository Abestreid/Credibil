from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import func, select

from credibil.domain.apikey.entities import APIKey, APIKeyStatus
from credibil.infrastructure.database.models_organization import APIKeyModel
from credibil.ports.repositories.apikey import APIKeyRepository

if TYPE_CHECKING:
    from uuid import UUID

    from sqlalchemy.ext.asyncio import AsyncSession


class SQLAlchemyAPIKeyRepository(APIKeyRepository):
    """PostgreSQL API key repository via SQLAlchemy."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_id(self, key_id: UUID) -> APIKey | None:
        stmt = select(APIKeyModel).where(APIKeyModel.id == key_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def find_by_hash(self, key_hash: str) -> APIKey | None:
        stmt = select(APIKeyModel).where(APIKeyModel.key_hash == key_hash)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def save(self, api_key: APIKey) -> APIKey:
        model = self._to_model(api_key)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_domain(model)

    async def delete(self, key_id: UUID) -> None:
        stmt = select(APIKeyModel).where(APIKeyModel.id == key_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model:
            await self._session.delete(model)

    async def list_by_tenant(
        self,
        tenant_id: UUID,
        offset: int = 0,
        limit: int = 25,
    ) -> tuple[list[APIKey], int]:
        base = select(APIKeyModel).where(APIKeyModel.tenant_id == tenant_id)
        count_q = (
            select(func.count()).select_from(APIKeyModel).where(APIKeyModel.tenant_id == tenant_id)
        )

        total_result = await self._session.execute(count_q)
        total = total_result.scalar_one()

        base = base.order_by(APIKeyModel.created_at.desc()).offset(offset).limit(limit)
        result = await self._session.execute(base)
        models = list(result.scalars().all())
        return [self._to_domain(m) for m in models], total

    def _to_domain(self, model: APIKeyModel) -> APIKey:
        return APIKey(
            key_id=model.id,
            tenant_id=model.tenant_id,
            name=model.name,
            key_prefix=model.key_prefix,
            key_hash=model.key_hash,
            scopes=model.scopes_ if model.scopes_ else [],
            rate_limit=model.rate_limit,
            status=APIKeyStatus(model.status),
            expires_at=model.expires_at,
            last_used_at=model.last_used_at,
            metadata=model.metadata_ if model.metadata_ else {},
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_model(self, key: APIKey) -> APIKeyModel:
        return APIKeyModel(
            id=key.id,
            tenant_id=key.tenant_id,
            name=key.name,
            key_prefix=key.key_prefix,
            key_hash=key.key_hash,
            scopes_=key.scopes,
            rate_limit=key.rate_limit,
            status=key.status.value,
            expires_at=key.expires_at,
            last_used_at=key.last_used_at,
            metadata_=key.metadata,
            created_at=key.created_at,
            updated_at=key.updated_at,
        )
