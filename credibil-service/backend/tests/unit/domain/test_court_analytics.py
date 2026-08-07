from __future__ import annotations

from datetime import date

from credibil.application.analytics.court_analytics import (
    compute_case_statistics,
    compute_court_distribution,
    compute_judge_frequency,
    compute_timeline,
)
from credibil.domain.court.entities import (
    CaseStatus,
    CaseType,
    CourtCase,
    CourtType,
)


def _make_case(**overrides: object) -> CourtCase:
    defaults = {
        "case_number": "2024-001",
        "case_type": CaseType.CIVIL,
        "court_name": "Judecătoria Chișinău",
        "court_type": CourtType.JUDECATORIE,
        "court_slug": "jc",
        "registration_date": date(2024, 1, 15),
        "status": CaseStatus.OPEN,
        "judge_name": "Ana Cazacu",
    }
    defaults.update(overrides)
    return CourtCase(**defaults)  # type: ignore[arg-type]


class TestComputeCaseStatistics:
    def test_empty_cases(self) -> None:
        stats = compute_case_statistics([])
        assert stats["total_cases"] == 0
        assert stats["active_cases"] == 0
        assert stats["closed_cases"] == 0

    def test_basic_statistics(self) -> None:
        cases = [
            _make_case(case_number="1", status=CaseStatus.OPEN),
            _make_case(case_number="2", status=CaseStatus.CLOSED),
            _make_case(case_number="3", status=CaseStatus.IN_PROGRESS),
        ]
        stats = compute_case_statistics(cases)
        assert stats["total_cases"] == 3
        assert stats["active_cases"] == 2
        assert stats["closed_cases"] == 1

    def test_by_type(self) -> None:
        cases = [
            _make_case(case_number="1", case_type=CaseType.CIVIL),
            _make_case(case_number="2", case_type=CaseType.CRIMINAL),
            _make_case(case_number="3", case_type=CaseType.CIVIL),
        ]
        stats = compute_case_statistics(cases)
        assert stats["cases_by_type"]["civil"] == 2
        assert stats["cases_by_type"]["criminal"] == 1

    def test_by_court_type(self) -> None:
        cases = [
            _make_case(case_number="1", court_type=CourtType.JUDECATORIE),
            _make_case(case_number="2", court_type=CourtType.APPEAL),
        ]
        stats = compute_case_statistics(cases)
        assert stats["cases_by_court_type"]["judecatorie"] == 1
        assert stats["cases_by_court_type"]["appeal"] == 1

    def test_by_year(self) -> None:
        cases = [
            _make_case(case_number="1", registration_date=date(2023, 1, 1)),
            _make_case(case_number="2", registration_date=date(2023, 6, 1)),
            _make_case(case_number="3", registration_date=date(2024, 1, 1)),
        ]
        stats = compute_case_statistics(cases)
        assert stats["cases_by_year"]["2023"] == 2
        assert stats["cases_by_year"]["2024"] == 1


class TestComputeJudgeFrequency:
    def test_empty(self) -> None:
        result = compute_judge_frequency([])
        assert result == []

    def test_frequency_count(self) -> None:
        cases = [
            _make_case(case_number="1", judge_name="Ana Cazacu"),
            _make_case(case_number="2", judge_name="Ana Cazacu"),
            _make_case(case_number="3", judge_name="Ion Popa"),
        ]
        result = compute_judge_frequency(cases)
        assert len(result) == 2
        assert result[0]["judge_name"] == "Ana Cazacu"
        assert result[0]["case_count"] == 2
        assert result[1]["judge_name"] == "Ion Popa"
        assert result[1]["case_count"] == 1

    def test_ignores_none_judge(self) -> None:
        cases = [
            _make_case(case_number="1", judge_name="Ana Cazacu"),
            _make_case(case_number="2", judge_name=None),
        ]
        result = compute_judge_frequency(cases)
        assert len(result) == 1


class TestComputeCourtDistribution:
    def test_empty(self) -> None:
        result = compute_court_distribution([])
        assert result == []

    def test_distribution(self) -> None:
        cases = [
            _make_case(case_number="1", court_name="Judecătoria Chișinău"),
            _make_case(case_number="2", court_name="Judecătoria Chișinău"),
            _make_case(case_number="3", court_name="Judecătoria Bălți"),
        ]
        result = compute_court_distribution(cases)
        assert len(result) == 2
        assert result[0]["court_name"] == "Judecătoria Chișinău"
        assert result[0]["case_count"] == 2


class TestComputeTimeline:
    def test_empty(self) -> None:
        result = compute_timeline([])
        assert result == []

    def test_timeline(self) -> None:
        cases = [
            _make_case(case_number="1", registration_date=date(2023, 1, 15)),
            _make_case(case_number="2", registration_date=date(2023, 1, 20)),
            _make_case(case_number="3", registration_date=date(2023, 3, 10)),
            _make_case(case_number="4", registration_date=date(2024, 1, 5)),
        ]
        result = compute_timeline(cases)
        assert len(result) == 3
        assert result[0]["month"] == "2023-01"
        assert result[0]["count"] == 2
        assert result[1]["month"] == "2023-03"
        assert result[1]["count"] == 1
        assert result[2]["month"] == "2024-01"
        assert result[2]["count"] == 1
