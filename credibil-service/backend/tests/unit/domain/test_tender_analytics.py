from __future__ import annotations

from datetime import date, datetime

from credibil.application.analytics.tender_analytics import (
    compute_award_statistics,
    compute_method_breakdown,
    compute_tender_statistics,
    compute_timeline,
    compute_win_rate,
)
from credibil.domain.tender.entities import (
    AwardStatus,
    ProcurementCategory,
    ProcurementMethod,
    Tender,
    TenderAward,
    TenderStatus,
)


def _make_tender(**overrides) -> Tender:
    defaults = {
        "ocid": "ocds-test-1",
        "title": "Test",
        "status": TenderStatus.ACTIVE,
        "procurement_method": ProcurementMethod.OPEN,
        "main_category": ProcurementCategory.GOODS,
        "value_amount": 100000.0,
        "value_currency": "MDL",
        "buyer_idno": "1000000000000",
        "published_date": datetime(2026, 1, 15),
    }
    defaults.update(overrides)
    return Tender(**defaults)


def _make_award(**overrides) -> TenderAward:
    defaults = {
        "tender_ocid": "ocds-test-1",
        "status": AwardStatus.ACTIVE,
        "value_amount": 95000.0,
        "value_currency": "MDL",
        "supplier_idno": "1000000000001",
        "supplier_name": "Supplier A",
        "award_date": date(2026, 2, 1),
    }
    defaults.update(overrides)
    return TenderAward(**defaults)


class TestTenderStatistics:
    def test_empty(self):
        stats = compute_tender_statistics([])
        assert stats["total_tenders"] == 0
        assert stats["total_value"] == 0

    def test_single_tender(self):
        stats = compute_tender_statistics([_make_tender()])
        assert stats["total_tenders"] == 1
        assert stats["active_tenders"] == 1
        assert stats["total_value"] == 100000.0
        assert stats["average_value"] == 100000.0

    def test_multiple_tenders(self):
        tenders = [
            _make_tender(ocid="t1", value_amount=100000.0, status=TenderStatus.ACTIVE),
            _make_tender(ocid="t2", value_amount=200000.0, status=TenderStatus.COMPLETE),
            _make_tender(ocid="t3", value_amount=300000.0, status=TenderStatus.ACTIVE),
        ]
        stats = compute_tender_statistics(tenders)
        assert stats["total_tenders"] == 3
        assert stats["active_tenders"] == 2
        assert stats["completed_tenders"] == 1
        assert stats["total_value"] == 600000.0
        assert stats["average_value"] == 200000.0

    def test_by_method(self):
        tenders = [
            _make_tender(ocid="t1", procurement_method=ProcurementMethod.OPEN),
            _make_tender(ocid="t2", procurement_method=ProcurementMethod.OPEN),
            _make_tender(ocid="t3", procurement_method=ProcurementMethod.LIMITED),
        ]
        stats = compute_tender_statistics(tenders)
        assert stats["tenders_by_method"]["open"] == 2
        assert stats["tenders_by_method"]["limited"] == 1

    def test_eu_funded(self):
        tenders = [
            _make_tender(ocid="t1", is_eu_funded=True),
            _make_tender(ocid="t2", is_eu_funded=False),
        ]
        stats = compute_tender_statistics(tenders)
        assert stats["eu_funded_count"] == 1


class TestAwardStatistics:
    def test_empty(self):
        stats = compute_award_statistics([])
        assert stats["total_awards"] == 0

    def test_single_award(self):
        stats = compute_award_statistics([_make_award()])
        assert stats["total_awards"] == 1
        assert stats["successful_awards"] == 1
        assert stats["total_award_value"] == 95000.0

    def test_pending_not_counted_as_successful(self):
        award = _make_award(status=AwardStatus.PENDING)
        stats = compute_award_statistics([award])
        assert stats["successful_awards"] == 0
        assert stats["pending_awards"] == 1


class TestWinRate:
    def test_no_participation(self):
        result = compute_win_rate([], [], "1000000000001")
        assert result["win_rate_percent"] == 0
        assert result["tenders_participated"] == 0

    def test_with_awards(self):
        tenders = [_make_tender(ocid="t1")]
        awards = [_make_award(tender_ocid="t1", supplier_idno="1000000000001")]
        result = compute_win_rate(tenders, awards, "1000000000001")
        assert result["tenders_participated"] == 1
        assert result["awards_won"] == 1
        assert result["win_rate_percent"] == 100.0


class TestMethodBreakdown:
    def test_empty(self):
        assert compute_method_breakdown([]) == []

    def test_breakdown(self):
        tenders = [
            _make_tender(ocid="t1", procurement_method=ProcurementMethod.OPEN, value_amount=100000),
            _make_tender(
                ocid="t2", procurement_method=ProcurementMethod.LIMITED, value_amount=50000
            ),
            _make_tender(ocid="t3", procurement_method=ProcurementMethod.OPEN, value_amount=200000),
        ]
        result = compute_method_breakdown(tenders)
        assert len(result) == 2
        open_entry = next(e for e in result if e["method"] == "open")
        assert open_entry["count"] == 2
        assert open_entry["total_value"] == 300000


class TestTimeline:
    def test_empty(self):
        assert compute_timeline([]) == []

    def test_timeline(self):
        tenders = [
            _make_tender(ocid="t1", published_date=datetime(2026, 1, 15)),
            _make_tender(ocid="t2", published_date=datetime(2026, 1, 20)),
            _make_tender(ocid="t3", published_date=datetime(2026, 2, 5)),
        ]
        result = compute_timeline(tenders)
        assert len(result) == 2
        assert result[0]["month"] == "2026-01"
        assert result[0]["count"] == 2
        assert result[1]["month"] == "2026-02"
        assert result[1]["count"] == 1
