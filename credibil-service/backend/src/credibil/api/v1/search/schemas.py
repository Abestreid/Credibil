from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class SearchResultItem(BaseModel):
    id: str
    entity_type: str = "company"
    data: dict[str, Any] = {}
    highlights: dict[str, str] = {}
    match_type: str | None = None
    matched_field: str | None = None
    match_reason: str | None = None


class SearchPaginationMeta(BaseModel):
    page: int
    page_size: int
    total_hits: int
    total_pages: int
    has_next: bool
    has_prev: bool


class SearchResponseSchema(BaseModel):
    hits: list[SearchResultItem]
    meta: SearchPaginationMeta
    processing_time_ms: int
    query: str


class AutocompleteSuggestionItem(BaseModel):
    id: str
    entity_type: str = "company"
    data: dict[str, Any] = {}
    match_type: str | None = None
    match_reason: str | None = None


class AutocompleteResponseSchema(BaseModel):
    suggestions: list[AutocompleteSuggestionItem]
    processing_time_ms: int


class IndexCountResponse(BaseModel):
    index: str
    count: int


class ReindexRequest(BaseModel):
    index: str = Field(..., description="Index to reindex")


class HealthResponse(BaseModel):
    search_healthy: bool
