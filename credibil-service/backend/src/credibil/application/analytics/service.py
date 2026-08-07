from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class GrowthMetrics:
    """Year-over-year growth metrics."""

    current_year: int
    previous_year: int | None = None
    revenue_growth_pct: float | None = None
    profit_growth_pct: float | None = None
    assets_growth_pct: float | None = None
    employees_growth_pct: float | None = None


@dataclass
class MarginMetrics:
    """Profitability margins."""

    year: int
    gross_margin_pct: float | None = None
    net_margin_pct: float | None = None
    operating_margin_pct: float | None = None
    expense_ratio_pct: float | None = None


@dataclass
class LiquidityMetrics:
    """Liquidity and solvency ratios."""

    year: int
    current_ratio: float | None = None
    debt_to_equity_ratio: float | None = None
    autonomy_ratio: float | None = None
    debt_ratio: float | None = None
    equity_ratio: float | None = None


@dataclass
class EmployeeDynamics:
    """Employee count trends."""

    year: int
    employees_count: int | None = None
    yoy_change: int | None = None
    yoy_change_pct: float | None = None


@dataclass
class CompanyAnalytics:
    """Complete analytics for a company across all years."""

    company_idno: str
    company_name: str | None = None
    years_analyzed: list[int] = field(default_factory=list)
    growth: list[GrowthMetrics] = field(default_factory=list)
    margins: list[MarginMetrics] = field(default_factory=list)
    liquidity: list[LiquidityMetrics] = field(default_factory=list)
    employee_dynamics: list[EmployeeDynamics] = field(default_factory=list)
    revenue_chart: list[dict[str, Any]] = field(default_factory=list)
    profit_chart: list[dict[str, Any]] = field(default_factory=list)
    assets_chart: list[dict[str, Any]] = field(default_factory=list)
    employees_chart: list[dict[str, Any]] = field(default_factory=list)


def _safe_div(a: float | None, b: float | None) -> float | None:
    if a is None or b is None or b == 0:
        return None
    return round((a / b) * 100, 2)


def _safe_pct_change(current: float | None, previous: float | None) -> float | None:
    if current is None or previous is None or previous == 0:
        return None
    return round(((current - previous) / abs(previous)) * 100, 2)


def compute_growth(current: dict[str, Any], previous: dict[str, Any] | None) -> GrowthMetrics:
    metrics = GrowthMetrics(
        current_year=current["year"],
        previous_year=previous["year"] if previous else None,
    )
    if previous:
        metrics.revenue_growth_pct = _safe_pct_change(
            current.get("revenue"), previous.get("revenue")
        )
        metrics.profit_growth_pct = _safe_pct_change(current.get("profit"), previous.get("profit"))
        metrics.assets_growth_pct = _safe_pct_change(
            current.get("total_assets"), previous.get("total_assets")
        )
        metrics.employees_growth_pct = _safe_pct_change(
            current.get("employees_count"), previous.get("employees_count")
        )
    return metrics


def compute_margins(data: dict[str, Any]) -> MarginMetrics:
    revenue = data.get("revenue")
    expenses = data.get("expenses")
    profit = data.get("profit")

    gross_margin = None
    if revenue and revenue > 0 and expenses is not None:
        gross_margin = _safe_div(revenue - expenses, revenue)

    net_margin = _safe_div(profit, revenue)
    expense_ratio = _safe_div(expenses, revenue)

    return MarginMetrics(
        year=data["year"],
        gross_margin_pct=gross_margin,
        net_margin_pct=net_margin,
        operating_margin_pct=gross_margin,
        expense_ratio_pct=expense_ratio,
    )


def compute_liquidity(data: dict[str, Any]) -> LiquidityMetrics:
    assets = data.get("total_assets")
    liabilities = data.get("total_liabilities")
    equity = data.get("equity")

    current_ratio = None
    if assets and liabilities and liabilities > 0:
        current_ratio = round(assets / liabilities, 3)

    debt_to_equity = None
    if liabilities and equity and equity > 0:
        debt_to_equity = round(liabilities / equity, 3)

    autonomy_ratio = _safe_div(equity, assets)
    debt_ratio = _safe_div(liabilities, assets)
    equity_ratio = _safe_div(equity, assets)

    return LiquidityMetrics(
        year=data["year"],
        current_ratio=current_ratio,
        debt_to_equity_ratio=debt_to_equity,
        autonomy_ratio=autonomy_ratio,
        debt_ratio=debt_ratio,
        equity_ratio=equity_ratio,
    )


def compute_employee_dynamics(
    current: dict[str, Any], previous: dict[str, Any] | None
) -> EmployeeDynamics:
    count = current.get("employees_count")
    dynamics = EmployeeDynamics(
        year=current["year"],
        employees_count=count,
    )
    if previous and count is not None:
        prev_count = previous.get("employees_count")
        if prev_count is not None:
            dynamics.yoy_change = count - prev_count
            dynamics.yoy_change_pct = _safe_pct_change(count, prev_count)
    return dynamics


def compute_analytics(reports: list[dict[str, Any]]) -> CompanyAnalytics:
    """Compute all analytics from a sorted list of annual report dicts."""
    if not reports:
        return CompanyAnalytics(company_idno="")

    sorted_reports = sorted(reports, key=lambda r: r["year"])
    analytics = CompanyAnalytics(
        company_idno=sorted_reports[0].get("company_idno", ""),
        company_name=sorted_reports[0].get("company_name"),
        years_analyzed=[r["year"] for r in sorted_reports],
    )

    for i, report in enumerate(sorted_reports):
        previous = sorted_reports[i - 1] if i > 0 else None

        analytics.growth.append(compute_growth(report, previous))
        analytics.margins.append(compute_margins(report))
        analytics.liquidity.append(compute_liquidity(report))
        analytics.employee_dynamics.append(compute_employee_dynamics(report, previous))

        if report.get("revenue") is not None:
            analytics.revenue_chart.append({"year": report["year"], "value": report["revenue"]})
        if report.get("profit") is not None:
            analytics.profit_chart.append({"year": report["year"], "value": report["profit"]})
        if report.get("total_assets") is not None:
            analytics.assets_chart.append({"year": report["year"], "value": report["total_assets"]})
        if report.get("employees_count") is not None:
            analytics.employees_chart.append(
                {"year": report["year"], "value": report["employees_count"]}
            )

    return analytics
