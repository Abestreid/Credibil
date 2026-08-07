from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends

from credibil.api.admin.schemas import AdminApiResponse
from credibil.api.auth.dependencies import require_admin

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users", response_model=AdminApiResponse)
async def list_users(
    page: int = 1,
    per_page: int = 25,
    current_user: dict[str, Any] = Depends(require_admin),
) -> AdminApiResponse:
    # Placeholder - will be implemented with actual repository calls
    return AdminApiResponse(data={"items": [], "total": 0})


@router.get("/organizations", response_model=AdminApiResponse)
async def list_organizations(
    page: int = 1,
    per_page: int = 25,
    current_user: dict[str, Any] = Depends(require_admin),
) -> AdminApiResponse:
    return AdminApiResponse(data={"items": [], "total": 0})


@router.get("/subscriptions", response_model=AdminApiResponse)
async def list_subscriptions(
    page: int = 1,
    per_page: int = 25,
    current_user: dict[str, Any] = Depends(require_admin),
) -> AdminApiResponse:
    return AdminApiResponse(data={"items": [], "total": 0})


@router.get("/audit-logs", response_model=AdminApiResponse)
async def list_audit_logs(
    page: int = 1,
    per_page: int = 25,
    current_user: dict[str, Any] = Depends(require_admin),
) -> AdminApiResponse:
    return AdminApiResponse(data={"items": [], "total": 0})


@router.get("/system/health", response_model=AdminApiResponse)
async def system_health(
    current_user: dict[str, Any] = Depends(require_admin),
) -> AdminApiResponse:
    return AdminApiResponse(data={"status": "healthy"})
