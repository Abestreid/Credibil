"""Provider for company data from date.gov.md (Moldova Government Data Portal).

Uses FlareSolverr to bypass Cloudflare and reCAPTCHA protection.
The portal provides tax debt information (Restanțe față de bugetul de stat).
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from typing import Any

import httpx

logger = logging.getLogger(__name__)

FLARESOLVERR_URL = "http://credibil-flaresolverr-1:8191/v1"
DATE_GOV_URL = "https://date.gov.md/open/company-details"
DATE_GOV_API_URL = "https://date.gov.md/open/data/4482c1ae-76fe-e911-80e4-0050568b7cd9"
CLIENT_TIMEOUT = 180


@dataclass
class CompanyDebtResult:
    idno: str
    has_debt: bool
    total_amount: float | None
    currency: str
    debt_details: list[dict[str, Any]]
    company_name: str | None
    fetched_at: str | None
    raw_html: str
    error: str | None = None


def _parse_debt_html(html: str, idno: str) -> CompanyDebtResult:
    """Parse the HTML response from date.gov.md to extract tax debt information."""
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        return CompanyDebtResult(
            idno=idno, has_debt=False, total_amount=None,
            currency="MDL", debt_details=[], company_name=None,
            fetched_at=None, raw_html=html,
            error="beautifulsoup4 not installed",
        )

    soup = BeautifulSoup(html, "html.parser")
    text_content = soup.get_text(separator=" ", strip=True)
    text_lower = text_content.lower()

    # Check if company was found
    if "resursa inexistentă" in text_lower or "resursa nu a fost gasita" in text_lower:
        return CompanyDebtResult(
            idno=idno, has_debt=False, total_amount=None,
            currency="MDL", debt_details=[], company_name=None,
            fetched_at=None, raw_html=html,
            error="Company not found on date.gov.md",
        )

    # Extract company name
    company_name = None
    name_el = soup.find("h2", class_="company-name")
    if name_el:
        company_name = name_el.get_text(strip=True)

    # Look for "Restanțe față de bugetul de stat" section
    debt_section = None
    for h3 in soup.find_all(["h3", "h4", "strong"]):
        if "restanț" in h3.get_text(strip=True).lower() or "restante" in h3.get_text(strip=True).lower():
            debt_section = h3.parent
            break

    if not debt_section:
        # Try to find debt info in the full text
        debt_match = re.search(
            r"restan[țt]e?\s+fa[țt][ăa]\s+bugetul(?:ului)?\s+de\s+stat[:\s]*([\d\s,.]+)\s*(MDL|mdl)?",
            text_content, re.IGNORECASE,
        )
        if debt_match:
            amount_str = debt_match.group(1).replace(" ", "").replace(",", ".")
            try:
                amount = float(amount_str)
                return CompanyDebtResult(
                    idno=idno, has_debt=amount > 0, total_amount=amount,
                    currency="MDL", debt_details=[], company_name=company_name,
                    fetched_at=None, raw_html=html,
                )
            except ValueError:
                pass

        # No debt section found - assume no debt
        return CompanyDebtResult(
            idno=idno, has_debt=False, total_amount=0.0,
            currency="MDL", debt_details=[], company_name=company_name,
            fetched_at=None, raw_html=html,
        )

    # Parse debt details from the section
    debt_details = []
    total_amount = 0.0

    table = debt_section.find("table")
    if table:
        rows = table.find_all("tr")
        for row in rows:
            cells = row.find_all(["td", "th"])
            if len(cells) >= 2:
                label = cells[0].get_text(strip=True)
                value = cells[1].get_text(strip=True)
                # Try to parse monetary amounts
                amount_match = re.search(r"([\d\s,.]+)\s*(MDL|mdl)?", value)
                if amount_match:
                    amount_str = amount_match.group(1).replace(" ", "").replace(",", ".")
                    try:
                        amount = float(amount_str)
                        debt_details.append({"label": label, "amount": amount, "currency": "MDL"})
                        total_amount += amount
                    except ValueError:
                        debt_details.append({"label": label, "amount": value, "currency": None})
                else:
                    debt_details.append({"label": label, "amount": value, "currency": None})

    # If no table, try to extract from text
    if not debt_details:
        amounts = re.findall(r"([\d\s,.]+)\s*MDL", text_content)
        for amt_str in amounts:
            amt_str = amt_str.replace(" ", "").replace(",", ".")
            try:
                amount = float(amt_str)
                total_amount += amount
                debt_details.append({"label": "Restanțe", "amount": amount, "currency": "MDL"})
            except ValueError:
                pass

    return CompanyDebtResult(
        idno=idno,
        has_debt=total_amount > 0,
        total_amount=total_amount if total_amount > 0 else 0.0,
        currency="MDL",
        debt_details=debt_details,
        company_name=company_name,
        fetched_at=None,
        raw_html=html,
    )


class DateGovProvider:
    """Fetches company data from date.gov.md using FlareSolverr.

    FlareSolverr handles Cloudflare bypass, reCAPTCHA solving, and session management.
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

    async def fetch_company_debt(self, idno: str, session_id: str | None = None) -> CompanyDebtResult:
        """Fetch tax debt for a single IDNO from date.gov.md."""
        own_session = session_id is None
        if own_session:
            session_id = await self._create_session()

        try:
            # Step 1: Navigate to the company details page
            page_url = f"{DATE_GOV_URL}?idno={idno}"
            logger.info("Fetching company details from %s", page_url)

            page_data = await self._flare_call({
                "cmd": "request.get",
                "url": page_url,
                "session": session_id,
                "maxTimeout": 60000,
            })

            if page_data.get("status") != "ok":
                error_msg = page_data.get("message", "Failed to load page")
                return CompanyDebtResult(
                    idno=idno, has_debt=False, total_amount=None,
                    currency="MDL", debt_details=[], company_name=None,
                    fetched_at=None, raw_html="", error=error_msg,
                )

            page_html = page_data.get("solution", {}).get("response", "")

            # Step 2: The page has reCAPTCHA that auto-submits.
            # FlareSolverr should handle this. Wait for the data to load.
            # The API endpoint returns JSON with fragment content.
            # Try to extract debt info directly from the page HTML first.
            result = _parse_debt_html(page_html, idno)
            if result.error is None:
                return result

            # Step 3: If page parsing failed, try the API directly
            logger.info("Trying API endpoint for %s", idno)
            api_data = await self._flare_call({
                "cmd": "request.post",
                "url": DATE_GOV_API_URL,
                "postData": json.dumps({"inputData": json.dumps({"idno": idno})}),
                "session": session_id,
                "maxTimeout": 60000,
            })

            if api_data.get("status") == "ok":
                api_response = api_data.get("solution", {}).get("response", "")
                # Try to parse as JSON
                try:
                    fragments = json.loads(api_response)
                    for fragment in fragments:
                        if "content" in fragment:
                            result = _parse_debt_html(fragment["content"], idno)
                            if result.error is None:
                                return result
                except (json.JSONDecodeError, TypeError):
                    # Not JSON, try as HTML
                    result = _parse_debt_html(api_response, idno)
                    if result.error is None:
                        return result

            # Return the original result even with error
            return result

        except httpx.TimeoutException:
            return CompanyDebtResult(
                idno=idno, has_debt=False, total_amount=None,
                currency="MDL", debt_details=[], company_name=None,
                fetched_at=None, raw_html="", error="FlareSolverr timeout",
            )
        except Exception as e:
            logger.error("Error fetching debt for %s: %s", idno, e)
            return CompanyDebtResult(
                idno=idno, has_debt=False, total_amount=None,
                currency="MDL", debt_details=[], company_name=None,
                fetched_at=None, raw_html="", error=str(e),
            )
        finally:
            if own_session:
                await self._destroy_session(session_id)

    async def fetch_company_debt_batch(
        self,
        idnos: list[str],
        delay_seconds: float = 2.0,
        reuse_session: bool = True,
    ) -> dict[str, CompanyDebtResult]:
        """Fetch tax debt for multiple IDNOs."""
        results: dict[str, CompanyDebtResult] = {}
        session_id = await self._create_session() if reuse_session else None

        try:
            for i, idno in enumerate(idnos):
                if i > 0:
                    import asyncio
                    await asyncio.sleep(delay_seconds)

                if session_id:
                    results[idno] = await self.fetch_company_debt(idno, session_id)
                else:
                    results[idno] = await self.fetch_company_debt(idno)

                # Log progress
                if (i + 1) % 10 == 0:
                    logger.info("Fetched debt for %d/%d companies", i + 1, len(idnos))

            return results
        finally:
            if session_id:
                await self._destroy_session(session_id)

    async def close(self) -> None:
        await self._client.aclose()
