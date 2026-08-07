from __future__ import annotations

import pytest

from credibil.domain.financial import FinancialReport, ReportPeriod


class TestFinancialReportEntity:
    def test_create_report(self) -> None:
        report = FinancialReport(
            company_idno="1234567890123",
            year=2023,
            revenue=1000.0,
            expenses=800.0,
            profit=200.0,
            total_assets=5000.0,
            total_liabilities=2000.0,
            equity=3000.0,
            employees_count=50,
        )
        assert report.company_idno == "1234567890123"
        assert report.year == 2023
        assert report.revenue == 1000.0
        assert report.profit == 200.0
        assert report.period == ReportPeriod.ANNUAL
        assert report.id is not None

    def test_update_report(self) -> None:
        report = FinancialReport(
            company_idno="1234567890123",
            year=2023,
            revenue=1000.0,
        )
        report.update(revenue=1200.0, profit=300.0, employees_count=55)
        assert report.revenue == 1200.0
        assert report.profit == 300.0
        assert report.employees_count == 55
        assert report.updated_at >= report.created_at

    def test_repr(self) -> None:
        report = FinancialReport(
            company_idno="1234567890123",
            year=2023,
            revenue=1000.0,
            profit=200.0,
        )
        r = repr(report)
        assert "1234567890123" in r
        assert "2023" in r


class TestFinancialReportRepository:
    @pytest.mark.asyncio
    async def test_save_and_find(self, financial_repo: "InMemoryFinancialReportRepository") -> None:
        report = FinancialReport(
            company_idno="1234567890123",
            year=2023,
            revenue=1000.0,
        )
        await financial_repo.save(report)
        found = await financial_repo.find_by_id(report.id)
        assert found is not None
        assert found.revenue == 1000.0

    @pytest.mark.asyncio
    async def test_find_by_idno_and_year(
        self, financial_repo: "InMemoryFinancialReportRepository"
    ) -> None:
        await financial_repo.save(
            FinancialReport(company_idno="1234567890123", year=2023, revenue=1000.0)
        )
        await financial_repo.save(
            FinancialReport(company_idno="1234567890123", year=2022, revenue=900.0)
        )
        found = await financial_repo.find_by_idno_and_year("1234567890123", 2022)
        assert found is not None
        assert found.revenue == 900.0

    @pytest.mark.asyncio
    async def test_find_by_idno_returns_descending(
        self, financial_repo: "InMemoryFinancialReportRepository"
    ) -> None:
        for year in [2020, 2021, 2022, 2023]:
            await financial_repo.save(
                FinancialReport(company_idno="1234567890123", year=year, revenue=float(year))
            )
        reports = await financial_repo.find_by_idno("1234567890123")
        assert [r.year for r in reports] == [2023, 2022, 2021, 2020]

    @pytest.mark.asyncio
    async def test_find_years(self, financial_repo: "InMemoryFinancialReportRepository") -> None:
        for year in [2020, 2022, 2023]:
            await financial_repo.save(FinancialReport(company_idno="1234567890123", year=year))
        years = await financial_repo.find_years_for_idno("1234567890123")
        assert years == [2023, 2022, 2020]

    @pytest.mark.asyncio
    async def test_find_latest(self, financial_repo: "InMemoryFinancialReportRepository") -> None:
        await financial_repo.save(
            FinancialReport(company_idno="1234567890123", year=2022, revenue=900.0)
        )
        await financial_repo.save(
            FinancialReport(company_idno="1234567890123", year=2023, revenue=1100.0)
        )
        latest = await financial_repo.find_latest_by_idno("1234567890123")
        assert latest is not None
        assert latest.year == 2023
        assert latest.revenue == 1100.0

    @pytest.mark.asyncio
    async def test_count(self, financial_repo: "InMemoryFinancialReportRepository") -> None:
        for year in range(2020, 2024):
            await financial_repo.save(FinancialReport(company_idno="1234567890123", year=year))
        count = await financial_repo.count_by_idno("1234567890123")
        assert count == 4

    @pytest.mark.asyncio
    async def test_delete(self, financial_repo: "InMemoryFinancialReportRepository") -> None:
        report = FinancialReport(company_idno="1234567890123", year=2023)
        await financial_repo.save(report)
        await financial_repo.delete(report.id)
        assert await financial_repo.find_by_id(report.id) is None
