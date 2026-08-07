from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class EnforcementProceedingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Any
    somation_id: int
    debtor_name: str | None = None
    debtor_idno: str | None = None
    debtor_idno_masked: str | None = None
    creditor_name: str | None = None
    creditor_idno: str | None = None
    executory_doc_number: str | None = None
    court_name: str | None = None
    case_number: str | None = None
    amount: float | None = None
    currency: str = "MDL"
    publication_date: Any = None
    state: str
    source_url: str | None = None
    fetched_at: Any = None
    created_at: Any = None
    updated_at: Any = None
    # role of the queried IDNO in this proceeding, when applicable
    role: str | None = None


class EnforcementSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    idno: str
    total: int = 0
    active: int = 0
    archived: int = 0
    as_debtor: int = 0
    as_creditor: int = 0


class ApiResponse(BaseModel):
    success: bool = True
    data: Any = None
    meta: Any = None
    request_id: str | None = None


class EnforcementMeta(BaseModel):
    total: int
    limit: int
    offset: int
    idno: str | None = None
    role: str | None = None
    state: str | None = None


class RefreshResponse(BaseModel):
    status: str = "accepted"
    idno: str
    task_id: str | None = None
    detail: str = Field(
        default="Enforcement sync scheduled; results will appear once the source responds."
    )
