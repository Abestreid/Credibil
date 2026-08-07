from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from credibil.core.database import get_session
from credibil.infrastructure.database.repositories.tender import (
    SQLAlchemyTenderAwardRepository,
    SQLAlchemyTenderBidRepository,
    SQLAlchemyTenderRepository,
)
from credibil.ports.repositories.tender import (
    TenderAwardRepository,
    TenderBidRepository,
    TenderRepository,
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with get_session() as session:
        yield session


async def get_tender_repo(
    session: AsyncSession = Depends(get_db_session),
) -> AsyncGenerator[TenderRepository, None]:
    yield SQLAlchemyTenderRepository(session)


async def get_tender_award_repo(
    session: AsyncSession = Depends(get_db_session),
) -> AsyncGenerator[TenderAwardRepository, None]:
    yield SQLAlchemyTenderAwardRepository(session)


async def get_tender_bid_repo(
    session: AsyncSession = Depends(get_db_session),
) -> AsyncGenerator[TenderBidRepository, None]:
    yield SQLAlchemyTenderBidRepository(session)
