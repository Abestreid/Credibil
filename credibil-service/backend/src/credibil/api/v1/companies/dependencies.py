from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from credibil.core.database import get_session
from credibil.infrastructure.database.repositories.company import SQLAlchemyCompanyRepository
from credibil.ports.repositories.company import CompanyRepository


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with get_session() as session:
        yield session


async def get_company_repo(
    session: AsyncSession = Depends(get_db_session),
) -> AsyncGenerator[CompanyRepository, None]:
    yield SQLAlchemyCompanyRepository(session)
