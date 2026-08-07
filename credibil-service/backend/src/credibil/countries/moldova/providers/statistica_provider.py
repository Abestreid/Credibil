from __future__ import annotations

import contextlib
import logging
import re
from typing import Any

import httpx

from credibil.domain.financial.errors import FinancialReportFetchError

logger = logging.getLogger(__name__)

STATISTICA_URL = "https://webapp.statistica.md/infoRSF/"


class StatisticaProvider:
    """On-demand provider that fetches financial statements from statistica.md.

    The portal has CAPTCHA (max 20 queries/day), so this is strictly on-demand.
    """

    def __init__(self) -> None:
        self._client = httpx.AsyncClient(
            timeout=30.0,
            headers={
                "User-Agent": "Mozilla/5.0 (compatible; CredibilBot/1.0)",
                "Accept": "text/html,application/xhtml+xml",
            },
        )

    async def close(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> StatisticaProvider:
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()

    async def fetch_financial_data(self, idno: str, year: int) -> dict[str, Any]:
        """Fetch financial indicators for a company by IDNO and year.

        Returns a dict with keys matching FinancialReport fields.
        Raises FinancialReportFetchError on failure.
        """
        try:
            resp = await self._client.get(
                STATISTICA_URL,
                params={"idno": idno, "an": str(year)},
            )
            resp.raise_for_status()
            result = self._parse_response(resp.text, idno, year)
            if result is None:
                return None
            return result
        except FinancialReportFetchError:
            raise
        except httpx.HTTPStatusError as e:
            raise FinancialReportFetchError(idno, f"HTTP {e.response.status_code}") from e
        except Exception as e:
            raise FinancialReportFetchError(idno, str(e)) from e

    async def health_check(self) -> bool:
        try:
            resp = await self._client.get(STATISTICA_URL)
            return resp.status_code == 200
        except Exception:
            return False

    def _parse_response(self, html: str, idno: str, year: int) -> dict[str, Any] | None:
        """Parse the HTML response from statistica.md into structured data.

        Returns None if the page is a CAPTCHA/search form instead of actual data.
        """
        # Detect CAPTCHA page or empty search form
        if "afisari pe zi" in html or "cod-text din imagine" in html or "Introduceti IDNO" in html:
            logger.info("Statistica returned CAPTCHA/search page for %s/%d, skipping", idno, year)
            return None

        data: dict[str, Any] = {
            "company_name": None,
            "caem_code": None,
            "caem_description": None,
            "business_category": None,
            "revenue": None,
            "expenses": None,
            "total_assets": None,
            "total_liabilities": None,
            "equity": None,
            "profit": None,
            "employees_count": None,
            "raw_data": {},
        }

        name_match = re.search(r"Denumire:\s*</[^>]+>\s*<[^>]+>([^<]+)", html)
        if name_match:
            data["company_name"] = name_match.group(1).strip()

        caem_match = re.search(r"CAEM2?:\s*</[^>]+>\s*<[^>]+>([^<]+)", html)
        if caem_match:
            data["caem_code"] = caem_match.group(1).strip()

        indicator_rows = re.findall(
            r"<tr[^>]*>\s*<td[^>]*>(.*?)</td>\s*<td[^>]*>(.*?)</td>\s*</tr>",
            html,
            re.DOTALL,
        )

        indicator_map = self._build_indicator_map()

        for label_raw, value_raw in indicator_rows:
            label = re.sub(r"<[^>]+>", "", label_raw).strip()
            value_str = re.sub(r"<[^>]+>", "", value_raw).strip()
            value_str = value_str.replace(".", "").replace(",", ".")
            value_str = re.sub(r"[^\d.\-]", "", value_str)

            data["raw_data"][label] = value_str

            for field_name, patterns in indicator_map.items():
                if any(p.lower() in label.lower() for p in patterns):
                    with contextlib.suppress(ValueError, TypeError):
                        data[field_name] = float(value_str) if value_str else None

        # Return None if no actual financial data was parsed
        financial_fields = ["revenue", "expenses", "total_assets", "total_liabilities", "equity", "profit"]
        if not any(data[f] is not None for f in financial_fields):
            logger.info("Statistica returned no financial indicators for %s/%d", idno, year)
            return None

        return data

    def _build_indicator_map(self) -> dict[str, list[str]]:
        """Map field names to search patterns in Romanian indicator labels."""
        return {
            "revenue": [
                "venituri din vânzări",
                "venituri totale",
                "venitul din vânzări",
                "veniturile totale",
                "venituri",
            ],
            "expenses": [
                "cheltuieli totale",
                "cheltuielile totale",
                "cheltuieli",
            ],
            "total_assets": [
                "active totale",
                "activele totale",
                "active",
                "total active",
            ],
            "total_liabilities": [
                "pasive totale",
                "pasivele totale",
                "pasive",
                "datorii totale",
            ],
            "equity": [
                "capital propriu",
                "capitalul propriu",
                "fonduri proprii",
            ],
            "profit": [
                "profitul net",
                "profit net",
                "profit",
                "rezultatul net",
            ],
            "employees_count": [
                "numărul angajaților",
                "personal",
                "angajați",
                "salariati",
            ],
        }
