from __future__ import annotations

import structlog

from credibil.application.search.commands import (
    AutocompleteCommandQuery,
    DeleteSearchCommand,
    SearchCommandQuery,
)
from credibil.application.search.service import SearchService
from credibil.domain.search.entities import SearchIndex

logger = structlog.get_logger()


class SearchHandlers:
    """Command/query handlers for search operations."""

    def __init__(self, search_service: SearchService) -> None:
        self._service = search_service

    async def handle_index_entity(
        self,
        index: SearchIndex,
        entity: object,
    ) -> None:
        await self._service.index_entity(index, entity)

    async def handle_index_entities(
        self,
        index: SearchIndex,
        entities: list[object],
    ) -> int:
        return await self._service.index_entities(index, entities)

    async def handle_delete_entity(self, index: SearchIndex, document_id: str) -> None:
        await self._service.delete_entity(index, document_id)

    async def handle_delete_entities(self, command: DeleteSearchCommand) -> int:
        return await self._service.delete_entities(command)

    async def handle_search(self, query: SearchCommandQuery):
        return await self._service.search(query)

    async def handle_autocomplete(self, query: AutocompleteCommandQuery):
        return await self._service.autocomplete(query)

    async def handle_reindex(self, index: SearchIndex) -> None:
        await self._service.reindex(index)

    async def handle_get_index_count(self, index: SearchIndex) -> int:
        return await self._service.get_index_count(index)

    async def handle_health_check(self) -> bool:
        return await self._service.health_check()
