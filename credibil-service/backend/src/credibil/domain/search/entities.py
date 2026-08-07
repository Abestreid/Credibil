from __future__ import annotations

from enum import StrEnum
from typing import Any


class SearchIndex(StrEnum):
    COMPANIES = "companies"
    PERSONS = "persons"


class MatchType(StrEnum):
    EXACT_IDNO = "exact_idno"
    EXACT_NAME = "exact_name"
    NORMALIZED_NAME = "normalized_name"
    PREFIX = "prefix"
    TRANSLITERATION = "transliteration"
    PERSON_EXACT = "person_exact"
    PERSON_PREFIX = "person_prefix"
    PERSON_RELATED = "person_related"
    FUZZY = "fuzzy"
    UNKNOWN = "unknown"


class SearchDocument:
    def __init__(self, *, id: str, index: SearchIndex, data: dict[str, Any]) -> None:
        self.id = id
        self.index = index
        self.data = data

    def to_dict(self) -> dict[str, Any]:
        return {"id": self.id, **self.data}

    def __repr__(self) -> str:
        return f"<SearchDocument id={self.id!r} index={self.index.value!r}>"


class SearchQuery:
    def __init__(
        self,
        *,
        q: str,
        index: SearchIndex,
        limit: int = 20,
        offset: int = 0,
        filter: dict[str, Any] | None = None,
        sort: list[str] | None = None,
        attributes_to_highlight: list[str] | None = None,
        matching_strategy: str = "all",
    ) -> None:
        self.q = q
        self.index = index
        self.limit = limit
        self.offset = offset
        self.filter = filter or {}
        self.sort = sort or []
        self.attributes_to_highlight = attributes_to_highlight or []
        self.matching_strategy = matching_strategy


class AutocompleteQuery:
    def __init__(self, *, q: str, index: SearchIndex, limit: int = 5) -> None:
        self.q = q
        self.index = index
        self.limit = limit


class SearchResult:
    def __init__(
        self,
        *,
        id: str,
        entity_type: str = "company",
        score: float | None = None,
        data: dict[str, Any] | None = None,
        highlights: dict[str, str] | None = None,
        match_type: MatchType | None = None,
        matched_field: str | None = None,
        match_reason: str | None = None,
    ) -> None:
        self.id = id
        self.entity_type = entity_type
        self.score = score
        self.data = data or {}
        self.highlights = highlights or {}
        self.match_type = match_type or MatchType.UNKNOWN
        self.matched_field = matched_field
        self.match_reason = match_reason

    def __repr__(self) -> str:
        return f"<SearchResult id={self.id!r} type={self.entity_type!r}>"


class SearchResponse:
    def __init__(
        self,
        *,
        hits: list[SearchResult],
        total_hits: int,
        page: int = 1,
        page_size: int = 20,
        total_pages: int = 1,
        processing_time_ms: int,
        query: str,
    ) -> None:
        self.hits = hits
        self.total_hits = total_hits
        self.page = page
        self.page_size = page_size
        self.total_pages = total_pages
        self.processing_time_ms = processing_time_ms
        self.query = query

    def __repr__(self) -> str:
        return (
            f"<SearchResponse hits={len(self.hits)} "
            f"total={self.total_hits} time={self.processing_time_ms}ms>"
        )


class AutocompleteResult:
    def __init__(
        self,
        *,
        suggestions: list[SearchResult],
        processing_time_ms: int,
    ) -> None:
        self.suggestions = suggestions
        self.processing_time_ms = processing_time_ms

    def __repr__(self) -> str:
        return (
            f"<AutocompleteResult suggestions={len(self.suggestions)} "
            f"time={self.processing_time_ms}ms>"
        )
