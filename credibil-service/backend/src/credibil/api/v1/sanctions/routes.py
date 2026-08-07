from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends

from credibil.api.v1.sanctions.dependencies import get_sdn_provider
from credibil.api.v1.sanctions.schemas import (
    SanctionsBatchRequest,
    SanctionsCheckResponse,
    SanctionsEntryResponse,
    SanctionsSearchRequest,
)

if TYPE_CHECKING:
    from credibil.infrastructure.sanctions.sdn_provider import SDNProvider

router = APIRouter(prefix="/sanctions", tags=["sanctions"])


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


@router.post("/search", response_model=list[SanctionsEntryResponse])
async def search_sanctions(
    body: SanctionsSearchRequest,
    provider: SDNProvider = Depends(get_sdn_provider),
):
    entries = await provider.search_by_name(body.name, limit=body.limit)
    return [_entry_to_response(e) for e in entries]


@router.post("/check", response_model=SanctionsCheckResponse)
async def check_company_sanctions(
    body: SanctionsSearchRequest,
    provider: SDNProvider = Depends(get_sdn_provider),
):
    entries = await provider.search_by_name(body.name, limit=body.limit)
    is_sanctioned = any(e.status.value == "active" for e in entries)
    return SanctionsCheckResponse(
        company_name=body.name,
        is_sanctioned=is_sanctioned,
        matches=[_entry_to_response(e) for e in entries],
        checked_at=datetime.now(tz=UTC).isoformat(),
    )


@router.post("/batch", response_model=list[SanctionsEntryResponse])
async def batch_search_sanctions(
    body: SanctionsBatchRequest,
    provider: SDNProvider = Depends(get_sdn_provider),
):
    entries = await provider.batch_search(body.names, only_sanctioned=body.only_sanctioned)
    return [_entry_to_response(e) for e in entries]


@router.get("/health")
async def sanctions_health(
    provider: SDNProvider = Depends(get_sdn_provider),
):
    healthy = await provider.health_check()
    return {"healthy": healthy}
