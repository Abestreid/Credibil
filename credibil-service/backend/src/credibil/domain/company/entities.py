from __future__ import annotations

from datetime import date, datetime
from enum import StrEnum
from typing import TYPE_CHECKING, Any

from credibil.core.id import new_id

if TYPE_CHECKING:
    from uuid import UUID


class CompanyStatus(StrEnum):
    ACTIVE = "active"
    LIQUIDATED = "liquidated"
    DISSOLVED = "dissolved"
    REORGANIZING = "reorganizing"
    SUSPENDED = "suspended"


class LegalForm(StrEnum):
    SRL = "SRL"  # Societate cu Răspundere Limitată
    SA = "SA"  # Societate pe Acțiuni
    II = "II"  # Întreprindere Individuală
    IF = "IF"  # Întreprindere Familială
    PFA = "PFA"  # Persoană Fizică Autorizată
    Cooperativa = "COOPERATIVA"
    ONC = "ONC"  # Organizație Non-Comercială
    OTHER = "OTHER"


class Company:
    """Core company entity — the central domain object of the platform."""

    def __init__(
        self,
        *,
        company_id: UUID | None = None,
        idno: str,
        name_ro: str,
        name_ru: str,
        registration_date: date | None = None,
        status: CompanyStatus = CompanyStatus.ACTIVE,
        legal_form: LegalForm = LegalForm.OTHER,
        legal_address: str | None = None,
        postal_code: str | None = None,
        caem: str | None = None,
        caem_description: str | None = None,
        cuatm: str | None = None,
        cuiio: str | None = None,
        cfp: str | None = None,
        cfoj: str | None = None,
        business_category: str | None = None,
        tax_debt: float | None = None,
        tax_debt_fetched_at: datetime | None = None,
        founder_count: int = 0,
        director_count: int = 0,
        metadata: dict[str, Any] | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        self.id = company_id or new_id()
        self.idno = idno
        self.name_ro = name_ro
        self.name_ru = name_ru
        self.registration_date = registration_date
        self.status = status
        self.legal_form = legal_form
        self.legal_address = legal_address
        self.postal_code = postal_code
        self.caem = caem
        self.caem_description = caem_description
        self.cuatm = cuatm
        self.cuiio = cuiio
        self.cfp = cfp
        self.cfoj = cfoj
        self.business_category = business_category
        self.tax_debt = tax_debt
        self.tax_debt_fetched_at = tax_debt_fetched_at
        self.founder_count = founder_count
        self.director_count = director_count
        self.metadata = metadata or {}
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    def update(self, **kwargs: Any) -> None:
        """Update mutable fields."""
        allowed = {
            "name_ro",
            "name_ru",
            "registration_date",
            "status",
            "legal_form",
            "legal_address",
            "postal_code",
            "caem",
            "caem_description",
            "cuatm",
            "cuiio",
            "cfp",
            "cfoj",
            "business_category",
            "tax_debt",
            "tax_debt_fetched_at",
            "founder_count",
            "director_count",
            "metadata",
        }
        for key, value in kwargs.items():
            if key in allowed:
                setattr(self, key, value)
        self.updated_at = datetime.utcnow()

    def __repr__(self) -> str:
        return f"<Company id={self.id} idno={self.idno} name_ro={self.name_ro!r}>"
