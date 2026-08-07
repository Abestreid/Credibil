from datetime import date, datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CompanyCreate(BaseModel):
    idno: str = Field(..., min_length=13, max_length=13, pattern=r"^\d{13}$")
    name_ro: str = Field(..., min_length=1, max_length=500)
    name_ru: str = Field(default="", max_length=500)
    registration_date: date | None = None
    status: str = Field(default="active")
    legal_form: str = Field(default="OTHER")
    legal_address: str | None = Field(default=None, max_length=1000)
    postal_code: str | None = Field(default=None, max_length=10)
    caem: str | None = Field(default=None, max_length=10)
    caem_description: str | None = Field(default=None, max_length=1000)
    cuatm: str | None = Field(default=None, max_length=20)
    cuiio: str | None = Field(default=None, max_length=50)
    cfp: str | None = Field(default=None, max_length=50)
    cfoj: str | None = Field(default=None, max_length=50)
    tax_debt: float | None = Field(default=None, ge=0)
    founder_count: int = Field(default=0, ge=0)
    director_count: int = Field(default=0, ge=0)
    metadata: dict[str, Any] | None = None


class CompanyUpdate(BaseModel):
    name_ro: str | None = Field(default=None, min_length=1, max_length=500)
    name_ru: str | None = Field(default=None, max_length=500)
    registration_date: date | None = None
    status: str | None = None
    legal_form: str | None = None
    legal_address: str | None = Field(default=None, max_length=1000)
    postal_code: str | None = Field(default=None, max_length=10)
    caem: str | None = Field(default=None, max_length=10)
    caem_description: str | None = Field(default=None, max_length=1000)
    cuatm: str | None = Field(default=None, max_length=20)
    cuiio: str | None = Field(default=None, max_length=50)
    cfp: str | None = Field(default=None, max_length=50)
    cfoj: str | None = Field(default=None, max_length=50)
    tax_debt: float | None = Field(default=None, ge=0)
    founder_count: int | None = Field(default=None, ge=0)
    director_count: int | None = Field(default=None, ge=0)
    metadata: dict[str, Any] | None = None


class CompanyResponse(BaseModel):
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


class PaginationMeta(BaseModel):
    page: int
    per_page: int
    total: int
    total_pages: int
    has_next: bool
    has_prev: bool


class CompanyListResponse(BaseModel):
    items: list[CompanyResponse]
    meta: PaginationMeta


class ApiResponse(BaseModel):
    success: bool = True
    data: Any = None
    meta: PaginationMeta | None = None
    request_id: str | None = None
