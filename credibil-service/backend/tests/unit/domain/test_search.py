from __future__ import annotations

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


class TestSearchIndex:
    def test_all_indexes(self):
        assert SearchIndex.COMPANIES.value == "companies"
        assert SearchIndex.PERSONS.value == "persons"

    def test_index_count(self):
        assert len(SearchIndex) == 2


class TestSearchDocument:
    def test_create_document(self):
        doc = SearchDocument(
            id="1234567890123",
            index=SearchIndex.COMPANIES,
            data={"name_ro": "Test SRL", "idno": "1234567890123"},
        )
        assert doc.id == "1234567890123"
        assert doc.index == SearchIndex.COMPANIES
        assert doc.data["name_ro"] == "Test SRL"

    def test_to_dict(self):
        doc = SearchDocument(
            id="123",
            index=SearchIndex.COMPANIES,
            data={"name": "Test"},
        )
        result = doc.to_dict()
        assert result["id"] == "123"
        assert result["name"] == "Test"

    def test_repr(self):
        doc = SearchDocument(id="123", index=SearchIndex.COMPANIES, data={})
        assert "123" in repr(doc)
        assert "companies" in repr(doc)


class TestSearchQuery:
    def test_create_query(self):
        query = SearchQuery(q="test", index=SearchIndex.COMPANIES)
        assert query.q == "test"
        assert query.index == SearchIndex.COMPANIES
        assert query.limit == 20
        assert query.offset == 0
        assert query.filter == {}

    def test_query_with_options(self):
        query = SearchQuery(
            q="test",
            index=SearchIndex.PERSONS,
            limit=10,
            offset=5,
            filter={"nationality": "MD"},
        )
        assert query.limit == 10
        assert query.offset == 5
        assert query.filter == {"nationality": "MD"}


class TestAutocompleteQuery:
    def test_create_query(self):
        query = AutocompleteQuery(q="test", index=SearchIndex.COMPANIES)
        assert query.q == "test"
        assert query.limit == 5

    def test_query_with_limit(self):
        query = AutocompleteQuery(q="test", index=SearchIndex.PERSONS, limit=10)
        assert query.limit == 10


class TestSearchResult:
    def test_create_result(self):
        result = SearchResult(id="123", data={"name": "Test"})
        assert result.id == "123"
        assert result.entity_type == "company"
        assert result.data == {"name": "Test"}
        assert result.score is None
        assert result.highlights == {}

    def test_result_with_entity_type(self):
        result = SearchResult(id="123", entity_type="person", data={"full_name": "John"})
        assert result.entity_type == "person"

    def test_result_with_highlights(self):
        result = SearchResult(
            id="123",
            data={"name": "Test"},
            highlights={"name": "<em>Test</em>"},
        )
        assert result.highlights == {"name": "<em>Test</em>"}

    def test_result_with_match_reason(self):
        result = SearchResult(
            id="123",
            data={"name": "Test"},
            match_type=MatchType.EXACT_NAME,
            match_reason="Exact company name",
        )
        assert result.match_reason == "Exact company name"

    def test_repr(self):
        result = SearchResult(id="123", entity_type="company")
        assert "123" in repr(result)


class TestSearchResponse:
    def test_create_response(self):
        hits = [SearchResult(id="1", data={}), SearchResult(id="2", data={})]
        response = SearchResponse(
            hits=hits,
            total_hits=2,
            processing_time_ms=5,
            query="test",
        )
        assert len(response.hits) == 2
        assert response.total_hits == 2
        assert response.processing_time_ms == 5
        assert response.query == "test"
        assert response.page == 1
        assert response.page_size == 20
        assert response.total_pages == 1

    def test_create_response_with_pagination(self):
        response = SearchResponse(
            hits=[],
            total_hits=100,
            page=3,
            page_size=20,
            total_pages=5,
            processing_time_ms=0,
            query="test",
        )
        assert response.page == 3
        assert response.total_pages == 5

    def test_repr(self):
        response = SearchResponse(hits=[], total_hits=0, processing_time_ms=0, query="test")
        assert "0" in repr(response)


class TestAutocompleteResult:
    def test_create_result(self):
        result = AutocompleteResult(
            suggestions=[SearchResult(id="1", data={})],
            processing_time_ms=3,
        )
        assert len(result.suggestions) == 1
        assert result.processing_time_ms == 3

    def test_repr(self):
        result = AutocompleteResult(suggestions=[], processing_time_ms=0)
        assert "0" in repr(result)


class TestMatchType:
    def test_person_match_types(self):
        assert MatchType.PERSON_EXACT.value == "person_exact"
        assert MatchType.PERSON_PREFIX.value == "person_prefix"
        assert MatchType.PERSON_RELATED.value == "person_related"
