from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID  # noqa: TC003

from fastapi import APIRouter, Depends, Query

from credibil.api.v1.companies.dependencies import get_company_repo
from credibil.api.v1.companies.schemas import (
    ApiResponse,
    CompanyCreate,
    CompanyResponse,
    CompanyUpdate,
    PaginationMeta,
)
from credibil.api.v1.sanctions.dependencies import get_sdn_provider
from credibil.api.v1.sanctions.schemas import SanctionsCheckResponse, SanctionsEntryResponse
from credibil.application.company.commands import (
    CreateCompanyCommand,
    DeleteCompanyCommand,
    UpdateCompanyCommand,
)
from credibil.application.company.handlers import CompanyHandlers
from credibil.application.company.queries import GetCompanyQuery, ListCompaniesQuery

if TYPE_CHECKING:
    from credibil.infrastructure.sanctions.sdn_provider import SDNProvider
    from credibil.ports.repositories.company import CompanyRepository

router = APIRouter(prefix="/companies", tags=["companies"])


def _get_handlers(repo: CompanyRepository) -> CompanyHandlers:
    return CompanyHandlers(company_repo=repo)


@router.post("", response_model=ApiResponse, status_code=201)
async def create_company(
    body: CompanyCreate,
    repo: CompanyRepository = Depends(get_company_repo),
) -> ApiResponse:
    handlers = _get_handlers(repo)
    cmd = CreateCompanyCommand(**body.model_dump())
    result = await handlers.create_company(cmd)
    return ApiResponse(data=CompanyResponse(**result.model_dump()))


@router.get("", response_model=ApiResponse)
async def list_companies(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=25, ge=1, le=100),
    search: str | None = Query(default=None, max_length=200),
    status: str | None = Query(default=None),
    legal_form: str | None = Query(default=None),
    caem: str | None = Query(default=None),
    cuatm: str | None = Query(default=None),
    sort_by: str = Query(default="created_at"),
    sort_order: str = Query(default="desc", pattern=r"^(asc|desc)$"),
    repo: CompanyRepository = Depends(get_company_repo),
) -> ApiResponse:
    handlers = _get_handlers(repo)
    filters = {}
    if status:
        filters["status"] = status
    if legal_form:
        filters["legal_form"] = legal_form
    if caem:
        filters["caem"] = caem
    if cuatm:
        filters["cuatm"] = cuatm

    query = ListCompaniesQuery(
        page=page,
        per_page=per_page,
        search=search,
        filters=filters or None,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    result = await handlers.list_companies(query)
    items = [CompanyResponse(**item.model_dump()) for item in result.items]
    return ApiResponse(
        data=items,
        meta=PaginationMeta(**result.meta.model_dump()),
    )


@router.get("/{company_id}", response_model=ApiResponse)
async def get_company(
    company_id: str,
    repo: CompanyRepository = Depends(get_company_repo),
) -> ApiResponse:
    handlers = _get_handlers(repo)
    result = await handlers.get_company(GetCompanyQuery(company_id=company_id))
    return ApiResponse(data=CompanyResponse(**result.model_dump()))


@router.put("/{company_id}", response_model=ApiResponse)
async def update_company(
    company_id: UUID,
    body: CompanyUpdate,
    repo: CompanyRepository = Depends(get_company_repo),
) -> ApiResponse:
    handlers = _get_handlers(repo)
    cmd = UpdateCompanyCommand(company_id=company_id, **body.model_dump(exclude_unset=True))
    result = await handlers.update_company(cmd)
    return ApiResponse(data=CompanyResponse(**result.model_dump()))


@router.delete("/{company_id}", status_code=204)
async def delete_company(
    company_id: UUID,
    repo: CompanyRepository = Depends(get_company_repo),
) -> None:
    handlers = _get_handlers(repo)
    await handlers.delete_company(DeleteCompanyCommand(company_id=company_id))


def _entry_to_response(entry) -> SanctionsEntryResponse:
    return SanctionsEntryResponse(
        target_name=entry.target_name,
        sanction_type=entry.sanction_type.value,
        status=entry.status.value,
        list_name=entry.list_name,
        country_code=entry.country_code,
        reason=entry.reason,
        program=entry.program,
        metadata=entry.metadata,
    )


@router.post("/{company_id}/sanctions", response_model=SanctionsCheckResponse)
async def check_company_sanctions(
    company_id: str,
    repo: CompanyRepository = Depends(get_company_repo),
    provider: SDNProvider = Depends(get_sdn_provider),
) -> SanctionsCheckResponse:
    """Check if a company appears on any sanctions list.

    Performs a live SDN API search by company name.
    """
    from datetime import UTC, datetime

    handlers = _get_handlers(repo)
    company = await handlers.get_company(GetCompanyQuery(company_id=company_id))

    # Prefer an exact IDNO match (SDN indexes registration numbers/IDNOs) — this
    # avoids the fuzzy-name false positives that generic company names produce.
    # Fall back to name search only when the IDNO yields nothing.
    entries = await provider.search_by_idno(company.idno) if company.idno else []
    if not entries:
        entries = await provider.search_by_name(company.name_ro, limit=10)
    is_sanctioned = any(e.status.value == "active" for e in entries)

    return SanctionsCheckResponse(
        company_name=company.name_ro,
        is_sanctioned=is_sanctioned,
        matches=[_entry_to_response(e) for e in entries],
        checked_at=datetime.now(tz=UTC).isoformat(),
    )


@router.post("/{company_id}/tax-debt")
async def check_tax_debt(
    company_id: str,
    repo: CompanyRepository = Depends(get_company_repo),
) -> dict:
    """Check tax debt for a company from the Moldovan Tax Service (SFS).

    Launches a Playwright browser to bypass Cloudflare and fetch tax debt data.
    This is slow (~10-30s) and results are cached in the company record.
    """
    from credibil.workers.tasks import sync_tax_debt

    handlers = _get_handlers(repo)
    company = await handlers.get_company(GetCompanyQuery(company_id=company_id))

    # Dispatch async Celery task
    task = sync_tax_debt.delay(company.idno)

    return {
        "status": "queued",
        "task_id": task.id,
        "idno": company.idno,
        "message": "Tax debt check queued. Poll task status for results.",
    }
