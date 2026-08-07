from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from credibil.domain.search.entities import (
        AutocompleteQuery,
        AutocompleteResult,
        SearchDocument,
        SearchIndex,
        SearchQuery,
        SearchResponse,
    )


class SearchProvider(ABC):
    """Abstract search provider interface.

    Meilisearch is the default implementation. Can be swapped for
    Elasticsearch, OpenSearch, or PostgreSQL FTS without changing
    business logic.
    """

    @abstractmethod
    async def search(self, query: SearchQuery) -> SearchResponse:
        """Execute a search query and return results."""
        ...

    @abstractmethod
    async def autocomplete(self, query: AutocompleteQuery) -> AutocompleteResult:
        """Execute an autocomplete query and return suggestions."""
        ...

    @abstractmethod
    async def index_documents(
        self,
        index: SearchIndex,
        documents: list[SearchDocument],
    ) -> int:
        """Index documents into the given index. Returns count indexed."""
        ...

    @abstractmethod
    async def delete_documents(
        self,
        index: SearchIndex,
        document_ids: list[str],
    ) -> int:
        """Delete documents by ID from the given index. Returns count deleted."""
        ...

    @abstractmethod
    async def delete_all_documents(self, index: SearchIndex) -> int:
        """Delete all documents from the given index. Returns count deleted."""
        ...

    @abstractmethod
    async def get_document_count(self, index: SearchIndex) -> int:
        """Return the number of documents in the given index."""
        ...

    @abstractmethod
    async def health_check(self) -> bool:
        """Return True if the search engine is reachable and healthy."""
        ...
