from __future__ import annotations

import pytest
from tests.in_memory_search import InMemorySearchProvider

from credibil.application.search.commands import (
    AutocompleteCommandQuery,
    DeleteSearchCommand,
    SearchCommand,
    SearchCommandQuery,
)
from credibil.application.search.service import SearchService
from credibil.domain.search.entities import SearchIndex


@pytest.fixture
def search_provider():
    return InMemorySearchProvider()


@pytest.fixture
def search_service(search_provider):
    return SearchService(search_provider=search_provider)


class TestSearchCommand:
    def test_create_command(self):
        cmd = SearchCommand(index=SearchIndex.COMPANIES)
        assert cmd.index == SearchIndex.COMPANIES
        assert cmd.entity_ids == []
        assert cmd.reindex_all is False

    def test_command_with_ids(self):
        cmd = SearchCommand(
            index=SearchIndex.PERSONS,
            entity_ids=["1", "2"],
            reindex_all=True,
        )
        assert len(cmd.entity_ids) == 2
        assert cmd.reindex_all is True


class TestDeleteSearchCommand:
    def test_create_command(self):
        cmd = DeleteSearchCommand(index=SearchIndex.COMPANIES, document_ids=["1", "2"])
        assert cmd.index == SearchIndex.COMPANIES
        assert len(cmd.document_ids) == 2


class TestSearchCommandQuery:
    def test_create_query(self):
        query = SearchCommandQuery(q="test")
        assert query.q == "test"
        assert query.index is None
        assert query.limit == 20

    def test_query_with_options(self):
        query = SearchCommandQuery(
            q="test",
            index=SearchIndex.PERSONS,
            limit=10,
            filter={"nationality": "MD"},
        )
        assert query.index == SearchIndex.PERSONS
        assert query.filter == {"nationality": "MD"}


class TestSearchService:
    @pytest.mark.asyncio
    async def test_index_entity(self, search_service, search_provider):
        from credibil.domain.company.entities import Company

        company = Company(
            idno="1234567890123",
            name_ro="Test SRL",
            name_ru="Тест СРЛ",
        )
        await search_service.index_entity(SearchIndex.COMPANIES, company)

        count = await search_service.get_index_count(SearchIndex.COMPANIES)
        assert count == 1

    @pytest.mark.asyncio
    async def test_index_entities(self, search_service, search_provider):
        from credibil.domain.company.entities import Company

        companies = [
            Company(idno="1111111111111", name_ro="Alpha", name_ru="Альфа"),
            Company(idno="2222222222222", name_ro="Beta", name_ru="Бета"),
        ]
        count = await search_service.index_entities(SearchIndex.COMPANIES, companies)
        assert count == 2

    @pytest.mark.asyncio
    async def test_delete_entity(self, search_service, search_provider):
        from credibil.domain.company.entities import Company

        company = Company(idno="1234567890123", name_ro="Test", name_ru="Тест")
        await search_service.index_entity(SearchIndex.COMPANIES, company)

        await search_service.delete_entity(SearchIndex.COMPANIES, "1234567890123")
        count = await search_service.get_index_count(SearchIndex.COMPANIES)
        assert count == 0

    @pytest.mark.asyncio
    async def test_delete_entities(self, search_service, search_provider):
        from credibil.domain.company.entities import Company

        companies = [
            Company(idno="1111111111111", name_ro="A", name_ru="А"),
            Company(idno="2222222222222", name_ro="B", name_ru="Б"),
        ]
        await search_service.index_entities(SearchIndex.COMPANIES, companies)

        cmd = DeleteSearchCommand(
            index=SearchIndex.COMPANIES,
            document_ids=["1111111111111"],
        )
        deleted = await search_service.delete_entities(cmd)
        assert deleted == 1

    @pytest.mark.asyncio
    async def test_search(self, search_service):
        from credibil.domain.company.entities import Company

        companies = [
            Company(idno="1111111111111", name_ro="Alpha Corp", name_ru="Альфа"),
            Company(idno="2222222222222", name_ro="Beta Inc", name_ru="Бета"),
        ]
        await search_service.index_entities(SearchIndex.COMPANIES, companies)

        query = SearchCommandQuery(q="Alpha", index=SearchIndex.COMPANIES)
        result = await search_service.search(query)

        assert result.total_hits == 1
        assert result.hits[0].id == "1111111111111"

    @pytest.mark.asyncio
    async def test_autocomplete(self, search_service):
        from credibil.domain.company.entities import Company

        companies = [
            Company(idno="1111111111111", name_ro="Alpha Corp", name_ru="Альфа"),
            Company(idno="2222222222222", name_ro="Beta Inc", name_ru="Бета"),
        ]
        await search_service.index_entities(SearchIndex.COMPANIES, companies)

        query = AutocompleteCommandQuery(q="Alp", index=SearchIndex.COMPANIES)
        result = await search_service.autocomplete(query)

        assert len(result.suggestions) == 1
        assert result.suggestions[0].id == "1111111111111"

    @pytest.mark.asyncio
    async def test_reindex(self, search_service):
        from credibil.domain.company.entities import Company

        company = Company(idno="1234567890123", name_ro="Test", name_ru="Тест")
        await search_service.index_entity(SearchIndex.COMPANIES, company)

        await search_service.reindex(SearchIndex.COMPANIES)
        count = await search_service.get_index_count(SearchIndex.COMPANIES)
        assert count == 0

    @pytest.mark.asyncio
    async def test_health_check(self, search_service):
        assert await search_service.health_check() is True

    @pytest.mark.asyncio
    async def test_get_index_count(self, search_service):
        count = await search_service.get_index_count(SearchIndex.COMPANIES)
        assert count == 0

    @pytest.mark.asyncio
    async def test_person_indexing(self, search_service):
        from credibil.domain.relationship.entities import Person, PersonType

        person = Person(
            idnp="1234567890123",
            full_name="John Doe",
            person_type=PersonType.NATURAL,
        )
        await search_service.index_entity(SearchIndex.PERSONS, person)

        count = await search_service.get_index_count(SearchIndex.PERSONS)
        assert count == 1

    @pytest.mark.asyncio
    async def test_autocomplete_across_indexes(self, search_service):
        from credibil.domain.company.entities import Company
        from credibil.domain.relationship.entities import Person

        company = Company(idno="1111111111111", name_ro="Alpha Corp", name_ru="А")
        person = Person(full_name="Alpha Tester", idnp="222")
        await search_service.index_entity(SearchIndex.COMPANIES, company)
        await search_service.index_entity(SearchIndex.PERSONS, person)

        query = AutocompleteCommandQuery(q="Alpha")
        result = await search_service.autocomplete(query)

        assert len(result.suggestions) == 2
