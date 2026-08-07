from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from credibil.core.database import get_session
from credibil.infrastructure.database.repositories.accreditation import (
    SQLAlchemyAccreditationRepository,
)
from credibil.infrastructure.database.repositories.sync_history import (
    SQLAlchemySyncHistoryRepository,
)
from credibil.ports.repositories.accreditation import AccreditationRepository
from credibil.ports.repositories.sync_history import SyncHistoryRepository


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with get_session() as session:
        yield session


async def get_accreditation_repo(
    session: AsyncSession = Depends(get_db_session),
) -> AsyncGenerator[AccreditationRepository, None]:
    yield SQLAlchemyAccreditationRepository(session)


async def get_sync_repo(
    session: AsyncSession = Depends(get_db_session),
) -> AsyncGenerator[SyncHistoryRepository, None]:
    yield SQLAlchemySyncHistoryRepository(session)


async def get_orchestrator(
    session: AsyncSession = Depends(get_db_session),
):
    from credibil.countries.moldova.providers.moldac_provider import MOLDACProvider
    from credibil.countries.moldova.sync.moldac_orchestrator import MoldacSyncOrchestrator

    provider = MOLDACProvider()
    accreditation_repo = SQLAlchemyAccreditationRepository(session)
    sync_repo = SQLAlchemySyncHistoryRepository(session)
    yield MoldacSyncOrchestrator(
        provider=provider,
        accreditation_repo=accreditation_repo,
        sync_repo=sync_repo,
    )
