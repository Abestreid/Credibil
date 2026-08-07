from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from credibil.domain.court.entities import CourtCase


def compute_case_statistics(cases: list[CourtCase]) -> dict[str, Any]:
    """Compute aggregate statistics for a list of court cases."""
    if not cases:
        return {
            "total_cases": 0,
            "active_cases": 0,
            "closed_cases": 0,
            "cases_by_type": {},
            "cases_by_court_type": {},
            "cases_by_status": {},
            "cases_by_year": {},
            "as_plaintiff": 0,
            "as_defendant": 0,
        }

    total = len(cases)
    active = sum(1 for c in cases if c.is_active)
    closed = sum(1 for c in cases if c.status.value == "closed")

    by_type: dict[str, int] = {}
    by_court_type: dict[str, int] = {}
    by_status: dict[str, int] = {}
    by_year: dict[str, int] = {}
    as_plaintiff = 0
    as_defendant = 0

    for case in cases:
        by_type[case.case_type.value] = by_type.get(case.case_type.value, 0) + 1
        by_court_type[case.court_type.value] = by_court_type.get(case.court_type.value, 0) + 1
        by_status[case.status.value] = by_status.get(case.status.value, 0) + 1

        if case.registration_date:
            year = str(case.registration_date.year)
            by_year[year] = by_year.get(year, 0) + 1

    return {
        "total_cases": total,
        "active_cases": active,
        "closed_cases": closed,
        "cases_by_type": by_type,
        "cases_by_court_type": by_court_type,
        "cases_by_status": by_status,
        "cases_by_year": by_year,
        "as_plaintiff": as_plaintiff,
        "as_defendant": as_defendant,
    }


def compute_judge_frequency(cases: list[CourtCase]) -> list[dict[str, Any]]:
    """Count how often each judge appears in the case list."""
    judge_counts: dict[str, int] = {}
    for case in cases:
        if case.judge_name:
            judge_counts[case.judge_name] = judge_counts.get(case.judge_name, 0) + 1

    sorted_judges = sorted(judge_counts.items(), key=lambda x: x[1], reverse=True)
    return [{"judge_name": name, "case_count": count} for name, count in sorted_judges]


def compute_court_distribution(cases: list[CourtCase]) -> list[dict[str, Any]]:
    """Count cases per court."""
    court_counts: dict[str, int] = {}
    for case in cases:
        court_counts[case.court_name] = court_counts.get(case.court_name, 0) + 1

    sorted_courts = sorted(court_counts.items(), key=lambda x: x[1], reverse=True)
    return [{"court_name": name, "case_count": count} for name, count in sorted_courts]


def compute_timeline(cases: list[CourtCase]) -> list[dict[str, Any]]:
    """Build a timeline of case registrations by month."""
    timeline: dict[str, int] = {}
    for case in cases:
        if case.registration_date:
            key = case.registration_date.strftime("%Y-%m")
            timeline[key] = timeline.get(key, 0) + 1

    sorted_timeline = sorted(timeline.items())
    return [{"month": month, "count": count} for month, count in sorted_timeline]
