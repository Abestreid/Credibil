from collections.abc import AsyncGenerator
from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from credibil.api.auth.dependencies import get_current_user
from credibil.application.monitoring.engine import MonitoringEngine
from credibil.core.database import get_session
from credibil.infrastructure.database.repositories.company import SQLAlchemyCompanyRepository
from credibil.infrastructure.database.repositories.court_case import (
    SQLAlchemyCourtCaseRepository,
)
from credibil.infrastructure.database.repositories.enforcement import (
    SQLAlchemyEnforcementRepository,
)
from credibil.infrastructure.database.repositories.monitoring import (
    SQLAlchemyMonitoringRepository,
)
from credibil.infrastructure.database.repositories.relationship import (
    SQLAlchemyPersonRepository,
    SQLAlchemyRelationshipRepository,
)
from credibil.ports.repositories.company import CompanyRepository
from credibil.ports.repositories.monitoring import MonitoringRepository


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with get_session() as session:
        yield session


def current_user_id(current_user: dict = Depends(get_current_user)) -> UUID:
    sub = current_user.get("sub")
    if not sub:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    try:
        return UUID(str(sub))
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user id"
        ) from exc


async def get_monitoring_repo(
    session: AsyncSession = Depends(get_db_session),
) -> AsyncGenerator[MonitoringRepository, None]:
    yield SQLAlchemyMonitoringRepository(session)


async def get_company_repo(
    session: AsyncSession = Depends(get_db_session),
) -> AsyncGenerator[CompanyRepository, None]:
    yield SQLAlchemyCompanyRepository(session)


def build_engine(session: AsyncSession) -> MonitoringEngine:
    return MonitoringEngine(
        monitoring_repo=SQLAlchemyMonitoringRepository(session),
        company_repo=SQLAlchemyCompanyRepository(session),
        relationship_repo=SQLAlchemyRelationshipRepository(session),
        person_repo=SQLAlchemyPersonRepository(session),
        court_repo=SQLAlchemyCourtCaseRepository(session),
        enforcement_repo=SQLAlchemyEnforcementRepository(session),
    )


async def get_monitoring_engine(
    session: AsyncSession = Depends(get_db_session),
) -> AsyncGenerator[MonitoringEngine, None]:
    yield build_engine(session)
