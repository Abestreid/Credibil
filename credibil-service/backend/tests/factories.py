from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING, Any

from credibil.application.company.dto import CompanyDTO
from credibil.core.pagination import PageParams, PaginatedResult, build_paginated_result
from credibil.domain.company.entities import Company, CompanyStatus, LegalForm
from credibil.ports.repositories.company import CompanyRepository

if TYPE_CHECKING:
    from uuid import UUID


class InMemoryCompanyRepository(CompanyRepository):
    """In-memory company repository for testing."""

    def __init__(self) -> None:
        self._companies: dict[UUID, Company] = {}

    async def find_by_id(self, company_id: UUID) -> Company | None:
        return self._companies.get(company_id)

    async def find_by_idno(self, idno: str) -> Company | None:
        for company in self._companies.values():
            if company.idno == idno:
                return company
        return None

    async def save(self, company: Company) -> Company:
        self._companies[company.id] = company
        return company

    async def delete(self, company_id: UUID) -> None:
        self._companies.pop(company_id, None)

    async def list_companies(
        self,
        page_params: PageParams,
        filters: dict[str, Any] | None = None,
        search: str | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> PaginatedResult[Company]:
        items = list(self._companies.values())

        if search:
            pattern = search.lower()
            items = [
                c
                for c in items
                if pattern in c.name_ro.lower() or pattern in c.name_ru.lower() or pattern in c.idno
            ]

        if filters:
            for key, value in filters.items():
                items = [c for c in items if getattr(c, key, None) == value]

        reverse = sort_order.lower() == "desc"
        items.sort(key=lambda c: str(getattr(c, sort_by, "")), reverse=reverse)

        total = len(items)
        start = page_params.offset
        end = start + page_params.limit
        page_items = items[start:end]

        return build_paginated_result(page_items, total, page_params)

    async def count_by_idno(self, idno: str) -> int:
        return sum(1 for c in self._companies.values() if c.idno == idno)

    async def exists(self, company_id: UUID) -> bool:
        return company_id in self._companies


def make_company(**overrides: Any) -> Company:
    """Factory for creating test company instances."""
    defaults = {
        "idno": "1234567890123",
        "name_ro": "Societatea Comercială Example SRL",
        "name_ru": 'ООО "Экземпл"',
        "registration_date": date(2020, 1, 15),
        "status": CompanyStatus.ACTIVE,
        "legal_form": LegalForm.SRL,
        "legal_address": "str. Principală 1, Chișinău",
        "postal_code": "MD-2012",
        "caem": "6201",
        "caem_description": "Activități de dezvoltare de programe informatice",
        "cuatm": "1000000",
        "cuiio": "12345",
        "cfp": "67890",
        "cfoj": "11111",
        "tax_debt": 0.0,
        "founder_count": 2,
        "director_count": 1,
        "metadata": {},
    }
    defaults.update(overrides)
    return Company(**defaults)


def make_company_dto(**overrides: Any) -> CompanyDTO:
    """Factory for creating test CompanyDTO instances."""
    company = make_company(**overrides)
    return CompanyDTO.model_validate(company.__dict__)
