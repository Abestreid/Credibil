from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class CompanyPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    idno: str = Field(..., description="Fiscal code (13-digit IDNO)")
    name_ro: str | None = None
    name_ru: str | None = None
    status: str | None = None
    legal_form: str | None = None
    legal_address: str | None = None
    registration_date: Any = None
    caem: str | None = None
    caem_description: str | None = None
    founder_count: int = 0
    director_count: int = 0
    tax_debt: float | None = None


class EnforcementPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    somation_id: int
    role: str | None = Field(default=None, description="debtor | creditor (relative to the queried IDNO)")
    debtor_name: str | None = None
    creditor_name: str | None = None
    executory_doc_number: str | None = None
    court_name: str | None = None
    case_number: str | None = None
    amount: float | None = None
    currency: str = "MDL"
    publication_date: Any = None
    state: str = Field(..., description="active | archived")
    source_url: str | None = None


class CourtCasePublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    case_number: str
    case_type: str
    court_name: str
    status: str
    plaintiff_name: str | None = None
    defendant_name: str | None = None
    registration_date: Any = None


class RelationshipPersonPublic(BaseModel):
    person_id: str
    full_name: str | None = None
    idnp: str | None = None
    role: str
    is_active: bool = True


class KeyInfo(BaseModel):
    name: str
    scopes: list[str]
    rate_limit: int = Field(..., description="Requests per hour allowed for this key")


class CompanyResponse(BaseModel):
    data: CompanyPublic


class CompaniesListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    data: list[CompanyPublic]


class EnforcementListResponse(BaseModel):
    idno: str
    total: int
    active: int
    archived: int
    data: list[EnforcementPublic]


class CourtListResponse(BaseModel):
    idno: str
    total: int
    data: list[CourtCasePublic]


class RelationshipsResponse(BaseModel):
    idno: str
    data: list[RelationshipPersonPublic]


class ErrorResponse(BaseModel):
    detail: str
