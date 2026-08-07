from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import select

from credibil.domain.sync.entities import SyncHistory, SyncStatus, SyncType
from credibil.infrastructure.database.models_sync import SyncHistoryModel
from credibil.ports.repositories.sync_history import SyncHistoryRepository

if TYPE_CHECKING:
    from uuid import UUID

    from sqlalchemy.ext.asyncio import AsyncSession


def _to_entity(model: SyncHistoryModel) -> SyncHistory:
    return SyncHistory(
        sync_id=model.id,
        provider_id=model.provider_id,
        sync_type=SyncType(model.sync_type),
        country_code=model.country_code,
        status=SyncStatus(model.status),
        started_at=model.started_at,
        finished_at=model.finished_at,
        records_total=model.records_total,
        records_created=model.records_created,
        records_updated=model.records_updated,
        records_unchanged=model.records_unchanged,
        records_failed=model.records_failed,
        error_message=model.error_message,
        file_checksum=model.file_checksum,
        file_path=model.file_path,
        duration_seconds=model.duration_seconds,
        metadata=model.metadata_,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def _to_model(entity: SyncHistory) -> SyncHistoryModel:
    return SyncHistoryModel(
        id=entity.id,
        provider_id=entity.provider_id,
        sync_type=entity.sync_type,
        country_code=entity.country_code,
        status=entity.status,
        started_at=entity.started_at,
        finished_at=entity.finished_at,
        records_total=entity.records_total,
        records_created=entity.records_created,
        records_updated=entity.records_updated,
        records_unchanged=entity.records_unchanged,
        records_failed=entity.records_failed,
        error_message=entity.error_message,
        file_checksum=entity.file_checksum,
        file_path=entity.file_path,
        duration_seconds=entity.duration_seconds,
        metadata_=entity.metadata,
        created_at=entity.created_at,
        updated_at=entity.updated_at,
    )


class SQLAlchemySyncHistoryRepository(SyncHistoryRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_id(self, sync_id: UUID) -> SyncHistory | None:
        result = await self._session.execute(
            select(SyncHistoryModel).where(SyncHistoryModel.id == sync_id)
        )
        model = result.scalar_one_or_none()
        return _to_entity(model) if model else None

    async def save(self, sync: SyncHistory) -> SyncHistory:
        existing = await self._session.get(SyncHistoryModel, sync.id)
        if existing:
            for attr in [
                "status",
                "started_at",
                "finished_at",
                "records_total",
                "records_created",
                "records_updated",
                "records_unchanged",
                "records_failed",
                "error_message",
                "file_checksum",
                "file_path",
                "duration_seconds",
            ]:
                setattr(existing, attr, getattr(sync, attr))
            existing.metadata_ = sync.metadata
            existing.updated_at = sync.updated_at
            await self._session.flush()
            return _to_entity(existing)

        model = _to_model(sync)
        self._session.add(model)
        await self._session.flush()
        return _to_entity(model)

    async def find_running_by_provider(self, provider_id: str) -> SyncHistory | None:
        result = await self._session.execute(
            select(SyncHistoryModel).where(
                SyncHistoryModel.provider_id == provider_id,
                SyncHistoryModel.status == SyncStatus.RUNNING,
            )
        )
        model = result.scalar_one_or_none()
        return _to_entity(model) if model else None

    async def find_latest_completed(
        self, provider_id: str, sync_type: SyncType
    ) -> SyncHistory | None:
        result = await self._session.execute(
            select(SyncHistoryModel)
            .where(
                SyncHistoryModel.provider_id == provider_id,
                SyncHistoryModel.sync_type == sync_type,
                SyncHistoryModel.status == SyncStatus.COMPLETED,
            )
            .order_by(SyncHistoryModel.finished_at.desc())
            .limit(1)
        )
        model = result.scalar_one_or_none()
        return _to_entity(model) if model else None

    async def list_by_provider(
        self, provider_id: str, limit: int = 20, offset: int = 0
    ) -> list[SyncHistory]:
        result = await self._session.execute(
            select(SyncHistoryModel)
            .where(SyncHistoryModel.provider_id == provider_id)
            .order_by(SyncHistoryModel.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return [_to_entity(m) for m in result.scalars().all()]

    async def count_by_provider(self, provider_id: str) -> int:
        from sqlalchemy import func

        result = await self._session.execute(
            select(func.count())
            .select_from(SyncHistoryModel)
            .where(SyncHistoryModel.provider_id == provider_id)
        )
        return result.scalar_one()

    async def delete(self, sync_id: UUID) -> None:
        model = await self._session.get(SyncHistoryModel, sync_id)
        if model:
            await self._session.delete(model)
            await self._session.flush()
