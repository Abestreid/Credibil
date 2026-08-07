from __future__ import annotations

from typing import Any

from credibil.domain.search.entities import (
    SearchIndex,
)


class SearchCommand:
    """Command to index documents into the search engine."""

    def __init__(
        self,
        *,
        index: SearchIndex,
        entity_ids: list[str] | None = None,
        reindex_all: bool = False,
    ) -> None:
        self.index = index
        self.entity_ids = entity_ids or []
        self.reindex_all = reindex_all


class DeleteSearchCommand:
    """Command to delete documents from the search engine."""

    def __init__(
        self,
        *,
        index: SearchIndex,
        document_ids: list[str],
    ) -> None:
        self.index = index
        self.document_ids = document_ids


class SearchCommandQuery:
    """Query to search documents in the search engine."""

    def __init__(
        self,
        *,
        q: str,
        index: SearchIndex | None = None,
        limit: int = 20,
        offset: int = 0,
        filter: dict[str, Any] | None = None,
        sort: list[str] | None = None,
    ) -> None:
        self.q = q
        self.index = index
        self.limit = limit
        self.offset = offset
        self.filter = filter or {}
        self.sort = sort or []


class AutocompleteCommandQuery:
    """Query to autocomplete a search term."""

    def __init__(
        self,
        *,
        q: str,
        index: SearchIndex | None = None,
        limit: int = 5,
    ) -> None:
        self.q = q
        self.index = index
        self.limit = limit
