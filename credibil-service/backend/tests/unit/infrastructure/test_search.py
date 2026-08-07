from __future__ import annotations

import pytest
from tests.in_memory_search import InMemorySearchProvider

from credibil.domain.search.entities import (
    AutocompleteQuery,
    SearchDocument,
    SearchIndex,
    SearchQuery,
)
from credibil.infrastructure.search.mappers import (
    CompanyMapper,
    PersonMapper,
    get_mapper,
)


class TestCompanyMapper:
    def test_index(self):
        mapper = CompanyMapper()
        assert mapper.index == SearchIndex.COMPANIES

    def test_to_document(self):
        from credibil.domain.company.entities import Company, CompanyStatus, LegalForm

        company = Company(
            idno="1234567890123",
            name_ro="Test SRL",
            name_ru="Тест СРЛ",
            status=CompanyStatus.ACTIVE,
            legal_form=LegalForm.SRL,
            caem="41.20",
            caem_description="Construction of buildings",
            legal_address="str. Test 1, Chisinau",
        )
        mapper = CompanyMapper()
        doc = mapper.to_document(company)

        assert doc.id == "1234567890123"
        assert doc.index == SearchIndex.COMPANIES
        assert doc.data["name_ro"] == "Test SRL"
        assert doc.data["name_ru"] == "Тест СРЛ"
        assert doc.data["idno"] == "1234567890123"
        assert doc.data["legal_form"] == "SRL"
        assert doc.data["caem"] == "41.20"
        assert doc.data["status"] == "active"
        assert doc.data["entity_type"] == "company"

    def test_to_document_minimal(self):
        from credibil.domain.company.entities import Company

        company = Company(idno="1111111111111", name_ro="Minimal", name_ru="Минимал")
        mapper = CompanyMapper()
        doc = mapper.to_document(company)

        assert doc.id == "1111111111111"
        assert doc.data["legal_form"] == "OTHER"
        assert doc.data["caem"] == ""
        assert doc.data["legal_address"] == ""


class TestPersonMapper:
    def test_index(self):
        mapper = PersonMapper()
        assert mapper.index == SearchIndex.PERSONS

    def test_to_document(self):
        from credibil.domain.relationship.entities import Person, PersonType

        person = Person(
            idnp="1234567890123",
            full_name="John Doe",
            person_type=PersonType.NATURAL,
            nationality="MD",
        )
        mapper = PersonMapper()
        doc = mapper.to_document(person)

        assert doc.id == str(person.id)
        assert doc.index == SearchIndex.PERSONS
        assert doc.data["full_name"] == "John Doe"
        assert doc.data["idnp"] == "1234567890123"
        assert doc.data["person_type"] == "natural"
        assert doc.data["nationality"] == "MD"
        assert doc.data["company_names"] == []
        assert doc.data["entity_type"] == "person"

    def test_to_document_minimal(self):
        from credibil.domain.relationship.entities import Person

        person = Person(full_name="Minimal Person")
        mapper = PersonMapper()
        doc = mapper.to_document(person)

        assert doc.data["idnp"] == ""
        assert doc.data["nationality"] == ""
        assert doc.data["person_type"] == "natural"


class TestGetMapper:
    def test_get_company_mapper(self):
        mapper = get_mapper(SearchIndex.COMPANIES)
        assert isinstance(mapper, CompanyMapper)

    def test_get_person_mapper(self):
        mapper = get_mapper(SearchIndex.PERSONS)
        assert isinstance(mapper, PersonMapper)

    def test_get_mapper_invalid_index(self):
        with pytest.raises((ValueError, KeyError)):
            get_mapper("invalid_index")


class TestInMemorySearchProvider:
    @pytest.fixture
    def provider(self):
        return InMemorySearchProvider()

    @pytest.mark.asyncio
    async def test_index_and_count(self, provider):
        docs = [
            SearchDocument(
                id="1111111111111",
                index=SearchIndex.COMPANIES,
                data={"name_ro": "Company A", "idno": "1111111111111"},
            ),
            SearchDocument(
                id="2222222222222",
                index=SearchIndex.COMPANIES,
                data={"name_ro": "Company B", "idno": "2222222222222"},
            ),
        ]
        count = await provider.index_documents(SearchIndex.COMPANIES, docs)
        assert count == 2

        total = await provider.get_document_count(SearchIndex.COMPANIES)
        assert total == 2

    @pytest.mark.asyncio
    async def test_search(self, provider):
        docs = [
            SearchDocument(
                id="1111111111111",
                index=SearchIndex.COMPANIES,
                data={"name_ro": "Alpha Company", "idno": "1111111111111"},
            ),
            SearchDocument(
                id="2222222222222",
                index=SearchIndex.COMPANIES,
                data={"name_ro": "Beta Company", "idno": "2222222222222"},
            ),
        ]
        await provider.index_documents(SearchIndex.COMPANIES, docs)

        query = SearchQuery(q="Alpha", index=SearchIndex.COMPANIES)
        result = await provider.search(query)

        assert len(result.hits) == 1
        assert result.hits[0].id == "1111111111111"
        assert result.total_hits == 1

    @pytest.mark.asyncio
    async def test_search_idno(self, provider):
        doc = SearchDocument(
            id="1234567890123",
            index=SearchIndex.COMPANIES,
            data={"name_ro": "Test", "idno": "1234567890123"},
        )
        await provider.index_documents(SearchIndex.COMPANIES, [doc])

        query = SearchQuery(q="1234567890123", index=SearchIndex.COMPANIES)
        result = await provider.search(query)
        assert len(result.hits) == 1
        assert result.hits[0].id == "1234567890123"

    @pytest.mark.asyncio
    async def test_autocomplete(self, provider):
        docs = [
            SearchDocument(
                id="1",
                index=SearchIndex.COMPANIES,
                data={"name_ro": "Alpha Corp", "idno": "111"},
            ),
            SearchDocument(
                id="2",
                index=SearchIndex.COMPANIES,
                data={"name_ro": "Beta Inc", "idno": "222"},
            ),
        ]
        await provider.index_documents(SearchIndex.COMPANIES, docs)

        query = AutocompleteQuery(q="Alp", index=SearchIndex.COMPANIES)
        result = await provider.autocomplete(query)

        assert len(result.suggestions) == 1
        assert result.suggestions[0].id == "1"

    @pytest.mark.asyncio
    async def test_delete_documents(self, provider):
        docs = [
            SearchDocument(id="1", index=SearchIndex.COMPANIES, data={"name": "A"}),
            SearchDocument(id="2", index=SearchIndex.COMPANIES, data={"name": "B"}),
        ]
        await provider.index_documents(SearchIndex.COMPANIES, docs)

        count = await provider.delete_documents(SearchIndex.COMPANIES, ["1"])
        assert count == 1

        total = await provider.get_document_count(SearchIndex.COMPANIES)
        assert total == 1

    @pytest.mark.asyncio
    async def test_delete_all_documents(self, provider):
        docs = [
            SearchDocument(id="1", index=SearchIndex.COMPANIES, data={"name": "A"}),
            SearchDocument(id="2", index=SearchIndex.COMPANIES, data={"name": "B"}),
        ]
        await provider.index_documents(SearchIndex.COMPANIES, docs)

        count = await provider.delete_all_documents(SearchIndex.COMPANIES)
        assert count == 2

        total = await provider.get_document_count(SearchIndex.COMPANIES)
        assert total == 0

    @pytest.mark.asyncio
    async def test_health_check(self, provider):
        assert await provider.health_check() is True

    @pytest.mark.asyncio
    async def test_index_empty(self, provider):
        count = await provider.index_documents(SearchIndex.COMPANIES, [])
        assert count == 0

    @pytest.mark.asyncio
    async def test_delete_empty(self, provider):
        count = await provider.delete_documents(SearchIndex.COMPANIES, [])
        assert count == 0

    @pytest.mark.asyncio
    async def test_search_empty(self, provider):
        query = SearchQuery(q="test", index=SearchIndex.COMPANIES)
        result = await provider.search(query)
        assert result.hits == []
        assert result.total_hits == 0
