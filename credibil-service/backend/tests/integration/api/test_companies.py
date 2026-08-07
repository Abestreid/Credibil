from __future__ import annotations

from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from credibil.api.v1.companies.dependencies import get_company_repo
from credibil.main import app
from tests.factories import InMemoryCompanyRepository


@pytest.fixture
def in_memory_repo() -> InMemoryCompanyRepository:
    return InMemoryCompanyRepository()


@pytest.fixture
async def client(in_memory_repo: InMemoryCompanyRepository) -> AsyncClient:
    async def _override_repo():
        yield in_memory_repo

    app.dependency_overrides[get_company_repo] = _override_repo

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c

    app.dependency_overrides.clear()


class TestHealthEndpoint:
    async def test_health(self) -> None:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as c:
            response = await c.get("/health")
            assert response.status_code == 200
            assert response.json()["status"] == "healthy"


class TestCompanyAPI:
    async def test_create_company(self, client: AsyncClient) -> None:
        response = await client.post(
            "/api/v1/companies",
            json={
                "idno": "1234567890123",
                "name_ro": "Test Company SRL",
                "name_ru": "Тест Компания",
                "status": "active",
                "legal_form": "SRL",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["data"]["idno"] == "1234567890123"
        assert data["data"]["name_ro"] == "Test Company SRL"

    async def test_create_company_validation_error(self, client: AsyncClient) -> None:
        response = await client.post(
            "/api/v1/companies",
            json={
                "idno": "123",  # Too short
                "name_ro": "",  # Empty
            },
        )
        assert response.status_code == 422

    async def test_create_company_missing_required(self, client: AsyncClient) -> None:
        response = await client.post(
            "/api/v1/companies",
            json={},
        )
        assert response.status_code == 422

    async def test_get_company(self, client: AsyncClient) -> None:
        create_resp = await client.post(
            "/api/v1/companies",
            json={
                "idno": "1234567890123",
                "name_ro": "Get Test Company",
            },
        )
        company_id = create_resp.json()["data"]["id"]

        response = await client.get(f"/api/v1/companies/{company_id}")
        assert response.status_code == 200
        assert response.json()["data"]["idno"] == "1234567890123"

    async def test_get_company_not_found(self, client: AsyncClient) -> None:
        response = await client.get(f"/api/v1/companies/{uuid4()}")
        assert response.status_code == 404

    async def test_update_company(self, client: AsyncClient) -> None:
        create_resp = await client.post(
            "/api/v1/companies",
            json={
                "idno": "1234567890123",
                "name_ro": "Original Name",
            },
        )
        company_id = create_resp.json()["data"]["id"]

        response = await client.put(
            f"/api/v1/companies/{company_id}",
            json={"name_ro": "Updated Name"},
        )
        assert response.status_code == 200
        assert response.json()["data"]["name_ro"] == "Updated Name"

    async def test_delete_company(self, client: AsyncClient) -> None:
        create_resp = await client.post(
            "/api/v1/companies",
            json={
                "idno": "1234567890123",
                "name_ro": "To Delete",
            },
        )
        company_id = create_resp.json()["data"]["id"]

        response = await client.delete(f"/api/v1/companies/{company_id}")
        assert response.status_code == 204

        get_resp = await client.get(f"/api/v1/companies/{company_id}")
        assert get_resp.status_code == 404

    async def test_list_companies(self, client: AsyncClient) -> None:
        for i in range(3):
            await client.post(
                "/api/v1/companies",
                json={
                    "idno": f"{1000000000000 + i:013d}",
                    "name_ro": f"Company {i}",
                },
            )

        response = await client.get("/api/v1/companies")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) == 3
        assert data["meta"]["total"] == 3

    async def test_list_companies_search(self, client: AsyncClient) -> None:
        await client.post(
            "/api/v1/companies",
            json={"idno": "1234567890123", "name_ro": "Alpha Corp"},
        )
        await client.post(
            "/api/v1/companies",
            json={"idno": "2234567890123", "name_ro": "Beta LLC"},
        )

        response = await client.get("/api/v1/companies", params={"search": "alpha"})
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 1
        assert data["data"][0]["name_ro"] == "Alpha Corp"

    async def test_list_companies_filter(self, client: AsyncClient) -> None:
        await client.post(
            "/api/v1/companies",
            json={"idno": "1234567890123", "name_ro": "Active Co", "status": "active"},
        )
        await client.post(
            "/api/v1/companies",
            json={
                "idno": "2234567890123",
                "name_ro": "Liquidated Co",
                "status": "liquidated",
            },
        )

        response = await client.get("/api/v1/companies", params={"status": "liquidated"})
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 1
        assert data["data"][0]["name_ro"] == "Liquidated Co"

    async def test_list_companies_pagination(self, client: AsyncClient) -> None:
        for i in range(5):
            await client.post(
                "/api/v1/companies",
                json={"idno": f"{1000000000000 + i:013d}", "name_ro": f"Co {i}"},
            )

        response = await client.get("/api/v1/companies", params={"page": 1, "per_page": 2})
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 2
        assert data["meta"]["total"] == 5
        assert data["meta"]["total_pages"] == 3
        assert data["meta"]["has_next"] is True
