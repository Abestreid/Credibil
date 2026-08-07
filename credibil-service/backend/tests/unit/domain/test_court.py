from __future__ import annotations

from datetime import date

import pytest

from credibil.domain.court.entities import (
    CaseStatus,
    CaseType,
    CourtCase,
    CourtHearing,
    CourtType,
    ParticipantRole,
)


class TestCourtCaseEntity:
    def test_create_case(self) -> None:
        case = CourtCase(
            case_number="2024-1234",
            case_type=CaseType.CIVIL,
            court_name="Judecătoria Chișinău",
            court_type=CourtType.JUDECATORIE,
            court_slug="jc",
            registration_date=date(2024, 1, 15),
            status=CaseStatus.OPEN,
            plaintiff_name="Ion Popescu",
            plaintiff_idno="1234567890123",
            defendant_name="Maria SRL",
            defendant_idno="9876543210987",
            judge_name="Ana Cazacu",
            subject_matter="Contract dispute",
        )
        assert case.case_number == "2024-1234"
        assert case.case_type == CaseType.CIVIL
        assert case.court_name == "Judecătoria Chișinău"
        assert case.court_type == CourtType.JUDECATORIE
        assert case.status == CaseStatus.OPEN
        assert case.is_active is True
        assert case.id is not None

    def test_case_is_active(self) -> None:
        for status in [CaseStatus.OPEN, CaseStatus.IN_PROGRESS, CaseStatus.PENDING]:
            case = CourtCase(case_number="1", court_name="Test", status=status)
            assert case.is_active is True

    def test_case_is_not_active(self) -> None:
        for status in [CaseStatus.CLOSED, CaseStatus.APPEALED]:
            case = CourtCase(case_number="1", court_name="Test", status=status)
            assert case.is_active is False

    def test_update_case(self) -> None:
        case = CourtCase(
            case_number="2024-1234",
            court_name="Judecătoria Chișinău",
            status=CaseStatus.OPEN,
        )
        case.update(
            status=CaseStatus.CLOSED,
            decision_date=date(2024, 6, 15),
            judge_name="Ana Cazacu",
        )
        assert case.status == CaseStatus.CLOSED
        assert case.decision_date == date(2024, 6, 15)
        assert case.judge_name == "Ana Cazacu"
        assert case.updated_at >= case.created_at

    def test_update_ignores_unknown_fields(self) -> None:
        case = CourtCase(case_number="2024-1234", court_name="Test")
        case.update(unknown_field="value")
        assert case.case_number == "2024-1234"

    def test_repr(self) -> None:
        case = CourtCase(
            case_number="2024-1234",
            court_name="Judecătoria Chișinău",
            status=CaseStatus.OPEN,
        )
        r = repr(case)
        assert "2024-1234" in r
        assert "Judecătoria Chișinău" in r

    def test_default_values(self) -> None:
        case = CourtCase(case_number="2024-1234", court_name="Test Court")
        assert case.case_type == CaseType.OTHER
        assert case.court_type == CourtType.JUDECATORIE
        assert case.status == CaseStatus.OPEN
        assert case.raw_data == {}
        assert case.metadata == {}
        assert case.registration_date is None
        assert case.decision_date is None

    def test_participant_roles(self) -> None:
        assert ParticipantRole.PLAINTIFF == "plaintiff"
        assert ParticipantRole.DEFENDANT == "defendant"
        assert ParticipantRole.APPELLANT == "appellant"
        assert ParticipantRole.INTERESTED_PARTY == "interested_party"


class TestCourtHearingEntity:
    def test_create_hearing(self) -> None:
        hearing = CourtHearing(
            case_number="2024-1234",
            hearing_date=date(2024, 3, 15),
            hearing_time="09:30",
            court_name="Judecătoria Chișinău",
            room="101",
            judge_name="Ana Cazacu",
            hearing_type="main_hearing",
        )
        assert hearing.case_number == "2024-1234"
        assert hearing.hearing_date == date(2024, 3, 15)
        assert hearing.hearing_time == "09:30"
        assert hearing.room == "101"
        assert hearing.judge_name == "Ana Cazacu"
        assert hearing.id is not None

    def test_hearing_repr(self) -> None:
        hearing = CourtHearing(
            case_number="2024-1234",
            hearing_date=date(2024, 3, 15),
            hearing_time="09:30",
        )
        r = repr(hearing)
        assert "2024-1234" in r
        assert "2024-03-15" in r


class TestCourtCaseRepository:
    @pytest.mark.asyncio
    async def test_save_and_find(self, court_case_repo: "InMemoryCourtCaseRepository") -> None:
        case = CourtCase(
            case_number="2024-1234",
            court_name="Test Court",
            plaintiff_idno="1234567890123",
        )
        await court_case_repo.save(case)
        found = await court_case_repo.find_by_id(case.id)
        assert found is not None
        assert found.case_number == "2024-1234"

    @pytest.mark.asyncio
    async def test_find_by_case_number(
        self, court_case_repo: "InMemoryCourtCaseRepository"
    ) -> None:
        case = CourtCase(case_number="2024-1234", court_name="Test Court")
        await court_case_repo.save(case)
        found = await court_case_repo.find_by_case_number("2024-1234")
        assert found is not None
        assert found.case_number == "2024-1234"

    @pytest.mark.asyncio
    async def test_find_by_idno(self, court_case_repo: "InMemoryCourtCaseRepository") -> None:
        await court_case_repo.save(
            CourtCase(
                case_number="2024-001",
                court_name="Court A",
                plaintiff_idno="1234567890123",
            )
        )
        await court_case_repo.save(
            CourtCase(
                case_number="2024-002",
                court_name="Court B",
                defendant_idno="1234567890123",
            )
        )
        await court_case_repo.save(
            CourtCase(
                case_number="2024-003",
                court_name="Court C",
                plaintiff_idno="9999999999999",
            )
        )

        cases = await court_case_repo.find_by_idno("1234567890123")
        assert len(cases) == 2

    @pytest.mark.asyncio
    async def test_find_by_idno_plaintiff_only(
        self, court_case_repo: "InMemoryCourtCaseRepository"
    ) -> None:
        await court_case_repo.save(
            CourtCase(case_number="1", court_name="A", plaintiff_idno="1234567890123")
        )
        await court_case_repo.save(
            CourtCase(case_number="2", court_name="B", defendant_idno="1234567890123")
        )
        cases = await court_case_repo.find_by_idno("1234567890123", role="plaintiff")
        assert len(cases) == 1
        assert cases[0].case_number == "1"

    @pytest.mark.asyncio
    async def test_count_by_idno(self, court_case_repo: "InMemoryCourtCaseRepository") -> None:
        await court_case_repo.save(
            CourtCase(case_number="1", court_name="A", plaintiff_idno="1234567890123")
        )
        await court_case_repo.save(
            CourtCase(case_number="2", court_name="B", defendant_idno="1234567890123")
        )
        count = await court_case_repo.count_by_idno("1234567890123")
        assert count == 2

    @pytest.mark.asyncio
    async def test_count_active_by_idno(
        self, court_case_repo: "InMemoryCourtCaseRepository"
    ) -> None:
        await court_case_repo.save(
            CourtCase(
                case_number="1",
                court_name="A",
                plaintiff_idno="1234567890123",
                status=CaseStatus.OPEN,
            )
        )
        await court_case_repo.save(
            CourtCase(
                case_number="2",
                court_name="B",
                plaintiff_idno="1234567890123",
                status=CaseStatus.CLOSED,
            )
        )
        count = await court_case_repo.count_active_by_idno("1234567890123")
        assert count == 1

    @pytest.mark.asyncio
    async def test_delete(self, court_case_repo: "InMemoryCourtCaseRepository") -> None:
        case = CourtCase(case_number="2024-1234", court_name="Test Court")
        await court_case_repo.save(case)
        await court_case_repo.delete(case.id)
        assert await court_case_repo.find_by_id(case.id) is None

    @pytest.mark.asyncio
    async def test_find_by_court(self, court_case_repo: "InMemoryCourtCaseRepository") -> None:
        await court_case_repo.save(
            CourtCase(case_number="1", court_name="Court A", court_slug="jc")
        )
        await court_case_repo.save(
            CourtCase(case_number="2", court_name="Court B", court_slug="jbl")
        )
        cases = await court_case_repo.find_by_court("jc")
        assert len(cases) == 1
        assert cases[0].court_slug == "jc"

    @pytest.mark.asyncio
    async def test_find_open_cases(self, court_case_repo: "InMemoryCourtCaseRepository") -> None:
        await court_case_repo.save(
            CourtCase(
                case_number="1",
                court_name="A",
                plaintiff_idno="1234567890123",
                status=CaseStatus.OPEN,
            )
        )
        await court_case_repo.save(
            CourtCase(
                case_number="2",
                court_name="B",
                plaintiff_idno="1234567890123",
                status=CaseStatus.CLOSED,
            )
        )
        open_cases = await court_case_repo.find_open_cases_by_idno("1234567890123")
        assert len(open_cases) == 1


class TestCourtHearingRepository:
    @pytest.mark.asyncio
    async def test_save_and_find(
        self, court_hearing_repo: "InMemoryCourtHearingRepository"
    ) -> None:
        hearing = CourtHearing(
            case_number="2024-1234",
            hearing_date=date(2024, 3, 15),
            hearing_time="09:30",
        )
        await court_hearing_repo.save(hearing)
        found = await court_hearing_repo.find_by_id(hearing.id)
        assert found is not None
        assert found.hearing_time == "09:30"

    @pytest.mark.asyncio
    async def test_find_by_case_number(
        self, court_hearing_repo: "InMemoryCourtHearingRepository"
    ) -> None:
        await court_hearing_repo.save(
            CourtHearing(case_number="2024-1234", hearing_date=date(2024, 3, 15))
        )
        await court_hearing_repo.save(
            CourtHearing(case_number="2024-1234", hearing_date=date(2024, 5, 20))
        )
        await court_hearing_repo.save(
            CourtHearing(case_number="2024-5678", hearing_date=date(2024, 4, 10))
        )
        hearings = await court_hearing_repo.find_by_case_number("2024-1234")
        assert len(hearings) == 2

    @pytest.mark.asyncio
    async def test_count_by_case(
        self, court_hearing_repo: "InMemoryCourtHearingRepository"
    ) -> None:
        await court_hearing_repo.save(
            CourtHearing(case_number="2024-1234", hearing_date=date(2024, 3, 15))
        )
        await court_hearing_repo.save(
            CourtHearing(case_number="2024-1234", hearing_date=date(2024, 5, 20))
        )
        count = await court_hearing_repo.count_by_case("2024-1234")
        assert count == 2

    @pytest.mark.asyncio
    async def test_delete(self, court_hearing_repo: "InMemoryCourtHearingRepository") -> None:
        hearing = CourtHearing(case_number="2024-1234", hearing_date=date(2024, 3, 15))
        await court_hearing_repo.save(hearing)
        await court_hearing_repo.delete(hearing.id)
        assert await court_hearing_repo.find_by_id(hearing.id) is None
