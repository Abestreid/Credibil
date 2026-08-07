from __future__ import annotations

import pytest

from credibil.application.accreditation import (
    GetAccreditationQuery,
    ListAccreditationsQuery,
)
from credibil.application.accreditation.handlers import AccreditationHandlers
from credibil.domain.accreditation.entities import (
    Accreditation,
    AccreditationCategory,
    AccreditationStatus,
)
from credibil.domain.accreditation.errors import AccreditationNotFoundError
from tests.in_memory_repos import InMemoryAccreditationRepository


@pytest.fixture
def repo():
    return InMemoryAccreditationRepository()


@pytest.fixture
def handlers(repo):
    return AccreditationHandlers(accreditation_repo=repo)


def _make_accreditation(
    cert_number: str = "LI-001",
    org_name: str = "Test Lab SRL",
    category: AccreditationCategory = AccreditationCategory.TESTING_LAB,
    status: AccreditationStatus = AccreditationStatus.ACTIVE,
) -> Accreditation:
    return Accreditation(
        organization_name=org_name,
        certificate_number=cert_number,
        category=category,
        standard="SM EN ISO/IEC 17025:2018",
        status=status,
    )


class TestAccreditationHandlers:
    @pytest.mark.anyio
    async def test_get_by_id(self, handlers, repo):
        acc = _make_accreditation()
        await repo.save(acc)

        result = await handlers.get(GetAccreditationQuery(accreditation_id=acc.id))
        assert result.certificate_number == "LI-001"
        assert result.organization_name == "Test Lab SRL"

    @pytest.mark.anyio
    async def test_get_by_cert_number(self, handlers, repo):
        acc = _make_accreditation(cert_number="LI-004")
        await repo.save(acc)

        result = await handlers.get(GetAccreditationQuery(certificate_number="LI-004"))
        assert result.certificate_number == "LI-004"

    @pytest.mark.anyio
    async def test_get_not_found(self, handlers):
        with pytest.raises(AccreditationNotFoundError):
            await handlers.get(GetAccreditationQuery(certificate_number="NOT-FOUND"))

    @pytest.mark.anyio
    async def test_list_all(self, handlers, repo):
        await repo.save(_make_accreditation("LI-001"))
        await repo.save(_make_accreditation("LI-002", "Other Lab"))

        result = await handlers.list(ListAccreditationsQuery())
        assert len(result) == 2

    @pytest.mark.anyio
    async def test_list_by_category(self, handlers, repo):
        await repo.save(_make_accreditation("LI-001", category=AccreditationCategory.TESTING_LAB))
        await repo.save(_make_accreditation("LM-001", category=AccreditationCategory.MEDICAL_LAB))

        result = await handlers.list(
            ListAccreditationsQuery(category=AccreditationCategory.MEDICAL_LAB)
        )
        assert len(result) == 1
        assert result[0].category == "medical_lab"

    @pytest.mark.anyio
    async def test_list_by_status(self, handlers, repo):
        await repo.save(_make_accreditation("LI-001", status=AccreditationStatus.ACTIVE))
        await repo.save(_make_accreditation("LI-002", status=AccreditationStatus.WITHDRAWN))

        result = await handlers.list(ListAccreditationsQuery(status=AccreditationStatus.WITHDRAWN))
        assert len(result) == 1
        assert result[0].status == "withdrawn"

    @pytest.mark.anyio
    async def test_list_with_keyword(self, handlers, repo):
        await repo.save(_make_accreditation("LI-001", org_name="Chisinau Lab"))
        await repo.save(_make_accreditation("LI-002", org_name="Balti Lab"))

        result = await handlers.list(ListAccreditationsQuery(keyword="Chisinau"))
        assert len(result) == 1
        assert "Chisinau" in result[0].organization_name

    @pytest.mark.anyio
    async def test_statistics(self, handlers, repo):
        await repo.save(_make_accreditation("LI-001", category=AccreditationCategory.TESTING_LAB))
        await repo.save(_make_accreditation("LI-002", category=AccreditationCategory.TESTING_LAB))
        await repo.save(_make_accreditation("LM-001", category=AccreditationCategory.MEDICAL_LAB))

        from credibil.application.accreditation import GetAccreditationStatisticsQuery

        result = await handlers.get_statistics(GetAccreditationStatisticsQuery())
        assert result.total == 3
        assert result.by_category["testing_lab"] == 2
        assert result.by_category["medical_lab"] == 1

    @pytest.mark.anyio
    async def test_search(self, handlers, repo):
        await repo.save(_make_accreditation("LI-001", org_name="Chisinau Testing Lab"))
        await repo.save(_make_accreditation("LI-002", org_name="Balti Calibration"))

        result = await handlers.search("testing")
        assert len(result) == 1
        assert "Testing" in result[0].organization_name
