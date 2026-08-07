from __future__ import annotations

from credibil.application.monitoring.engine import MonitoringEngine
from credibil.domain.monitoring.entities import ChangeCategory


def _snapshot(**overrides):
    base = {
        "company": {
            "status": "active",
            "legal_form": "SRL",
            "legal_address": "str. Ismail 84",
            "name_ro": "TRANS CARGO LOGISTIC SRL",
            "name_ru": "ТРАНС КАРГО",
            "caem": "Transport",
            "tax_debt": None,
            "founder_count": 2,
            "director_count": 1,
        },
        "participants": [
            {"role": "founder", "person_id": "p1", "name": "Andrei Munteanu", "active": True},
            {"role": "director", "person_id": "p2", "name": "Elena Rusu", "active": True},
        ],
        "court": {"total": 1, "active": 0},
        "enforcement": {"total": 0, "active": 0},
        "_name": "TRANS CARGO LOGISTIC SRL",
    }
    base["company"].update(overrides.get("company", {}))
    for key in ("participants", "court", "enforcement"):
        if key in overrides:
            base[key] = overrides[key]
    return base


def _engine() -> MonitoringEngine:
    return MonitoringEngine.__new__(MonitoringEngine)


def test_hash_is_stable_and_ignores_private_keys() -> None:
    a = _snapshot()
    b = _snapshot()
    b["_name"] = "DIFFERENT DISPLAY NAME"  # private key must not affect the hash
    assert MonitoringEngine.hash_snapshot(a) == MonitoringEngine.hash_snapshot(b)

    c = _snapshot(company={"status": "liquidated"})
    assert MonitoringEngine.hash_snapshot(a) != MonitoringEngine.hash_snapshot(c)


def test_no_change_no_events() -> None:
    events = _engine().diff(_snapshot(), _snapshot(), "1013600012345", "batch1")
    assert events == []


def test_status_change_detected() -> None:
    old = _snapshot()
    new = _snapshot(company={"status": "liquidated"})
    events = _engine().diff(old, new, "1013600012345", "batch1")
    assert len(events) == 1
    e = events[0]
    assert e.category is ChangeCategory.STATUS
    assert e.old_value == "active"
    assert e.new_value == "liquidated"


def test_tax_debt_and_management_changes() -> None:
    old = _snapshot()
    new = _snapshot(
        company={"tax_debt": 15000.0, "founder_count": 3},
        participants=[
            {"role": "founder", "person_id": "p1", "name": "Andrei Munteanu", "active": True},
            {"role": "director", "person_id": "p2", "name": "Elena Rusu", "active": True},
            {"role": "founder", "person_id": "p3", "name": "Sergiu Lupu", "active": True},
        ],
    )
    events = _engine().diff(old, new, "1013600012345", "batch1")
    cats = {e.category for e in events}
    assert ChangeCategory.TAX_DEBT in cats
    assert ChangeCategory.MANAGEMENT in cats
    added = [e for e in events if e.field == "participant_added"]
    assert len(added) == 1
    assert "Sergiu Lupu" in added[0].description


def test_new_enforcement_and_court_volume() -> None:
    old = _snapshot()
    new = _snapshot(court={"total": 3, "active": 2}, enforcement={"total": 2, "active": 2})
    events = _engine().diff(old, new, "1013600012345", "batch1")
    fields = {e.field: e for e in events}
    assert "court_total" in fields
    assert "enforcement_total" in fields
    assert fields["enforcement_total"].new_value == "2"


def test_removed_participant_detected() -> None:
    old = _snapshot()
    new = _snapshot(
        participants=[
            {"role": "founder", "person_id": "p1", "name": "Andrei Munteanu", "active": True},
        ]
    )
    events = _engine().diff(old, new, "1013600012345", "batch1")
    removed = [e for e in events if e.field == "participant_removed"]
    assert len(removed) == 1
    assert "Elena Rusu" in removed[0].description
