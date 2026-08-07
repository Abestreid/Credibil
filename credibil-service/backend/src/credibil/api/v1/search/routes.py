from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query

from credibil.api.v1.search.dependencies import get_search_service
from credibil.api.v1.search.schemas import (
    AutocompleteResponseSchema,
    AutocompleteSuggestionItem,
    HealthResponse,
    IndexCountResponse,
    ReindexRequest,
    SearchPaginationMeta,
    SearchResponseSchema,
    SearchResultItem,
)
from credibil.application.search.commands import (
    AutocompleteCommandQuery,
    SearchCommandQuery,
)
from credibil.application.search.service import SearchService
from credibil.domain.search.entities import SearchIndex

router = APIRouter(prefix="/search", tags=["search"])


def _parse_index(index_str: str | None) -> SearchIndex | None:
    if index_str is None:
        return None
    try:
        return SearchIndex(index_str)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid index: {index_str}. Must be one of: {[i.value for i in SearchIndex]}",
        )


def _to_response(result) -> SearchResponseSchema:
    return SearchResponseSchema(
        hits=[
            SearchResultItem(
                id=h.id,
                entity_type=h.entity_type,
                data=h.data,
                highlights=h.highlights,
                match_type=h.match_type.value if h.match_type else None,
                matched_field=h.matched_field,
                match_reason=h.match_reason,
            )
            for h in result.hits
        ],
        meta=SearchPaginationMeta(
            page=result.page,
            page_size=result.page_size,
            total_hits=result.total_hits,
            total_pages=result.total_pages,
            has_next=result.page < result.total_pages,
            has_prev=result.page > 1,
        ),
        processing_time_ms=result.processing_time_ms,
        query=result.query,
    )


@router.get("", response_model=SearchResponseSchema)
async def search(
    q: str = Query(..., min_length=1, max_length=200),
    index: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search_service: SearchService = Depends(get_search_service),
):
    parsed_index = _parse_index(index)
    offset = (page - 1) * page_size
    query = SearchCommandQuery(
        q=q,
        index=parsed_index,
        limit=page_size,
        offset=offset,
    )
    result = await search_service.search(query)
    return _to_response(result)


@router.get("/companies", response_model=SearchResponseSchema)
async def search_companies(
    q: str = Query(..., min_length=1, max_length=200),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search_service: SearchService = Depends(get_search_service),
):
    offset = (page - 1) * page_size
    query = SearchCommandQuery(q=q, index=SearchIndex.COMPANIES, limit=page_size, offset=offset)
    result = await search_service.search(query)
    return _to_response(result)


@router.get("/persons", response_model=SearchResponseSchema)
async def search_persons(
    q: str = Query(..., min_length=1, max_length=200),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search_service: SearchService = Depends(get_search_service),
):
    offset = (page - 1) * page_size
    query = SearchCommandQuery(q=q, index=SearchIndex.PERSONS, limit=page_size, offset=offset)
    result = await search_service.search(query)
    return _to_response(result)


@router.get("/autocomplete", response_model=AutocompleteResponseSchema)
async def autocomplete(
    q: str = Query(..., min_length=2, max_length=100),
    index: str | None = Query(None),
    limit: int = Query(8, ge=1, le=20),
    search_service: SearchService = Depends(get_search_service),
):
    parsed_index = _parse_index(index)
    query = AutocompleteCommandQuery(q=q, index=parsed_index, limit=limit)
    result = await search_service.autocomplete(query)
    return AutocompleteResponseSchema(
        suggestions=[
            AutocompleteSuggestionItem(
                id=s.id,
                entity_type=s.entity_type,
                data=s.data,
                match_type=s.match_type.value if s.match_type else None,
                match_reason=s.match_reason,
            )
            for s in result.suggestions
        ],
        processing_time_ms=result.processing_time_ms,
    )


@router.get("/index/{index_name}", response_model=IndexCountResponse)
async def get_index_count(
    index_name: str,
    search_service: SearchService = Depends(get_search_service),
):
    parsed = _parse_index(index_name)
    count = await search_service.get_index_count(parsed)
    return IndexCountResponse(index=index_name, count=count)


@router.post("/reindex", status_code=202)
async def reindex(
    body: ReindexRequest,
    search_service: SearchService = Depends(get_search_service),
):
    parsed = _parse_index(body.index)
    await search_service.reindex(parsed)

    from credibil.workers.tasks import search_reindex_all

    search_reindex_all.delay()

    return {"message": f"Index '{body.index}' cleared. Reindex dispatched."}


@router.get("/health", response_model=HealthResponse)
async def search_health(
    search_service: SearchService = Depends(get_search_service),
):
    healthy = await search_service.health_check()
    return HealthResponse(search_healthy=healthy)
