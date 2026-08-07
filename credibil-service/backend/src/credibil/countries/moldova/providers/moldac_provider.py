from __future__ import annotations

import asyncio
import logging
import re
from datetime import date, datetime
from typing import Any

from credibil.domain.accreditation.entities import (
    Accreditation,
    AccreditationCategory,
    AccreditationStatus,
)
from credibil.domain.accreditation.errors import AccreditationFetchError

logger = logging.getLogger(__name__)

CATEGORY_SLUGS: dict[str, AccreditationCategory] = {
    "laboratoare-de-incercari": AccreditationCategory.TESTING_LAB,
    "laboratoare-de-etalonari": AccreditationCategory.CALIBRATION_LAB,
    "laboratoare-medicale": AccreditationCategory.MEDICAL_LAB,
    "organisme-de-certificare-produse": AccreditationCategory.PRODUCT_CERT_BODY,
    "organisme-de-certificare-produse-ecologice": AccreditationCategory.ORGANIC_CERT_BODY,
    "organisme-de-certificare-sisteme-de-management": AccreditationCategory.MANAGEMENT_SYSTEM_CERT_BODY,
    "organisme-de-inspectie": AccreditationCategory.INSPECTION_BODY,
}

CATEGORY_STANDARDS: dict[AccreditationCategory, str] = {
    AccreditationCategory.TESTING_LAB: "SM EN ISO/IEC 17025:2018",
    AccreditationCategory.CALIBRATION_LAB: "SM EN ISO/IEC 17025:2018",
    AccreditationCategory.MEDICAL_LAB: "SM EN ISO 15189:2022",
    AccreditationCategory.PRODUCT_CERT_BODY: "SM EN ISO/CEI 17065:2013",
    AccreditationCategory.ORGANIC_CERT_BODY: "SM EN ISO/CEI 17065:2013",
    AccreditationCategory.MANAGEMENT_SYSTEM_CERT_BODY: "SM SR EN ISO/CEI 17021-1:2015",
    AccreditationCategory.INSPECTION_BODY: "SM EN ISO/CEI 17020:2013",
}

_STATUS_MAP: dict[str, AccreditationStatus] = {
    "activ": AccreditationStatus.ACTIVE,
    "suspendat": AccreditationStatus.SUSPENDED,
    "suspendat partial": AccreditationStatus.SUSPENDED_PARTIAL,
    "retras": AccreditationStatus.WITHDRAWN,
}


def _parse_date(date_str: str) -> date | None:
    """Parse date from DD.MM.YYYY format."""
    if not date_str or not date_str.strip():
        return None
    date_str = date_str.strip()
    for fmt in ("%d.%m.%Y", "%d.%m.%y", "%Y-%m-%d"):
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    return None


def _parse_contact_info(contact_html: str) -> dict[str, str | None]:
    """Parse contact info from HTML text."""
    info: dict[str, str | None] = {
        "address": None,
        "phone": None,
        "fax": None,
        "email": None,
    }

    # Replace <br> tags with newlines for easier parsing
    text = re.sub(r"<br\s*/?>", "\n", contact_html)
    text = re.sub(r"<[^>]+>", "", text)
    text = text.strip()

    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue
        if line.lower().startswith("adresa") or line.lower().startswith("str."):
            info["address"] = line.strip()
        elif re.match(r"^tel[.:]", line, re.IGNORECASE):
            info["phone"] = re.sub(r"^tel[.:\s]*", "", line, flags=re.IGNORECASE).strip()
        elif re.match(r"^fax[.:]", line, re.IGNORECASE):
            info["fax"] = re.sub(r"^fax[.:\s]*", "", line, flags=re.IGNORECASE).strip()
        elif re.match(r"^e?-?mail[.:]", line, re.IGNORECASE):
            info["email"] = re.sub(r"^e?-?mail[.:\s]*", "", line, flags=re.IGNORECASE).strip()
        elif not info["address"]:
            info["address"] = line.strip()

    return info


class MOLDACProvider:
    """Provider that scrapes acreditare.md for accreditation data."""

    BASE_URL = "https://acreditare.md"

    def __init__(self, rate_limit_delay: float = 1.0) -> None:
        self.rate_limit_delay = rate_limit_delay

    async def fetch_page(self, url: str) -> str:
        """Fetch HTML content from a URL with rate limiting."""
        import httpx

        await asyncio.sleep(self.rate_limit_delay)
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(url, follow_redirects=True)
                response.raise_for_status()
                return response.text
            except httpx.HTTPStatusError as e:
                raise AccreditationFetchError(reason=f"HTTP {e.response.status_code}: {url}") from e
            except httpx.RequestError as e:
                raise AccreditationFetchError(reason=str(e)) from e

    async def fetch_all_categories(self) -> list[Accreditation]:
        """Fetch accreditations from all 7 registry categories."""
        all_accreditations: list[Accreditation] = []
        for _slug, category in CATEGORY_SLUGS.items():
            try:
                accreditations = await self.fetch_by_category(category)
                all_accreditations.extend(accreditations)
                logger.info(
                    "Fetched %d accreditations from category %s",
                    len(accreditations),
                    category.value,
                )
            except AccreditationFetchError as e:
                logger.error("Failed to fetch category %s: %s", category.value, e)
                continue
        return all_accreditations

    async def fetch_by_category(self, category: AccreditationCategory) -> list[Accreditation]:
        """Fetch accreditations for a single category."""
        slug = next(
            (s for s, c in CATEGORY_SLUGS.items() if c == category),
            None,
        )
        if not slug:
            raise AccreditationFetchError(reason=f"Unknown category: {category}")

        url = f"{self.BASE_URL}/{slug}/"
        html = await self.fetch_page(url)
        return self._parse_category_page(html, category)

    def _parse_category_page(
        self, html: str, category: AccreditationCategory
    ) -> list[Accreditation]:
        """Parse the HTML of a category page and extract accreditation records."""
        try:
            from bs4 import BeautifulSoup
        except ImportError:
            logger.error("beautifulsoup4 not installed")
            return []

        soup = BeautifulSoup(html, "html.parser")
        accreditations: list[Accreditation] = []

        # Find the detail table container
        table = soup.select_one("div.detail__table")
        if not table:
            # Try alternative: actual <table> tag
            table = soup.select_one("table")
            if table:
                return self._parse_html_table(table, category)
            logger.warning("No table found in page")
            return []

        # Parse div-based table
        rows = table.select("div.detail__row")
        for row in rows:
            # Skip header row
            if "head" in (row.get("class") or []):
                continue

            acc = self._parse_div_row(row, category)
            if acc:
                accreditations.append(acc)

        return accreditations

    def _parse_html_table(self, table: Any, category: AccreditationCategory) -> list[Accreditation]:
        """Parse a standard HTML <table> element."""
        accreditations: list[Accreditation] = []
        rows = table.find_all("tr")
        start_idx = 0
        # Skip header row if first row contains <th>
        if rows and rows[0].find("th"):
            start_idx = 1
        for row in rows[start_idx:]:
            cells = row.find_all(["td", "th"])
            if len(cells) < 6:
                continue
            acc = self._parse_table_cells(cells, category)
            if acc:
                accreditations.append(acc)
        return accreditations

    def _parse_table_cells(
        self, cells: list[Any], category: AccreditationCategory
    ) -> Accreditation | None:
        """Parse cells from an HTML table row."""
        if len(cells) < 6:
            return None

        # Column indices based on the MOLDAC structure:
        # 0: Nr., 1: Name+Director, 2: Contact, 3: Certificate, 4: Annexes, 5: Status, 6: Remarks
        name_cell = cells[1] if len(cells) > 1 else None
        contact_cell = cells[2] if len(cells) > 2 else None
        cert_cell = cells[3] if len(cells) > 3 else None
        annex_cell = cells[4] if len(cells) > 4 else None
        status_cell = cells[5] if len(cells) > 5 else None
        remarks_cell = cells[6] if len(cells) > 6 else None

        return self._extract_accreditation(
            name_cell, contact_cell, cert_cell, annex_cell, status_cell, remarks_cell, category
        )

    def _parse_div_row(self, row: Any, category: AccreditationCategory) -> Accreditation | None:
        """Parse a div-based table row."""
        cols = row.select("div.detail__col")
        if len(cols) < 6:
            return None

        name_cell = cols[1] if len(cols) > 1 else None
        contact_cell = cols[2] if len(cols) > 2 else None
        cert_cell = cols[3] if len(cols) > 3 else None
        annex_cell = cols[4] if len(cols) > 4 else None
        status_cell = cols[5] if len(cols) > 5 else None
        remarks_cell = cols[6] if len(cols) > 6 else None

        return self._extract_accreditation(
            name_cell, contact_cell, cert_cell, annex_cell, status_cell, remarks_cell, category
        )

    def _extract_accreditation(
        self,
        name_cell: Any,
        contact_cell: Any,
        cert_cell: Any,
        annex_cell: Any,
        status_cell: Any,
        remarks_cell: Any,
        category: AccreditationCategory,
    ) -> Accreditation | None:
        """Extract accreditation data from parsed cells."""
        if not name_cell or not cert_cell:
            return None

        # Parse organization name and director
        name_text = self._cell_text(name_cell)
        name_lines = [line.strip() for line in name_text.split("\n") if line.strip()]
        organization_name = name_lines[0] if name_lines else ""
        director_name = name_lines[1] if len(name_lines) > 1 else None

        if not organization_name:
            return None

        # Parse contact info
        contact_html = str(contact_cell) if contact_cell else ""
        contact = _parse_contact_info(contact_html)

        # Parse certificate number and URL
        cert_text = self._cell_text(cert_cell)
        cert_link = cert_cell.find("a") if cert_cell else None
        certificate_url = cert_link["href"] if cert_link and cert_link.get("href") else None
        certificate_number = cert_text.strip() if cert_text else ""

        if not certificate_number:
            return None

        # Parse annexes
        annexes: list[dict[str, str]] = []
        if annex_cell:
            for link in annex_cell.find_all("a"):
                annex_name = link.get_text(strip=True)
                annex_url = link.get("href", "")
                if annex_name and annex_url:
                    annexes.append({"name": annex_name, "url": annex_url})

        # Parse status
        status = AccreditationStatus.ACTIVE
        if status_cell:
            status_text = self._cell_text(status_cell).strip().lower()
            # Also check CSS class
            status_span = status_cell.find("span")
            if status_span:
                status_icon = status_span.find("i")
                if status_icon:
                    classes = status_icon.get("class", [])
                    for cls in classes:
                        if cls == "status--4":
                            status_text = "retras"
                        elif cls == "status--2":
                            status_text = "suspendat"
                        elif cls == "status--3":
                            status_text = "suspendat partial"
                        elif cls == "status--1":
                            status_text = "activ"
            status = _STATUS_MAP.get(status_text, AccreditationStatus.ACTIVE)

        # Parse remarks
        remarks = self._cell_text(remarks_cell).strip() if remarks_cell else None
        if remarks and not remarks.strip():
            remarks = None

        # Determine standard from category
        standard = CATEGORY_STANDARDS.get(category, "")

        # Extract dates from remarks if present
        issue_date: date | None = None
        expiry_date: date | None = None
        if remarks:
            # Try to extract dates from remarks like "Retras din 28.07.2025"
            date_match = re.search(r"(\d{2}\.\d{2}\.\d{4})", remarks)
            if date_match:
                issue_date = _parse_date(date_match.group(1))

        return Accreditation(
            organization_name=organization_name,
            director_name=director_name,
            address=contact.get("address"),
            phone=contact.get("phone"),
            fax=contact.get("fax"),
            email=contact.get("email"),
            certificate_number=certificate_number,
            category=category,
            standard=standard,
            status=status,
            issue_date=issue_date,
            expiry_date=expiry_date,
            scope=None,
            certificate_url=certificate_url,
            annex_urls=annexes,
            remarks=remarks,
            source_url=f"{self.BASE_URL}/{next((s for s, c in CATEGORY_SLUGS.items() if c == category), '')}/",
            raw_data={
                "name_text": name_text,
                "cert_text": cert_text,
                "status_text": self._cell_text(status_cell) if status_cell else "",
            },
        )

    def _cell_text(self, cell: Any) -> str:
        """Extract text content from a cell."""
        if cell is None:
            return ""
        return cell.get_text(separator="\n", strip=True)
