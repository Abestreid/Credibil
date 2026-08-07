from __future__ import annotations

from typing import TYPE_CHECKING, Any

from credibil.application.company.dto import CompanyDTO
from credibil.core.pagination import PaginatedResult, parse_page_params
from credibil.domain.company.entities import Company, CompanyStatus, LegalForm
from credibil.domain.company.errors import CompanyAlreadyExistsError, CompanyNotFoundError

if TYPE_CHECKING:
    from credibil.application.company.commands import (
        CreateCompanyCommand,
        DeleteCompanyCommand,
        UpdateCompanyCommand,
    )
    from credibil.application.company.queries import GetCompanyQuery, ListCompaniesQuery
    from credibil.ports.repositories.company import CompanyRepository


class CompanyHandlers:
    """Application service for company operations."""

    def __init__(self, company_repo: CompanyRepository) -> None:
        self._repo = company_repo

    async def create_company(self, cmd: CreateCompanyCommand) -> CompanyDTO:
        existing = await self._repo.find_by_idno(cmd.idno)
        if existing:
            raise CompanyAlreadyExistsError(cmd.idno)

        company = Company(
            idno=cmd.idno,
            name_ro=cmd.name_ro,
            name_ru=cmd.name_ru,
            registration_date=cmd.registration_date,
            status=CompanyStatus(cmd.status),
            legal_form=LegalForm(cmd.legal_form),
            legal_address=cmd.legal_address,
            postal_code=cmd.postal_code,
            caem=cmd.caem,
            caem_description=cmd.caem_description,
            cuatm=cmd.cuatm,
            cuiio=cmd.cuiio,
            cfp=cmd.cfp,
            cfoj=cmd.cfoj,
            tax_debt=cmd.tax_debt,
            founder_count=cmd.founder_count,
            director_count=cmd.director_count,
            metadata=cmd.metadata,
        )
        saved = await self._repo.save(company)
        return CompanyDTO.model_validate(saved.__dict__)

    async def get_company(self, query: GetCompanyQuery) -> CompanyDTO:
        identifier = query.company_id
        company = None
        try:
            from uuid import UUID
            uid = UUID(str(identifier))
            company = await self._repo.find_by_id(uid)
        except (ValueError, TypeError):
            company = None

        if not company and identifier:
            company = await self._repo.find_by_idno(str(identifier))

        if not company:
            raise CompanyNotFoundError(str(identifier))
        return CompanyDTO.model_validate(company.__dict__)

    async def update_company(self, cmd: UpdateCompanyCommand) -> CompanyDTO:
        company = await self._repo.find_by_id(cmd.company_id)
        if not company:
            raise CompanyNotFoundError(str(cmd.company_id))

        update_fields: dict[str, Any] = {}
        for field_name in [
            "name_ro",
            "name_ru",
            "registration_date",
            "legal_address",
            "postal_code",
            "caem",
            "caem_description",
            "cuatm",
            "cuiio",
            "cfp",
            "cfoj",
            "tax_debt",
            "metadata",
        ]:
            value = getattr(cmd, field_name)
            if value is not None:
                update_fields[field_name] = value

        if cmd.status is not None:
            update_fields["status"] = CompanyStatus(cmd.status)
        if cmd.legal_form is not None:
            update_fields["legal_form"] = LegalForm(cmd.legal_form)
        if cmd.founder_count is not None:
            update_fields["founder_count"] = cmd.founder_count
        if cmd.director_count is not None:
            update_fields["director_count"] = cmd.director_count

        company.update(**update_fields)
        saved = await self._repo.save(company)
        return CompanyDTO.model_validate(saved.__dict__)

    async def delete_company(self, cmd: DeleteCompanyCommand) -> None:
        company = await self._repo.find_by_id(cmd.company_id)
        if not company:
            raise CompanyNotFoundError(str(cmd.company_id))
        await self._repo.delete(cmd.company_id)

    async def list_companies(self, query: ListCompaniesQuery) -> PaginatedResult[CompanyDTO]:
        page_params = parse_page_params(query.page, query.per_page)
        result = await self._repo.list_companies(
            page_params=page_params,
            filters=query.filters,
            search=query.search,
            sort_by=query.sort_by,
            sort_order=query.sort_order,
        )
        items = [CompanyDTO.model_validate(c.__dict__) for c in result.items]
        return PaginatedResult(items=items, meta=result.meta)
