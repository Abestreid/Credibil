from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from credibil.core.database import get_session
from credibil.infrastructure.database.repositories.court_case import (
    SQLAlchemyCourtCaseRepository,
    SQLAlchemyCourtHearingRepository,
)
from credibil.ports.repositories.court_case import CourtCaseRepository, CourtHearingRepository


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with get_session() as session:
        yield session


async def get_court_case_repo(
    session: AsyncSession = Depends(get_db_session),
) -> AsyncGenerator[CourtCaseRepository, None]:
    yield SQLAlchemyCourtCaseRepository(session)


async def get_court_hearing_repo(
    session: AsyncSession = Depends(get_db_session),
) -> AsyncGenerator[CourtHearingRepository, None]:
    yield SQLAlchemyCourtHearingRepository(session)
