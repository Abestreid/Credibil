from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from credibil.core.database import get_session
from credibil.infrastructure.database.repositories.enforcement import (
    SQLAlchemyEnforcementRepository,
)
from credibil.ports.repositories.enforcement import EnforcementRepository


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with get_session() as session:
        yield session


async def get_enforcement_repo(
    session: AsyncSession = Depends(get_db_session),
) -> AsyncGenerator[EnforcementRepository, None]:
    yield SQLAlchemyEnforcementRepository(session)
