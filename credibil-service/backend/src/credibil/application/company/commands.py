from datetime import date
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class CreateCompanyCommand(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    idno: str
    name_ro: str
    name_ru: str = ""
    registration_date: date | None = None
    status: str = "active"
    legal_form: str = "OTHER"
    legal_address: str | None = None
    postal_code: str | None = None
    caem: str | None = None
    caem_description: str | None = None
    cuatm: str | None = None
    cuiio: str | None = None
    cfp: str | None = None
    cfoj: str | None = None
    tax_debt: float | None = None
    founder_count: int = 0
    director_count: int = 0
    metadata: dict[str, Any] | None = None


class UpdateCompanyCommand(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    company_id: UUID
    name_ro: str | None = None
    name_ru: str | None = None
    registration_date: date | None = None
    status: str | None = None
    legal_form: str | None = None
    legal_address: str | None = None
    postal_code: str | None = None
    caem: str | None = None
    caem_description: str | None = None
    cuatm: str | None = None
    cuiio: str | None = None
    cfp: str | None = None
    cfoj: str | None = None
    tax_debt: float | None = None
    founder_count: int | None = None
    director_count: int | None = None
    metadata: dict[str, Any] | None = None


class DeleteCompanyCommand(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    company_id: UUID
