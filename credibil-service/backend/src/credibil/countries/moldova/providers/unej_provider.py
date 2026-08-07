from __future__ import annotations

import asyncio
import logging
import re
from datetime import date
from typing import Any

import httpx
from bs4 import BeautifulSoup

from credibil.domain.enforcement.entities import EnforcementProceeding
from credibil.domain.enforcement.errors import EnforcementFetchError

logger = logging.getLogger(__name__)

UNEJ_BASE = "https://www.unej.md"
UNEJ_SOMATIONS_URL = f"{UNEJ_BASE}/somations"

# unej.md publishes only the public "Somații" board (pre-execution summons).
# It is server-rendered HTML with GET params: debtor, creditor, date_from,
# date_to, page. There is no JSON API. Markup is semi-structured and varies by
# the executor who authored each summons, so every extraction below is
# best-effort and tolerant of missing fields.

_RE_SOMATION_HREF = re.compile(r"/somations/(\d+)")
_RE_IDNO_FULL = re.compile(r"IDN[OP]\s*[:\-]?\s*(\d{13})", re.IGNORECASE)
_RE_IDNO_MASKED = re.compile(r"IDN[OP]\s*[:\-]?\s*(\*+\s*\d+)", re.IGNORECASE)
_RE_DOC_NUMBER = re.compile(
    r"document\w*\s+executoriu\s+nr\.?\s*([\w\-/.]+)", re.IGNORECASE
)
# Prefer the case number anchored to "dosar(ul) nr."; fall back to any court-style number.
_RE_CASE_NUMBER = re.compile(r"dosar\w*\s+nr\.?\s*(\d+\-\d+/\d{2,4})", re.IGNORECASE)
_RE_CASE_NUMBER_FALLBACK = re.compile(r"nr\.?\s*(\d+\-\d+/\d{4})")
_RE_COURT = re.compile(r"(Judec[ăa]toria[^,.\n<]{0,60})", re.IGNORECASE)
_RE_AMOUNT = re.compile(r"([\d][\d\s.,]*)\s*lei", re.IGNORECASE)
_RE_PUB_DATE = re.compile(
    r"Publicat[ăa]?\s*[:\-]?\s*(\d{2})[.\-/](\d{2})[.\-/](\d{4})", re.IGNORECASE
)
_RE_ANY_DATE = re.compile(r"(\d{2})[.\-/](\d{2})[.\-/](\d{4})")
# Stop the debtor name at the first field boundary (IDNO / "cu domiciliul" / Creditor).
_RE_DEBTOR_TITLE = re.compile(
    r"Somați[ei]\s+debitor\s+(.+?)"
    r"(?:\s*,?\s*IDN[OP]\b|\s*,?\s*cu\s+domiciliul|\s+Creditor\b|$)",
    re.IGNORECASE,
)


class UnejProvider:
    """Scrapes the public "Somații" board on unej.md.

    Two access patterns:
      * ``crawl_page`` / ``crawl_all`` — walk the paginated list to ingest the
        whole board (used by the daily full crawl).
      * ``search`` — query by debtor/creditor IDNO or name. The source masks
        the debtor IDNO in the display but matches on the full stored value, so
        searching a full 13-digit IDNO reliably resolves the debtor side.
    """

    def __init__(self, timeout: float = 30.0) -> None:
        # unej.md's WAF 403s obvious bot user-agents, so present as a normal browser.
        self._client = httpx.AsyncClient(
            timeout=timeout,
            follow_redirects=True,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
                ),
                "Accept": (
                    "text/html,application/xhtml+xml,application/xml;q=0.9,"
                    "image/avif,image/webp,*/*;q=0.8"
                ),
                "Accept-Language": "ro-RO,ro;q=0.9,ru;q=0.8,en;q=0.7",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
            },
        )

    async def __aenter__(self) -> UnejProvider:
        return self

    async def __aexit__(self, *_exc: object) -> None:
        await self.close()

    async def close(self) -> None:
        await self._client.aclose()

    async def health_check(self) -> bool:
        try:
            resp = await self._client.get(UNEJ_SOMATIONS_URL)
            return resp.status_code == 200
        except Exception:
            return False

    # ------------------------------------------------------------------ list
    async def crawl_page(self, page: int = 1) -> list[EnforcementProceeding]:
        params = {"page": page} if page > 1 else {}
        try:
            resp = await self._client.get(UNEJ_SOMATIONS_URL, params=params)
            resp.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise EnforcementFetchError(
                f"page={page}", f"HTTP {e.response.status_code}"
            ) from e
        except Exception as e:  # noqa: BLE001
            raise EnforcementFetchError(f"page={page}", str(e)) from e
        return self._parse_list(resp.text)

    async def crawl_all(
        self, max_pages: int = 60, delay: float = 0.4
    ) -> list[EnforcementProceeding]:
        """Walk every list page until one comes back empty (or ``max_pages``)."""
        seen: dict[int, EnforcementProceeding] = {}
        for page in range(1, max_pages + 1):
            rows = await self.crawl_page(page)
            if not rows:
                logger.info("unej crawl: page %d empty, stopping", page)
                break
            new_on_page = 0
            for row in rows:
                if row.somation_id not in seen:
                    seen[row.somation_id] = row
                    new_on_page += 1
            logger.info("unej crawl: page %d -> %d rows (%d new)", page, len(rows), new_on_page)
            if new_on_page == 0:
                # pagination looped or returned duplicates only
                break
            if delay:
                await asyncio.sleep(delay)
        return list(seen.values())

    async def search(
        self,
        debtor: str | None = None,
        creditor: str | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        max_pages: int = 3,
    ) -> list[EnforcementProceeding]:
        params: dict[str, Any] = {}
        if debtor:
            params["debtor"] = debtor
        if creditor:
            params["creditor"] = creditor
        if date_from:
            params["date_from"] = date_from.strftime("%d.%m.%Y")
        if date_to:
            params["date_to"] = date_to.strftime("%d.%m.%Y")

        results: dict[int, EnforcementProceeding] = {}
        for page in range(1, max_pages + 1):
            page_params = dict(params)
            if page > 1:
                page_params["page"] = page
            try:
                resp = await self._client.get(UNEJ_SOMATIONS_URL, params=page_params)
                resp.raise_for_status()
            except httpx.HTTPStatusError as e:
                raise EnforcementFetchError(
                    f"search:{debtor or creditor}", f"HTTP {e.response.status_code}"
                ) from e
            except Exception as e:  # noqa: BLE001
                raise EnforcementFetchError(f"search:{debtor or creditor}", str(e)) from e
            rows = self._parse_list(resp.text)
            if not rows:
                break
            for row in rows:
                results[row.somation_id] = row
        return list(results.values())

    # ---------------------------------------------------------------- detail
    async def fetch_detail(self, somation_id: int) -> dict[str, Any]:
        url = f"{UNEJ_SOMATIONS_URL}/{somation_id}"
        try:
            resp = await self._client.get(url)
            resp.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise EnforcementFetchError(
                f"detail:{somation_id}", f"HTTP {e.response.status_code}"
            ) from e
        except Exception as e:  # noqa: BLE001
            raise EnforcementFetchError(f"detail:{somation_id}", str(e)) from e
        return self._parse_detail(resp.text, somation_id)

    # --------------------------------------------------------------- parsing
    def _parse_list(self, html: str) -> list[EnforcementProceeding]:
        soup = BeautifulSoup(html, "html.parser")
        blocks: dict[int, tuple[Any, str]] = {}
        for anchor in soup.find_all("a", href=_RE_SOMATION_HREF):
            match = _RE_SOMATION_HREF.search(anchor.get("href", ""))
            if not match:
                continue
            somation_id = int(match.group(1))
            if somation_id in blocks:
                continue
            anchor_text = anchor.get_text(" ", strip=True)
            # climb to a reasonable container to capture the whole row's text
            container = anchor
            for _ in range(4):
                if container.parent is None:
                    break
                container = container.parent
                if container.name in ("article", "li", "tr") or (
                    container.name == "div" and container.get("class")
                ):
                    break
            blocks[somation_id] = (container, anchor_text)

        proceedings: list[EnforcementProceeding] = []
        for somation_id, (container, anchor_text) in blocks.items():
            text = container.get_text(" ", strip=True) if container else ""
            proceedings.append(
                self._proceeding_from_text(somation_id, text, title_text=anchor_text)
            )
        return proceedings

    def _proceeding_from_text(
        self, somation_id: int, text: str, title_text: str | None = None
    ) -> EnforcementProceeding:
        # The debtor name is most reliable from the anchor/title ("Somație
        # debitor <NAME>"); the surrounding block often folds in the address.
        debtor_name = None
        title_match = _RE_DEBTOR_TITLE.search(title_text or "") or _RE_DEBTOR_TITLE.search(text)
        if title_match:
            debtor_name = _clean(title_match.group(1))[:400]

        masked = _RE_IDNO_MASKED.search(text)
        full_idnos = _RE_IDNO_FULL.findall(text)
        pub_date = _parse_pub_date(text)

        return EnforcementProceeding(
            somation_id=somation_id,
            debtor_name=debtor_name,
            debtor_idno_masked=_clean(masked.group(1)).replace(" ", "") if masked else None,
            # a full IDNO on the list view (if present) is the creditor's
            creditor_idno=full_idnos[0] if full_idnos else None,
            publication_date=pub_date,
            source_url=f"{UNEJ_SOMATIONS_URL}/{somation_id}",
            raw_data={"list_text": text[:2000]},
        )

    def _parse_detail(self, html: str, somation_id: int) -> dict[str, Any]:
        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text(" ", strip=True)

        data: dict[str, Any] = {"somation_id": somation_id, "raw_text": text[:5000]}

        title_match = _RE_DEBTOR_TITLE.search(text)
        if title_match:
            data["debtor_name"] = _clean(title_match.group(1))[:400]

        masked = _RE_IDNO_MASKED.search(text)
        if masked:
            data["debtor_idno_masked"] = _clean(masked.group(1)).replace(" ", "")

        # The creditor IDNO is shown unmasked; take the first full 13-digit id.
        full_idnos = _RE_IDNO_FULL.findall(text)
        if full_idnos:
            data["creditor_idno"] = full_idnos[0]

        doc = _RE_DOC_NUMBER.search(text)
        if doc:
            data["executory_doc_number"] = _clean(doc.group(1))

        case = _RE_CASE_NUMBER.search(text) or _RE_CASE_NUMBER_FALLBACK.search(text)
        if case:
            data["case_number"] = _clean(case.group(1))

        court = _RE_COURT.search(text)
        if court:
            data["court_name"] = _clean(court.group(1))

        amount = _RE_AMOUNT.search(text)
        if amount:
            data["amount"] = _parse_amount(amount.group(1))
            data["currency"] = "MDL"

        pub = _parse_pub_date(text)
        if pub:
            data["publication_date"] = pub

        return data


def _clean(value: str | None) -> str:
    if not value:
        return ""
    return re.sub(r"\s+", " ", value).strip()


def _parse_amount(raw: str) -> float | None:
    cleaned = raw.strip().replace(" ", "")
    # Moldovan formatting uses "." as thousands and "," as decimals.
    cleaned = cleaned.replace(".", "").replace(",", ".")
    try:
        return float(cleaned)
    except ValueError:
        return None


def _parse_pub_date(text: str) -> date | None:
    match = _RE_PUB_DATE.search(text) or _RE_ANY_DATE.search(text)
    if not match:
        return None
    try:
        day, month, year = int(match.group(1)), int(match.group(2)), int(match.group(3))
        return date(year, month, day)
    except (ValueError, IndexError):
        return None
