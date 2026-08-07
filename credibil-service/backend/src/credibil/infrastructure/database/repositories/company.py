from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sqlalchemy import delete as sa_delete
from sqlalchemy import func, select

from credibil.core.pagination import PageParams, PaginatedResult, build_paginated_result
from credibil.domain.company.entities import Company, CompanyStatus, LegalForm
from credibil.infrastructure.database.models_company import CompanyModel
from credibil.ports.repositories.company import CompanyRepository

if TYPE_CHECKING:
    from uuid import UUID

    from sqlalchemy.ext.asyncio import AsyncSession


class SQLAlchemyCompanyRepository(CompanyRepository):
    """PostgreSQL company repository via SQLAlchemy."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_id(self, company_id: UUID) -> Company | None:
        stmt = select(CompanyModel).where(CompanyModel.id == company_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def find_by_idno(self, idno: str) -> Company | None:
        stmt = select(CompanyModel).where(CompanyModel.idno == idno)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def save(self, company: Company) -> Company:
        model = self._to_model(company)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_domain(model)

    async def delete(self, company_id: UUID) -> None:
        stmt = sa_delete(CompanyModel).where(CompanyModel.id == company_id)
        await self._session.execute(stmt)

    async def list_companies(
        self,
        page_params: PageParams,
        filters: dict[str, Any] | None = None,
        search: str | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> PaginatedResult[Company]:
        base_query = select(CompanyModel)
        count_query = select(func.count()).select_from(CompanyModel)

        base_query, count_query = self._apply_filters(base_query, count_query, filters)
        base_query, count_query = self._apply_search(base_query, count_query, search)

        sort_column = self._get_sort_column(sort_by)
        if sort_order.lower() == "desc":
            base_query = base_query.order_by(sort_column.desc())
        else:
            base_query = base_query.order_by(sort_column.asc())

        total_result = await self._session.execute(count_query)
        total = total_result.scalar_one()

        base_query = base_query.offset(page_params.offset).limit(page_params.limit)
        result = await self._session.execute(base_query)
        models = list(result.scalars().all())

        items = [self._to_domain(m) for m in models]
        return build_paginated_result(items, total, page_params)

    async def count_by_idno(self, idno: str) -> int:
        stmt = select(func.count()).select_from(CompanyModel).where(CompanyModel.idno == idno)
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def exists(self, company_id: UUID) -> bool:
        stmt = select(func.count()).select_from(CompanyModel).where(CompanyModel.id == company_id)
        result = await self._session.execute(stmt)
        return result.scalar_one() > 0

    # ── Private helpers ──────────────────────────────────────────

    def _apply_filters(
        self,
        base_query: Any,
        count_query: Any,
        filters: dict[str, Any] | None,
    ) -> tuple[Any, Any]:
        if not filters:
            return base_query, count_query

        filter_map: dict[str, Any] = {
            "status": CompanyModel.status,
            "legal_form": CompanyModel.legal_form,
            "caem": CompanyModel.caem,
            "cuatm": CompanyModel.cuatm,
            "postal_code": CompanyModel.postal_code,
            "business_category": CompanyModel.business_category,
        }

        for key, value in filters.items():
            if key in filter_map and value is not None:
                col = filter_map[key]
                if isinstance(value, list):
                    base_query = base_query.where(col.in_(value))
                    count_query = count_query.where(col.in_(value))
                else:
                    base_query = base_query.where(col == value)
                    count_query = count_query.where(col == value)

        return base_query, count_query

    def _apply_search(
        self,
        base_query: Any,
        count_query: Any,
        search: str | None,
    ) -> tuple[Any, Any]:
        if not search:
            return base_query, count_query

        pattern = f"%{search}%"
        condition = (
            CompanyModel.name_ro.ilike(pattern)
            | CompanyModel.name_ru.ilike(pattern)
            | CompanyModel.idno.ilike(pattern)
        )
        return base_query.where(condition), count_query.where(condition)

    def _get_sort_column(self, sort_by: str) -> Any:
        sort_columns = {
            "name_ro": CompanyModel.name_ro,
            "name_ru": CompanyModel.name_ru,
            "idno": CompanyModel.idno,
            "status": CompanyModel.status,
            "registration_date": CompanyModel.registration_date,
            "created_at": CompanyModel.created_at,
            "updated_at": CompanyModel.updated_at,
            "tax_debt": CompanyModel.tax_debt,
            "founder_count": CompanyModel.founder_count,
            "director_count": CompanyModel.director_count,
        }
        return sort_columns.get(sort_by, CompanyModel.created_at)

    def _to_domain(self, model: CompanyModel) -> Company:
        return Company(
            company_id=model.id,
            idno=model.idno,
            name_ro=model.name_ro,
            name_ru=model.name_ru,
            registration_date=model.registration_date,
            status=CompanyStatus(model.status),
            legal_form=LegalForm(model.legal_form),
            legal_address=model.legal_address,
            postal_code=model.postal_code,
            caem=model.caem,
            caem_description=model.caem_description,
            cuatm=model.cuatm,
            cuiio=model.cuiio,
            cfp=model.cfp,
            cfoj=model.cfoj,
            business_category=model.business_category,
            tax_debt=model.tax_debt,
            tax_debt_fetched_at=model.tax_debt_fetched_at,
            founder_count=model.founder_count,
            director_count=model.director_count,
            metadata=model.metadata_ if model.metadata_ else {},
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_model(self, company: Company) -> CompanyModel:
        return CompanyModel(
            id=company.id,
            idno=company.idno,
            name_ro=company.name_ro,
            name_ru=company.name_ru,
            registration_date=company.registration_date,
            status=company.status.value,
            legal_form=company.legal_form.value,
            legal_address=company.legal_address,
            postal_code=company.postal_code,
            caem=company.caem,
            caem_description=company.caem_description,
            cuatm=company.cuatm,
            cuiio=company.cuiio,
            cfp=company.cfp,
            cfoj=company.cfoj,
            business_category=company.business_category,
            tax_debt=company.tax_debt,
            tax_debt_fetched_at=company.tax_debt_fetched_at,
            founder_count=company.founder_count,
            director_count=company.director_count,
            metadata_=company.metadata,
            created_at=company.created_at,
            updated_at=company.updated_at,
        )
