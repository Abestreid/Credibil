from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import delete, func, select

from credibil.domain.audit.entities import AuditLogEntry
from credibil.infrastructure.database.models_audit import AuditLogModel
from credibil.ports.repositories.audit_log import AuditLogRepository

if TYPE_CHECKING:
    from datetime import datetime

    from sqlalchemy.ext.asyncio import AsyncSession


class SQLAlchemyAuditLogRepository(AuditLogRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def _to_entity(self, model: AuditLogModel) -> AuditLogEntry:
        return AuditLogEntry(
            id=model.id,
            request_id=model.request_id,
            method=model.method,
            path=model.path,
            status_code=model.status_code,
            client_ip=model.client_ip,
            user_id=model.user_id,
            api_key_prefix=model.api_key_prefix,
            user_agent=model.user_agent or "",
            request_body=model.request_body,
            duration_ms=float(model.duration_ms),
            error_message=model.error_message,
            created_at=model.created_at,
        )

    def _to_model(self, entry: AuditLogEntry) -> AuditLogModel:
        return AuditLogModel(
            id=entry.id,
            request_id=entry.request_id,
            method=entry.method,
            path=entry.path,
            status_code=entry.status_code,
            client_ip=entry.client_ip,
            user_id=entry.user_id,
            api_key_prefix=entry.api_key_prefix,
            user_agent=entry.user_agent,
            request_body=entry.request_body,
            duration_ms=int(entry.duration_ms),
            error_message=entry.error_message,
            created_at=entry.created_at,
        )

    async def create(self, entry: AuditLogEntry) -> AuditLogEntry:
        model = self._to_model(entry)
        self.session.add(model)
        await self.session.flush()
        return entry

    async def find_by_request_id(self, request_id: str) -> AuditLogEntry | None:
        result = await self.session.execute(
            select(AuditLogModel).where(AuditLogModel.request_id == request_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def list_recent(self, limit: int = 100) -> list[AuditLogEntry]:
        result = await self.session.execute(
            select(AuditLogModel).order_by(AuditLogModel.created_at.desc()).limit(limit)
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    async def list_by_user(self, user_id: str, limit: int = 100) -> list[AuditLogEntry]:
        result = await self.session.execute(
            select(AuditLogModel)
            .where(AuditLogModel.user_id == user_id)
            .order_by(AuditLogModel.created_at.desc())
            .limit(limit)
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    async def list_by_path(self, path: str, limit: int = 100) -> list[AuditLogEntry]:
        result = await self.session.execute(
            select(AuditLogModel)
            .where(AuditLogModel.path.ilike(f"%{path}%"))
            .order_by(AuditLogModel.created_at.desc())
            .limit(limit)
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    async def list_by_date_range(self, start: datetime, end: datetime) -> list[AuditLogEntry]:
        result = await self.session.execute(
            select(AuditLogModel)
            .where(AuditLogModel.created_at.between(start, end))
            .order_by(AuditLogModel.created_at.desc())
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    async def count_total(self) -> int:
        result = await self.session.execute(select(func.count(AuditLogModel.id)))
        return result.scalar_one()

    async def purge_before(self, cutoff: datetime) -> int:
        result = await self.session.execute(
            delete(AuditLogModel).where(AuditLogModel.created_at < cutoff)
        )
        return result.rowcount
