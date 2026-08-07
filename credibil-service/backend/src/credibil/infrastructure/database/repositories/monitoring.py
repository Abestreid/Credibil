from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

from sqlalchemy import func, select, text, update

from credibil.domain.monitoring.entities import (
    ChangeCategory,
    CompanyChangeEvent,
    MonitoredCompany,
    MonitoringNotification,
)
from credibil.infrastructure.database.models_monitoring import (
    CompanyChangeEventModel,
    MonitoredCompanyModel,
    MonitoringNotificationModel,
)
from credibil.ports.repositories.monitoring import MonitoringRepository

if TYPE_CHECKING:
    from uuid import UUID

    from sqlalchemy.ext.asyncio import AsyncSession


def _monitored_to_entity(m: MonitoredCompanyModel) -> MonitoredCompany:
    return MonitoredCompany(
        monitored_id=m.id,
        user_id=m.user_id,
        idno=m.idno,
        company_id=m.company_id,
        company_name=m.company_name,
        is_active=m.is_active,
        created_at=m.created_at,
        last_checked_at=m.last_checked_at,
        last_change_at=m.last_change_at,
        updated_at=m.updated_at,
    )


def _event_to_entity(m: CompanyChangeEventModel) -> CompanyChangeEvent:
    return CompanyChangeEvent(
        event_id=m.id,
        idno=m.idno,
        category=ChangeCategory(m.category),
        field=m.field,
        description=m.description,
        old_value=m.old_value,
        new_value=m.new_value,
        batch_id=m.batch_id,
        detected_at=m.detected_at,
    )


def _notification_to_entity(m: MonitoringNotificationModel) -> MonitoringNotification:
    meta = m.metadata_ or {}
    return MonitoringNotification(
        notification_id=m.id,
        user_id=m.user_id,
        idno=m.idno,
        company_name=m.company_name,
        change_count=m.change_count,
        change_event_ids=meta.get("change_event_ids", []),
        categories=meta.get("categories", []),
        summary=m.summary,
        is_read=m.is_read,
        email_sent=m.email_sent,
        created_at=m.created_at,
        read_at=m.read_at,
    )


class SQLAlchemyMonitoringRepository(MonitoringRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # ------------------------------------------------------------ subscriptions
    async def add_monitored(self, monitored: MonitoredCompany) -> MonitoredCompany:
        existing = await self._session.execute(
            select(MonitoredCompanyModel).where(
                MonitoredCompanyModel.user_id == monitored.user_id,
                MonitoredCompanyModel.idno == monitored.idno,
            )
        )
        model = existing.scalar_one_or_none()
        if model:
            model.is_active = True
            model.company_id = monitored.company_id or model.company_id
            model.company_name = monitored.company_name or model.company_name
            await self._session.flush()
            return _monitored_to_entity(model)

        model = MonitoredCompanyModel(
            id=monitored.id,
            user_id=monitored.user_id,
            idno=monitored.idno,
            company_id=monitored.company_id,
            company_name=monitored.company_name,
            is_active=True,
        )
        self._session.add(model)
        await self._session.flush()
        return _monitored_to_entity(model)

    async def remove_monitored(self, user_id: UUID, idno: str) -> bool:
        result = await self._session.execute(
            update(MonitoredCompanyModel)
            .where(
                MonitoredCompanyModel.user_id == user_id,
                MonitoredCompanyModel.idno == idno,
                MonitoredCompanyModel.is_active.is_(True),
            )
            .values(is_active=False)
        )
        await self._session.flush()
        return (result.rowcount or 0) > 0

    async def find_monitored(self, user_id: UUID, idno: str) -> MonitoredCompany | None:
        result = await self._session.execute(
            select(MonitoredCompanyModel).where(
                MonitoredCompanyModel.user_id == user_id,
                MonitoredCompanyModel.idno == idno,
            )
        )
        model = result.scalar_one_or_none()
        return _monitored_to_entity(model) if model else None

    async def list_monitored(self, user_id: UUID) -> list[MonitoredCompany]:
        result = await self._session.execute(
            select(MonitoredCompanyModel)
            .where(
                MonitoredCompanyModel.user_id == user_id,
                MonitoredCompanyModel.is_active.is_(True),
            )
            .order_by(MonitoredCompanyModel.created_at.desc())
        )
        return [_monitored_to_entity(m) for m in result.scalars().all()]

    async def distinct_monitored_idnos(self) -> list[str]:
        result = await self._session.execute(
            select(MonitoredCompanyModel.idno)
            .where(MonitoredCompanyModel.is_active.is_(True))
            .distinct()
        )
        return [row for (row,) in result.all()]

    async def watchers_of(self, idno: str) -> list[MonitoredCompany]:
        result = await self._session.execute(
            select(MonitoredCompanyModel).where(
                MonitoredCompanyModel.idno == idno,
                MonitoredCompanyModel.is_active.is_(True),
            )
        )
        return [_monitored_to_entity(m) for m in result.scalars().all()]

    async def touch_checked(self, idno: str, changed: bool) -> None:
        values: dict[str, Any] = {"last_checked_at": func.now()}
        if changed:
            values["last_change_at"] = func.now()
        await self._session.execute(
            update(MonitoredCompanyModel)
            .where(
                MonitoredCompanyModel.idno == idno,
                MonitoredCompanyModel.is_active.is_(True),
            )
            .values(**values)
        )
        await self._session.flush()

    # ----------------------------------------------------------------- snapshots
    async def get_snapshot(self, idno: str) -> dict[str, Any] | None:
        result = await self._session.execute(
            text(
                "SELECT snapshot_hash, snapshot_json, snapshot_at "
                "FROM company_snapshots WHERE idno = :idno"
            ),
            {"idno": idno},
        )
        row = result.first()
        if not row:
            return None
        return {"hash": row[0], "snapshot": row[1], "snapshot_at": row[2]}

    async def save_snapshot(
        self, idno: str, snapshot_hash: str, snapshot: dict[str, Any]
    ) -> None:
        # Rotate current -> prev in one atomic upsert (2-slot buffer).
        await self._session.execute(
            text(
                """
                INSERT INTO company_snapshots (idno, snapshot_hash, snapshot_json, snapshot_at)
                VALUES (:idno, :hash, CAST(:snapshot AS jsonb), NOW())
                ON CONFLICT (idno) DO UPDATE SET
                    prev_snapshot_json = company_snapshots.snapshot_json,
                    prev_snapshot_at   = company_snapshots.snapshot_at,
                    snapshot_hash      = EXCLUDED.snapshot_hash,
                    snapshot_json      = EXCLUDED.snapshot_json,
                    snapshot_at        = EXCLUDED.snapshot_at
                """
            ),
            {"idno": idno, "hash": snapshot_hash, "snapshot": json.dumps(snapshot, default=str)},
        )
        await self._session.flush()

    # ------------------------------------------------------------- change events
    async def add_change_events(self, events: list[CompanyChangeEvent]) -> None:
        for e in events:
            self._session.add(
                CompanyChangeEventModel(
                    id=e.id,
                    idno=e.idno,
                    category=e.category.value if hasattr(e.category, "value") else e.category,
                    field=e.field,
                    description=e.description,
                    old_value=e.old_value,
                    new_value=e.new_value,
                    batch_id=e.batch_id,
                    detected_at=e.detected_at,
                )
            )
        await self._session.flush()

    async def list_change_events(
        self, idno: str, limit: int = 100, offset: int = 0
    ) -> list[CompanyChangeEvent]:
        result = await self._session.execute(
            select(CompanyChangeEventModel)
            .where(CompanyChangeEventModel.idno == idno)
            .order_by(CompanyChangeEventModel.detected_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return [_event_to_entity(m) for m in result.scalars().all()]

    # ------------------------------------------------------------- notifications
    async def add_notifications(self, notifications: list[MonitoringNotification]) -> None:
        for n in notifications:
            self._session.add(
                MonitoringNotificationModel(
                    id=n.id,
                    user_id=n.user_id,
                    idno=n.idno,
                    company_name=n.company_name,
                    change_count=n.change_count,
                    summary=n.summary,
                    metadata_=n.to_metadata(),
                    is_read=n.is_read,
                    email_sent=n.email_sent,
                    created_at=n.created_at,
                )
            )
        await self._session.flush()

    async def list_notifications(
        self, user_id: UUID, unread_only: bool = False, limit: int = 50, offset: int = 0
    ) -> list[MonitoringNotification]:
        stmt = select(MonitoringNotificationModel).where(
            MonitoringNotificationModel.user_id == user_id
        )
        if unread_only:
            stmt = stmt.where(MonitoringNotificationModel.is_read.is_(False))
        stmt = (
            stmt.order_by(MonitoringNotificationModel.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return [_notification_to_entity(m) for m in result.scalars().all()]

    async def count_unread(self, user_id: UUID) -> int:
        result = await self._session.execute(
            select(func.count())
            .select_from(MonitoringNotificationModel)
            .where(
                MonitoringNotificationModel.user_id == user_id,
                MonitoringNotificationModel.is_read.is_(False),
            )
        )
        return result.scalar_one()

    async def mark_notification_read(self, user_id: UUID, notification_id: UUID) -> bool:
        result = await self._session.execute(
            update(MonitoringNotificationModel)
            .where(
                MonitoringNotificationModel.id == notification_id,
                MonitoringNotificationModel.user_id == user_id,
            )
            .values(is_read=True, read_at=func.now())
        )
        await self._session.flush()
        return (result.rowcount or 0) > 0

    async def mark_all_read(self, user_id: UUID) -> int:
        result = await self._session.execute(
            update(MonitoringNotificationModel)
            .where(
                MonitoringNotificationModel.user_id == user_id,
                MonitoringNotificationModel.is_read.is_(False),
            )
            .values(is_read=True, read_at=func.now())
        )
        await self._session.flush()
        return result.rowcount or 0
