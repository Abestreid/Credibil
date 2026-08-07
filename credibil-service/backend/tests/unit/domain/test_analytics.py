from __future__ import annotations

import pytest

from credibil.application.analytics.service import (
    compute_analytics,
    compute_employee_dynamics,
    compute_growth,
    compute_liquidity,
    compute_margins,
)


class TestGrowthMetrics:
    def test_with_previous_year(self) -> None:
        current = {
            "year": 2023,
            "revenue": 1200,
            "profit": 300,
            "total_assets": 6000,
            "employees_count": 55,
        }
        previous = {
            "year": 2022,
            "revenue": 1000,
            "profit": 200,
            "total_assets": 5000,
            "employees_count": 50,
        }
        growth = compute_growth(current, previous)
        assert growth.current_year == 2023
        assert growth.previous_year == 2022
        assert growth.revenue_growth_pct == 20.0
        assert growth.profit_growth_pct == 50.0
        assert growth.employees_growth_pct == 10.0

    def test_without_previous_year(self) -> None:
        current = {"year": 2023, "revenue": 1200}
        growth = compute_growth(current, None)
        assert growth.current_year == 2023
        assert growth.previous_year is None
        assert growth.revenue_growth_pct is None

    def test_zero_previous(self) -> None:
        current = {"year": 2023, "revenue": 1200}
        previous = {"year": 2022, "revenue": 0}
        growth = compute_growth(current, previous)
        assert growth.revenue_growth_pct is None


class TestMarginMetrics:
    def test_basic_margins(self) -> None:
        data = {"year": 2023, "revenue": 1000, "expenses": 800, "profit": 200}
        margins = compute_margins(data)
        assert margins.year == 2023
        assert margins.gross_margin_pct == 20.0
        assert margins.net_margin_pct == 20.0
        assert margins.expense_ratio_pct == 80.0

    def test_no_data(self) -> None:
        data = {"year": 2023}
        margins = compute_margins(data)
        assert margins.gross_margin_pct is None
        assert margins.net_margin_pct is None


class TestLiquidityMetrics:
    def test_basic_liquidity(self) -> None:
        data = {"year": 2023, "total_assets": 5000, "total_liabilities": 2000, "equity": 3000}
        liquidity = compute_liquidity(data)
        assert liquidity.year == 2023
        assert liquidity.current_ratio == 2.5
        assert liquidity.debt_to_equity_ratio == pytest.approx(0.667, abs=0.01)
        assert liquidity.autonomy_ratio == 60.0
        assert liquidity.debt_ratio == 40.0

    def test_no_data(self) -> None:
        data = {"year": 2023}
        liquidity = compute_liquidity(data)
        assert liquidity.current_ratio is None
        assert liquidity.debt_to_equity_ratio is None


class TestEmployeeDynamics:
    def test_with_previous(self) -> None:
        current = {"year": 2023, "employees_count": 55}
        previous = {"year": 2022, "employees_count": 50}
        dynamics = compute_employee_dynamics(current, previous)
        assert dynamics.employees_count == 55
        assert dynamics.yoy_change == 5
        assert dynamics.yoy_change_pct == 10.0

    def test_without_previous(self) -> None:
        current = {"year": 2023, "employees_count": 55}
        dynamics = compute_employee_dynamics(current, None)
        assert dynamics.employees_count == 55
        assert dynamics.yoy_change is None


class TestComputeAnalytics:
    def test_empty_reports(self) -> None:
        analytics = compute_analytics([])
        assert analytics.company_idno == ""
        assert analytics.years_analyzed == []

    def test_single_year(self) -> None:
        reports = [
            {
                "company_idno": "1234567890123",
                "company_name": "Test SRL",
                "year": 2023,
                "revenue": 1000,
                "profit": 200,
                "total_assets": 5000,
                "total_liabilities": 2000,
                "equity": 3000,
                "employees_count": 50,
            }
        ]
        analytics = compute_analytics(reports)
        assert analytics.company_idno == "1234567890123"
        assert analytics.years_analyzed == [2023]
        assert len(analytics.growth) == 1
        assert analytics.growth[0].previous_year is None
        assert len(analytics.revenue_chart) == 1
        assert analytics.revenue_chart[0]["value"] == 1000

    def test_multi_year(self) -> None:
        reports = [
            {
                "company_idno": "1234567890123",
                "company_name": "Test SRL",
                "year": 2022,
                "revenue": 1000,
                "expenses": 800,
                "profit": 200,
                "total_assets": 5000,
                "total_liabilities": 2000,
                "equity": 3000,
                "employees_count": 50,
            },
            {
                "company_idno": "1234567890123",
                "company_name": "Test SRL",
                "year": 2023,
                "revenue": 1200,
                "expenses": 900,
                "profit": 300,
                "total_assets": 6000,
                "total_liabilities": 2500,
                "equity": 3500,
                "employees_count": 55,
            },
        ]
        analytics = compute_analytics(reports)
        assert analytics.years_analyzed == [2022, 2023]
        assert len(analytics.growth) == 2
        assert analytics.growth[0].previous_year is None
        assert analytics.growth[1].revenue_growth_pct == 20.0
        assert analytics.growth[1].profit_growth_pct == 50.0
        assert len(analytics.margins) == 2
        assert analytics.margins[0].gross_margin_pct == 20.0
        assert len(analytics.liquidity) == 2
        assert len(analytics.employee_dynamics) == 2
        assert analytics.employee_dynamics[1].yoy_change == 5
        assert len(analytics.revenue_chart) == 2
