from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

from credibil.application.search.service import SearchService
from credibil.infrastructure.search.meilisearch import MeilisearchProvider
from credibil.ports.providers.search import SearchProvider


def get_search_provider() -> SearchProvider:
    """Create a Meilisearch provider instance."""
    from credibil.config import get_settings

    settings = get_settings()
    return MeilisearchProvider(
        url=settings.meilisearch_url,
        api_key=settings.meilisearch_api_key,
    )


async def get_search_service() -> AsyncGenerator[SearchService, None]:
    """Dependency that provides a SearchService with company repo for IDNO lookups."""
    from credibil.core.database import get_session_factory
    from credibil.infrastructure.database.repositories.company import (
        SQLAlchemyCompanyRepository,
    )

    provider = get_search_provider()
    factory = get_session_factory()
    async with factory() as session:
        company_repo = SQLAlchemyCompanyRepository(session)
        yield SearchService(search_provider=provider, company_repo=company_repo)
