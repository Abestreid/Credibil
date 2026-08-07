from __future__ import annotations

from collections.abc import AsyncGenerator
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from credibil.api.apikey.schemas import (
    VALID_SCOPES,
    ApiKeyApiResponse,
    CreateKeyRequest,
    IssuedKeyResponse,
    KeyListItem,
)
from credibil.api.auth.dependencies import get_current_user
from credibil.core.database import get_session
from credibil.domain.apikey.entities import APIKey
from credibil.infrastructure.database.models_organization import APIKeyModel
from credibil.infrastructure.database.repositories.apikey import SQLAlchemyAPIKeyRepository
from credibil.infrastructure.database.repositories.user import SQLAlchemyUserRepository

router = APIRouter(prefix="/api-keys", tags=["api-keys"])


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with get_session() as session:
        yield session


async def _resolve_tenant(session: AsyncSession, current_user: dict) -> UUID:
    sub = current_user.get("sub")
    if not sub:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user_id = UUID(str(sub))
    user = await SQLAlchemyUserRepository(session).find_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unknown user")
    return getattr(user, "tenant_id", None) or user_id


@router.post("", response_model=ApiKeyApiResponse, status_code=status.HTTP_201_CREATED)
async def create_key(
    body: CreateKeyRequest,
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> ApiKeyApiResponse:
    invalid = [s for s in body.scopes if s not in VALID_SCOPES]
    if invalid:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid scope(s): {', '.join(invalid)}. Allowed: {', '.join(VALID_SCOPES)}",
        )

    tenant_id = await _resolve_tenant(session, current_user)
    raw_key, prefix, key_hash = APIKey.generate_key()
    key = APIKey(
        tenant_id=tenant_id,
        name=body.name,
        key_prefix=prefix,
        key_hash=key_hash,
        scopes=body.scopes,
        rate_limit=body.rate_limit,
        expires_at=body.expires_at,
    )
    saved = await SQLAlchemyAPIKeyRepository(session).save(key)

    return ApiKeyApiResponse(
        data=IssuedKeyResponse(
            id=str(saved.id),
            name=saved.name,
            api_key=raw_key,  # shown exactly once
            key_prefix=saved.key_prefix,
            scopes=saved.scopes,
            rate_limit=saved.rate_limit,
            expires_at=saved.expires_at,
        )
    )


@router.get("", response_model=ApiKeyApiResponse)
async def list_keys(
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> ApiKeyApiResponse:
    tenant_id = await _resolve_tenant(session, current_user)
    keys, _total = await SQLAlchemyAPIKeyRepository(session).list_by_tenant(tenant_id)
    return ApiKeyApiResponse(
        data=[
            KeyListItem(
                id=str(k.id),
                name=k.name,
                key_prefix=k.key_prefix,
                scopes=k.scopes,
                rate_limit=k.rate_limit,
                status=k.status.value if hasattr(k.status, "value") else k.status,
                last_used_at=k.last_used_at,
                created_at=k.created_at,
            )
            for k in keys
        ]
    )


@router.post("/{key_id}/revoke", response_model=ApiKeyApiResponse)
async def revoke_key(
    key_id: UUID,
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> ApiKeyApiResponse:
    tenant_id = await _resolve_tenant(session, current_user)
    result = await session.execute(
        update(APIKeyModel)
        .where(APIKeyModel.id == key_id, APIKeyModel.tenant_id == tenant_id)
        .values(status="revoked", updated_at=datetime.utcnow())
    )
    if (result.rowcount or 0) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="API key not found")
    return ApiKeyApiResponse(data={"id": str(key_id), "revoked": True})
