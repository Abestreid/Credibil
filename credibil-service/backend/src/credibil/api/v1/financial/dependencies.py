from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from credibil.core.database import get_session
from credibil.infrastructure.database.repositories.financial_report import (
    SQLAlchemyFinancialReportRepository,
)
from credibil.infrastructure.database.repositories.sync_history import (
    SQLAlchemySyncHistoryRepository,
)
from credibil.ports.repositories.financial_report import FinancialReportRepository
from credibil.ports.repositories.sync_history import SyncHistoryRepository


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with get_session() as session:
        yield session


async def get_financial_repo(
    session: AsyncSession = Depends(get_db_session),
) -> AsyncGenerator[FinancialReportRepository, None]:
    yield SQLAlchemyFinancialReportRepository(session)


async def get_sync_repo(
    session: AsyncSession = Depends(get_db_session),
) -> AsyncGenerator[SyncHistoryRepository, None]:
    yield SQLAlchemySyncHistoryRepository(session)
