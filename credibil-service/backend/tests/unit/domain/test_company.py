from __future__ import annotations

import pytest

from credibil.application.company.commands import CreateCompanyCommand, UpdateCompanyCommand
from credibil.application.company.handlers import CompanyHandlers
from credibil.application.company.queries import GetCompanyQuery, ListCompaniesQuery
from credibil.domain.company.entities import CompanyStatus, LegalForm
from credibil.domain.company.errors import CompanyAlreadyExistsError, CompanyNotFoundError
from credibil.domain.company.value_objects import CAEM, IDNO, PostalCode
from tests.factories import InMemoryCompanyRepository, make_company

# ── Domain Entity Tests ─────────────────────────────────────────


class TestCompanyEntity:
    def test_create_company_with_defaults(self) -> None:
        company = make_company()
        assert company.id is not None
        assert company.idno == "1234567890123"
        assert company.name_ro == "Societatea Comercială Example SRL"
        assert company.status == CompanyStatus.ACTIVE
        assert company.legal_form == LegalForm.SRL
        assert company.founder_count == 2
        assert company.director_count == 1

    def test_company_update(self) -> None:
        company = make_company()
        old_updated = company.updated_at
        company.update(name_ro="Updated Name", tax_debt=1500.50)
        assert company.name_ro == "Updated Name"
        assert company.tax_debt == 1500.50
        assert company.updated_at >= old_updated

    def test_company_repr(self) -> None:
        company = make_company()
        r = repr(company)
        assert "Company" in r
        assert "1234567890123" in r

    def test_company_statuses(self) -> None:
        for status in CompanyStatus:
            company = make_company(status=status)
            assert company.status == status


# ── Value Object Tests ──────────────────────────────────────────


class TestIDNO:
    def test_valid_idno(self) -> None:
        idno = IDNO("1234567890123")
        assert str(idno) == "1234567890123"

    def test_idno_strips_spaces(self) -> None:
        idno = IDNO("123 456 789 012 3")
        assert str(idno) == "1234567890123"

    def test_invalid_idno_too_short(self) -> None:
        with pytest.raises(ValueError, match="Invalid IDNO"):
            IDNO("12345")

    def test_invalid_idno_letters(self) -> None:
        with pytest.raises(ValueError, match="Invalid IDNO"):
            IDNO("123456789012a")


class TestCAEM:
    def test_valid_caem(self) -> None:
        caem = CAEM("6201")
        assert str(caem) == "6201"

    def test_valid_caem_with_subdivision(self) -> None:
        caem = CAEM("62.01")
        assert str(caem) == "62.01"

    def test_invalid_caem(self) -> None:
        with pytest.raises(ValueError, match="Invalid CAEM"):
            CAEM("INVALID")


class TestPostalCode:
    def test_valid_postal_code(self) -> None:
        pc = PostalCode("MD-2012")
        assert str(pc) == "2012"

    def test_valid_postal_code_without_prefix(self) -> None:
        pc = PostalCode("2012")
        assert str(pc) == "2012"

    def test_invalid_postal_code(self) -> None:
        with pytest.raises(ValueError, match="Invalid postal code"):
            PostalCode("12")


# ── Application Service Tests ───────────────────────────────────


class TestCompanyHandlers:
    @pytest.fixture
    def repo(self) -> InMemoryCompanyRepository:
        return InMemoryCompanyRepository()

    @pytest.fixture
    def handlers(self, repo: InMemoryCompanyRepository) -> CompanyHandlers:
        return CompanyHandlers(company_repo=repo)

    async def test_create_company(
        self, handlers: CompanyHandlers, repo: InMemoryCompanyRepository
    ) -> None:
        cmd = CreateCompanyCommand(
            idno="1234567890123",
            name_ro="Test Company SRL",
            name_ru="Тест Компания",
            status="active",
            legal_form="SRL",
        )
        result = await handlers.create_company(cmd)
        assert result.idno == "1234567890123"
        assert result.name_ro == "Test Company SRL"
        assert result.name_ru == "Тест Компания"
        assert len(str(result.id)) == 36

    async def test_create_company_duplicate_idno(
        self, handlers: CompanyHandlers, repo: InMemoryCompanyRepository
    ) -> None:
        cmd = CreateCompanyCommand(
            idno="1234567890123",
            name_ro="First Company",
        )
        await handlers.create_company(cmd)

        cmd2 = CreateCompanyCommand(
            idno="1234567890123",
            name_ro="Second Company",
        )
        with pytest.raises(CompanyAlreadyExistsError):
            await handlers.create_company(cmd2)

    async def test_get_company(self, handlers: CompanyHandlers) -> None:
        cmd = CreateCompanyCommand(
            idno="1234567890123",
            name_ro="Test Company",
        )
        created = await handlers.create_company(cmd)

        result = await handlers.get_company(GetCompanyQuery(company_id=str(created.id)))
        assert result.idno == "1234567890123"
        assert result.name_ro == "Test Company"

    async def test_get_company_not_found(self, handlers: CompanyHandlers) -> None:
        from uuid import uuid4

        with pytest.raises(CompanyNotFoundError):
            await handlers.get_company(GetCompanyQuery(company_id=str(uuid4())))

    async def test_update_company(self, handlers: CompanyHandlers) -> None:
        cmd = CreateCompanyCommand(
            idno="1234567890123",
            name_ro="Original Name",
        )
        created = await handlers.create_company(cmd)

        update_cmd = UpdateCompanyCommand(
            company_id=created.id,
            name_ro="Updated Name",
            tax_debt=5000.0,
        )
        updated = await handlers.update_company(update_cmd)
        assert updated.name_ro == "Updated Name"
        assert updated.tax_debt == 5000.0

    async def test_delete_company(self, handlers: CompanyHandlers) -> None:
        from credibil.application.company.commands import DeleteCompanyCommand

        cmd = CreateCompanyCommand(
            idno="1234567890123",
            name_ro="To Delete",
        )
        created = await handlers.create_company(cmd)
        await handlers.delete_company(DeleteCompanyCommand(company_id=created.id))

        with pytest.raises(CompanyNotFoundError):
            await handlers.get_company(GetCompanyQuery(company_id=str(created.id)))

    async def test_list_companies_empty(self, handlers: CompanyHandlers) -> None:
        query = ListCompaniesQuery(page=1, per_page=25)
        result = await handlers.list_companies(query)
        assert len(result.items) == 0
        assert result.meta.total == 0

    async def test_list_companies_with_data(self, handlers: CompanyHandlers) -> None:
        for i in range(5):
            await handlers.create_company(
                CreateCompanyCommand(
                    idno=f"{1000000000000 + i:013d}",
                    name_ro=f"Company {i}",
                )
            )

        query = ListCompaniesQuery(page=1, per_page=3)
        result = await handlers.list_companies(query)
        assert len(result.items) == 3
        assert result.meta.total == 5
        assert result.meta.total_pages == 2
        assert result.meta.has_next is True
        assert result.meta.has_prev is False

    async def test_list_companies_search(self, handlers: CompanyHandlers) -> None:
        await handlers.create_company(
            CreateCompanyCommand(idno="1234567890123", name_ro="Alpha Corp")
        )
        await handlers.create_company(
            CreateCompanyCommand(idno="2234567890123", name_ro="Beta LLC")
        )

        query = ListCompaniesQuery(page=1, per_page=25, search="alpha")
        result = await handlers.list_companies(query)
        assert len(result.items) == 1
        assert result.items[0].name_ro == "Alpha Corp"

    async def test_list_companies_filter_status(self, handlers: CompanyHandlers) -> None:
        await handlers.create_company(
            CreateCompanyCommand(idno="1234567890123", name_ro="Active Co", status="active")
        )
        await handlers.create_company(
            CreateCompanyCommand(idno="2234567890123", name_ro="Liquidated Co", status="liquidated")
        )

        query = ListCompaniesQuery(page=1, per_page=25, filters={"status": "liquidated"})
        result = await handlers.list_companies(query)
        assert len(result.items) == 1
        assert result.items[0].name_ro == "Liquidated Co"

    async def test_list_companies_sort(self, handlers: CompanyHandlers) -> None:
        await handlers.create_company(
            CreateCompanyCommand(idno="3234567890123", name_ro="Z Company")
        )
        await handlers.create_company(
            CreateCompanyCommand(idno="1234567890123", name_ro="A Company")
        )

        query = ListCompaniesQuery(page=1, per_page=25, sort_by="name_ro", sort_order="asc")
        result = await handlers.list_companies(query)
        assert result.items[0].name_ro == "A Company"
        assert result.items[1].name_ro == "Z Company"
