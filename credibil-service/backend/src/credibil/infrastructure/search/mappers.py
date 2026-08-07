from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from credibil.domain.search.entities import SearchDocument, SearchIndex


class SearchDocumentMapper(ABC):
    @property
    @abstractmethod
    def index(self) -> SearchIndex: ...

    @abstractmethod
    def to_document(self, entity: Any) -> SearchDocument: ...

    def to_documents(self, entities: list[Any]) -> list[SearchDocument]:
        return [self.to_document(e) for e in entities]


class CompanyMapper(SearchDocumentMapper):
    @property
    def index(self) -> SearchIndex:
        return SearchIndex.COMPANIES

    def to_document(self, entity: Any) -> SearchDocument:
        from credibil.domain.company.entities import Company

        company: Company = entity
        return SearchDocument(
            id=company.idno,
            index=self.index,
            data={
                "entity_type": "company",
                "name_ro": company.name_ro or "",
                "name_ru": company.name_ru or "",
                "idno": company.idno,
                "legal_form": company.legal_form.value if company.legal_form else "",
                "caem": company.caem or "",
                "caem_description": company.caem_description or "",
                "legal_address": company.legal_address or "",
                "registration_date": (
                    company.registration_date.isoformat() if company.registration_date else None
                ),
                "status": company.status.value if company.status else "",
            },
        )

    def to_document_with_relationships(
        self,
        company: Any,
        director_names: list[str],
        founder_names: list[str],
    ) -> SearchDocument:
        return SearchDocument(
            id=company.idno,
            index=self.index,
            data={
                "entity_type": "company",
                "name_ro": company.name_ro or "",
                "name_ru": company.name_ru or "",
                "idno": company.idno,
                "legal_form": company.legal_form.value if company.legal_form else "",
                "caem": company.caem or "",
                "caem_description": company.caem_description or "",
                "legal_address": company.legal_address or "",
                "registration_date": (
                    company.registration_date.isoformat() if company.registration_date else None
                ),
                "status": company.status.value if company.status else "",
                "director_names": director_names,
                "founder_names": founder_names,
            },
        )


class PersonMapper(SearchDocumentMapper):
    @property
    def index(self) -> SearchIndex:
        return SearchIndex.PERSONS

    def to_document(self, entity: Any) -> SearchDocument:
        from credibil.domain.relationship.entities import Person

        person: Person = entity
        return SearchDocument(
            id=str(person.id),
            index=self.index,
            data={
                "entity_type": "person",
                "full_name": person.full_name or "",
                "idnp": person.idnp or "",
                "person_type": person.person_type.value if person.person_type else "",
                "nationality": person.nationality or "",
                "company_names": [],
                "company_idnos": [],
                "relationship_types": [],
            },
        )

    def to_document_with_relationships(
        self,
        person: Any,
        company_names: list[str],
        company_idnos: list[str],
        relationship_types: list[str],
    ) -> SearchDocument:
        return SearchDocument(
            id=str(person.id),
            index=self.index,
            data={
                "entity_type": "person",
                "full_name": person.full_name or "",
                "idnp": person.idnp or "",
                "person_type": person.person_type.value if person.person_type else "",
                "nationality": person.nationality or "",
                "company_names": company_names,
                "company_idnos": company_idnos,
                "relationship_types": relationship_types,
                "connected_companies_count": len(company_idnos),
            },
        )


MAPPER_REGISTRY: dict[SearchIndex, SearchDocumentMapper] = {
    SearchIndex.COMPANIES: CompanyMapper(),
    SearchIndex.PERSONS: PersonMapper(),
}


def get_mapper(index: SearchIndex) -> SearchDocumentMapper:
    mapper = MAPPER_REGISTRY.get(index)
    if mapper is None:
        index_value = index.value if hasattr(index, "value") else str(index)
        raise ValueError(f"No mapper registered for index {index_value}")
    return mapper
