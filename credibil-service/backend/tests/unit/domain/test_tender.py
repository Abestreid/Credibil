from __future__ import annotations

from datetime import date, datetime

from credibil.domain.tender.entities import (
    AwardStatus,
    BidStatus,
    ProcurementCategory,
    ProcurementMethod,
    Tender,
    TenderAward,
    TenderBid,
    TenderStatus,
)


class TestTender:
    def test_create_minimal(self):
        tender = Tender(ocid="ocds-b3wdp1-MD-123", title="Test Tender")
        assert tender.ocid == "ocds-b3wdp1-MD-123"
        assert tender.title == "Test Tender"
        assert tender.status == TenderStatus.PLANNING
        assert tender.id is not None
        assert tender.created_at is not None

    def test_create_full(self):
        tender = Tender(
            ocid="ocds-b3wdp1-MD-456",
            title="Medical Equipment",
            description="Supply of medical equipment",
            status=TenderStatus.ACTIVE,
            status_details="evaluation",
            procurement_method=ProcurementMethod.OPEN,
            procurement_method_details="openTender",
            main_category=ProcurementCategory.GOODS,
            cpv_code="33100000-1",
            cpv_description="Medical equipment",
            buyer_idno="1003600150196",
            buyer_name="IMSP CRDM",
            value_amount=410000.0,
            value_currency="MDL",
            budget_amount=500000.0,
            budget_currency="MDL",
            is_eu_funded=False,
            tender_start_date=date(2026, 6, 1),
            tender_end_date=date(2026, 6, 12),
            contract_start_date=date(2026, 7, 1),
            contract_end_date=date(2026, 12, 31),
            published_date=datetime(2026, 5, 22, 13, 6, 55),
        )
        assert tender.procurement_method == ProcurementMethod.OPEN
        assert tender.main_category == ProcurementCategory.GOODS
        assert tender.value_amount == 410000.0
        assert tender.is_eu_funded is False

    def test_update(self):
        tender = Tender(ocid="ocds-123", title="Old Title")
        tender.update(title="New Title", value_amount=1000.0)
        assert tender.title == "New Title"
        assert tender.value_amount == 1000.0
        assert tender.updated_at >= tender.created_at

    def test_is_active(self):
        assert Tender(ocid="x", title="t", status=TenderStatus.ACTIVE).is_active
        assert Tender(ocid="x", title="t", status=TenderStatus.PLANNING).is_active
        assert Tender(ocid="x", title="t", status=TenderStatus.COMPLETE).is_active is False
        assert Tender(ocid="x", title="t", status=TenderStatus.CANCELLED).is_active is False

    def test_repr(self):
        t = Tender(ocid="ocds-123", title="Test", status=TenderStatus.ACTIVE)
        assert "ocds-123" in repr(t)
        assert "active" in repr(t).lower()


class TestTenderAward:
    def test_create(self):
        award = TenderAward(
            tender_ocid="ocds-123",
            status=AwardStatus.ACTIVE,
            value_amount=246385.0,
            value_currency="MDL",
            supplier_idno="1003600117582",
            supplier_name="GBG-MLD SRL",
        )
        assert award.tender_ocid == "ocds-123"
        assert award.supplier_name == "GBG-MLD SRL"
        assert award.is_successful is True

    def test_pending_not_successful(self):
        award = TenderAward(tender_ocid="x", status=AwardStatus.PENDING)
        assert award.is_successful is False

    def test_successful_statuses(self):
        for status in [AwardStatus.ACTIVE, AwardStatus.COMPLETE]:
            award = TenderAward(tender_ocid="x", status=status)
            assert award.is_successful is True

        for status in [AwardStatus.PENDING, AwardStatus.CANCELLED, AwardStatus.UNSUCCESSFUL]:
            award = TenderAward(tender_ocid="x", status=status)
            assert award.is_successful is False


class TestTenderBid:
    def test_create(self):
        bid = TenderBid(
            tender_ocid="ocds-123",
            status=BidStatus.PENDING,
            value_amount=246385.0,
            value_currency="MDL",
            tenderer_idno="1003600117582",
            tenderer_name="GBG-MLD SRL",
        )
        assert bid.tender_ocid == "ocds-123"
        assert bid.tenderer_name == "GBG-MLD SRL"
        assert bid.value_amount == 246385.0
