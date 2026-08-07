from __future__ import annotations

import contextlib
from collections.abc import AsyncGenerator
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader
from sqlalchemy import update

from credibil.core.database import get_session
from credibil.domain.apikey.entities import APIKey
from credibil.infrastructure.database.models_organization import APIKeyModel
from credibil.infrastructure.database.repositories.apikey import SQLAlchemyAPIKeyRepository

if TYPE_CHECKING:
    from collections.abc import Callable

    from sqlalchemy.ext.asyncio import AsyncSession

API_KEY_HEADER = "X-API-Key"
api_key_scheme = APIKeyHeader(name=API_KEY_HEADER, auto_error=False)


@dataclass
class APIKeyContext:
    key_id: UUID
    tenant_id: UUID
    name: str
    scopes: list[str] = field(default_factory=list)
    rate_limit: int = 1000

    def has_scope(self, scope: str) -> bool:
        return "*" in self.scopes or scope in self.scopes


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with get_session() as session:
        yield session


async def require_api_key(
    api_key: str | None = Security(api_key_scheme),
    session: AsyncSession = Depends(get_db_session),
) -> APIKeyContext:
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key. Send it in the 'X-API-Key' header.",
            headers={"WWW-Authenticate": API_KEY_HEADER},
        )

    repo = SQLAlchemyAPIKeyRepository(session)
    key = await repo.find_by_hash(APIKey.hash_key(api_key))
    if key is None or not key.is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid, revoked, or expired API key.",
            headers={"WWW-Authenticate": API_KEY_HEADER},
        )

    # Best-effort last-used stamp; never fail the request over it.
    with contextlib.suppress(Exception):
        await session.execute(
            update(APIKeyModel)
            .where(APIKeyModel.id == key.id)
            .values(last_used_at=datetime.utcnow())
        )

    return APIKeyContext(
        key_id=key.id,
        tenant_id=key.tenant_id,
        name=key.name,
        scopes=key.scopes,
        rate_limit=key.rate_limit,
    )


def require_scope(scope: str) -> Callable[[APIKeyContext], APIKeyContext]:
    """Dependency factory enforcing a scope on the authenticated key."""

    async def _dep(ctx: APIKeyContext = Depends(require_api_key)) -> APIKeyContext:
        if not ctx.has_scope(scope):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"API key is missing the required scope: '{scope}'.",
            )
        return ctx

    return _dep
