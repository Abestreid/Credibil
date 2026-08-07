from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from credibil.application.analytics.court_analytics import (
    compute_case_statistics,
    compute_court_distribution,
    compute_judge_frequency,
)
from credibil.application.analytics.court_analytics import (
    compute_timeline as compute_court_timeline,
)
from credibil.application.analytics.service import (
    CompanyAnalytics,
    compute_analytics,
)
from credibil.application.analytics.tender_analytics import (
    compute_award_statistics,
    compute_method_breakdown,
    compute_tender_statistics,
    compute_win_rate,
)
from credibil.application.analytics.tender_analytics import (
    compute_timeline as compute_tender_timeline,
)
from credibil.domain.sanctions.enums import RiskLevel, SanctionStatus


@dataclass
class CompanySummary:
    """High-level company summary for the dashboard."""

    idno: str
    name_ro: str | None = None
    name_ru: str | None = None
    status: str | None = None
    legal_form: str | None = None
    caem: str | None = None
    caem_description: str | None = None
    legal_address: str | None = None
    registration_date: str | None = None
    founder_count: int = 0
    director_count: int = 0
    tax_debt: float | None = None


@dataclass
class RelationshipNode:
    """A node in the relationship graph."""

    id: str
    label: str
    node_type: str  # "company" or "person"
    idno: str | None = None
    idnp: str | None = None


@dataclass
class RelationshipEdge:
    """An edge in the relationship graph."""

    source: str
    target: str
    relationship_type: str
    is_active: bool = True
    start_date: str | None = None


@dataclass
class RelationshipGraph:
    """Graph representation of company-person relationships."""

    nodes: list[RelationshipNode] = field(default_factory=list)
    edges: list[RelationshipEdge] = field(default_factory=list)
    total_nodes: int = 0
    total_edges: int = 0


@dataclass
class TimelineEntry:
    """A single timeline event."""

    date: str
    event_type: str
    title: str
    description: str | None = None
    source: str | None = None


@dataclass
class RiskIndicator:
    """Risk indicator for the dashboard."""

    category: str
    level: RiskLevel
    score: float | None = None
    factors: list[str] = field(default_factory=list)
    details: str | None = None


@dataclass
class SanctionsIndicator:
    """Sanctions indicator for the dashboard."""

    is_sanctioned: bool = False
    sanctions_count: int = 0
    active_sanctions: int = 0
    sanction_types: list[str] = field(default_factory=list)
    lists: list[str] = field(default_factory=list)
    latest_entry_date: str | None = None


@dataclass
class CompanyDashboard:
    """Complete analytics dashboard for a company."""

    summary: CompanySummary | None = None
    financial: CompanyAnalytics | None = None
    court_statistics: dict[str, Any] = field(default_factory=dict)
    court_judges: list[dict[str, Any]] = field(default_factory=list)
    court_distribution: list[dict[str, Any]] = field(default_factory=list)
    court_timeline: list[dict[str, Any]] = field(default_factory=list)
    tender_statistics: dict[str, Any] = field(default_factory=dict)
    tender_awards: dict[str, Any] = field(default_factory=dict)
    tender_win_rate: dict[str, Any] = field(default_factory=dict)
    tender_methods: list[dict[str, Any]] = field(default_factory=list)
    tender_timeline: list[dict[str, Any]] = field(default_factory=list)
    relationship_graph: RelationshipGraph = field(default_factory=RelationshipGraph)
    timeline: list[TimelineEntry] = field(default_factory=list)
    risk_indicators: list[RiskIndicator] = field(default_factory=list)
    sanctions: SanctionsIndicator = field(default_factory=SanctionsIndicator)


class DashboardService:
    """Aggregates data from all domain services into a unified dashboard."""

    def __init__(
        self,
        company_repo: Any,
        financial_repo: Any,
        court_case_repo: Any,
        court_hearing_repo: Any,
        tender_repo: Any,
        tender_award_repo: Any,
        tender_bid_repo: Any,
        relationship_repo: Any,
        person_repo: Any,
        sanctions_repo: Any | None = None,
    ) -> None:
        self._company_repo = company_repo
        self._financial_repo = financial_repo
        self._court_case_repo = court_case_repo
        self._court_hearing_repo = court_hearing_repo
        self._tender_repo = tender_repo
        self._tender_award_repo = tender_award_repo
        self._tender_bid_repo = tender_bid_repo
        self._relationship_repo = relationship_repo
        self._person_repo = person_repo
        self._sanctions_repo = sanctions_repo

    async def get_company_dashboard(self, idno: str) -> CompanyDashboard:
        """Build the complete dashboard for a company."""
        dashboard = CompanyDashboard()

        # 1. Company summary
        company = await self._company_repo.find_by_idno(idno)
        if company:
            dashboard.summary = CompanySummary(
                idno=company.idno,
                name_ro=company.name_ro,
                name_ru=company.name_ru,
                status=company.status.value if company.status else None,
                legal_form=company.legal_form.value if company.legal_form else None,
                caem=company.caem,
                caem_description=company.caem_description,
                legal_address=company.legal_address,
                registration_date=(
                    company.registration_date.isoformat() if company.registration_date else None
                ),
                founder_count=company.founder_count,
                director_count=company.director_count,
                tax_debt=company.tax_debt,
            )

        # 2. Financial analytics
        financial_reports = await self._financial_repo.find_by_idno(idno)
        if financial_reports:
            report_dicts = []
            for r in financial_reports:
                report_dicts.append(
                    {
                        "company_idno": r.company_idno,
                        "company_name": r.company_name,
                        "year": r.year,
                        "revenue": r.revenue,
                        "expenses": r.expenses,
                        "total_assets": r.total_assets,
                        "total_liabilities": r.total_liabilities,
                        "equity": r.equity,
                        "profit": r.profit,
                        "employees_count": r.employees_count,
                    }
                )
            dashboard.financial = compute_analytics(report_dicts)

        # 3. Court analytics
        court_cases = await self._court_case_repo.find_by_idno(idno)
        if court_cases:
            dashboard.court_statistics = compute_case_statistics(court_cases)
            dashboard.court_judges = compute_judge_frequency(court_cases)
            dashboard.court_distribution = compute_court_distribution(court_cases)
            dashboard.court_timeline = compute_court_timeline(court_cases)

        # 4. Tender analytics
        buyer_tenders = await self._tender_repo.find_by_buyer_idno(idno)
        all_awards = []
        for t in buyer_tenders:
            awards = await self._tender_award_repo.find_by_tender_ocid(t.ocid)
            all_awards.extend(awards)

        if buyer_tenders:
            dashboard.tender_statistics = compute_tender_statistics(buyer_tenders)
            dashboard.tender_awards = compute_award_statistics(all_awards)
            dashboard.tender_win_rate = compute_win_rate(buyer_tenders, all_awards, idno)
            dashboard.tender_methods = compute_method_breakdown(buyer_tenders)
            dashboard.tender_timeline = compute_tender_timeline(buyer_tenders)

        # 5. Relationship graph
        dashboard.relationship_graph = await self._build_relationship_graph(idno)

        # 6. Timeline (unified from all sources)
        dashboard.timeline = await self._build_timeline(idno, court_cases, buyer_tenders)

        # 7. Sanctions indicators (must come before risk indicators)
        if self._sanctions_repo:
            dashboard.sanctions = await self._compute_sanctions_indicator(idno)

        # 8. Risk indicators
        dashboard.risk_indicators = await self._compute_risk_indicators(
            idno, court_cases, dashboard.financial, dashboard.sanctions
        )

        return dashboard

    async def _build_relationship_graph(self, idno: str) -> RelationshipGraph:
        """Build a relationship graph for a company."""
        graph = RelationshipGraph()

        # Add the company as central node
        graph.nodes.append(
            RelationshipNode(
                id=f"company_{idno}",
                label=idno,
                node_type="company",
                idno=idno,
            )
        )

        # Get relationships for this company
        relationships = await self._relationship_repo.find_by_company_idno(idno)

        person_ids_seen: set[str] = set()
        for rel in relationships:
            person_id_str = str(rel.person_id)

            # Add person node if not yet seen
            if person_id_str not in person_ids_seen:
                person_ids_seen.add(person_id_str)
                person = await self._person_repo.find_by_id(rel.person_id)
                label = person.full_name if person else person_id_str
                graph.nodes.append(
                    RelationshipNode(
                        id=f"person_{person_id_str}",
                        label=label,
                        node_type="person",
                        idnp=person.idnp if person else None,
                    )
                )

            # Add edge
            graph.edges.append(
                RelationshipEdge(
                    source=f"person_{person_id_str}",
                    target=f"company_{idno}",
                    relationship_type=rel.relationship_type.value,
                    is_active=rel.is_active,
                    start_date=rel.start_date.isoformat() if rel.start_date else None,
                )
            )

        graph.total_nodes = len(graph.nodes)
        graph.total_edges = len(graph.edges)
        return graph

    async def _build_timeline(
        self,
        idno: str,
        court_cases: list[Any],
        tenders: list[Any],
    ) -> list[TimelineEntry]:
        """Build a unified timeline from all data sources."""
        entries: list[TimelineEntry] = []

        # Company registration
        company = await self._company_repo.find_by_idno(idno)
        if company and company.registration_date:
            entries.append(
                TimelineEntry(
                    date=company.registration_date.isoformat(),
                    event_type="company_registered",
                    title="Company registered",
                    description=f"{company.name_ro} registered as {company.legal_form.value if company.legal_form else 'N/A'}",
                    source="CKAN",
                )
            )

        # Court cases
        for case in court_cases:
            if case.registration_date:
                entries.append(
                    TimelineEntry(
                        date=case.registration_date.isoformat(),
                        event_type="court_case",
                        title=f"Court case: {case.case_number}",
                        description=f"{case.case_type.value} - {case.court_name}",
                        source="instente.justice.md",
                    )
                )

        # Tenders
        for tender in tenders:
            if tender.published_date:
                entries.append(
                    TimelineEntry(
                        date=tender.published_date.isoformat(),
                        event_type="tender",
                        title=f"Tender: {tender.title or tender.ocid}",
                        description=f"Status: {tender.status.value}",
                        source="MTender",
                    )
                )

        entries.sort(key=lambda e: e.date, reverse=True)
        return entries

    async def _compute_risk_indicators(
        self,
        idno: str,
        court_cases: list[Any],
        financial: CompanyAnalytics | None,
        sanctions: SanctionsIndicator,
    ) -> list[RiskIndicator]:
        """Compute risk indicators based on available data."""
        indicators: list[RiskIndicator] = []

        # Litigation risk
        if court_cases:
            active = sum(1 for c in court_cases if c.is_active)
            total = len(court_cases)
            if active > 5 or total > 20:
                level = RiskLevel.HIGH
            elif active > 2 or total > 10:
                level = RiskLevel.MEDIUM
            elif total > 0:
                level = RiskLevel.LOW
            else:
                level = RiskLevel.UNKNOWN

            indicators.append(
                RiskIndicator(
                    category="litigation",
                    level=level,
                    score=min(total / 20.0, 1.0),
                    factors=[
                        f"{active} active cases",
                        f"{total} total cases",
                    ],
                )
            )

        # Financial risk
        if financial and financial.liquidity:
            latest = financial.liquidity[-1] if financial.liquidity else None
            if latest:
                factors = []
                level = RiskLevel.LOW

                if latest.debt_to_equity_ratio and latest.debt_to_equity_ratio > 2.0:
                    level = RiskLevel.HIGH
                    factors.append(f"High debt-to-equity: {latest.debt_to_equity_ratio}")
                elif latest.debt_to_equity_ratio and latest.debt_to_equity_ratio > 1.0:
                    level = RiskLevel.MEDIUM
                    factors.append(f"Elevated debt-to-equity: {latest.debt_to_equity_ratio}")

                if latest.current_ratio and latest.current_ratio < 1.0:
                    level = RiskLevel.HIGH
                    factors.append(f"Low current ratio: {latest.current_ratio}")

                indicators.append(
                    RiskIndicator(
                        category="financial",
                        level=level,
                        factors=factors or ["Financials within normal range"],
                    )
                )

        # Sanctions risk
        if sanctions.is_sanctioned:
            indicators.append(
                RiskIndicator(
                    category="sanctions",
                    level=RiskLevel.CRITICAL,
                    score=1.0,
                    factors=[
                        f"{sanctions.active_sanctions} active sanctions",
                        f"Lists: {', '.join(sanctions.lists)}",
                    ],
                )
            )

        # Tax debt risk
        company = await self._company_repo.find_by_idno(idno)
        if company and company.tax_debt and company.tax_debt > 0:
            if company.tax_debt > 1_000_000:
                level = RiskLevel.HIGH
            elif company.tax_debt > 100_000:
                level = RiskLevel.MEDIUM
            else:
                level = RiskLevel.LOW
            indicators.append(
                RiskIndicator(
                    category="tax",
                    level=level,
                    factors=[f"Tax debt: {company.tax_debt:,.0f} MDL"],
                )
            )

        return indicators

    async def _compute_sanctions_indicator(self, idno: str) -> SanctionsIndicator:
        """Compute sanctions indicator from sanctions repository."""
        if not self._sanctions_repo:
            return SanctionsIndicator()

        entries = await self._sanctions_repo.find_active_by_target(idno=idno)
        if not entries:
            return SanctionsIndicator()

        types = list({e.sanction_type.value for e in entries})
        lists = list({e.list_name for e in entries if e.list_name})
        latest = max(
            (e.listed_date for e in entries if e.listed_date),
            default=None,
        )

        return SanctionsIndicator(
            is_sanctioned=True,
            sanctions_count=len(entries),
            active_sanctions=sum(1 for e in entries if e.status == SanctionStatus.ACTIVE),
            sanction_types=types,
            lists=lists,
            latest_entry_date=latest.isoformat() if latest else None,
        )
