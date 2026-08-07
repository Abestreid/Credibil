from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from credibil.domain.tender.entities import Tender, TenderAward


def compute_tender_statistics(tenders: list[Tender]) -> dict[str, Any]:
    """Compute aggregate statistics for a list of tenders."""
    if not tenders:
        return {
            "total_tenders": 0,
            "active_tenders": 0,
            "completed_tenders": 0,
            "tenders_by_status": {},
            "tenders_by_method": {},
            "tenders_by_category": {},
            "tenders_by_year": {},
            "total_value": 0,
            "average_value": 0,
            "total_budget": 0,
            "eu_funded_count": 0,
        }

    total = len(tenders)
    active = sum(1 for t in tenders if t.is_active)
    completed = sum(1 for t in tenders if t.status.value == "complete")

    by_status: dict[str, int] = {}
    by_method: dict[str, int] = {}
    by_category: dict[str, int] = {}
    by_year: dict[str, int] = {}
    total_value = 0.0
    total_budget = 0.0
    eu_funded = 0
    value_count = 0

    for t in tenders:
        by_status[t.status.value] = by_status.get(t.status.value, 0) + 1

        if t.procurement_method:
            by_method[t.procurement_method.value] = by_method.get(t.procurement_method.value, 0) + 1

        if t.main_category:
            by_category[t.main_category.value] = by_category.get(t.main_category.value, 0) + 1

        if t.published_date:
            year = str(t.published_date.year)
            by_year[year] = by_year.get(year, 0) + 1

        if t.value_amount:
            total_value += t.value_amount
            value_count += 1

        if t.budget_amount:
            total_budget += t.budget_amount

        if t.is_eu_funded:
            eu_funded += 1

    return {
        "total_tenders": total,
        "active_tenders": active,
        "completed_tenders": completed,
        "tenders_by_status": by_status,
        "tenders_by_method": by_method,
        "tenders_by_category": by_category,
        "tenders_by_year": by_year,
        "total_value": total_value,
        "average_value": total_value / value_count if value_count > 0 else 0,
        "total_budget": total_budget,
        "eu_funded_count": eu_funded,
    }


def compute_award_statistics(awards: list[TenderAward]) -> dict[str, Any]:
    """Compute aggregate statistics for tender awards."""
    if not awards:
        return {
            "total_awards": 0,
            "successful_awards": 0,
            "pending_awards": 0,
            "total_award_value": 0,
            "average_award_value": 0,
            "awards_by_status": {},
            "awards_by_year": {},
            "top_suppliers": [],
        }

    total = len(awards)
    successful = sum(1 for a in awards if a.is_successful)
    pending = sum(1 for a in awards if a.status.value == "pending")

    total_value = 0.0
    value_count = 0
    by_status: dict[str, int] = {}
    by_year: dict[str, int] = {}
    supplier_counts: dict[str, int] = {}
    supplier_values: dict[str, float] = {}

    for a in awards:
        by_status[a.status.value] = by_status.get(a.status.value, 0) + 1

        if a.award_date:
            year = str(a.award_date.year)
            by_year[year] = by_year.get(year, 0) + 1

        if a.value_amount:
            total_value += a.value_amount
            value_count += 1

        if a.supplier_name:
            supplier_counts[a.supplier_name] = supplier_counts.get(a.supplier_name, 0) + 1
            if a.value_amount:
                supplier_values[a.supplier_name] = (
                    supplier_values.get(a.supplier_name, 0) + a.value_amount
                )

    top_suppliers = sorted(
        [
            {"name": name, "count": count, "total_value": supplier_values.get(name, 0)}
            for name, count in supplier_counts.items()
        ],
        key=lambda x: x["count"],
        reverse=True,
    )[:10]

    return {
        "total_awards": total,
        "successful_awards": successful,
        "pending_awards": pending,
        "total_award_value": total_value,
        "average_award_value": total_value / value_count if value_count > 0 else 0,
        "awards_by_status": by_status,
        "awards_by_year": by_year,
        "top_suppliers": top_suppliers,
    }


def compute_win_rate(
    tenders: list[Tender], awards: list[TenderAward], company_idno: str
) -> dict[str, Any]:
    """Compute win rate for a company based on tenders they bid on vs awards won."""
    bids_as_supplier = sum(
        1
        for t in tenders
        if any(a.supplier_idno == company_idno for a in awards if a.tender_ocid == t.ocid)
    )
    won = sum(1 for a in awards if a.supplier_idno == company_idno and a.is_successful)

    win_rate = (won / bids_as_supplier * 100) if bids_as_supplier > 0 else 0

    return {
        "company_idno": company_idno,
        "tenders_participated": bids_as_supplier,
        "awards_won": won,
        "win_rate_percent": round(win_rate, 2),
    }


def compute_method_breakdown(tenders: list[Tender]) -> list[dict[str, Any]]:
    """Breakdown of tenders by procurement method."""
    counts: dict[str, int] = {}
    values: dict[str, float] = {}

    for t in tenders:
        method = t.procurement_method.value if t.procurement_method else "unknown"
        counts[method] = counts.get(method, 0) + 1
        if t.value_amount:
            values[method] = values.get(method, 0) + t.value_amount

    return [
        {"method": method, "count": count, "total_value": values.get(method, 0)}
        for method, count in sorted(counts.items(), key=lambda x: x[1], reverse=True)
    ]


def compute_timeline(tenders: list[Tender]) -> list[dict[str, Any]]:
    """Build a timeline of tenders by month."""
    timeline: dict[str, int] = {}
    for t in tenders:
        if t.published_date:
            key = t.published_date.strftime("%Y-%m")
            timeline[key] = timeline.get(key, 0) + 1

    sorted_timeline = sorted(timeline.items())
    return [{"month": month, "count": count} for month, count in sorted_timeline]
