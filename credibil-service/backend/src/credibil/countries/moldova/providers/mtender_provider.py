from __future__ import annotations

import logging
from datetime import date, datetime
from typing import Any

import httpx

from credibil.domain.tender.entities import (
    AwardStatus,
    BidStatus,
    ProcurementCategory,
    ProcurementMethod,
    Tender,
    TenderAward,
    TenderBid,
    TenderStatus,
)
from credibil.domain.tender.errors import TenderFetchError, TenderSyncError

logger = logging.getLogger(__name__)

MTENDER_BASE = "https://public.mtender.gov.md"


class MTenderProvider:
    """Provider that fetches procurement data from mtender.gov.md via OCDS API.

    The API returns data in Open Contracting Data Standard (OCDS) format.
    Endpoint: GET /tenders - lists tenders with ocid and date (cursor-based pagination)
    Endpoint: GET /tenders/{ocid} - full tender record with releases
    """

    def __init__(self) -> None:
        self._client = httpx.AsyncClient(
            timeout=30.0,
            follow_redirects=True,
            headers={
                "User-Agent": "Mozilla/5.0 (compatible; CredibilBot/1.0)",
                "Accept": "application/json",
            },
        )

    async def close(self) -> None:
        await self._client.aclose()

    async def list_tenders(
        self,
        offset: str | None = None,
        limit: int = 100,
    ) -> tuple[list[dict[str, str]], str | None]:
        """List tender IDs with cursor-based pagination.

        Returns:
            Tuple of (list of {ocid, date} dicts, next offset string).
        """
        params: dict[str, Any] = {"limit": limit}
        if offset:
            params["offset"] = offset

        try:
            resp = await self._client.get(f"{MTENDER_BASE}/tenders", params=params)
            resp.raise_for_status()
            data = resp.json()
            return data.get("data", []), data.get("offset")
        except httpx.HTTPStatusError as e:
            raise TenderSyncError(f"HTTP {e.response.status_code}") from e
        except Exception as e:
            raise TenderSyncError(str(e)) from e

    async def fetch_tender(self, ocid: str) -> dict[str, Any]:
        """Fetch full tender record by OCID.

        Returns the raw OCDS JSON record.
        """
        try:
            resp = await self._client.get(f"{MTENDER_BASE}/tenders/{ocid}")
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPStatusError as e:
            raise TenderFetchError(ocid, f"HTTP {e.response.status_code}") from e
        except Exception as e:
            raise TenderFetchError(ocid, str(e)) from e

    async def fetch_recent_tenders(
        self, since: str | None = None, limit: int = 100
    ) -> list[dict[str, Any]]:
        """Fetch recent tenders with full details.

        Args:
            since: ISO timestamp cursor to paginate from.
            limit: Number of tenders to fetch.

        Returns:
            List of full OCDS tender records.
        """
        ocids, _ = await self.list_tenders(offset=since, limit=limit)
        records: list[dict[str, Any]] = []
        for entry in ocids:
            ocid = entry.get("ocid", "")
            if ocid:
                try:
                    record = await self.fetch_tender(ocid)
                    records.append(record)
                except TenderFetchError:
                    logger.warning("Failed to fetch tender %s, skipping", ocid)
        return records

    async def health_check(self) -> bool:
        try:
            resp = await self._client.get(f"{MTENDER_BASE}/tenders", params={"limit": 1})
            return resp.status_code == 200
        except Exception:
            return False


def parse_tender(record: dict[str, Any]) -> Tender | None:
    """Parse an OCDS tender record into a Tender entity.

    The record contains 'records' array. The first record with tag 'compiled'
    contains the full tender info.
    """
    records = record.get("records", [])
    if not records:
        return None

    compiled_release = None

    for r in records:
        cr = r.get("compiledRelease", {})
        tags = cr.get("tag", [])
        if "compiled" in tags:
            compiled_release = cr
        if "award" in tags:
            pass
        if "tender" in tags and "award" not in tags:
            pass

    if not compiled_release:
        compiled_release = records[0].get("compiledRelease", {})

    tender_data = compiled_release.get("tender", {})
    planning_data = compiled_release.get("planning", {})
    parties = compiled_release.get("parties", [])

    ocid = record.get("ocid", "")
    if not ocid:
        return None

    title = tender_data.get("title", "")
    description = tender_data.get("description")
    status_str = tender_data.get("status", "planning")
    status_details = tender_data.get("statusDetails")

    try:
        status = TenderStatus(status_str)
    except ValueError:
        status = TenderStatus.PLANNING

    method_str = tender_data.get("procurementMethod")
    procurement_method = None
    if method_str:
        try:
            procurement_method = ProcurementMethod(method_str)
        except ValueError:
            procurement_method = None

    method_details = tender_data.get("procurementMethodDetails")

    category_str = tender_data.get("mainProcurementCategory")
    main_category = None
    if category_str:
        try:
            main_category = ProcurementCategory(category_str)
        except ValueError:
            main_category = None

    classification = tender_data.get("classification", {})
    cpv_code = classification.get("id")
    cpv_description = classification.get("description")

    buyer_idno = None
    buyer_name = None
    for party in parties:
        roles = party.get("roles", [])
        if "buyer" in roles or "procuringEntity" in roles:
            ident = party.get("identifier", {})
            buyer_idno = ident.get("id")
            buyer_name = party.get("name")
            break

    if not buyer_idno:
        procuring = tender_data.get("procuringEntity", {})
        buyer_idno = procuring.get("id")
        buyer_name = procuring.get("name")

    value = tender_data.get("value", {})
    value_amount = value.get("amount")
    value_currency = value.get("currency")

    budget_data = planning_data.get("budget", {})
    budget_amount_data = budget_data.get("amount", {})
    budget_amount = budget_amount_data.get("amount")
    budget_currency = budget_amount_data.get("currency")
    is_eu_funded = budget_data.get("isEuropeanUnionFunded", False)

    tender_period = tender_data.get("tenderPeriod", {})
    tender_start_str = tender_period.get("startDate")
    tender_end_str = tender_period.get("endDate")
    tender_start_date = _parse_date_str(tender_start_str)
    tender_end_date = _parse_date_str(tender_end_str)

    contract_period = tender_data.get("contractPeriod", {})
    contract_start_str = contract_period.get("startDate")
    contract_end_str = contract_period.get("endDate")
    contract_start_date = _parse_date_str(contract_start_str)
    contract_end_date = _parse_date_str(contract_end_str)

    published_str = record.get("publishedDate") or compiled_release.get("date")
    published_date = _parse_datetime_str(published_str)

    source_url = f"{MTENDER_BASE}/tenders/{ocid}"

    return Tender(
        ocid=ocid,
        title=title,
        description=description,
        status=status,
        status_details=status_details,
        procurement_method=procurement_method,
        procurement_method_details=method_details,
        main_category=main_category,
        cpv_code=cpv_code,
        cpv_description=cpv_description,
        buyer_idno=buyer_idno,
        buyer_name=buyer_name,
        value_amount=value_amount,
        value_currency=value_currency,
        budget_amount=budget_amount,
        budget_currency=budget_currency,
        is_eu_funded=is_eu_funded,
        tender_start_date=tender_start_date,
        tender_end_date=tender_end_date,
        contract_start_date=contract_start_date,
        contract_end_date=contract_end_date,
        published_date=published_date,
        source_url=source_url,
        raw_data=record,
    )


def parse_awards(record: dict[str, Any]) -> list[TenderAward]:
    """Parse awards from an OCDS tender record."""
    awards: list[TenderAward] = []
    records = record.get("records", [])

    for r in records:
        cr = r.get("compiledRelease", {})
        tags = cr.get("tag", [])
        if "award" not in tags:
            continue

        tender_data = cr.get("tender", {})
        ocds_awards = tender_data.get("awards", [])
        ocid = record.get("ocid", "")

        for award_data in ocds_awards:
            award_id_str = award_data.get("id")
            status_str = award_data.get("status", "pending")
            try:
                award_status = AwardStatus(status_str)
            except ValueError:
                award_status = AwardStatus.PENDING

            award_date_str = award_data.get("date")
            award_date = _parse_date_str(award_date_str)

            value = award_data.get("value", {})
            value_amount = value.get("amount")
            value_currency = value.get("currency")

            suppliers = award_data.get("suppliers", [])
            supplier_idno = None
            supplier_name = None
            if suppliers:
                supplier_idno = suppliers[0].get("id")
                supplier_name = suppliers[0].get("name")

            related_lots = award_data.get("relatedLots", [])
            related_bid = award_data.get("relatedBid")

            awards.append(
                TenderAward(
                    tender_ocid=ocid,
                    ocds_award_id=award_id_str,
                    status=award_status,
                    status_details=award_data.get("statusDetails"),
                    award_date=award_date,
                    value_amount=value_amount,
                    value_currency=value_currency,
                    supplier_idno=supplier_idno,
                    supplier_name=supplier_name,
                    related_lots=related_lots,
                    related_bid_id=related_bid,
                    source_url=f"{MTENDER_BASE}/tenders/{ocid}",
                    raw_data=award_data,
                )
            )

    return awards


def parse_bids(record: dict[str, Any]) -> list[TenderBid]:
    """Parse bids from an OCDS tender record."""
    bids: list[TenderBid] = []
    records = record.get("records", [])

    for r in records:
        cr = r.get("compiledRelease", {})
        tags = cr.get("tag", [])
        if "tender" not in tags and "award" not in tags:
            continue

        tender_data = cr.get("tender", {})
        bids_data = tender_data.get("bids", {})
        details = bids_data.get("details", [])
        ocid = record.get("ocid", "")

        for bid_data in details:
            bid_id_str = bid_data.get("id")
            status_str = bid_data.get("status", "pending")
            try:
                bid_status = BidStatus(status_str)
            except ValueError:
                bid_status = BidStatus.PENDING

            bid_date_str = bid_data.get("date")
            bid_date = _parse_date_str(bid_date_str)

            value = bid_data.get("value", {})
            value_amount = value.get("amount")
            value_currency = value.get("currency")

            tenderers = bid_data.get("tenderers", [])
            tenderer_idno = None
            tenderer_name = None
            if tenderers:
                tenderer_idno = tenderers[0].get("id")
                tenderer_name = tenderers[0].get("name")

            related_lots = bid_data.get("relatedLots", [])

            bids.append(
                TenderBid(
                    tender_ocid=ocid,
                    ocds_bid_id=bid_id_str,
                    status=bid_status,
                    bid_date=bid_date,
                    value_amount=value_amount,
                    value_currency=value_currency,
                    tenderer_idno=tenderer_idno,
                    tenderer_name=tenderer_name,
                    related_lots=related_lots,
                    source_url=f"{MTENDER_BASE}/tenders/{ocid}",
                    raw_data=bid_data,
                )
            )

    return bids


def _parse_date_str(s: str | None) -> date | None:
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00")).date()
    except (ValueError, TypeError):
        return None


def _parse_datetime_str(s: str | None) -> datetime | None:
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None
