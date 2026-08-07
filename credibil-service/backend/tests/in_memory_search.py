from __future__ import annotations

import math
from typing import Any

from credibil.domain.search.entities import (
    AutocompleteQuery,
    AutocompleteResult,
    MatchType,
    SearchDocument,
    SearchIndex,
    SearchQuery,
    SearchResponse,
    SearchResult,
)
from credibil.ports.providers.search import SearchProvider


def _classify(q_lower: str, data: dict[str, Any]) -> tuple[MatchType, str | None]:
    idno = str(data.get("idno", "")).lower()
    name_ro = str(data.get("name_ro", "")).lower().strip()
    name_ru = str(data.get("name_ru", "")).lower().strip()
    full_name = str(data.get("full_name", "")).lower().strip()

    if q_lower == idno:
        return MatchType.EXACT_IDNO, "idno"

    for name, field in [(name_ro, "name_ro"), (name_ru, "name_ru"), (full_name, "full_name")]:
        if q_lower == name:
            return MatchType.EXACT_NAME, field
        if name.startswith(q_lower):
            return MatchType.PREFIX, field

    for name, field in [(name_ro, "name_ro"), (name_ru, "name_ru"), (full_name, "full_name")]:
        if q_lower in name:
            return MatchType.FUZZY, field

    return MatchType.UNKNOWN, None


class InMemorySearchProvider(SearchProvider):
    """In-memory search provider for testing."""

    def __init__(self) -> None:
        self._indexes: dict[SearchIndex, dict[str, dict[str, Any]]] = {}
        self._healthy = True

    def _get_index(self, index: SearchIndex) -> dict[str, dict[str, Any]]:
        if index not in self._indexes:
            self._indexes[index] = {}
        return self._indexes[index]

    async def search(self, query: SearchQuery) -> SearchResponse:
        index = self._get_index(query.index)
        q_lower = query.q.lower().strip()
        hits = []

        for doc_id, data in index.items():
            matched = False
            for value in data.values():
                if isinstance(value, str) and q_lower in value.lower():
                    matched = True
                    break
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, str) and q_lower in item.lower():
                            matched = True
                            break
                    if matched:
                        break

            if matched or q_lower == str(data.get("idno", "")).lower():
                match_type, matched_field = _classify(q_lower, data)
                entity_type = data.get("entity_type", "company")
                hits.append(
                    SearchResult(
                        id=doc_id,
                        entity_type=entity_type,
                        score=1.0 if match_type in (MatchType.EXACT_IDNO, MatchType.EXACT_NAME) else 0.8,
                        data=data,
                        match_type=match_type,
                        matched_field=matched_field,
                    )
                )

        hits.sort(key=lambda h: {
            MatchType.EXACT_IDNO: 100,
            MatchType.EXACT_NAME: 90,
            MatchType.NORMALIZED_NAME: 80,
            MatchType.PREFIX: 70,
            MatchType.TRANSLITERATION: 60,
            MatchType.FUZZY: 50,
            MatchType.UNKNOWN: 0,
        }.get(h.match_type, 0), reverse=True)

        total = len(hits)
        page_size = query.limit
        page_hits = hits[query.offset : query.offset + page_size]
        page = (query.offset // page_size) + 1 if page_size > 0 else 1
        total_pages = max(1, math.ceil(total / page_size)) if page_size > 0 else 1

        return SearchResponse(
            hits=page_hits,
            total_hits=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            processing_time_ms=0,
            query=query.q,
        )

    async def autocomplete(self, query: AutocompleteQuery) -> AutocompleteResult:
        index = self._get_index(query.index)
        suggestions = []
        q_lower = query.q.lower()

        for doc_id, data in index.items():
            for field in ["name_ro", "name_ru", "full_name"]:
                value = data.get(field, "")
                if isinstance(value, str) and value.lower().startswith(q_lower):
                    entity_type = data.get("entity_type", "company")
                    suggestions.append(
                        SearchResult(id=doc_id, entity_type=entity_type, data=data)
                    )
                    break

        suggestions = suggestions[: query.limit]
        return AutocompleteResult(
            suggestions=suggestions,
            processing_time_ms=0,
        )

    async def index_documents(
        self,
        index: SearchIndex,
        documents: list[SearchDocument],
    ) -> int:
        store = self._get_index(index)
        for doc in documents:
            store[doc.id] = doc.data
        return len(documents)

    async def delete_documents(
        self,
        index: SearchIndex,
        document_ids: list[str],
    ) -> int:
        store = self._get_index(index)
        count = 0
        for doc_id in document_ids:
            if doc_id in store:
                del store[doc_id]
                count += 1
        return count

    async def delete_all_documents(self, index: SearchIndex) -> int:
        store = self._get_index(index)
        count = len(store)
        store.clear()
        return count

    async def get_document_count(self, index: SearchIndex) -> int:
        return len(self._get_index(index))

    async def health_check(self) -> bool:
        return self._healthy
