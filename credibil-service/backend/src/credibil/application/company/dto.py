from datetime import date, datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CompanyDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    idno: str
    name_ro: str
    name_ru: str
    registration_date: date | None = None
    status: str
    legal_form: str
    legal_address: str | None = None
    postal_code: str | None = None
    caem: str | None = None
    caem_description: str | None = None
    cuatm: str | None = None
    cuiio: str | None = None
    cfp: str | None = None
    cfoj: str | None = None
    business_category: str | None = None
    tax_debt: float | None = None
    tax_debt_fetched_at: datetime | None = None
    founder_count: int = 0
    director_count: int = 0
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime
