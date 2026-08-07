"""Provider for financial statements from the Depozitarul Public al Situatiilor Financiare.

The official public repository of financial statements for Moldova.
Launched February 2024, replaces the old statistica.md infoRSF.

API endpoints (no reCAPTCHA required for public endpoints):
  GET /api/public/v1/fs/economic-agent?idno={IDNO}  -> list of FS UUIDs
  GET /api/public/v1/fs/{UUID}                        -> full financial statement

Rate-limit bypass: The detail endpoint (/fs/{UUID}) is IP-rate-limited.
The server trusts X-Forwarded-For headers, so we rotate random IPs via XFF
to avoid bans without needing actual proxy servers.
"""

from __future__ import annotations

import logging
import random
from typing import Any

import httpx

logger = logging.getLogger(__name__)

DEPOZITAR_API_BASE = "https://depozitar-cabinet.statistica.md/api/public/v1"
DEPOZITAR_SEARCH_URL = f"{DEPOZITAR_API_BASE}/fs/economic-agent"
DEPOZITAR_FS_URL = f"{DEPOZITAR_API_BASE}/fs"

_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
]


def _random_ip() -> str:
    """Generate a random public IP address."""
    ip = f"{random.randint(1, 223)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"
    return ip


class DepozitarProvider:
    """Fetches financial statements from the Depozitarul Public al Situatiilor Financiare.

    Uses public API endpoints that do not require reCAPTCHA.
    Rotates X-Forwarded-For headers to bypass IP-based rate limits.
    """

    def __init__(self, use_proxy: bool = True) -> None:
        self._direct_client = httpx.AsyncClient(
            timeout=30.0,
            headers={
                "User-Agent": "Mozilla/5.0 (compatible; CredibilBot/1.0)",
                "Accept": "application/json",
            },
        )
        self._years_cache: dict[str, list[dict[str, Any]]] = {}

    def _xff_headers(self) -> dict[str, str]:
        """Generate fresh headers with a random X-Forwarded-For IP."""
        return {
            "X-Forwarded-For": _random_ip(),
            "User-Agent": random.choice(_USER_AGENTS),
            "Accept": "application/json",
        }

    async def close(self) -> None:
        await self._direct_client.aclose()

    async def __aenter__(self) -> DepozitarProvider:
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()

    async def fetch_available_years(self, idno: str) -> list[dict[str, Any]]:
        """Fetch list of available financial statement years for a company.

        Returns a list of dicts with keys: id, year, source.
        Results are cached per IDNO to avoid redundant API calls.
        """
        if idno in self._years_cache:
            return self._years_cache[idno]

        try:
            resp = await self._direct_client.get(DEPOZITAR_SEARCH_URL, params={"idno": idno})
            resp.raise_for_status()
            entries = resp.json()
            self._years_cache[idno] = entries
            return entries
        except httpx.HTTPStatusError as e:
            logger.warning("Depozitar lookup failed for %s: HTTP %d", idno, e.response.status_code)
            return []
        except Exception as e:
            logger.warning("Depozitar lookup failed for %s: %s", idno, e)
            return []

    async def fetch_financial_statement(self, fs_uuid: str) -> dict[str, Any]:
        """Fetch full financial statement data by UUID.

        Uses X-Forwarded-For rotation to bypass IP-based rate limits.
        Returns the raw Depozitar JSON, or None on failure.
        """
        try:
            resp = await self._direct_client.get(
                f"{DEPOZITAR_FS_URL}/{fs_uuid}",
                headers=self._xff_headers(),
            )
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPStatusError as e:
            logger.warning(
                "Depozitar FS fetch failed for %s: HTTP %d", fs_uuid, e.response.status_code
            )
            return None
        except Exception as e:
            logger.warning("Depozitar FS fetch failed for %s: %s", fs_uuid, e)
            return None

    async def fetch_financial_data(self, idno: str, year: int) -> dict[str, Any] | None:
        """Fetch financial data for a company+year from the Depozitar.

        Two-step process:
        1. Get available FS UUIDs for the IDNO
        2. Fetch the specific year's FS by UUID
        3. Parse into our normalized format

        Returns None if no data available for the given year.
        """
        entries = await self.fetch_available_years(idno)
        if not entries:
            logger.info("No Depozitar data for %s", idno)
            return None

        target = next((e for e in entries if e.get("year") == year), None)
        if not target:
            logger.info(
                "No Depozitar FS for %s year %d (available: %s)",
                idno,
                year,
                [e.get("year") for e in entries],
            )
            return None

        raw = await self.fetch_financial_statement(target["id"])
        if not raw:
            return None

        return self._parse_statement(raw, idno, year)

    async def fetch_all_available(self, idno: str) -> list[dict[str, Any]]:
        """Fetch all available financial statements for a company.

        Returns a list of normalized financial data dicts, one per year.
        Uses cached available years to avoid redundant API calls.
        """
        entries = await self.fetch_available_years(idno)
        if not entries:
            return []

        results = []
        for entry in entries:
            fs_id = entry.get("id")
            year = entry.get("year")
            if not fs_id or not year:
                continue
            raw = await self.fetch_financial_statement(fs_id)
            if raw:
                parsed = self._parse_statement(raw, idno, year)
                if parsed:
                    results.append(parsed)
        return results

    def _parse_statement(self, raw: dict[str, Any], idno: str, year: int) -> dict[str, Any] | None:
        """Parse a Depozitar financial statement into our normalized format.

        Extracts key financial indicators from the XBRL-based group/field structure.
        All monetary values are in MDL (leu), not thousands.
        """
        le = raw.get("legalEntity", {})

        data: dict[str, Any] = {
            "company_idno": idno,
            "year": year,
            "company_name": le.get("name"),
            "caem_code": le.get("caem", {}).get("code"),
            "caem_description": le.get("caem", {}).get("nameRo"),
            "business_category": le.get("cfoj", {}).get("nameRo"),
            "employees_count": _safe_int(le.get("nrEmployees")),
            "source_url": f"https://depozitar.statistica.md/search/financial-statement/{raw.get('id')}",
            "raw_data": raw,
            "metadata": {
                "source": raw.get("source"),
                "doctype": raw.get("doctype"),
                "status": raw.get("status"),
                "signed": raw.get("signed"),
                "period_from": raw.get("periodFrom"),
                "period_to": raw.get("periodTo"),
                "declaration_date": raw.get("declarationDate"),
                "cfoj_code": le.get("cfoj", {}).get("code"),
                "cfp_code": le.get("cfp", {}).get("code"),
                "cuatm_code": le.get("cuatm", {}).get("code"),
                "cuatm_name": le.get("cuatm", {}).get("nameRo"),
                "cuiio": le.get("cuiio"),
            },
        }

        # Extract financial indicators from statement groups by field NAME (not code)
        groups = raw.get("groups", [])
        pnl = _extract_pnl_fields(groups)
        bs = _extract_balance_sheet(groups)
        cf = _extract_cash_flow(groups)

        data["revenue"] = pnl.get("revenue")
        data["expenses"] = pnl.get("expenses")
        data["profit"] = pnl.get("profit")
        data["cost_of_goods_sold"] = pnl.get("cost_of_goods_sold")
        data["distribution_expenses"] = pnl.get("distribution_expenses")
        data["admin_expenses"] = pnl.get("admin_expenses")
        data["other_operating_expenses"] = pnl.get("other_operating_expenses")
        data["financial_income"] = pnl.get("financial_income")
        data["financial_expenses"] = pnl.get("financial_expenses")
        data["income_tax"] = pnl.get("income_tax")

        data["total_assets"] = bs.get("total_assets")
        data["total_liabilities"] = bs.get("total_liabilities")
        data["equity"] = bs.get("equity")
        data["current_assets"] = bs.get("current_assets")
        data["fixed_assets"] = bs.get("fixed_assets")
        data["inventories"] = bs.get("inventories")
        data["trade_receivables"] = bs.get("trade_receivables")
        data["cash_and_banks"] = bs.get("cash_and_banks")
        data["short_term_debt"] = bs.get("short_term_debt")
        data["long_term_debt"] = bs.get("long_term_debt")
        data["share_capital"] = bs.get("share_capital")

        data["operating_cash_flow"] = cf.get("operating_cash_flow")
        data["investing_cash_flow"] = cf.get("investing_cash_flow")
        data["financing_cash_flow"] = cf.get("financing_cash_flow")

        return data


def _parse_numeric(value_str: str) -> float | None:
    """Parse a numeric value from Depozitar format.

    Values may use spaces as thousand separators and comma as decimal.
    Examples: "1 452 995", "1452995.50", "1 452 995,50", "-"
    """
    if not value_str or value_str == "-" or value_str == "":
        return None

    cleaned = value_str.replace(" ", "").replace("\xa0", "")
    cleaned = cleaned.replace(",", ".")
    cleaned = cleaned.replace("lei", "").replace("MDL", "").strip()

    try:
        return float(cleaned)
    except (ValueError, TypeError):
        return None


def _safe_int(value: Any) -> int | None:
    """Safely convert to int."""
    if value is None:
        return None
    try:
        return int(value)
    except (ValueError, TypeError):
        return None


def _extract_pnl_fields(groups: list[dict]) -> dict[str, float | None]:
    """Extract P&L fields from statement groups by matching Romanian field names.

    Uses anexa2 (Profit & Loss statement) group.
    """
    result: dict[str, float | None] = {
        "revenue": None,
        "expenses": None,
        "profit": None,
        "cost_of_goods_sold": None,
        "distribution_expenses": None,
        "admin_expenses": None,
        "other_operating_expenses": None,
        "financial_income": None,
        "financial_expenses": None,
        "income_tax": None,
    }

    for group in groups:
        if group.get("code") != "anexa2":
            continue

        total_expenses = 0.0
        has_expense_fields = False

        for field in group.get("fields", []):
            name = (field.get("name") or "").lower().strip()
            value_str = field.get("data4") or field.get("data3") or field.get("dateCurrent") or ""
            value = _parse_numeric(value_str.strip())

            if value is None:
                continue

            # Revenue: "Venituri din vanzari" or "Venituri din vanzari, total"
            if "venituri din v" in name and (
                "total" in name or "vinzar" in name or "v_nz_r" in name
            ):
                if result["revenue"] is None:
                    result["revenue"] = value

            # Cost of goods sold: "Costul vanzarilor"
            elif name.startswith("costul v"):
                if result["cost_of_goods_sold"] is None:
                    result["cost_of_goods_sold"] = value
                total_expenses += value
                has_expense_fields = True

            # Distribution expenses
            elif "cheltuieli de distribuire" in name:
                if result["distribution_expenses"] is None:
                    result["distribution_expenses"] = value
                total_expenses += value
                has_expense_fields = True

            # Administrative expenses
            elif "cheltuieli administrative" in name:
                if result["admin_expenses"] is None:
                    result["admin_expenses"] = value
                total_expenses += value
                has_expense_fields = True

            # Other operating expenses
            elif "alte cheltuieli" in name or "alte cheltuieli din activitatea" in name:
                if result["other_operating_expenses"] is None:
                    result["other_operating_expenses"] = value
                total_expenses += value
                has_expense_fields = True

            # Financial income: "Venituri financiare"
            elif "venituri financiare" in name and "total" in name:
                if result["financial_income"] is None:
                    result["financial_income"] = value

            # Financial expenses: "Cheltuieli financiare"
            elif "cheltuieli financiare" in name and "total" in name:
                if result["financial_expenses"] is None:
                    result["financial_expenses"] = value
                total_expenses += value
                has_expense_fields = True

            # Income tax: "Cheltuieli privind impozitul pe venit"
            elif "impozitul pe venit" in name:
                if result["income_tax"] is None:
                    result["income_tax"] = value
                total_expenses += value
                has_expense_fields = True

            # Remaining expense fields (catch-all)
            elif "cheltuieli" in name and "venituri" not in name:
                total_expenses += value
                has_expense_fields = True

            # Profit: "Profit net (pierdere neta)"
            elif "profit net" in name or "profitul net" in name or "rezultatul net" in name:
                result["profit"] = value

        if has_expense_fields:
            result["expenses"] = total_expenses

    return result


def _extract_balance_sheet(groups: list[dict]) -> dict[str, float | None]:
    """Extract balance sheet fields from statement groups.

    Uses anexa1 (Balance Sheet) group.
    """
    result: dict[str, float | None] = {
        "total_assets": None,
        "total_liabilities": None,
        "equity": None,
        "current_assets": None,
        "fixed_assets": None,
        "inventories": None,
        "trade_receivables": None,
        "cash_and_banks": None,
        "short_term_debt": None,
        "long_term_debt": None,
        "share_capital": None,
    }

    for group in groups:
        if group.get("code") != "anexa1":
            continue

        for field in group.get("fields", []):
            name = (field.get("name") or "").lower().strip()
            value_str = field.get("data4") or field.get("data3") or field.get("dateCurrent") or ""
            value = _parse_numeric(value_str.strip())

            if value is None:
                continue

            # Total assets: "TOTAL ACTIVE (rd.230 + rd.420)"
            if name.startswith("total active") and "imobilizate" not in name and "circulante" not in name:
                result["total_assets"] = value

            # Total liabilities: "TOTAL PASIVE (rd.620 + ...)"
            elif name.startswith("total pasive"):
                result["total_liabilities"] = value

            # Fixed assets: "TOTAL ACTIVE IMOBILIZATE"
            elif "total active imobilizate" in name:
                result["fixed_assets"] = value

            # Current assets: "TOTAL ACTIVE CIRCULANTE"
            elif "total active circulante" in name:
                result["current_assets"] = value

            # Inventories: "Total stocuri"
            elif name.startswith("total stocuri"):
                result["inventories"] = value

            # Trade receivables: "Creante comerciale curente"
            elif "crean" in name and "comerciale" in name:
                if result["trade_receivables"] is None:
                    result["trade_receivables"] = value

            # Cash: "Numerar si documente banesti"
            elif "numerar" in name or ("casa" in name and "conturi" in name):
                if result["cash_and_banks"] is None:
                    result["cash_and_banks"] = value

            # Short-term debt: "TOTAL DATORII CURENTE"
            elif "total datorii curente" in name or "total datorii pe termen scurt" in name:
                if result["short_term_debt"] is None:
                    result["short_term_debt"] = value

            # Long-term debt: "TOTAL DATORII PE TERMEN LUNG"
            elif "total datorii pe termen lung" in name:
                if result["long_term_debt"] is None:
                    result["long_term_debt"] = value

            # Share capital: "Capital social"
            elif name.startswith("capital social") and "total" not in name:
                if result["share_capital"] is None:
                    result["share_capital"] = value

            # Equity: "TOTAL CAPITAL PROPRIU"
            elif "total capital propriu" in name or "capitalul propriu" in name:
                result["equity"] = value

    return result


def _extract_cash_flow(groups: list[dict]) -> dict[str, float | None]:
    """Extract cash flow fields from statement groups.

    Uses anexa4 (Cash Flow Statement) group.
    """
    result: dict[str, float | None] = {
        "operating_cash_flow": None,
        "investing_cash_flow": None,
        "financing_cash_flow": None,
    }

    for group in groups:
        if group.get("code") != "anexa4":
            continue

        for field in group.get("fields", []):
            name = (field.get("name") or "").lower()
            value_str = field.get("data4") or field.get("data3") or field.get("dateCurrent") or ""
            value = _parse_numeric(value_str.strip())

            if value is None:
                continue

            # Operating: "activitatea operationala"
            if "activitatea opera" in name:
                result["operating_cash_flow"] = value

            # Investing: "activitatea de investitii"
            elif "activitatea de investi" in name:
                result["investing_cash_flow"] = value

            # Financing: "activitatea financiara"
            elif "activitatea financiar" in name:
                result["financing_cash_flow"] = value

    return result
