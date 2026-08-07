from __future__ import annotations

from credibil.domain.sanctions.entities import RiskAssessment, SanctionsEntry
from credibil.domain.sanctions.enums import RiskLevel, SanctionStatus, SanctionType


class TestSanctionType:
    def test_all_types(self):
        assert SanctionType.INTERNATIONAL.value == "international"
        assert SanctionType.NATIONAL.value == "national"
        assert SanctionType.EU.value == "eu"
        assert SanctionType.US_OFAC.value == "us_ofac"
        assert SanctionType.UN.value == "un"


class TestSanctionStatus:
    def test_all_statuses(self):
        assert SanctionStatus.ACTIVE.value == "active"
        assert SanctionStatus.LIFTED.value == "lifted"
        assert SanctionStatus.PENDING.value == "pending"
        assert SanctionStatus.UNDER_REVIEW.value == "under_review"


class TestRiskLevel:
    def test_all_levels(self):
        assert RiskLevel.LOW.value == "low"
        assert RiskLevel.MEDIUM.value == "medium"
        assert RiskLevel.HIGH.value == "high"
        assert RiskLevel.CRITICAL.value == "critical"
        assert RiskLevel.UNKNOWN.value == "unknown"


class TestSanctionsEntry:
    def test_create_minimal(self):
        entry = SanctionsEntry(
            target_name="Test Entity",
            sanction_type=SanctionType.EU,
        )
        assert entry.target_name == "Test Entity"
        assert entry.sanction_type == SanctionType.EU
        assert entry.status == SanctionStatus.ACTIVE
        assert entry.id is not None

    def test_create_full(self):
        from datetime import date

        entry = SanctionsEntry(
            target_name="Bad Corp",
            target_idno="1234567890123",
            sanction_type=SanctionType.US_OFAC,
            status=SanctionStatus.ACTIVE,
            list_name="SDN List",
            list_url="https://example.com/sdn",
            country_code="MD",
            reason="Supporting sanctioned activities",
            program="UKRAINE-EO13662",
            listed_date=date(2024, 1, 15),
        )
        assert entry.target_idno == "1234567890123"
        assert entry.list_name == "SDN List"
        assert entry.country_code == "MD"
        assert entry.reason == "Supporting sanctioned activities"

    def test_update(self):
        entry = SanctionsEntry(
            target_name="Entity",
            sanction_type=SanctionType.NATIONAL,
        )
        entry.update(status=SanctionStatus.LIFTED, reason="Cleared")
        assert entry.status == SanctionStatus.LIFTED
        assert entry.reason == "Cleared"

    def test_repr(self):
        entry = SanctionsEntry(
            target_name="Test",
            sanction_type=SanctionType.UN,
        )
        assert "Test" in repr(entry)
        assert "un" in repr(entry)


class TestRiskAssessment:
    def test_create_minimal(self):
        assessment = RiskAssessment()
        assert assessment.overall_risk == RiskLevel.UNKNOWN
        assert assessment.sanctions_count == 0
        assert assessment.risk_factors == []

    def test_create_full(self):
        assessment = RiskAssessment(
            target_idno="1234567890123",
            target_name="Risky Corp",
            overall_risk=RiskLevel.HIGH,
            sanctions_risk=RiskLevel.CRITICAL,
            litigation_risk=RiskLevel.MEDIUM,
            financial_risk=RiskLevel.LOW,
            sanctions_count=3,
            active_cases_count=5,
            total_cases_count=12,
            risk_factors=["High debt-to-equity", "Active sanctions"],
        )
        assert assessment.overall_risk == RiskLevel.HIGH
        assert assessment.sanctions_count == 3
        assert len(assessment.risk_factors) == 2

    def test_repr(self):
        assessment = RiskAssessment(
            target_idno="111",
            overall_risk=RiskLevel.MEDIUM,
        )
        assert "111" in repr(assessment)
        assert "medium" in repr(assessment)
