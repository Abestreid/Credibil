from __future__ import annotations

import pytest

from credibil.domain.tender.entities import (
    AwardStatus,
    ProcurementCategory,
    ProcurementMethod,
    Tender,
    TenderAward,
    TenderStatus,
)


@pytest.fixture
def sample_tender():
    return Tender(
        ocid="ocds-b3wdp1-MD-123",
        title="Medical Equipment Supply",
        status=TenderStatus.ACTIVE,
        procurement_method=ProcurementMethod.OPEN,
        main_category=ProcurementCategory.GOODS,
        cpv_code="33100000-1",
        buyer_idno="1003600150196",
        buyer_name="IMSP CRDM",
        value_amount=410000.0,
        value_currency="MDL",
        published_date=None,
    )


@pytest.fixture
def sample_award():
    return TenderAward(
        tender_ocid="ocds-b3wdp1-MD-123",
        status=AwardStatus.ACTIVE,
        value_amount=390000.0,
        value_currency="MDL",
        supplier_idno="1003600117582",
        supplier_name="GBG-MLD SRL",
    )


@pytest.mark.anyio
async def test_list_tenders_empty(tender_repo, tender_award_repo, tender_bid_repo):
    from credibil.application.tender.handlers import TenderHandlers

    handlers = TenderHandlers(
        tender_repo=tender_repo, award_repo=tender_award_repo, bid_repo=tender_bid_repo
    )
    from credibil.application.tender.commands import ListTendersQuery

    result = await handlers.list_tenders(ListTendersQuery(limit=10))
    assert result == []


@pytest.mark.anyio
async def test_list_tenders_with_data(
    tender_repo, tender_award_repo, tender_bid_repo, sample_tender
):
    await tender_repo.save(sample_tender)

    from credibil.application.tender.commands import ListTendersQuery
    from credibil.application.tender.handlers import TenderHandlers

    handlers = TenderHandlers(
        tender_repo=tender_repo, award_repo=tender_award_repo, bid_repo=tender_bid_repo
    )
    result = await handlers.list_tenders(ListTendersQuery(limit=10))
    assert len(result) == 1
    assert result[0].ocid == "ocds-b3wdp1-MD-123"
    assert result[0].title == "Medical Equipment Supply"


@pytest.mark.anyio
async def test_get_tender_by_ocid(tender_repo, tender_award_repo, tender_bid_repo, sample_tender):
    await tender_repo.save(sample_tender)

    from credibil.application.tender.commands import GetTenderByOcidQuery
    from credibil.application.tender.handlers import TenderHandlers

    handlers = TenderHandlers(
        tender_repo=tender_repo, award_repo=tender_award_repo, bid_repo=tender_bid_repo
    )
    result = await handlers.get_tender_by_ocid(GetTenderByOcidQuery(ocid="ocds-b3wdp1-MD-123"))
    assert result.ocid == "ocds-b3wdp1-MD-123"


@pytest.mark.anyio
async def test_get_tender_by_buyer(tender_repo, tender_award_repo, tender_bid_repo, sample_tender):
    await tender_repo.save(sample_tender)

    from credibil.application.tender.commands import GetTendersByBuyerQuery
    from credibil.application.tender.handlers import TenderHandlers

    handlers = TenderHandlers(
        tender_repo=tender_repo, award_repo=tender_award_repo, bid_repo=tender_bid_repo
    )
    result = await handlers.get_tenders_by_buyer(GetTendersByBuyerQuery(idno="1003600150196"))
    assert len(result) == 1
    assert result[0].buyer_idno == "1003600150196"


@pytest.mark.anyio
async def test_get_analytics(
    tender_repo, tender_award_repo, tender_bid_repo, sample_tender, sample_award
):
    await tender_repo.save(sample_tender)
    await tender_award_repo.save(sample_award)

    from credibil.application.tender.commands import GetTenderAnalyticsQuery
    from credibil.application.tender.handlers import TenderHandlers

    handlers = TenderHandlers(
        tender_repo=tender_repo, award_repo=tender_award_repo, bid_repo=tender_bid_repo
    )
    result = await handlers.get_analytics(GetTenderAnalyticsQuery(idno="1003600150196"))
    assert result.idno == "1003600150196"
    assert result.statistics.total_tenders >= 1


@pytest.mark.anyio
async def test_tender_not_found(tender_repo, tender_award_repo, tender_bid_repo):
    from credibil.application.tender.commands import GetTenderByOcidQuery
    from credibil.application.tender.handlers import TenderHandlers
    from credibil.domain.tender.errors import TenderNotFoundError

    handlers = TenderHandlers(
        tender_repo=tender_repo, award_repo=tender_award_repo, bid_repo=tender_bid_repo
    )
    with pytest.raises(TenderNotFoundError):
        await handlers.get_tender_by_ocid(GetTenderByOcidQuery(ocid="nonexistent"))
