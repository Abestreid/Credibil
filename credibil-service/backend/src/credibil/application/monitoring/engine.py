from __future__ import annotations

import hashlib
import json
import logging
from typing import TYPE_CHECKING, Any

from credibil.domain.monitoring.entities import (
    ChangeCategory,
    CompanyChangeEvent,
    MonitoringNotification,
)

if TYPE_CHECKING:
    from credibil.ports.repositories.company import CompanyRepository
    from credibil.ports.repositories.court_case import CourtCaseRepository
    from credibil.ports.repositories.enforcement import EnforcementRepository
    from credibil.ports.repositories.monitoring import MonitoringRepository
    from credibil.ports.repositories.relationship import (
        PersonRepository,
        RelationshipRepository,
    )

logger = logging.getLogger(__name__)

# Human-readable labels + category per scalar company field we track.
_COMPANY_FIELDS: dict[str, tuple[ChangeCategory, str]] = {
    "status": (ChangeCategory.STATUS, "Статус"),
    "legal_form": (ChangeCategory.GENERAL, "Правовая форма"),
    "legal_address": (ChangeCategory.ADDRESS, "Юридический адрес"),
    "name_ro": (ChangeCategory.GENERAL, "Название (RO)"),
    "name_ru": (ChangeCategory.GENERAL, "Название (RU)"),
    "caem": (ChangeCategory.GENERAL, "Вид деятельности (CAEM)"),
    "tax_debt": (ChangeCategory.TAX_DEBT, "Налоговая задолженность"),
    "founder_count": (ChangeCategory.MANAGEMENT, "Число учредителей"),
    "director_count": (ChangeCategory.MANAGEMENT, "Число руководителей"),
}


class MonitoringEngine:
    """Builds canonical company snapshots, diffs them, and emits change events
    and per-user notifications. Snapshots exist only for monitored companies.
    """

    def __init__(
        self,
        monitoring_repo: MonitoringRepository,
        company_repo: CompanyRepository,
        relationship_repo: RelationshipRepository,
        person_repo: PersonRepository,
        court_repo: CourtCaseRepository,
        enforcement_repo: EnforcementRepository,
    ) -> None:
        self._repo = monitoring_repo
        self._company_repo = company_repo
        self._relationship_repo = relationship_repo
        self._person_repo = person_repo
        self._court_repo = court_repo
        self._enforcement_repo = enforcement_repo

    async def build_snapshot(self, idno: str) -> dict[str, Any] | None:
        """Canonical "company card + related data" state used for diffing."""
        company = await self._company_repo.find_by_idno(idno)
        if company is None:
            return None

        participants: list[dict[str, Any]] = []
        try:
            relationships = await self._relationship_repo.find_by_company_idno(idno)
            for rel in relationships:
                name = None
                try:
                    person = await self._person_repo.find_by_id(rel.person_id)
                    name = person.full_name if person else None
                except Exception:  # noqa: BLE001
                    name = None
                participants.append(
                    {
                        "role": getattr(rel.relationship_type, "value", str(rel.relationship_type)),
                        "person_id": str(rel.person_id),
                        "name": name,
                        "active": bool(getattr(rel, "is_active", True)),
                    }
                )
        except Exception as exc:  # noqa: BLE001
            logger.warning("snapshot: relationships failed for %s: %s", idno, exc)

        participants.sort(key=lambda p: (p["role"], p["person_id"]))

        court_total = await self._court_repo.count_by_idno(idno)
        court_active = await self._court_repo.count_active_by_idno(idno)
        enf_total = await self._enforcement_repo.count_by_idno(idno)
        enf_active = await self._enforcement_repo.count_by_idno(idno, state="active")

        return {
            "company": {
                "status": company.status.value
                if hasattr(company.status, "value")
                else company.status,
                "legal_form": company.legal_form.value
                if hasattr(company.legal_form, "value")
                else company.legal_form,
                "legal_address": company.legal_address,
                "name_ro": company.name_ro,
                "name_ru": company.name_ru,
                "caem": company.caem,
                "tax_debt": company.tax_debt,
                "founder_count": company.founder_count,
                "director_count": company.director_count,
            },
            "participants": participants,
            "court": {"total": court_total, "active": court_active},
            "enforcement": {"total": enf_total, "active": enf_active},
            "_name": company.name_ro or company.name_ru,
        }

    @staticmethod
    def hash_snapshot(snapshot: dict[str, Any]) -> str:
        payload = {k: v for k, v in snapshot.items() if not k.startswith("_")}
        return hashlib.sha256(
            json.dumps(payload, sort_keys=True, default=str).encode("utf-8")
        ).hexdigest()

    def diff(
        self, old: dict[str, Any], new: dict[str, Any], idno: str, batch_id: str
    ) -> list[CompanyChangeEvent]:
        events: list[CompanyChangeEvent] = []
        old_c = old.get("company", {})
        new_c = new.get("company", {})

        for field, (category, label) in _COMPANY_FIELDS.items():
            ov, nv = old_c.get(field), new_c.get(field)
            if ov != nv:
                events.append(
                    CompanyChangeEvent(
                        idno=idno,
                        category=category,
                        field=field,
                        description=f"{label}: {_fmt(ov)} → {_fmt(nv)}",
                        old_value=_fmt(ov),
                        new_value=_fmt(nv),
                        batch_id=batch_id,
                    )
                )

        # participants (founders / directors / etc.)
        old_p = {(p["role"], p["person_id"], p["active"]): p for p in old.get("participants", [])}
        new_p = {(p["role"], p["person_id"], p["active"]): p for p in new.get("participants", [])}
        for key, p in new_p.items():
            if key not in old_p:
                events.append(
                    CompanyChangeEvent(
                        idno=idno,
                        category=ChangeCategory.MANAGEMENT,
                        field="participant_added",
                        description=f"Добавлен участник ({_role_ru(p['role'])}): {p.get('name') or '—'}",
                        new_value=p.get("name"),
                        batch_id=batch_id,
                    )
                )
        for key, p in old_p.items():
            if key not in new_p:
                events.append(
                    CompanyChangeEvent(
                        idno=idno,
                        category=ChangeCategory.MANAGEMENT,
                        field="participant_removed",
                        description=f"Удалён участник ({_role_ru(p['role'])}): {p.get('name') or '—'}",
                        old_value=p.get("name"),
                        batch_id=batch_id,
                    )
                )

        # court / enforcement volume
        for key, category, label in (
            ("court", ChangeCategory.COURT, "судебных дел"),
            ("enforcement", ChangeCategory.ENFORCEMENT, "исполнительных производств"),
        ):
            ot = old.get(key, {}).get("total", 0)
            nt = new.get(key, {}).get("total", 0)
            if nt > ot:
                events.append(
                    CompanyChangeEvent(
                        idno=idno,
                        category=category,
                        field=f"{key}_total",
                        description=f"Новых {label}: {nt - ot} (всего {nt})",
                        old_value=str(ot),
                        new_value=str(nt),
                        batch_id=batch_id,
                    )
                )

        return events

    async def check_company(self, idno: str, batch_id: str) -> int:
        """Snapshot + diff one company. Returns number of change events emitted."""
        new_snapshot = await self.build_snapshot(idno)
        if new_snapshot is None:
            logger.info("monitoring: company %s not found, skipping", idno)
            return 0

        new_hash = self.hash_snapshot(new_snapshot)
        stored = await self._repo.get_snapshot(idno)

        if stored is None:
            await self._repo.save_snapshot(idno, new_hash, new_snapshot)
            await self._repo.touch_checked(idno, changed=False)
            return 0

        if stored["hash"] == new_hash:
            await self._repo.touch_checked(idno, changed=False)
            return 0

        events = self.diff(stored["snapshot"], new_snapshot, idno, batch_id)
        await self._repo.save_snapshot(idno, new_hash, new_snapshot)

        if not events:
            await self._repo.touch_checked(idno, changed=False)
            return 0

        await self._repo.add_change_events(events)
        await self._fan_out(idno, new_snapshot.get("_name"), events)
        await self._repo.touch_checked(idno, changed=True)
        return len(events)

    async def _fan_out(
        self, idno: str, company_name: str | None, events: list[CompanyChangeEvent]
    ) -> None:
        watchers = await self._repo.watchers_of(idno)
        if not watchers:
            return
        categories = sorted({e.category.value for e in events})
        event_ids = [str(e.id) for e in events]
        summary = "; ".join(e.description for e in events[:4])
        if len(events) > 4:
            summary += f" и ещё {len(events) - 4}"
        notifications = [
            MonitoringNotification(
                user_id=w.user_id,
                idno=idno,
                company_name=company_name or w.company_name,
                change_count=len(events),
                change_event_ids=event_ids,
                categories=categories,
                summary=summary,
            )
            for w in watchers
        ]
        await self._repo.add_notifications(notifications)

    async def run_checks(self, batch_id: str) -> dict[str, int]:
        idnos = await self._repo.distinct_monitored_idnos()
        checked = changed = total_events = 0
        for idno in idnos:
            try:
                n = await self.check_company(idno, batch_id)
                checked += 1
                if n:
                    changed += 1
                    total_events += n
            except Exception as exc:  # noqa: BLE001
                logger.error("monitoring check failed for %s: %s", idno, exc)
        return {"checked": checked, "changed": changed, "events": total_events}


def _fmt(value: Any) -> str:
    if value is None:
        return "—"
    if isinstance(value, float):
        return f"{value:,.2f}".rstrip("0").rstrip(".")
    return str(value)


_ROLE_RU = {
    "founder": "учредитель",
    "shareholder": "акционер",
    "director": "руководитель",
    "administrator": "администратор",
    "owner": "владелец",
    "beneficiary": "бенефициар",
}


def _role_ru(role: str) -> str:
    return _ROLE_RU.get(role, role)
