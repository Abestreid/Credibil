from __future__ import annotations

import logging
import re
from datetime import date
from typing import Any

import httpx

from credibil.domain.court.entities import (
    CaseStatus,
    CourtCase,
    CourtHearing,
    CourtType,
)
from credibil.domain.court.errors import CourtCaseFetchError, CourtSearchError

logger = logging.getLogger(__name__)

INSTANTE_BASE = "https://instante.justice.md"
INSTANTE_SEARCH_URL = f"{INSTANTE_BASE}/ro/search"

COURT_SLUGS: dict[str, dict[str, str]] = {
    "curtea-suprema": {"name": "Curtea Supremă de Justiție", "type": CourtType.SUPREME},
    "ca-centru": {"name": "Curtea de Apel Centru", "type": CourtType.APPEAL},
    "ca-nord": {"name": "Curtea de Apel Nord", "type": CourtType.APPEAL},
    "ca-sud": {"name": "Curtea de Apel Sud", "type": CourtType.APPEAL},
    "jc": {"name": "Judecătoria Chișinău", "type": CourtType.JUDECATORIE},
    "jcr": {"name": "Judecătoria Criuleni", "type": CourtType.JUDECATORIE},
    "jhn": {"name": "Judecătoria Hîncești", "type": CourtType.JUDECATORIE},
    "jst": {"name": "Judecătoria Strășeni", "type": CourtType.JUDECATORIE},
    "jcs": {"name": "Judecătoria Căușeni", "type": CourtType.JUDECATORIE},
    "jbl": {"name": "Judecătoria Bălți", "type": CourtType.JUDECATORIE},
    "jdr": {"name": "Judecătoria Drochia", "type": CourtType.JUDECATORIE},
    "jed": {"name": "Judecătoria Edineț", "type": CourtType.JUDECATORIE},
    "jor": {"name": "Judecătoria Orhei", "type": CourtType.JUDECATORIE},
    "jsr": {"name": "Judecătoria Soroca", "type": CourtType.JUDECATORIE},
    "jun": {"name": "Judecătoria Ungheni", "type": CourtType.JUDECATORIE},
    "jch": {"name": "Judecătoria Cahul", "type": CourtType.JUDECATORIE},
    "jco": {"name": "Judecătoria Comrat", "type": CourtType.JUDECATORIE},
    "jcm": {"name": "Judecătoria Cimișlia", "type": CourtType.JUDECATORIE},
}


class InstanteProvider:
    """Provider that scrapes instente.justice.md for court case data.

    The portal is a Drupal 7 site with HTML search. We scrape search results
    and parse the HTML to extract case information.
    """

    def __init__(self) -> None:
        self._client = httpx.AsyncClient(
            timeout=30.0,
            follow_redirects=True,
            headers={
                "User-Agent": "Mozilla/5.0 (compatible; CredibilBot/1.0)",
                "Accept": "text/html,application/xhtml+xml",
                "Accept-Language": "ro,en;q=0.9",
            },
        )

    async def close(self) -> None:
        await self._client.aclose()

    async def search_cases(
        self,
        query: str,
        case_type: str | None = None,
        court_slug: str | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        limit: int = 50,
    ) -> list[CourtCase]:
        """Search for cases on instente.justice.md by query string.

        The query can be a case number, IDNO, or party name.
        """
        params: dict[str, Any] = {"search_api_views_fulltext": query}
        if case_type:
            params["type"] = case_type
        if court_slug:
            params["court"] = court_slug
        if date_from:
            params["date_from"] = date_from.isoformat()
        if date_to:
            params["date_to"] = date_to.isoformat()

        try:
            resp = await self._client.get(INSTANTE_SEARCH_URL, params=params)
            resp.raise_for_status()
            return self._parse_search_results(resp.text, query)
        except CourtSearchError:
            raise
        except httpx.HTTPStatusError as e:
            raise CourtSearchError(query, f"HTTP {e.response.status_code}") from e
        except Exception as e:
            raise CourtSearchError(query, str(e)) from e

    async def fetch_case_detail(self, case_url: str) -> dict[str, Any]:
        """Fetch detailed information for a specific case by URL."""
        try:
            resp = await self._client.get(case_url)
            resp.raise_for_status()
            return self._parse_case_detail(resp.text, case_url)
        except httpx.HTTPStatusError as e:
            raise CourtCaseFetchError(case_url, f"HTTP {e.response.status_code}") from e
        except Exception as e:
            raise CourtCaseFetchError(case_url, str(e)) from e

    async def fetch_hearings(
        self,
        court_slug: str | None = None,
        hearing_date: date | None = None,
        limit: int = 50,
    ) -> list[CourtHearing]:
        """Fetch hearing agenda entries from the agenda section."""
        params: dict[str, Any] = {}
        if court_slug:
            params["court"] = court_slug
        if hearing_date:
            params["date"] = hearing_date.isoformat()

        try:
            resp = await self._client.get(f"{INSTANTE_BASE}/ro/agenda-sedintelor", params=params)
            resp.raise_for_status()
            return self._parse_hearings(resp.text, court_slug)
        except httpx.HTTPStatusError as e:
            raise CourtSearchError("hearings", f"HTTP {e.response.status_code}") from e
        except Exception as e:
            raise CourtSearchError("hearings", str(e)) from e

    async def health_check(self) -> bool:
        try:
            resp = await self._client.get(INSTANTE_BASE)
            return resp.status_code == 200
        except Exception:
            return False

    def _parse_search_results(self, html: str, query: str) -> list[CourtCase]:
        """Parse HTML search results into CourtCase entities."""
        cases: list[CourtCase] = []

        result_pattern = re.findall(
            r'<div[^>]*class="[^"]*views-row[^"]*"[^>]*>(.*?)</div>\s*</div>',
            html,
            re.DOTALL,
        )

        if not result_pattern:
            result_pattern = re.findall(
                r"<tr[^>]*>.*?<td[^>]*>(.*?)</td>.*?</tr>",
                html,
                re.DOTALL,
            )

        for block in result_pattern:
            case = self._parse_case_block(block, query)
            if case:
                cases.append(case)

        if not cases:
            link_pattern = re.findall(
                r'href="(/ro/[a-z\-]+/[a-z\-]+/\d+)"[^>]*>([^<]+)</a>',
                html,
            )
            for href, text in link_pattern:
                case_number = text.strip()
                if case_number and len(case_number) > 3:
                    cases.append(
                        CourtCase(
                            case_number=case_number,
                            court_name="Unknown",
                            source_url=f"{INSTANTE_BASE}{href}",
                        )
                    )

        return cases[:50]

    def _parse_case_block(self, block: str, query: str) -> CourtCase | None:
        """Parse a single case result block from the search HTML."""
        case_number = self._extract_field(block, r"(?:Număr|Dosar|Caz)[:\s]*([^<\n]+)")
        if not case_number:
            text_match = re.search(r">([^<]{5,})<", block)
            if text_match:
                case_number = text_match.group(1).strip()
            else:
                return None

        court_name = self._extract_field(block, r"(?:Instanță|Judecătorie|Curte)[:\s]*([^<\n]+)")
        judge = self._extract_field(block, r"(?:Judecător|Președinte)[:\s]*([^<\n]+)")
        plaintiff = self._extract_field(block, r"(?:Reclamant|Pârât)[:\s]*([^<\n]+)")

        status = CaseStatus.OPEN
        status_str = self._extract_field(block, r"(?:Stare|Status)[:\s]*([^<\n]+)")
        if status_str:
            status_lower = status_str.lower()
            if "închis" in status_lower or "solutionat" in status_lower:
                status = CaseStatus.CLOSED
            elif "în curs" in status_lower or "examinare" in status_lower:
                status = CaseStatus.IN_PROGRESS
            elif "apel" in status_lower:
                status = CaseStatus.APPEALED

        reg_date = self._extract_date(
            block, r"(?:Data înregistrării|Înregistrat)[:\s]*(\d{2}\.\d{2}\.\d{4})"
        )
        dec_date = self._extract_date(
            block, r"(?:Data hotărârii|Hotărât)[:\s]*(\d{2}\.\d{2}\.\d{4})"
        )

        slug_match = re.search(r'href="/ro/([^/]+)/([^/]+)/\d+"', block)
        court_slug = slug_match.group(1) if slug_match else None

        return CourtCase(
            case_number=case_number.strip(),
            court_name=court_name.strip() if court_name else "Unknown",
            court_slug=court_slug,
            judge_name=judge.strip() if judge else None,
            plaintiff_name=plaintiff.strip() if plaintiff else None,
            registration_date=reg_date,
            decision_date=dec_date,
            status=status,
            source_url=f"{INSTANTE_BASE}/ro/search?search_api_views_fulltext={query}",
            raw_data={"block": block[:2000]},
        )

    def _parse_case_detail(self, html: str, url: str) -> dict[str, Any]:
        """Parse a case detail page into structured data."""
        data: dict[str, Any] = {
            "case_number": None,
            "court_name": None,
            "judge_name": None,
            "plaintiff_name": None,
            "defendant_name": None,
            "registration_date": None,
            "decision_date": None,
            "status": None,
            "subject_matter": None,
            "raw_fields": {},
        }

        field_patterns = {
            "case_number": r"(?:Număr dosar|Numărul)[:\s]*([^<\n]+)",
            "court_name": r"(?:Instanța|Judecătoria)[:\s]*([^<\n]+)",
            "judge_name": r"(?:Judecătorul|Judecător)[:\s]*([^<\n]+)",
            "plaintiff_name": r"(?:Reclamantul|Reclamant)[:\s]*([^<\n]+)",
            "defendant_name": r"(?:Pârâtul|Pârât)[:\s]*([^<\n]+)",
            "subject_matter": r"(?:Obiectul|Subiect)[:\s]*([^<\n]+)",
        }

        for field, pattern in field_patterns.items():
            value = self._extract_field(html, pattern)
            if value:
                data[field] = value.strip()
                data["raw_fields"][field] = value.strip()

        reg_str = self._extract_field(html, r"(?:Data înregistrării)[:\s]*(\d{2}\.\d{2}\.\d{4})")
        if reg_str:
            data["registration_date"] = reg_str.strip()

        dec_str = self._extract_field(html, r"(?:Data hotărârii)[:\s]*(\d{2}\.\d{2}\.\d{4})")
        if dec_str:
            data["decision_date"] = dec_str.strip()

        status_str = self._extract_field(html, r"(?:Stare dosar|Stare)[:\s]*([^<\n]+)")
        if status_str:
            data["status"] = status_str.strip()

        return data

    def _parse_hearings(self, html: str, court_slug: str | None) -> list[CourtHearing]:
        """Parse hearing agenda entries from HTML."""
        hearings: list[CourtHearing] = []

        blocks = re.findall(
            r'<div[^>]*class="[^"]*views-row[^"]*"[^>]*>(.*?)</div>',
            html,
            re.DOTALL,
        )

        for block in blocks:
            case_num = self._extract_field(block, r"(?:Dosar|Caz)[:\s]*([^<\n]+)")
            time_str = self._extract_field(block, r"(\d{1,2}:\d{2})")
            room_str = self._extract_field(block, r"(?:Sala|Sală)[:\s]*(\d+)")
            judge = self._extract_field(block, r"(?:Judecător)[:\s]*([^<\n]+)")

            date_str = self._extract_field(block, r"(\d{2}\.\d{2}\.\d{4})")
            hearing_date = self._parse_date_str(date_str) if date_str else date.today()

            if case_num:
                hearings.append(
                    CourtHearing(
                        case_number=case_num.strip(),
                        hearing_date=hearing_date,
                        hearing_time=time_str,
                        court_name=court_slug,
                        room=room_str,
                        judge_name=judge.strip() if judge else None,
                        source_url=f"{INSTANTE_BASE}/ro/agenda-sedintelor",
                        raw_data={"block": block[:1000]},
                    )
                )

        return hearings[:50]

    def _extract_field(self, text: str, pattern: str) -> str | None:
        match = re.search(pattern, text, re.IGNORECASE)
        return match.group(1).strip() if match else None

    def _extract_date(self, text: str, pattern: str) -> date | None:
        date_str = self._extract_field(text, pattern)
        return self._parse_date_str(date_str)

    def _parse_date_str(self, date_str: str | None) -> date | None:
        if not date_str:
            return None
        try:
            parts = date_str.strip().split(".")
            if len(parts) == 3:
                return date(int(parts[2]), int(parts[1]), int(parts[0]))
        except (ValueError, IndexError):
            pass
        return None
