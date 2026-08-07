from __future__ import annotations

from credibil.countries.moldova.providers.mtender_provider import (
    parse_awards,
    parse_bids,
    parse_tender,
)
from credibil.domain.tender.entities import (
    AwardStatus,
    BidStatus,
    ProcurementCategory,
    ProcurementMethod,
    TenderStatus,
)

SAMPLE_OCDS_RECORD = {
    "ocid": "ocds-b3wdp1-MD-1779455216051",
    "publishedDate": "2026-05-22T13:06:55Z",
    "records": [
        {
            "ocid": "ocds-b3wdp1-MD-1779455216051",
            "compiledRelease": {
                "ocid": "ocds-b3wdp1-MD-1779455216051",
                "date": "2026-06-15T05:11:50Z",
                "tag": ["compiled"],
                "planning": {
                    "budget": {
                        "amount": {"amount": 410000.0, "currency": "MDL"},
                        "isEuropeanUnionFunded": False,
                    }
                },
                "tender": {
                    "id": "761cc754-207a-46cc-b537-80ad945825af",
                    "title": "piese pentru echipamentul medical",
                    "description": "piese pentru echipamentul medical PENTAX",
                    "status": "active",
                    "statusDetails": "evaluation",
                    "value": {"amount": 410000.0, "currency": "MDL"},
                    "procurementMethod": "open",
                    "procurementMethodDetails": "openTender",
                    "mainProcurementCategory": "goods",
                    "classification": {
                        "scheme": "CPV",
                        "id": "33100000-1",
                        "description": "Echipamente medicale",
                    },
                    "procuringEntity": {
                        "id": "MD-IDNO-1003600150196",
                        "name": "IMSP CRDM",
                    },
                    "contractPeriod": {
                        "startDate": "2026-07-01T00:00:00Z",
                        "endDate": "2026-12-31T00:00:00Z",
                    },
                },
                "parties": [
                    {
                        "id": "MD-IDNO-1003600150196",
                        "name": "IMSP CRDM",
                        "identifier": {"id": "1003600150196"},
                        "roles": ["buyer", "procuringEntity"],
                    }
                ],
            },
        },
        {
            "ocid": "ocds-b3wdp1-MD-1779455216051-EV-1779457581736",
            "compiledRelease": {
                "ocid": "ocds-b3wdp1-MD-1779455216051-EV-1779457581736",
                "date": "2026-06-15T05:11:50Z",
                "tag": ["award"],
                "tender": {
                    "awards": [
                        {
                            "id": "adcd5718-6e07-4921-92d4-3616ddb24ccb",
                            "status": "pending",
                            "statusDetails": "consideration",
                            "date": "2026-06-12T08:00:00Z",
                            "value": {"amount": 246385.0, "currency": "MDL"},
                            "suppliers": [{"id": "1003600117582", "name": "GBG-MLD SRL"}],
                            "relatedLots": ["4d323544-2288-4547-b41e-435a6277054d"],
                            "relatedBid": "a0914b17-1d1f-4546-ac74-15bb7bb971e7",
                        }
                    ],
                    "bids": {
                        "details": [
                            {
                                "id": "a0914b17-1d1f-4546-ac74-15bb7bb971e7",
                                "date": "2026-06-11T14:59:56Z",
                                "status": "pending",
                                "tenderers": [{"id": "1003600117582", "name": "GBG-MLD SRL"}],
                                "value": {"amount": 246385.0, "currency": "MDL"},
                                "relatedLots": ["4d323544-2288-4547-b41e-435a6277054d"],
                            }
                        ]
                    },
                },
            },
        },
    ],
}


class TestParseTender:
    def test_parse_basic(self):
        tender = parse_tender(SAMPLE_OCDS_RECORD)
        assert tender is not None
        assert tender.ocid == "ocds-b3wdp1-MD-1779455216051"
        assert tender.title == "piese pentru echipamentul medical"
        assert tender.status == TenderStatus.ACTIVE
        assert tender.status_details == "evaluation"

    def test_parse_procurement_method(self):
        tender = parse_tender(SAMPLE_OCDS_RECORD)
        assert tender is not None
        assert tender.procurement_method == ProcurementMethod.OPEN
        assert tender.procurement_method_details == "openTender"

    def test_parse_category(self):
        tender = parse_tender(SAMPLE_OCDS_RECORD)
        assert tender is not None
        assert tender.main_category == ProcurementCategory.GOODS

    def test_parse_cpv(self):
        tender = parse_tender(SAMPLE_OCDS_RECORD)
        assert tender is not None
        assert tender.cpv_code == "33100000-1"
        assert tender.cpv_description == "Echipamente medicale"

    def test_parse_buyer(self):
        tender = parse_tender(SAMPLE_OCDS_RECORD)
        assert tender is not None
        assert tender.buyer_idno == "1003600150196"
        assert tender.buyer_name == "IMSP CRDM"

    def test_parse_value(self):
        tender = parse_tender(SAMPLE_OCDS_RECORD)
        assert tender is not None
        assert tender.value_amount == 410000.0
        assert tender.value_currency == "MDL"

    def test_parse_budget(self):
        tender = parse_tender(SAMPLE_OCDS_RECORD)
        assert tender is not None
        assert tender.budget_amount == 410000.0
        assert tender.is_eu_funded is False

    def test_parse_contract_period(self):
        tender = parse_tender(SAMPLE_OCDS_RECORD)
        assert tender is not None
        assert tender.contract_start_date is not None
        assert tender.contract_end_date is not None

    def test_parse_empty_record(self):
        assert parse_tender({"ocid": "x", "records": []}) is None

    def test_parse_no_records(self):
        assert parse_tender({"ocid": "x"}) is None


class TestParseAwards:
    def test_parse_awards(self):
        awards = parse_awards(SAMPLE_OCDS_RECORD)
        assert len(awards) == 1
        award = awards[0]
        assert award.tender_ocid == "ocds-b3wdp1-MD-1779455216051"
        assert award.status == AwardStatus.PENDING
        assert award.value_amount == 246385.0
        assert award.supplier_name == "GBG-MLD SRL"
        assert award.supplier_idno == "1003600117582"
        assert len(award.related_lots) == 1

    def test_parse_awards_empty(self):
        awards = parse_awards({"ocid": "x", "records": []})
        assert awards == []


class TestParseBids:
    def test_parse_bids(self):
        bids = parse_bids(SAMPLE_OCDS_RECORD)
        assert len(bids) == 1
        bid = bids[0]
        assert bid.tender_ocid == "ocds-b3wdp1-MD-1779455216051"
        assert bid.status == BidStatus.PENDING
        assert bid.value_amount == 246385.0
        assert bid.tenderer_name == "GBG-MLD SRL"

    def test_parse_bids_empty(self):
        bids = parse_bids({"ocid": "x", "records": []})
        assert bids == []
