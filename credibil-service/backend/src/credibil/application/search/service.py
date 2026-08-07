from __future__ import annotations

import re
import time
import unicodedata
from typing import TYPE_CHECKING

import structlog

from credibil.application.search.commands import (
    AutocompleteCommandQuery,
    DeleteSearchCommand,
    SearchCommandQuery,
)
from credibil.domain.search.entities import (
    AutocompleteQuery,
    AutocompleteResult,
    MatchType,
    SearchIndex,
    SearchQuery,
    SearchResponse,
    SearchResult,
)
from credibil.infrastructure.search.mappers import get_mapper
from credibil.ports.providers.search import SearchProvider

if TYPE_CHECKING:
    from credibil.ports.repositories.company import CompanyRepository

logger = structlog.get_logger()

_IDNO_RE = re.compile(r"^\d{8,13}$")

_CYRILLIC_TO_LATIN: dict[str, str] = {
    "а": "a",
    "б": "b",
    "в": "v",
    "г": "g",
    "д": "d",
    "е": "e",
    "ё": "yo",
    "ж": "zh",
    "з": "z",
    "и": "i",
    "й": "y",
    "к": "k",
    "л": "l",
    "м": "m",
    "н": "n",
    "о": "o",
    "п": "p",
    "р": "r",
    "с": "s",
    "т": "t",
    "у": "u",
    "ф": "f",
    "х": "kh",
    "ц": "ts",
    "ч": "ch",
    "ш": "sh",
    "щ": "shch",
    "ъ": "",
    "ы": "y",
    "ь": "",
    "э": "e",
    "ю": "yu",
    "я": "ya",
}

_DIAGRITICAL_MAP: dict[str, str] = {
    "ș": "s",
    "ț": "t",
    "ă": "a",
    "â": "a",
    "î": "i",
    "Ș": "S",
    "Ț": "T",
    "Ă": "A",
    "Â": "A",
    "Î": "I",
}


def _is_idno_query(q: str) -> bool:
    stripped = q.strip().replace(" ", "").replace("-", "")
    return bool(_IDNO_RE.match(stripped))


def _normalize_idno(q: str) -> str:
    return q.strip().replace(" ", "").replace("-", "")


def _normalize_name(name: str) -> str:
    if not name:
        return ""
    n = name.lower().strip()
    n = re.sub(r"\s+", " ", n)
    n = unicodedata.normalize("NFKD", n)
    n = "".join(c for c in n if not unicodedata.combining(c))
    return n


def _transliterate_cyrillic(text: str) -> str:
    if not text:
        return ""
    return "".join(_CYRILLIC_TO_LATIN.get(c, c) for c in text.lower())


def _diacritics_insensitive(text: str) -> str:
    """Normalize diacritics (ș→s, ț→t, etc.) for comparison."""
    if not text:
        return ""
    result = text.lower()
    for diag, plain in _DIAGRITICAL_MAP.items():
        result = result.replace(diag, plain)
    result = unicodedata.normalize("NFKD", result)
    result = "".join(c for c in result if not unicodedata.combining(c))
    return result.strip()


class SearchService:
    """Orchestrates search with two-stage strategy:

    Stage 1: Strict search (exact + high-confidence matches)
    Stage 2: Broader search (only if Stage 1 has few results)

    Supports cross-index search (companies + persons).
    """

    def __init__(
        self,
        search_provider: SearchProvider,
        company_repo: CompanyRepository | None = None,
    ) -> None:
        self._provider = search_provider
        self._company_repo = company_repo

    async def index_entity(self, index: SearchIndex, entity: object) -> None:
        mapper = get_mapper(index)
        doc = mapper.to_document(entity)
        await self._provider.index_documents(index, [doc])

    async def index_entities(self, index: SearchIndex, entities: list[object]) -> int:
        mapper = get_mapper(index)
        docs = mapper.to_documents(entities)
        return await self._provider.index_documents(index, docs)

    async def delete_entity(self, index: SearchIndex, document_id: str) -> None:
        await self._provider.delete_documents(index, [document_id])

    async def delete_entities(self, command: DeleteSearchCommand) -> int:
        return await self._provider.delete_documents(command.index, command.document_ids)

    async def search(self, query: SearchCommandQuery) -> SearchResponse:
        """Execute search with two-stage strategy.

        If no index specified, searches both companies and persons.
        """
        q = query.q.strip()
        start = time.monotonic()

        if not q:
            return SearchResponse(
                hits=[],
                total_hits=0,
                page=1,
                page_size=query.limit,
                total_pages=0,
                processing_time_ms=0,
                query=q,
            )

        if _is_idno_query(q):
            return await self._search_idno(q, query, start)

        if query.index:
            response = await self._search_single_index(q, query, query.index)
        else:
            response = await self._search_cross_index(q, query)

        elapsed_ms = int((time.monotonic() - start) * 1000)
        response.processing_time_ms = elapsed_ms
        return response

    async def _search_idno(self, q: str, query: SearchCommandQuery, start: float) -> SearchResponse:
        """IDNO: exact PostgreSQL lookup first, then Meilisearch filter."""
        normalized = _normalize_idno(q)

        if self._company_repo is not None:
            company = await self._company_repo.find_by_idno(normalized)
            if company:
                elapsed_ms = int((time.monotonic() - start) * 1000)
                return SearchResponse(
                    hits=[
                        SearchResult(
                            id=str(company.id),
                            entity_type="company",
                            data={
                                "id": str(company.id),
                                "idno": company.idno,
                                "name_ro": company.name_ro or "",
                                "name_ru": company.name_ru or "",
                                "status": company.status.value if company.status else "",
                                "legal_form": company.legal_form.value
                                if company.legal_form
                                else "",
                                "legal_address": company.legal_address or "",
                                "caem": company.caem or "",
                                "caem_description": company.caem_description or "",
                                "registration_date": (
                                    company.registration_date.isoformat()
                                    if company.registration_date
                                    else None
                                ),
                            },
                            match_type=MatchType.EXACT_IDNO,
                            matched_field="idno",
                            match_reason=f"Exact IDNO: {normalized}",
                        )
                    ],
                    total_hits=1,
                    page=1,
                    page_size=1,
                    total_pages=1,
                    processing_time_ms=elapsed_ms,
                    query=q,
                )

        meili_query = SearchQuery(
            q=q,
            index=SearchIndex.COMPANIES,
            limit=query.limit,
            offset=query.offset,
            filter={"idno": normalized},
        )
        response = await self._provider.search(meili_query)
        elapsed_ms = int((time.monotonic() - start) * 1000)
        response.processing_time_ms = elapsed_ms
        return response

    async def _search_single_index(
        self, q: str, query: SearchCommandQuery, index: SearchIndex
    ) -> SearchResponse:
        """Search a single index with matchingStrategy='all' for precision."""
        meili_query = SearchQuery(
            q=q,
            index=index,
            limit=query.limit,
            offset=query.offset,
            filter=query.filter,
            sort=query.sort,
            matching_strategy="all",
        )
        return await self._provider.search(meili_query)

    async def _search_cross_index(self, q: str, query: SearchCommandQuery) -> SearchResponse:
        """Search both indexes and merge results.

        Stage 1: Search both indexes with strict matching.
        Stage 2: If few strict results, do broader search.
        """
        company_results = await self._search_single_index(q, query, SearchIndex.COMPANIES)
        person_results = await self._search_single_index(q, query, SearchIndex.PERSONS)

        all_hits = company_results.hits + person_results.hits

        all_hits.sort(
            key=lambda h: _MATCH_PRIORITY.get(h.match_type, 0),
            reverse=True,
        )

        total_hits = company_results.total_hits + person_results.total_hits
        total_time = company_results.processing_time_ms + person_results.processing_time_ms

        page_size = query.limit
        total_pages = max(1, -(-total_hits // page_size)) if page_size > 0 else 1
        page = (query.offset // page_size) + 1 if page_size > 0 else 1

        return SearchResponse(
            hits=all_hits[:page_size],
            total_hits=total_hits,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            processing_time_ms=total_time,
            query=q,
        )

    async def autocomplete(self, query: AutocompleteCommandQuery) -> AutocompleteResult:
        results: list = []
        total_time = 0

        indexes = [query.index] if query.index else [SearchIndex.COMPANIES, SearchIndex.PERSONS]
        remaining = query.limit

        for idx in indexes:
            if remaining <= 0:
                break
            ac_query = AutocompleteQuery(q=query.q, index=idx, limit=remaining)
            result = await self._provider.autocomplete(ac_query)
            results.extend(result.suggestions)
            total_time += result.processing_time_ms
            remaining -= len(result.suggestions)

        return AutocompleteResult(
            suggestions=results[: query.limit],
            processing_time_ms=total_time,
        )

    async def reindex(self, index: SearchIndex) -> None:
        await self._provider.delete_all_documents(index)
        logger.info("search.index_cleared", index=index.value)

    async def get_index_count(self, index: SearchIndex) -> int:
        return await self._provider.get_document_count(index)

    async def health_check(self) -> bool:
        return await self._provider.health_check()


_MATCH_PRIORITY: dict[MatchType, int] = {
    MatchType.EXACT_IDNO: 100,
    MatchType.EXACT_NAME: 95,
    MatchType.PERSON_EXACT: 90,
    MatchType.NORMALIZED_NAME: 85,
    MatchType.PERSON_PREFIX: 80,
    MatchType.PREFIX: 75,
    MatchType.TRANSLITERATION: 70,
    MatchType.PERSON_RELATED: 65,
    MatchType.FUZZY: 50,
    MatchType.UNKNOWN: 0,
}
