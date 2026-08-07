from __future__ import annotations

import os

import pytest

os.environ["CREDIBIL_DATABASE_URL"] = "sqlite+aiosqlite:///test.db"
os.environ["CREDIBIL_DEBUG"] = "true"


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture
def sync_repo():
    from tests.in_memory_repos import InMemorySyncHistoryRepository

    return InMemorySyncHistoryRepository()


@pytest.fixture
def person_repo():
    from tests.in_memory_repos import InMemoryPersonRepository

    return InMemoryPersonRepository()


@pytest.fixture
def relationship_repo():
    from tests.in_memory_repos import InMemoryRelationshipRepository

    return InMemoryRelationshipRepository()


@pytest.fixture
def financial_repo():
    from tests.in_memory_repos import InMemoryFinancialReportRepository

    return InMemoryFinancialReportRepository()


@pytest.fixture
def court_case_repo():
    from tests.in_memory_repos import InMemoryCourtCaseRepository

    return InMemoryCourtCaseRepository()


@pytest.fixture
def court_hearing_repo():
    from tests.in_memory_repos import InMemoryCourtHearingRepository

    return InMemoryCourtHearingRepository()


@pytest.fixture
def tender_repo():
    from tests.in_memory_repos import InMemoryTenderRepository

    return InMemoryTenderRepository()


@pytest.fixture
def tender_award_repo():
    from tests.in_memory_repos import InMemoryTenderAwardRepository

    return InMemoryTenderAwardRepository()


@pytest.fixture
def tender_bid_repo():
    from tests.in_memory_repos import InMemoryTenderBidRepository

    return InMemoryTenderBidRepository()


@pytest.fixture
def accreditation_repo():
    from tests.in_memory_repos import InMemoryAccreditationRepository

    return InMemoryAccreditationRepository()
