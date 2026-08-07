from __future__ import annotations

from datetime import date, datetime
from enum import StrEnum
from typing import TYPE_CHECKING, Any

from credibil.core.id import new_id

if TYPE_CHECKING:
    from uuid import UUID


class AccreditationCategory(StrEnum):
    TESTING_LAB = "testing_lab"
    CALIBRATION_LAB = "calibration_lab"
    MEDICAL_LAB = "medical_lab"
    PRODUCT_CERT_BODY = "product_cert_body"
    ORGANIC_CERT_BODY = "organic_cert_body"
    MANAGEMENT_SYSTEM_CERT_BODY = "management_system_cert_body"
    INSPECTION_BODY = "inspection_body"


class AccreditationStatus(StrEnum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    SUSPENDED_PARTIAL = "suspended_partial"
    WITHDRAWN = "withdrawn"


class Accreditation:
    """An accreditation record from acreditare.md (MOLDAC)."""

    def __init__(
        self,
        *,
        accreditation_id: UUID | None = None,
        organization_name: str,
        director_name: str | None = None,
        address: str | None = None,
        phone: str | None = None,
        fax: str | None = None,
        email: str | None = None,
        certificate_number: str,
        category: AccreditationCategory,
        standard: str,
        status: AccreditationStatus = AccreditationStatus.ACTIVE,
        issue_date: date | None = None,
        expiry_date: date | None = None,
        scope: str | None = None,
        certificate_url: str | None = None,
        annex_urls: list[dict[str, str]] | None = None,
        remarks: str | None = None,
        country_code: str = "MD",
        source_url: str | None = None,
        raw_data: dict[str, Any] | None = None,
        last_synced: datetime | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        self.id = accreditation_id or new_id()
        self.organization_name = organization_name
        self.director_name = director_name
        self.address = address
        self.phone = phone
        self.fax = fax
        self.email = email
        self.certificate_number = certificate_number
        self.category = category
        self.standard = standard
        self.status = status
        self.issue_date = issue_date
        self.expiry_date = expiry_date
        self.scope = scope
        self.certificate_url = certificate_url
        self.annex_urls = annex_urls or []
        self.remarks = remarks
        self.country_code = country_code
        self.source_url = source_url
        self.raw_data = raw_data or {}
        self.last_synced = last_synced or datetime.now()
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()

    def update(self, **kwargs: Any) -> None:
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.now()

    def __repr__(self) -> str:
        return (
            f"<Accreditation cert={self.certificate_number!r} "
            f"org={self.organization_name[:50]!r} status={self.status.value!r}>"
        )
