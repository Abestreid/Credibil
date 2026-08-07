from __future__ import annotations

from datetime import date, datetime
from enum import StrEnum
from typing import TYPE_CHECKING, Any

from credibil.core.id import new_id

if TYPE_CHECKING:
    from uuid import UUID


class CourtType(StrEnum):
    SUPREME = "supreme"
    APPEAL = "appeal"
    JUDECATORIE = "judecatorie"


class CaseType(StrEnum):
    CIVIL = "civil"
    CRIMINAL = "criminal"
    ADMINISTRATIVE = "administrative"
    BANKRUPTCY = "bankruptcy"
    COMMERCIAL = "commercial"
    LABOR = "labor"
    FAMILY = "family"
    OTHER = "other"


class CaseStatus(StrEnum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    CLOSED = "closed"
    APPEALED = "appealed"
    PENDING = "pending"


class ParticipantRole(StrEnum):
    PLAINTIFF = "plaintiff"
    DEFENDANT = "defendant"
    APPELLANT = "appellant"
    APPELLEE = "appellee"
    INTERESTED_PARTY = "interested_party"
    WITNESS = "witness"
    LAWYER = "lawyer"


class CourtCase:
    """A court case from instente.justice.md."""

    def __init__(
        self,
        *,
        case_id: UUID | None = None,
        case_number: str,
        case_type: CaseType = CaseType.OTHER,
        court_name: str,
        court_type: CourtType = CourtType.JUDECATORIE,
        court_slug: str | None = None,
        registration_date: date | None = None,
        decision_date: date | None = None,
        status: CaseStatus = CaseStatus.OPEN,
        plaintiff_name: str | None = None,
        plaintiff_idno: str | None = None,
        defendant_name: str | None = None,
        defendant_idno: str | None = None,
        judge_name: str | None = None,
        subject_matter: str | None = None,
        decision_summary: str | None = None,
        source_url: str | None = None,
        raw_data: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
        fetched_at: datetime | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        self.id = case_id or new_id()
        self.case_number = case_number
        self.case_type = case_type
        self.court_name = court_name
        self.court_type = court_type
        self.court_slug = court_slug
        self.registration_date = registration_date
        self.decision_date = decision_date
        self.status = status
        self.plaintiff_name = plaintiff_name
        self.plaintiff_idno = plaintiff_idno
        self.defendant_name = defendant_name
        self.defendant_idno = defendant_idno
        self.judge_name = judge_name
        self.subject_matter = subject_matter
        self.decision_summary = decision_summary
        self.source_url = source_url
        self.raw_data = raw_data or {}
        self.metadata = metadata or {}
        self.fetched_at = fetched_at
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    def update(self, **kwargs: Any) -> None:
        allowed = {
            "case_type",
            "court_name",
            "court_type",
            "court_slug",
            "registration_date",
            "decision_date",
            "status",
            "plaintiff_name",
            "plaintiff_idno",
            "defendant_name",
            "defendant_idno",
            "judge_name",
            "subject_matter",
            "decision_summary",
            "source_url",
            "raw_data",
            "metadata",
            "fetched_at",
        }
        for key, value in kwargs.items():
            if key in allowed:
                setattr(self, key, value)
        self.updated_at = datetime.utcnow()

    @property
    def is_active(self) -> bool:
        return self.status in (CaseStatus.OPEN, CaseStatus.IN_PROGRESS, CaseStatus.PENDING)

    def __repr__(self) -> str:
        return (
            f"<CourtCase number={self.case_number!r} "
            f"court={self.court_name!r} status={self.status}>"
        )


class CourtHearing:
    """A hearing/agenda entry for a court case."""

    def __init__(
        self,
        *,
        hearing_id: UUID | None = None,
        case_id: UUID | None = None,
        case_number: str,
        hearing_date: date,
        hearing_time: str | None = None,
        court_name: str | None = None,
        department: str | None = None,
        room: str | None = None,
        judge_name: str | None = None,
        hearing_type: str | None = None,
        outcome: str | None = None,
        source_url: str | None = None,
        raw_data: dict[str, Any] | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        self.id = hearing_id or new_id()
        self.case_id = case_id
        self.case_number = case_number
        self.hearing_date = hearing_date
        self.hearing_time = hearing_time
        self.court_name = court_name
        self.department = department
        self.room = room
        self.judge_name = judge_name
        self.hearing_type = hearing_type
        self.outcome = outcome
        self.source_url = source_url
        self.raw_data = raw_data or {}
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    def __repr__(self) -> str:
        return (
            f"<CourtHearing case={self.case_number!r} "
            f"date={self.hearing_date} time={self.hearing_time}>"
        )
