from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class GetCompanyQuery(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    company_id: str


class ListCompaniesQuery(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    page: int = 1
    per_page: int = 25
    search: str | None = None
    filters: dict[str, Any] | None = None
    sort_by: str = "created_at"
    sort_order: str = "desc"
