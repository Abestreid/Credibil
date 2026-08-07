from __future__ import annotations

from datetime import date, datetime
from enum import StrEnum
from typing import TYPE_CHECKING, Any

from credibil.core.id import new_id

if TYPE_CHECKING:
    from uuid import UUID


class EnforcementRole(StrEnum):
    """Role a company plays in an enforcement proceeding.

    Derived by matching the company IDNO against the debtor/creditor side.
    """

    DEBTOR = "debtor"  # должник — the party being pursued
    CREDITOR = "creditor"  # взыскатель — the party pursuing the debt


class EnforcementState(StrEnum):
    """Lifecycle of a proceeding relative to the unej.md source.

    ACTIVE   — present in the most recent crawl of unej.md.
    ARCHIVED — was ingested previously but has since disappeared from the
               source. We never delete these; they move to the "archived"
               tab of the company card.
    """

    ACTIVE = "active"
    ARCHIVED = "archived"


class EnforcementProceeding:
    """An enforcement summons ("somație") published on unej.md.

    unej.md exposes only the public "Somații" board — pre-execution summons an
    executor posts when a debtor could not be served in person. Each entry is
    keyed by its sequential ``somation_id`` on the source. A company is linked
    via ``debtor_idno`` / ``creditor_idno`` matching its fiscal code (IDNO).

    The debtor IDNO is masked on the source (only the trailing digits are
    shown); ``debtor_idno`` is populated with the full value only when resolved
    through a targeted IDNO search, while ``debtor_idno_masked`` keeps the
    original masked string as ingested.
    """

    def __init__(
        self,
        *,
        proceeding_id: UUID | None = None,
        somation_id: int,
        debtor_name: str | None = None,
        debtor_idno: str | None = None,
        debtor_idno_masked: str | None = None,
        creditor_name: str | None = None,
        creditor_idno: str | None = None,
        executory_doc_number: str | None = None,
        court_name: str | None = None,
        case_number: str | None = None,
        amount: float | None = None,
        currency: str = "MDL",
        publication_date: date | None = None,
        state: EnforcementState = EnforcementState.ACTIVE,
        source_url: str | None = None,
        raw_data: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
        first_seen_at: datetime | None = None,
        last_seen_at: datetime | None = None,
        fetched_at: datetime | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        self.id = proceeding_id or new_id()
        self.somation_id = somation_id
        self.debtor_name = debtor_name
        self.debtor_idno = debtor_idno
        self.debtor_idno_masked = debtor_idno_masked
        self.creditor_name = creditor_name
        self.creditor_idno = creditor_idno
        self.executory_doc_number = executory_doc_number
        self.court_name = court_name
        self.case_number = case_number
        self.amount = amount
        self.currency = currency
        self.publication_date = publication_date
        self.state = state
        self.source_url = source_url
        self.raw_data = raw_data or {}
        self.metadata = metadata or {}
        self.first_seen_at = first_seen_at
        self.last_seen_at = last_seen_at
        self.fetched_at = fetched_at
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    def update(self, **kwargs: Any) -> None:
        allowed = {
            "debtor_name",
            "debtor_idno",
            "debtor_idno_masked",
            "creditor_name",
            "creditor_idno",
            "executory_doc_number",
            "court_name",
            "case_number",
            "amount",
            "currency",
            "publication_date",
            "state",
            "source_url",
            "raw_data",
            "metadata",
            "first_seen_at",
            "last_seen_at",
            "fetched_at",
        }
        for key, value in kwargs.items():
            if key in allowed:
                setattr(self, key, value)
        self.updated_at = datetime.utcnow()

    @property
    def is_active(self) -> bool:
        return self.state == EnforcementState.ACTIVE

    def role_for_idno(self, idno: str) -> EnforcementRole | None:
        """Return the role the given IDNO plays in this proceeding, if any."""
        if self.debtor_idno and self.debtor_idno == idno:
            return EnforcementRole.DEBTOR
        if self.creditor_idno and self.creditor_idno == idno:
            return EnforcementRole.CREDITOR
        return None

    def matches_masked_idno(self, idno: str) -> bool:
        """Best-effort debtor match when only the masked suffix is known.

        unej.md masks the debtor IDNO (e.g. ``*******31705``). When the full
        IDNO has not been resolved we fall back to a trailing-digits comparison.
        """
        if not self.debtor_idno_masked:
            return False
        suffix = self.debtor_idno_masked.replace("*", "").strip()
        return bool(suffix) and idno.endswith(suffix)

    def __repr__(self) -> str:
        return (
            f"<EnforcementProceeding somation_id={self.somation_id} "
            f"debtor={self.debtor_name!r} state={self.state}>"
        )
