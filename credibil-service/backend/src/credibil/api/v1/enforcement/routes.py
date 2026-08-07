from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID  # noqa: TC003

from fastapi import APIRouter, Depends, Query

from credibil.api.v1.enforcement.dependencies import get_enforcement_repo
from credibil.api.v1.enforcement.schemas import (
    ApiResponse,
    EnforcementMeta,
    EnforcementProceedingResponse,
    EnforcementSummaryResponse,
    RefreshResponse,
)
from credibil.domain.enforcement.errors import EnforcementProceedingNotFoundError

if TYPE_CHECKING:
    from credibil.ports.repositories.enforcement import EnforcementRepository

router = APIRouter(prefix="/enforcement", tags=["enforcement"])

_IDNO = Query(..., min_length=13, max_length=13, pattern=r"^\d{13}$")


def _to_response(proceeding, idno: str | None = None) -> EnforcementProceedingResponse:
    resp = EnforcementProceedingResponse.model_validate(proceeding)
    if idno:
        role = proceeding.role_for_idno(idno)
        resp.role = role.value if role else None
    return resp


@router.get("/proceedings", response_model=ApiResponse)
async def list_proceedings_by_idno(
    idno: str = _IDNO,
    role: str | None = Query(default=None, pattern=r"^(debtor|creditor)$"),
    state: str | None = Query(default=None, pattern=r"^(active|archived)$"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    repo: EnforcementRepository = Depends(get_enforcement_repo),
) -> ApiResponse:
    """Enforcement proceedings matched to a company by fiscal code (IDNO).

    Filter by ``role`` (debtor/creditor) and ``state`` (active/archived).
    """
    items = await repo.find_by_idno(idno, role=role, state=state, limit=limit, offset=offset)
    total = await repo.count_by_idno(idno, role=role, state=state)
    return ApiResponse(
        data=[_to_response(p, idno) for p in items],
        meta=EnforcementMeta(
            total=total, limit=limit, offset=offset, idno=idno, role=role, state=state
        ),
    )


@router.get("/summary", response_model=ApiResponse)
async def get_summary(
    idno: str = _IDNO,
    repo: EnforcementRepository = Depends(get_enforcement_repo),
) -> ApiResponse:
    """Counts for the company card badges (active/archived, debtor/creditor)."""
    summary = EnforcementSummaryResponse(
        idno=idno,
        total=await repo.count_by_idno(idno),
        active=await repo.count_by_idno(idno, state="active"),
        archived=await repo.count_by_idno(idno, state="archived"),
        as_debtor=await repo.count_by_idno(idno, role="debtor"),
        as_creditor=await repo.count_by_idno(idno, role="creditor"),
    )
    return ApiResponse(data=summary)


@router.get("/proceedings/{proceeding_id}", response_model=ApiResponse)
async def get_proceeding(
    proceeding_id: UUID,
    repo: EnforcementRepository = Depends(get_enforcement_repo),
) -> ApiResponse:
    proceeding = await repo.find_by_id(proceeding_id)
    if proceeding is None:
        raise EnforcementProceedingNotFoundError(str(proceeding_id))
    return ApiResponse(data=_to_response(proceeding))


@router.post("/refresh", response_model=ApiResponse)
async def refresh_by_idno(idno: str = _IDNO) -> ApiResponse:
    """Trigger an on-demand unej.md lookup for one company (async)."""
    task_id: str | None = None
    try:
        from credibil.workers.tasks import sync_enforcement_by_idno

        result = sync_enforcement_by_idno.delay(idno)
        task_id = getattr(result, "id", None)
    except Exception:  # noqa: BLE001 — broker may be unavailable in some envs
        task_id = None
    return ApiResponse(data=RefreshResponse(idno=idno, task_id=task_id))
