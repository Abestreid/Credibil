from __future__ import annotations

import logging
import math
from typing import Any

import meilisearch_python_sdk as meilisearch

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

logger = logging.getLogger(__name__)

INDEX_SETTINGS: dict[SearchIndex, dict[str, Any]] = {
    SearchIndex.COMPANIES: {
        "searchableAttributes": [
            "name_ro",
            "name_ru",
            "caem_description",
            "legal_address",
        ],
        "filterableAttributes": [
            "idno",
            "status",
            "legal_form",
            "caem",
            "entity_type",
        ],
        "sortableAttributes": [
            "name_ro",
            "registration_date",
        ],
        "rankingRules": [
            "words",
            "typo",
            "proximity",
            "attribute",
            "sort",
            "exactness",
        ],
        "typoTolerance": {
            "enabled": True,
            "minWordSizeForTypos": {
                "oneTypo": 5,
                "twoTypos": 8,
            },
        },
        "pagination": {"maxTotalHits": 5000},
    },
    SearchIndex.PERSONS: {
        "searchableAttributes": [
            "full_name",
        ],
        "filterableAttributes": [
            "idnp",
            "person_type",
            "nationality",
            "relationship_types",
            "company_idnos",
            "entity_type",
        ],
        "sortableAttributes": [
            "full_name",
        ],
        "rankingRules": [
            "words",
            "typo",
            "proximity",
            "attribute",
            "sort",
            "exactness",
        ],
        "typoTolerance": {
            "enabled": True,
            "minWordSizeForTypos": {
                "oneTypo": 5,
                "twoTypos": 8,
            },
        },
        "pagination": {"maxTotalHits": 5000},
    },
}


def _classify_company_match(
    q_lower: str, data: dict[str, Any]
) -> tuple[MatchType, str | None, str | None]:
    """Classify how a search result matched the query for companies."""
    idno = str(data.get("idno", "")).strip()
    name_ro = str(data.get("name_ro", "")).strip()
    name_ru = str(data.get("name_ru", "")).strip()

    if q_lower == idno:
        return MatchType.EXACT_IDNO, "idno", f"Exact IDNO: {idno}"

    q_norm = q_lower.replace(" ", "").replace("-", "")
    idno_norm = idno.replace(" ", "").replace("-", "")
    if q_norm == idno_norm:
        return MatchType.EXACT_IDNO, "idno", f"Exact IDNO: {idno}"

    name_ro_lower = name_ro.lower()
    name_ru_lower = name_ru.lower()

    if q_lower == name_ro_lower:
        return MatchType.EXACT_NAME, "name_ro", "Exact company name"
    if q_lower == name_ru_lower:
        return MatchType.EXACT_NAME, "name_ru", "Exact company name"

    if name_ro_lower.startswith(q_lower):
        return MatchType.PREFIX, "name_ro", "Company name prefix"
    if name_ru_lower.startswith(q_lower):
        return MatchType.PREFIX, "name_ru", "Company name prefix"

    return MatchType.FUZZY, None, None


def _classify_person_match(
    q_lower: str, data: dict[str, Any]
) -> tuple[MatchType, str | None, str | None]:
    """Classify how a search result matched the query for persons."""
    full_name = str(data.get("full_name", "")).strip().lower()
    idnp = str(data.get("idnp", "")).strip()

    if q_lower == idnp:
        return MatchType.EXACT_IDNO, "idnp", f"Exact IDNP: {idnp}"

    if q_lower == full_name:
        return MatchType.PERSON_EXACT, "full_name", f"Person: {data.get('full_name', '')}"

    q_parts = set(q_lower.split())
    name_parts = set(full_name.split())
    if q_parts and q_parts.issubset(name_parts):
        return MatchType.PERSON_EXACT, "full_name", f"Person: {data.get('full_name', '')}"

    if full_name.startswith(q_lower):
        return MatchType.PERSON_PREFIX, "full_name", "Person name prefix"

    return MatchType.FUZZY, None, None


class MeilisearchProvider(SearchProvider):
    """Meilisearch adapter implementing the SearchProvider port."""

    def __init__(self, url: str = "http://localhost:7700", api_key: str | None = None) -> None:
        self._client = meilisearch.AsyncClient(url, api_key or "")
        self._initialized = False

    async def _ensure_indexes(self) -> None:
        if self._initialized:
            return
        from meilisearch_python_sdk.models.settings import MeilisearchSettings

        for index_enum, settings_dict in INDEX_SETTINGS.items():
            try:
                idx = self._client.index(index_enum.value)
                settings_model = MeilisearchSettings(**settings_dict)
                await idx.update_settings(settings_model)
            except Exception:
                try:
                    await self._client.create_index(index_enum.value, primary_key="id")
                    idx = self._client.index(index_enum.value)
                    settings_model = MeilisearchSettings(**settings_dict)
                    await idx.update_settings(settings_model)
                except Exception:
                    logger.warning("Failed to create/update Meilisearch index %s", index_enum.value)
                    continue
        self._initialized = True

    async def search(self, query: SearchQuery) -> SearchResponse:
        await self._ensure_indexes()
        idx = self._client.index(query.index.value)

        search_kwargs: dict[str, Any] = {
            "offset": query.offset,
            "limit": query.limit,
            "show_ranking_score": True,
        }
        if query.attributes_to_highlight:
            search_kwargs["attributes_to_highlight"] = query.attributes_to_highlight
        if query.matching_strategy:
            search_kwargs["matching_strategy"] = query.matching_strategy

        filter_parts = []
        for k, v in query.filter.items():
            if v is not None and v != "":
                filter_parts.append(f'{k} = "{v}"')
        if filter_parts:
            search_kwargs["filter"] = " AND ".join(filter_parts)

        if query.sort:
            search_kwargs["sort"] = query.sort

        raw = await idx.search(query.q, **search_kwargs)

        q_lower = query.q.lower().strip()
        is_person_index = query.index == SearchIndex.PERSONS

        hits = []
        for hit in raw.hits:
            if isinstance(hit, dict):
                hit_dict = hit
            else:
                hit_dict = hit.model_dump() if hasattr(hit, "model_dump") else vars(hit)

            filtered = {k: v for k, v in hit_dict.items() if not k.startswith("_")}

            if is_person_index:
                match_type, matched_field, match_reason = _classify_person_match(q_lower, filtered)
                entity_type = "person"
            else:
                match_type, matched_field, match_reason = _classify_company_match(q_lower, filtered)
                entity_type = "company"

            highlights = {}
            if isinstance(hit, dict):
                formatted = hit.get("_formatted")
            else:
                formatted = getattr(hit, "_formatted", None)
            if isinstance(formatted, dict):
                for key, val in formatted.items():
                    if key != "id":
                        highlights[key] = val

            hits.append(
                SearchResult(
                    id=str(hit_dict.get("id", "")),
                    entity_type=entity_type,
                    data=filtered,
                    highlights=highlights,
                    match_type=match_type,
                    matched_field=matched_field,
                    match_reason=match_reason,
                    score=hit_dict.get("_rankingScore"),
                )
            )

        total = raw.estimated_total_hits or 0
        page_size = query.limit
        page = (query.offset // page_size) + 1 if page_size > 0 else 1
        total_pages = math.ceil(total / page_size) if page_size > 0 else 1

        return SearchResponse(
            hits=hits,
            total_hits=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            processing_time_ms=raw.processing_time_ms or 0,
            query=raw.query or query.q,
        )

    async def autocomplete(self, query: AutocompleteQuery) -> AutocompleteResult:
        await self._ensure_indexes()
        idx = self._client.index(query.index.value)

        raw = await idx.search(
            query.q,
            limit=query.limit,
            attributes_to_highlight=["name_ro", "full_name"],
            matching_strategy="last",
            show_ranking_score=True,
        )

        q_lower = query.q.lower().strip()
        is_person_index = query.index == SearchIndex.PERSONS

        suggestions = []
        for hit in raw.hits:
            if isinstance(hit, dict):
                hit_dict = hit
            else:
                hit_dict = hit.model_dump() if hasattr(hit, "model_dump") else vars(hit)

            filtered = {k: v for k, v in hit_dict.items() if not k.startswith("_")}

            if is_person_index:
                match_type, matched_field, match_reason = _classify_person_match(q_lower, filtered)
                entity_type = "person"
            else:
                match_type, matched_field, match_reason = _classify_company_match(q_lower, filtered)
                entity_type = "company"

            suggestions.append(
                SearchResult(
                    id=str(hit_dict.get("id", "")),
                    entity_type=entity_type,
                    data=filtered,
                    match_type=match_type,
                    matched_field=matched_field,
                    match_reason=match_reason,
                )
            )

        return AutocompleteResult(
            suggestions=suggestions,
            processing_time_ms=raw.processing_time_ms or 0,
        )

    async def index_documents(self, index: SearchIndex, documents: list[SearchDocument]) -> int:
        await self._ensure_indexes()
        if not documents:
            return 0
        idx = self._client.index(index.value)
        payload = [doc.to_dict() for doc in documents]
        await idx.add_documents(payload)
        return len(documents)

    async def delete_documents(self, index: SearchIndex, document_ids: list[str]) -> int:
        await self._ensure_indexes()
        if not document_ids:
            return 0
        idx = self._client.index(index.value)
        await idx.delete_documents(document_ids)
        return len(document_ids)

    async def delete_all_documents(self, index: SearchIndex) -> int:
        await self._ensure_indexes()
        idx = self._client.index(index.value)
        stats = await idx.get_stats()
        count = stats.number_of_documents
        await idx.delete_all_documents()
        return count

    async def get_document_count(self, index: SearchIndex) -> int:
        await self._ensure_indexes()
        idx = self._client.index(index.value)
        stats = await idx.get_stats()
        return stats.number_of_documents

    async def health_check(self) -> bool:
        try:
            await self._client.health()
            return True
        except Exception:
            return False
