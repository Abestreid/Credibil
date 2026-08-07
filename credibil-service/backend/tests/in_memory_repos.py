from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING, Any

from credibil.domain.accreditation.entities import (
    Accreditation,
    AccreditationCategory,
    AccreditationStatus,
)
from credibil.domain.court.entities import CourtCase, CourtHearing
from credibil.domain.financial import FinancialReport
from credibil.domain.relationship.entities import (
    CompanyRelationship,
    Person,
    RelationshipType,
)
from credibil.domain.sync.entities import SyncHistory, SyncStatus, SyncType
from credibil.domain.tender.entities import Tender, TenderAward, TenderBid
from credibil.ports.repositories.accreditation import AccreditationRepository
from credibil.ports.repositories.court_case import CourtCaseRepository, CourtHearingRepository
from credibil.ports.repositories.financial_report import FinancialReportRepository
from credibil.ports.repositories.relationship import PersonRepository, RelationshipRepository
from credibil.ports.repositories.sync_history import SyncHistoryRepository
from credibil.ports.repositories.tender import (
    TenderAwardRepository,
    TenderBidRepository,
    TenderRepository,
)

if TYPE_CHECKING:
    from uuid import UUID


# ── In-Memory SyncHistoryRepository ─────────────────────────────────────────


class InMemorySyncHistoryRepository(SyncHistoryRepository):
    def __init__(self) -> None:
        self._records: dict[UUID, SyncHistory] = {}

    async def find_by_id(self, sync_id: UUID) -> SyncHistory | None:
        return self._records.get(sync_id)

    async def save(self, sync: SyncHistory) -> SyncHistory:
        self._records[sync.id] = sync
        return sync

    async def find_running_by_provider(self, provider_id: str) -> SyncHistory | None:
        for s in self._records.values():
            if s.provider_id == provider_id and s.status == SyncStatus.RUNNING:
                return s
        return None

    async def find_latest_completed(
        self, provider_id: str, sync_type: SyncType
    ) -> SyncHistory | None:
        candidates = [
            s
            for s in self._records.values()
            if s.provider_id == provider_id
            and s.sync_type == sync_type
            and s.status == SyncStatus.COMPLETED
        ]
        if not candidates:
            return None
        return max(candidates, key=lambda s: s.finished_at or s.created_at)

    async def list_by_provider(
        self, provider_id: str, limit: int = 20, offset: int = 0
    ) -> list[SyncHistory]:
        items = [s for s in self._records.values() if s.provider_id == provider_id]
        items.sort(key=lambda s: s.created_at, reverse=True)
        return items[offset : offset + limit]

    async def count_by_provider(self, provider_id: str) -> int:
        return sum(1 for s in self._records.values() if s.provider_id == provider_id)

    async def delete(self, sync_id: UUID) -> None:
        self._records.pop(sync_id, None)


# ── In-Memory PersonRepository ──────────────────────────────────────────────


class InMemoryPersonRepository(PersonRepository):
    def __init__(self) -> None:
        self._records: dict[UUID, Person] = {}

    async def find_by_id(self, person_id: UUID) -> Person | None:
        return self._records.get(person_id)

    async def find_by_idnp(self, idnp: str) -> Person | None:
        for p in self._records.values():
            if p.idnp == idnp:
                return p
        return None

    async def save(self, person: Person) -> Person:
        self._records[person.id] = person
        return person

    async def delete(self, person_id: UUID) -> None:
        self._records.pop(person_id, None)

    async def list_persons(
        self,
        limit: int = 100,
        offset: int = 0,
        filters: dict[str, Any] | None = None,
        search: str | None = None,
    ) -> list[Person]:
        items = list(self._records.values())
        if filters:
            if "person_type" in filters:
                items = [p for p in items if p.person_type.value == filters["person_type"]]
            if "nationality" in filters:
                items = [p for p in items if p.nationality == filters["nationality"]]
        if search:
            kw = search.lower()
            items = [p for p in items if kw in p.full_name.lower() or kw in p.idnp.lower()]
        items.sort(key=lambda p: p.full_name)
        return items[offset : offset + limit]

    async def count_all(self) -> int:
        return len(self._records)

    async def exists(self, person_id: UUID) -> bool:
        return person_id in self._records


# ── In-Memory RelationshipRepository ────────────────────────────────────────


class InMemoryRelationshipRepository(RelationshipRepository):
    def __init__(self) -> None:
        self._records: dict[UUID, CompanyRelationship] = {}

    async def find_by_id(self, relationship_id: UUID) -> CompanyRelationship | None:
        return self._records.get(relationship_id)

    async def find_by_person_id(
        self,
        person_id: UUID,
        relationship_type: RelationshipType | None = None,
        active_only: bool = True,
    ) -> list[CompanyRelationship]:
        items = [r for r in self._records.values() if r.person_id == person_id]
        if relationship_type:
            items = [r for r in items if r.relationship_type == relationship_type]
        if active_only:
            items = [r for r in items if r.is_active]
        return items

    async def find_by_company_idno(
        self,
        idno: str,
        relationship_type: RelationshipType | None = None,
        active_only: bool = True,
    ) -> list[CompanyRelationship]:
        items = [r for r in self._records.values() if r.company_idno == idno]
        if relationship_type:
            items = [r for r in items if r.relationship_type == relationship_type]
        if active_only:
            items = [r for r in items if r.is_active]
        return items

    async def find_by_person_idnp(
        self,
        idnp: str,
        relationship_type: RelationshipType | None = None,
        active_only: bool = True,
    ) -> list[CompanyRelationship]:
        items = [r for r in self._records.values() if r.person_idnp == idnp]
        if relationship_type:
            items = [r for r in items if r.relationship_type == relationship_type]
        if active_only:
            items = [r for r in items if r.is_active]
        return items

    async def find_related_companies(
        self, idno: str, active_only: bool = True
    ) -> list[CompanyRelationship]:
        items = [r for r in self._records.values() if r.company_idno == idno]
        if active_only:
            items = [r for r in items if r.is_active]
        return items

    async def find_shared_directors(self, idno_a: str, idno_b: str) -> list[CompanyRelationship]:
        persons_a = {
            r.person_id
            for r in self._records.values()
            if r.company_idno == idno_a and r.relationship_type == RelationshipType.DIRECTOR
        }
        persons_b = {
            r.person_id
            for r in self._records.values()
            if r.company_idno == idno_b and r.relationship_type == RelationshipType.DIRECTOR
        }
        shared = persons_a & persons_b
        return [
            r
            for r in self._records.values()
            if r.person_id in shared and r.relationship_type == RelationshipType.DIRECTOR
        ]

    async def find_shared_founders(self, idno_a: str, idno_b: str) -> list[CompanyRelationship]:
        persons_a = {
            r.person_id
            for r in self._records.values()
            if r.company_idno == idno_a and r.relationship_type == RelationshipType.FOUNDER
        }
        persons_b = {
            r.person_id
            for r in self._records.values()
            if r.company_idno == idno_b and r.relationship_type == RelationshipType.FOUNDER
        }
        shared = persons_a & persons_b
        return [
            r
            for r in self._records.values()
            if r.person_id in shared
            and r.company_idno == idno_a
            and r.relationship_type == RelationshipType.FOUNDER
        ]

    async def count_by_company(self, idno: str) -> int:
        return sum(1 for r in self._records.values() if r.company_idno == idno and r.is_active)

    async def count_by_person(self, person_id: UUID) -> int:
        return sum(1 for r in self._records.values() if r.person_id == person_id and r.is_active)

    async def find_existing(
        self,
        person_id: UUID,
        company_idno: str,
        relationship_type: RelationshipType,
    ) -> CompanyRelationship | None:
        for r in self._records.values():
            if (
                r.person_id == person_id
                and r.company_idno == company_idno
                and r.relationship_type == relationship_type
            ):
                return r
        return None

    async def save(self, relationship: CompanyRelationship) -> CompanyRelationship:
        self._records[relationship.id] = relationship
        return relationship

    async def delete(self, relationship_id: UUID) -> None:
        self._records.pop(relationship_id, None)


# ── In-Memory FinancialReportRepository ─────────────────────────────────────


class InMemoryFinancialReportRepository(FinancialReportRepository):
    def __init__(self) -> None:
        self._records: dict[UUID, FinancialReport] = {}

    async def find_by_id(self, report_id: UUID) -> FinancialReport | None:
        return self._records.get(report_id)

    async def find_by_idno_and_year(self, idno: str, year: int) -> FinancialReport | None:
        for r in self._records.values():
            if r.company_idno == idno and r.year == year:
                return r
        return None

    async def find_by_idno(
        self, idno: str, limit: int = 100, offset: int = 0
    ) -> list[FinancialReport]:
        items = [r for r in self._records.values() if r.company_idno == idno]
        items.sort(key=lambda r: r.year, reverse=True)
        return items[offset : offset + limit]

    async def save(self, report: FinancialReport) -> FinancialReport:
        self._records[report.id] = report
        return report

    async def delete(self, report_id: UUID) -> None:
        self._records.pop(report_id, None)

    async def list_reports(
        self,
        limit: int = 100,
        offset: int = 0,
        filters: dict[str, Any] | None = None,
    ) -> list[FinancialReport]:
        items = list(self._records.values())
        if filters:
            if "idno" in filters:
                items = [r for r in items if r.company_idno == filters["idno"]]
            if "year" in filters:
                items = [r for r in items if r.year == filters["year"]]
        items.sort(key=lambda r: r.created_at, reverse=True)
        return items[offset : offset + limit]

    async def count_by_idno(self, idno: str) -> int:
        return sum(1 for r in self._records.values() if r.company_idno == idno)

    async def find_years_for_idno(self, idno: str) -> list[int]:
        years = sorted(
            {r.year for r in self._records.values() if r.company_idno == idno},
            reverse=True,
        )
        return years

    async def find_latest_by_idno(self, idno: str) -> FinancialReport | None:
        items = [r for r in self._records.values() if r.company_idno == idno]
        if not items:
            return None
        return max(items, key=lambda r: r.year)


# ── In-Memory CourtCaseRepository ───────────────────────────────────────────


class InMemoryCourtCaseRepository(CourtCaseRepository):
    def __init__(self) -> None:
        self._records: dict[UUID, CourtCase] = {}

    async def find_by_id(self, case_id: UUID) -> CourtCase | None:
        return self._records.get(case_id)

    async def find_by_case_number(self, case_number: str) -> CourtCase | None:
        for c in self._records.values():
            if c.case_number == case_number:
                return c
        return None

    async def find_by_idno(
        self, idno: str, role: str | None = None, limit: int = 100, offset: int = 0
    ) -> list[CourtCase]:
        items = [
            c
            for c in self._records.values()
            if c.plaintiff_idno == idno or c.defendant_idno == idno
        ]
        if role == "plaintiff":
            items = [c for c in items if c.plaintiff_idno == idno]
        elif role == "defendant":
            items = [c for c in items if c.defendant_idno == idno]
        items.sort(key=lambda c: c.registration_date or date.min, reverse=True)
        return items[offset : offset + limit]

    async def save(self, case: CourtCase) -> CourtCase:
        self._records[case.id] = case
        return case

    async def delete(self, case_id: UUID) -> None:
        self._records.pop(case_id, None)

    async def list_cases(
        self,
        limit: int = 100,
        offset: int = 0,
        filters: dict[str, Any] | None = None,
    ) -> list[CourtCase]:
        items = list(self._records.values())
        if filters:
            if "court_slug" in filters:
                items = [c for c in items if c.court_slug == filters["court_slug"]]
            if "status" in filters:
                items = [c for c in items if c.status.value == filters["status"]]
            if "case_type" in filters:
                items = [c for c in items if c.case_type.value == filters["case_type"]]
            if "idno" in filters:
                idno = filters["idno"]
                items = [c for c in items if c.plaintiff_idno == idno or c.defendant_idno == idno]
        items.sort(key=lambda c: c.created_at or datetime.min, reverse=True)
        return items[offset : offset + limit]

    async def count_by_idno(self, idno: str) -> int:
        return sum(
            1
            for c in self._records.values()
            if c.plaintiff_idno == idno or c.defendant_idno == idno
        )

    async def find_by_court(
        self, court_slug: str, limit: int = 100, offset: int = 0
    ) -> list[CourtCase]:
        items = [c for c in self._records.values() if c.court_slug == court_slug]
        items.sort(key=lambda c: c.created_at or datetime.min, reverse=True)
        return items[offset : offset + limit]

    async def find_by_date_range(
        self,
        start_date: date,
        end_date: date,
        court_slug: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[CourtCase]:
        items = [
            c
            for c in self._records.values()
            if c.registration_date and start_date <= c.registration_date <= end_date
        ]
        if court_slug:
            items = [c for c in items if c.court_slug == court_slug]
        items.sort(key=lambda c: c.registration_date or date.min, reverse=True)
        return items[offset : offset + limit]

    async def count_active_by_idno(self, idno: str) -> int:
        from credibil.domain.court.entities import CaseStatus

        return sum(
            1
            for c in self._records.values()
            if (c.plaintiff_idno == idno or c.defendant_idno == idno)
            and c.status in (CaseStatus.OPEN, CaseStatus.IN_PROGRESS, CaseStatus.PENDING)
        )

    async def find_open_cases_by_idno(self, idno: str) -> list[CourtCase]:
        from credibil.domain.court.entities import CaseStatus

        return [
            c
            for c in self._records.values()
            if (c.plaintiff_idno == idno or c.defendant_idno == idno)
            and c.status in (CaseStatus.OPEN, CaseStatus.IN_PROGRESS, CaseStatus.PENDING)
        ]


# ── In-Memory CourtHearingRepository ────────────────────────────────────────


class InMemoryCourtHearingRepository(CourtHearingRepository):
    def __init__(self) -> None:
        self._records: dict[UUID, CourtHearing] = {}

    async def find_by_id(self, hearing_id: UUID) -> CourtHearing | None:
        return self._records.get(hearing_id)

    async def find_by_case_number(
        self, case_number: str, limit: int = 100, offset: int = 0
    ) -> list[CourtHearing]:
        items = [h for h in self._records.values() if h.case_number == case_number]
        items.sort(key=lambda h: h.hearing_date or datetime.min, reverse=True)
        return items[offset : offset + limit]

    async def save(self, hearing: CourtHearing) -> CourtHearing:
        self._records[hearing.id] = hearing
        return hearing

    async def delete(self, hearing_id: UUID) -> None:
        self._records.pop(hearing_id, None)

    async def find_upcoming_by_idno(self, idno: str, limit: int = 50) -> list[CourtHearing]:
        now = datetime.now()
        items = [h for h in self._records.values() if h.hearing_date and h.hearing_date > now]
        items.sort(key=lambda h: h.hearing_date or datetime.max)
        return items[:limit]

    async def find_by_date_range(
        self,
        start_date: date,
        end_date: date,
        court_slug: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[CourtHearing]:
        items = [
            h
            for h in self._records.values()
            if h.hearing_date and start_date <= h.hearing_date.date() <= end_date
        ]
        items.sort(key=lambda h: h.hearing_date or datetime.min, reverse=True)
        return items[offset : offset + limit]

    async def count_by_case(self, case_number: str) -> int:
        return sum(1 for h in self._records.values() if h.case_number == case_number)


# ── In-Memory TenderRepository ──────────────────────────────────────────────


class InMemoryTenderRepository(TenderRepository):
    def __init__(self) -> None:
        self._records: dict[UUID, Tender] = {}

    async def find_by_id(self, tender_id: UUID) -> Tender | None:
        return self._records.get(tender_id)

    async def find_by_ocid(self, ocid: str) -> Tender | None:
        for t in self._records.values():
            if t.ocid == ocid:
                return t
        return None

    async def find_by_buyer_idno(
        self, idno: str, limit: int = 100, offset: int = 0
    ) -> list[Tender]:
        items = [t for t in self._records.values() if t.buyer_idno == idno]
        items.sort(key=lambda t: t.published_date or datetime.min, reverse=True)
        return items[offset : offset + limit]

    async def find_by_supplier_idno(
        self, idno: str, limit: int = 100, offset: int = 0
    ) -> list[Tender]:
        return []

    async def save(self, tender: Tender) -> Tender:
        self._records[tender.id] = tender
        return tender

    async def delete(self, tender_id: UUID) -> None:
        self._records.pop(tender_id, None)

    async def list_tenders(
        self, limit: int = 100, offset: int = 0, filters: dict[str, Any] | None = None
    ) -> list[Tender]:
        items = list(self._records.values())
        if filters:
            if "status" in filters:
                items = [t for t in items if t.status.value == filters["status"]]
            if "buyer_idno" in filters:
                items = [t for t in items if t.buyer_idno == filters["buyer_idno"]]
        items.sort(key=lambda t: t.published_date or datetime.min, reverse=True)
        return items[offset : offset + limit]

    async def count_by_buyer_idno(self, idno: str) -> int:
        return sum(1 for t in self._records.values() if t.buyer_idno == idno)

    async def find_by_date_range(
        self, start_date: date, end_date: date, limit: int = 100, offset: int = 0
    ) -> list[Tender]:
        items = [
            t
            for t in self._records.values()
            if t.published_date and start_date <= t.published_date.date() <= end_date
        ]
        items.sort(key=lambda t: t.published_date or datetime.min, reverse=True)
        return items[offset : offset + limit]

    async def find_by_status(self, status: str, limit: int = 100, offset: int = 0) -> list[Tender]:
        items = [t for t in self._records.values() if t.status.value == status]
        items.sort(key=lambda t: t.published_date or datetime.min, reverse=True)
        return items[offset : offset + limit]

    async def find_active_by_buyer_idno(self, idno: str) -> list[Tender]:
        from credibil.domain.tender.entities import TenderStatus

        return [
            t
            for t in self._records.values()
            if t.buyer_idno == idno and t.status in (TenderStatus.ACTIVE, TenderStatus.PLANNING)
        ]

    async def find_by_cpv_code(
        self, cpv_code: str, limit: int = 100, offset: int = 0
    ) -> list[Tender]:
        items = [t for t in self._records.values() if t.cpv_code == cpv_code]
        items.sort(key=lambda t: t.published_date or datetime.min, reverse=True)
        return items[offset : offset + limit]


# ── In-Memory TenderAwardRepository ─────────────────────────────────────────


class InMemoryTenderAwardRepository(TenderAwardRepository):
    def __init__(self) -> None:
        self._records: dict[UUID, TenderAward] = {}

    async def find_by_id(self, award_id: UUID) -> TenderAward | None:
        return self._records.get(award_id)

    async def find_by_tender_ocid(
        self, tender_ocid: str, limit: int = 100, offset: int = 0
    ) -> list[TenderAward]:
        items = [a for a in self._records.values() if a.tender_ocid == tender_ocid]
        return items[offset : offset + limit]

    async def find_by_supplier_idno(
        self, idno: str, limit: int = 100, offset: int = 0
    ) -> list[TenderAward]:
        items = [a for a in self._records.values() if a.supplier_idno == idno]
        return items[offset : offset + limit]

    async def save(self, award: TenderAward) -> TenderAward:
        self._records[award.id] = award
        return award

    async def delete(self, award_id: UUID) -> None:
        self._records.pop(award_id, None)

    async def count_by_supplier_idno(self, idno: str) -> int:
        return sum(1 for a in self._records.values() if a.supplier_idno == idno)

    async def find_successful_by_supplier_idno(self, idno: str) -> list[TenderAward]:
        from credibil.domain.tender.entities import AwardStatus

        return [
            a
            for a in self._records.values()
            if a.supplier_idno == idno and a.status == AwardStatus.ACTIVE
        ]

    async def find_by_date_range(
        self, start_date: date, end_date: date, limit: int = 100, offset: int = 0
    ) -> list[TenderAward]:
        items = [
            a
            for a in self._records.values()
            if a.award_date and start_date <= a.award_date <= end_date
        ]
        items.sort(key=lambda a: a.award_date or date.min, reverse=True)
        return items[offset : offset + limit]


# ── In-Memory TenderBidRepository ───────────────────────────────────────────


class InMemoryTenderBidRepository(TenderBidRepository):
    def __init__(self) -> None:
        self._records: dict[UUID, TenderBid] = {}

    async def find_by_id(self, bid_id: UUID) -> TenderBid | None:
        return self._records.get(bid_id)

    async def find_by_tender_ocid(
        self, tender_ocid: str, limit: int = 100, offset: int = 0
    ) -> list[TenderBid]:
        items = [b for b in self._records.values() if b.tender_ocid == tender_ocid]
        return items[offset : offset + limit]

    async def find_by_tenderer_idno(
        self, idno: str, limit: int = 100, offset: int = 0
    ) -> list[TenderBid]:
        items = [b for b in self._records.values() if b.tenderer_idno == idno]
        return items[offset : offset + limit]

    async def save(self, bid: TenderBid) -> TenderBid:
        self._records[bid.id] = bid
        return bid

    async def delete(self, bid_id: UUID) -> None:
        self._records.pop(bid_id, None)

    async def count_by_tenderer_idno(self, idno: str) -> int:
        return sum(1 for b in self._records.values() if b.tenderer_idno == idno)

    async def find_by_date_range(
        self, start_date: date, end_date: date, limit: int = 100, offset: int = 0
    ) -> list[TenderBid]:
        return []


# ── In-Memory AccreditationRepository ───────────────────────────────────────


class InMemoryAccreditationRepository(AccreditationRepository):
    def __init__(self) -> None:
        self._records: dict[UUID, Accreditation] = {}

    async def find_by_id(self, accreditation_id: UUID) -> Accreditation | None:
        return self._records.get(accreditation_id)

    async def find_by_certificate_number(self, cert_number: str) -> Accreditation | None:
        for acc in self._records.values():
            if acc.certificate_number == cert_number:
                return acc
        return None

    async def find_by_category(
        self, category: AccreditationCategory, limit: int = 100, offset: int = 0
    ) -> list[Accreditation]:
        items = [a for a in self._records.values() if a.category == category]
        items.sort(key=lambda a: a.organization_name)
        return items[offset : offset + limit]

    async def find_by_status(
        self, status: AccreditationStatus, limit: int = 100, offset: int = 0
    ) -> list[Accreditation]:
        items = [a for a in self._records.values() if a.status == status]
        items.sort(key=lambda a: a.organization_name)
        return items[offset : offset + limit]

    async def find_by_organization(
        self, organization_name: str, limit: int = 100, offset: int = 0
    ) -> list[Accreditation]:
        items = [
            a
            for a in self._records.values()
            if organization_name.lower() in a.organization_name.lower()
        ]
        items.sort(key=lambda a: a.organization_name)
        return items[offset : offset + limit]

    async def save(self, accreditation: Accreditation) -> Accreditation:
        accreditation.updated_at = datetime.now()
        self._records[accreditation.id] = accreditation
        return accreditation

    async def delete(self, accreditation_id: UUID) -> None:
        self._records.pop(accreditation_id, None)

    async def list_accreditations(
        self, limit: int = 100, offset: int = 0, filters: dict[str, Any] | None = None
    ) -> list[Accreditation]:
        items = list(self._records.values())
        if filters:
            if "category" in filters:
                items = [a for a in items if a.category.value == filters["category"]]
            if "status" in filters:
                items = [a for a in items if a.status.value == filters["status"]]
            if "country_code" in filters:
                items = [a for a in items if a.country_code == filters["country_code"]]
            if "keyword" in filters:
                kw = filters["keyword"].lower()
                items = [
                    a
                    for a in items
                    if kw in a.organization_name.lower()
                    or kw in a.certificate_number.lower()
                    or (a.scope and kw in a.scope.lower())
                ]
        items.sort(key=lambda a: a.organization_name)
        return items[offset : offset + limit]

    async def count_by_category(self, category: AccreditationCategory) -> int:
        return sum(1 for a in self._records.values() if a.category == category)

    async def count_by_status(self, status: AccreditationStatus) -> int:
        return sum(1 for a in self._records.values() if a.status == status)

    async def search_by_keyword(self, keyword: str, limit: int = 100) -> list[Accreditation]:
        kw = keyword.lower()
        items = [
            a
            for a in self._records.values()
            if kw in a.organization_name.lower()
            or kw in a.certificate_number.lower()
            or (a.scope and kw in a.scope.lower())
            or (a.director_name and kw in a.director_name.lower())
        ]
        items.sort(key=lambda a: a.organization_name)
        return items[:limit]
