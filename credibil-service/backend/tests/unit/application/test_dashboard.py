from __future__ import annotations

import pytest
from tests.factories import InMemoryCompanyRepository
from tests.in_memory_repos import (
    InMemoryCourtCaseRepository,
    InMemoryCourtHearingRepository,
    InMemoryFinancialReportRepository,
    InMemoryRelationshipRepository,
    InMemoryTenderAwardRepository,
    InMemoryTenderBidRepository,
    InMemoryTenderRepository,
)
from tests.in_memory_sanctions import InMemorySanctionsRepository

from credibil.application.analytics.dashboard import (
    CompanySummary,
    DashboardService,
    RelationshipEdge,
    RelationshipGraph,
    RelationshipNode,
    RiskIndicator,
    SanctionsIndicator,
    TimelineEntry,
)
from credibil.domain.sanctions.entities import SanctionsEntry
from credibil.domain.sanctions.enums import RiskLevel, SanctionStatus, SanctionType


@pytest.fixture
def repos():
    return {
        "company": InMemoryCompanyRepository(),
        "financial": InMemoryFinancialReportRepository(),
        "court_case": InMemoryCourtCaseRepository(),
        "court_hearing": InMemoryCourtHearingRepository(),
        "tender": InMemoryTenderRepository(),
        "tender_award": InMemoryTenderAwardRepository(),
        "tender_bid": InMemoryTenderBidRepository(),
        "relationship": InMemoryRelationshipRepository(),
        "person": InMemoryRelationshipRepository(),
        "sanctions": InMemorySanctionsRepository(),
    }


@pytest.fixture
def service(repos):
    return DashboardService(
        company_repo=repos["company"],
        financial_repo=repos["financial"],
        court_case_repo=repos["court_case"],
        court_hearing_repo=repos["court_hearing"],
        tender_repo=repos["tender"],
        tender_award_repo=repos["tender_award"],
        tender_bid_repo=repos["tender_bid"],
        relationship_repo=repos["relationship"],
        person_repo=repos["person"],
        sanctions_repo=repos["sanctions"],
    )


class TestCompanySummary:
    def test_create_summary(self):
        summary = CompanySummary(
            idno="1234567890123",
            name_ro="Test SRL",
            status="active",
            legal_form="SRL",
        )
        assert summary.idno == "1234567890123"
        assert summary.name_ro == "Test SRL"
        assert summary.founder_count == 0


class TestRelationshipGraph:
    def test_empty_graph(self):
        graph = RelationshipGraph()
        assert graph.total_nodes == 0
        assert graph.total_edges == 0

    def test_graph_with_data(self):
        graph = RelationshipGraph(
            nodes=[
                RelationshipNode(id="c1", label="Company", node_type="company"),
                RelationshipNode(id="p1", label="Person", node_type="person"),
            ],
            edges=[
                RelationshipEdge(source="p1", target="c1", relationship_type="director"),
            ],
            total_nodes=2,
            total_edges=1,
        )
        assert graph.total_nodes == 2
        assert graph.edges[0].relationship_type == "director"


class TestTimelineEntry:
    def test_create_entry(self):
        entry = TimelineEntry(
            date="2024-01-15",
            event_type="court_case",
            title="Case 123",
            description="Civil case",
            source="instente.justice.md",
        )
        assert entry.date == "2024-01-15"
        assert entry.event_type == "court_case"


class TestRiskIndicator:
    def test_create_indicator(self):
        indicator = RiskIndicator(
            category="litigation",
            level=RiskLevel.HIGH,
            score=0.8,
            factors=["5 active cases"],
        )
        assert indicator.category == "litigation"
        assert indicator.level == RiskLevel.HIGH
        assert indicator.score == 0.8


class TestSanctionsIndicator:
    def test_default_not_sanctioned(self):
        indicator = SanctionsIndicator()
        assert indicator.is_sanctioned is False
        assert indicator.sanctions_count == 0

    def test_sanctioned(self):
        indicator = SanctionsIndicator(
            is_sanctioned=True,
            sanctions_count=2,
            active_sanctions=2,
            sanction_types=["eu", "us_ofac"],
            lists=["SDN List", "EU Consolidated"],
        )
        assert indicator.is_sanctioned is True
        assert len(indicator.lists) == 2


class TestDashboardService:
    @pytest.mark.asyncio
    async def test_empty_dashboard(self, service):
        dashboard = await service.get_company_dashboard("0000000000000")
        assert dashboard.summary is None
        assert dashboard.financial is None
        assert dashboard.court_statistics == {}
        assert dashboard.tender_statistics == {}
        # Graph always has the company as the central node
        assert dashboard.relationship_graph.total_nodes == 1
        assert dashboard.relationship_graph.total_edges == 0
        assert dashboard.timeline == []
        assert dashboard.risk_indicators == []

    @pytest.mark.asyncio
    async def test_dashboard_with_company(self, service, repos):
        from credibil.domain.company.entities import Company, CompanyStatus, LegalForm

        company = Company(
            idno="1234567890123",
            name_ro="Test SRL",
            name_ru="Тест СРЛ",
            status=CompanyStatus.ACTIVE,
            legal_form=LegalForm.SRL,
        )
        await repos["company"].save(company)

        dashboard = await service.get_company_dashboard("1234567890123")
        assert dashboard.summary is not None
        assert dashboard.summary.idno == "1234567890123"
        assert dashboard.summary.name_ro == "Test SRL"
        assert dashboard.summary.status == "active"

    @pytest.mark.asyncio
    async def test_dashboard_with_financial(self, service, repos):
        from credibil.domain.company.entities import Company
        from credibil.domain.financial import FinancialReport

        company = Company(idno="1234567890123", name_ro="Test", name_ru="Тест")
        await repos["company"].save(company)

        for year in [2021, 2022, 2023]:
            report = FinancialReport(
                company_idno="1234567890123",
                year=year,
                revenue=float(year * 1000),
                profit=float(year * 100),
            )
            await repos["financial"].save(report)

        dashboard = await service.get_company_dashboard("1234567890123")
        assert dashboard.financial is not None
        assert len(dashboard.financial.years_analyzed) == 3
        assert len(dashboard.financial.revenue_chart) == 3

    @pytest.mark.asyncio
    async def test_dashboard_with_sanctions(self, service, repos):
        entry = SanctionsEntry(
            target_name="Sanctioned Corp",
            target_idno="1234567890123",
            sanction_type=SanctionType.EU,
            status=SanctionStatus.ACTIVE,
            list_name="EU Consolidated",
        )
        await repos["sanctions"].save(entry)

        dashboard = await service.get_company_dashboard("1234567890123")
        assert dashboard.sanctions.is_sanctioned is True
        assert dashboard.sanctions.sanctions_count == 1
        assert "eu" in dashboard.sanctions.sanction_types
        assert "EU Consolidated" in dashboard.sanctions.lists

    @pytest.mark.asyncio
    async def test_risk_indicators_with_sanctions(self, service, repos):
        entry = SanctionsEntry(
            target_name="Sanctioned",
            target_idno="1234567890123",
            sanction_type=SanctionType.US_OFAC,
            status=SanctionStatus.ACTIVE,
        )
        await repos["sanctions"].save(entry)

        dashboard = await service.get_company_dashboard("1234567890123")
        sanctions_risk = [r for r in dashboard.risk_indicators if r.category == "sanctions"]
        assert len(sanctions_risk) == 1
        assert sanctions_risk[0].level == RiskLevel.CRITICAL

    @pytest.mark.asyncio
    async def test_no_sanctions_repo(self, repos):
        service = DashboardService(
            company_repo=repos["company"],
            financial_repo=repos["financial"],
            court_case_repo=repos["court_case"],
            court_hearing_repo=repos["court_hearing"],
            tender_repo=repos["tender"],
            tender_award_repo=repos["tender_award"],
            tender_bid_repo=repos["tender_bid"],
            relationship_repo=repos["relationship"],
            person_repo=repos["person"],
            sanctions_repo=None,
        )
        dashboard = await service.get_company_dashboard("1234567890123")
        assert dashboard.sanctions.is_sanctioned is False
