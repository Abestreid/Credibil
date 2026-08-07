from __future__ import annotations

import logging
from datetime import datetime
from typing import TYPE_CHECKING, Any

from credibil.domain.financial import FinancialReport, ReportPeriod
from credibil.domain.sync.entities import SyncHistory, SyncType

if TYPE_CHECKING:
    from credibil.ports.repositories.financial_report import FinancialReportRepository
    from credibil.ports.repositories.sync_history import SyncHistoryRepository

logger = logging.getLogger(__name__)


class FinancialSyncOrchestrator:
    """Orchestrates financial data fetching from the Depozitar (primary) or Statistica (fallback).

    Permanent caching: once a report is stored, it is never re-fetched unless explicitly refreshed.
    """

    def __init__(
        self,
        financial_repo: FinancialReportRepository,
        sync_repo: SyncHistoryRepository,
        provider: Any = None,
        fallback_provider: Any = None,
    ) -> None:
        self._financial_repo = financial_repo
        self._sync_repo = sync_repo
        self._provider = provider
        self._fallback = fallback_provider

    async def fetch_and_store(self, idno: str, year: int) -> FinancialReport:
        """Fetch financial data for one company+year and store it.

        Permanent caching: if a report already exists for this IDNO+year, return it immediately.
        Never re-fetch historical data.
        """
        existing = await self._financial_repo.find_by_idno_and_year(idno, year)
        if existing:
            logger.info("Financial data for %s/%d already cached, returning existing", idno, year)
            return existing

        # Try primary provider (Depozitar)
        raw = None
        source = None
        if self._provider:
            raw = await self._provider.fetch_financial_data(idno, year)
            if raw:
                source = "depozitar"

        # Fallback to Statistica if Depozitar has no data
        if not raw and self._fallback:
            raw = await self._fallback.fetch_financial_data(idno, year)
            if raw:
                source = "statistica"

        if not raw:
            raise ValueError(f"No financial data available for {idno}/{year}")

        # Skip storing if no actual financial fields were populated
        financial_fields = ["revenue", "expenses", "total_assets", "total_liabilities", "equity", "profit"]
        if not any(raw.get(f) is not None for f in financial_fields):
            raise ValueError(f"No financial indicators for {idno}/{year} — all fields empty")

        report = FinancialReport(
            company_idno=idno,
            year=year,
            period=ReportPeriod.ANNUAL,
            company_name=raw.get("company_name"),
            caem_code=raw.get("caem_code"),
            caem_description=raw.get("caem_description"),
            business_category=raw.get("business_category"),
            revenue=raw.get("revenue"),
            expenses=raw.get("expenses"),
            total_assets=raw.get("total_assets"),
            total_liabilities=raw.get("total_liabilities"),
            equity=raw.get("equity"),
            profit=raw.get("profit"),
            employees_count=raw.get("employees_count"),
            source_url=raw.get("source_url"),
            raw_data=raw.get("raw_data", {}),
            metadata=raw.get("metadata", {}),
            fetched_at=datetime.utcnow(),
        )

        saved = await self._financial_repo.save(report)
        return saved

    async def fetch_multi_year(self, idno: str, years: list[int]) -> list[FinancialReport]:
        """Fetch financial data for multiple years."""
        reports = []
        for year in sorted(years):
            try:
                report = await self.fetch_and_store(idno, year)
                reports.append(report)
            except Exception as e:
                logger.warning("Failed to fetch %s/%d: %s", idno, year, e)
        return reports

    async def fetch_all_available(self, idno: str) -> list[FinancialReport]:
        """Fetch all available financial statements for a company from the Depozitar.

        Uses the Depozitar's listing endpoint to discover all available years,
        then fetches and stores each one. Permanent caching ensures we never
        re-fetch data that's already been stored.
        """
        if not self._provider:
            raise ValueError("No provider configured for fetch_all_available")

        entries = await self._provider.fetch_available_years(idno)
        if not entries:
            logger.info("No Depozitar data for %s", idno)
            return []

        years = [e.get("year") for e in entries if e.get("year")]
        return await self.fetch_multi_year(idno, years)
