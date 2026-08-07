"""Provider for tax debt information from the Moldovan Tax Service (SFS).

Uses FlareSolverr (undetected_chromedriver + Selenium) to bypass Cloudflare,
submit the tax debt search form, and parse the result.
FlareSolverr runs as a separate container (credibil-flaresolverr-1:8191).
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Any

import httpx

logger = logging.getLogger(__name__)

FLARESOLVERR_URL = "http://credibil-flaresolverr-1:8191/v1"
SFS_URL = "https://sfs.md/ro/services-online/route.taxpayer_information"
CLIENT_TIMEOUT = 180


@dataclass
class TaxDebtResult:
    idno: str
    has_debt: bool
    total_amount: float | None
    currency: str
    debt_details: list[dict[str, Any]]
    company_name: str | None
    fetched_at: str | None
    raw_html: str
    error: str | None = None


def _parse_tax_debt_html(full_html: str, idno: str) -> TaxDebtResult:
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        return TaxDebtResult(
            idno=idno, has_debt=False, total_amount=None,
            currency="MDL", debt_details=[], company_name=None,
            fetched_at=None, raw_html=full_html,
            error="beautifulsoup4 not installed",
        )

    soup = BeautifulSoup(full_html, "html.parser")
    text_content = soup.get_text(separator=" ", strip=True)
    text_lower = text_content.lower()

    taxpayer_not_found = any(p in text_lower for p in [
        "contribuabilul nu a fost găsit",
        "contribuabilul nu a fost gasit",
        "nu a fost găsit",
    ])
    if taxpayer_not_found:
        return TaxDebtResult(
            idno=idno, has_debt=False, total_amount=0.0,
            currency="MDL", debt_details=[], company_name=None,
            fetched_at=None, raw_html=full_html,
        )

    company_name = None
    nf = soup.find(id="response-info")
    if nf:
        table = nf.find("table", class_="services-table")
        if table:
            rows = table.find_all("tr")
            for row in rows:
                cells = row.find_all("td")
                if len(cells) == 2:
                    label = cells[0].get_text(strip=True).lower()
                    value = cells[1].get_text(strip=True)
                    if "denumire" == label:
                        company_name = value.strip()

    no_debt_indicators = [
        "lipsește restanță",
        "lipseste restanta",
        "nu înregistrează restanță",
        "nu inregistreaza restanta",
        "nu există datorii",
        "nu exista datorii",
        "fără datorii",
        "fara datorii",
        "nu sunt datorii",
    ]
    if any(ind in text_lower for ind in no_debt_indicators):
        fetched_at = None
        date_match = re.search(
            r"La situația din (\d{2}\.\d{2}\.\d{4})",
            text_content, re.IGNORECASE,
        )
        if date_match:
            fetched_at = date_match.group(1)
        return TaxDebtResult(
            idno=idno, has_debt=False, total_amount=0.0,
            currency="MDL", debt_details=[], company_name=company_name,
            fetched_at=fetched_at, raw_html=full_html,
        )

    debt_details: list[dict[str, Any]] = []
    debt_keywords = {"restanță", "datorie", "suma", "lei", "total", "plată", "achitat"}
    amount_pattern = re.compile(r"(\d{1,3}(?:[\s\xa0]\d{3})*(?:\.\d{2})?)")

    tables = soup.find_all("table")
    for table in tables:
        table_text = table.get_text(strip=True).lower()
        is_debt_table = any(kw in table_text for kw in debt_keywords)
        if not is_debt_table:
            continue

        rows = table.find_all("tr")
        for row in rows:
            cells = row.find_all(["td", "th"])
            if len(cells) < 2:
                continue
            row_text = [cell.get_text(strip=True) for cell in cells]
            for cell_text in row_text:
                amount_match = amount_pattern.search(cell_text)
                if amount_match:
                    amount_str = amount_match.group(1).replace(
                        "\xa0", ""
                    ).replace(" ", "")
                    try:
                        amount = float(amount_str)
                        if amount > 0:
                            debt_details.append({
                                "period": row_text[0] if len(row_text) > 0 else "",
                                "type": row_text[1] if len(row_text) > 1 else "",
                                "amount": amount,
                            })
                    except ValueError:
                        continue

    if debt_details:
        total_amount = sum(d["amount"] for d in debt_details)
        has_debt = total_amount > 0
    else:
        has_debt = False
        total_amount = 0.0

    fetched_at = None
    date_match = re.search(
        r"La situația din (\d{2}\.\d{2}\.\d{4})",
        text_content, re.IGNORECASE,
    )
    if date_match:
        fetched_at = date_match.group(1)

    return TaxDebtResult(
        idno=idno, has_debt=has_debt, total_amount=total_amount,
        currency="MDL", debt_details=debt_details,
        company_name=company_name, fetched_at=fetched_at,
        raw_html=full_html,
    )


class SFSProvider:
    """Fetches tax debt using FlareSolverr (Selenium + undetected_chromedriver).

    Communicates with the FlareSolverr container via its HTTP API.
    FlareSolverr handles Cloudflare bypass, session management, and form submission.
    """

    def __init__(
        self,
        flaresolverr_url: str = FLARESOLVERR_URL,
        timeout_seconds: int = CLIENT_TIMEOUT,
    ) -> None:
        self.flaresolverr_url = flaresolverr_url
        self.timeout_seconds = timeout_seconds
        self._client = httpx.AsyncClient(timeout=httpx.Timeout(timeout_seconds))

    async def _flare_call(self, payload: dict) -> dict:
        resp = await self._client.post(self.flaresolverr_url, json=payload)
        resp.raise_for_status()
        return resp.json()

    async def _create_session(self) -> str:
        data = await self._flare_call({"cmd": "sessions.create"})
        session_id = data.get("session")
        logger.debug("Created FlareSolverr session %s", session_id)
        return session_id

    async def _destroy_session(self, session_id: str) -> None:
        try:
            await self._flare_call({"cmd": "sessions.destroy", "session": session_id})
        except Exception as e:
            logger.warning("Failed to destroy FlareSolverr session %s: %s", session_id, e)

    async def _fetch_one(self, idno: str, session_id: str) -> TaxDebtResult:
        """Fetch tax debt for a single IDNO using an existing session."""
        try:
            data = await self._flare_call({
                "cmd": "request.post",
                "url": SFS_URL,
                "postData": f"idno={idno}",
                "session": session_id,
                "maxTimeout": 120000,
            })

            if data.get("status") != "ok":
                error_msg = data.get("message", "Unknown FlareSolverr error")
                return TaxDebtResult(
                    idno=idno, has_debt=False, total_amount=None,
                    currency="MDL", debt_details=[], company_name=None,
                    fetched_at=None, raw_html="", error=error_msg,
                )

            sol = data.get("solution", {})
            resp_html = sol.get("response", "")
            return _parse_tax_debt_html(resp_html, idno)

        except httpx.TimeoutException:
            return TaxDebtResult(
                idno=idno, has_debt=False, total_amount=None,
                currency="MDL", debt_details=[], company_name=None,
                fetched_at=None, raw_html="", error="FlareSolverr timeout",
            )
        except Exception as e:
            return TaxDebtResult(
                idno=idno, has_debt=False, total_amount=None,
                currency="MDL", debt_details=[], company_name=None,
                fetched_at=None, raw_html="", error=str(e),
            )

    async def fetch_tax_debt(self, idno: str) -> TaxDebtResult:
        """Fetch tax debt for a single IDNO (creates its own session)."""
        session_id = await self._create_session()
        try:
            return await self._fetch_one(idno, session_id)
        finally:
            await self._destroy_session(session_id)

    async def fetch_tax_debt_batch(
        self,
        idnos: list[str],
        delay_seconds: float = 1.0,
        reuse_session: bool = True,
    ) -> dict[str, TaxDebtResult]:
        """Fetch tax debt for multiple IDNOs.

        When reuse_session=True (default), a single FlareSolverr session is used
        for all requests, saving browser launch + Cloudflare challenge overhead.
        The session is destroyed when the batch completes.

        Returns a dict mapping idno -> TaxDebtResult.
        """
        results: dict[str, TaxDebtResult] = {}
        session_id = await self._create_session() if reuse_session else None

        try:
            for i, idno in enumerate(idnos):
                if i > 0:
                    import asyncio
                    await asyncio.sleep(delay_seconds)

                if session_id:
                    results[idno] = await self._fetch_one(idno, session_id)
                else:
                    results[idno] = await self.fetch_tax_debt(idno)

            return results
        finally:
            if session_id:
                await self._destroy_session(session_id)

    async def close(self) -> None:
        await self._client.aclose()
