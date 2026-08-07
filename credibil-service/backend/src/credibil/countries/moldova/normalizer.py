from __future__ import annotations

import re
from datetime import date, datetime
from typing import Any

from credibil.domain.company.entities import Company, CompanyStatus, LegalForm
from credibil.domain.sync.provenance import DataSource, FieldProvenance

# Legal form mapping from ASP numeric codes
LEGAL_FORM_MAP: dict[str, LegalForm] = {
    "1": LegalForm.SRL,
    "2": LegalForm.SA,
    "3": LegalForm.II,
    "4": LegalForm.IF,
    "5": LegalForm.PFA,
    "6": LegalForm.Cooperativa,
    "7": LegalForm.ONC,
}

# CAEM regex: 2 digits optionally followed by .XX
CAEM_RE = re.compile(r"^\d{2}(\.?\d{2})?$")

# Postal code: MD-XXXX
POSTAL_RE = re.compile(r"^MD-\d{4}$")

# IDNP pattern: 13 digits inside parentheses
_IDNP_RE = re.compile(r"\((\d{13})\)$")


def _split_outside_parens(text: str, delimiter: str = ",") -> list[str]:
    """Split text by delimiter, but only when outside parentheses.

    This handles European-format percentages like "100,00%" inside "(100,00%)"
    where a naive comma split would incorrectly break the entry.
    """
    parts = []
    depth = 0
    current: list[str] = []

    for ch in text:
        if ch == "(":
            depth += 1
            current.append(ch)
        elif ch == ")":
            depth -= 1
            current.append(ch)
        elif ch == delimiter and depth == 0:
            if current:
                parts.append("".join(current).strip())
                current = []
        else:
            current.append(ch)

    if current:
        parts.append("".join(current).strip())

    return [p for p in parts if p]


def normalize_idno(raw: str) -> str:
    """Strip whitespace, ensure 13 digits."""
    cleaned = raw.strip().replace(" ", "")
    return cleaned[:13] if len(cleaned) >= 13 else cleaned


def normalize_date(value: Any) -> date | None:
    """Parse date from various formats found in XLSX."""
    if value is None:
        return None
    if isinstance(value, date):
        return value
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, str):
        value = value.strip()
        if not value or value == "None":
            return None
        for fmt in ("%Y-%m-%d", "%d.%m.%Y", "%d/%m/%Y", "%Y-%m-%dT%H:%M:%S"):
            try:
                return datetime.strptime(value, fmt).date()
            except ValueError:
                continue
    return None


def normalize_caem(raw: str) -> str | None:
    """Validate and normalize CAEM code."""
    cleaned = raw.strip()
    if not cleaned or cleaned == "None":
        return None
    return cleaned if CAEM_RE.match(cleaned) else None


def normalize_postal_code(raw: str) -> str | None:
    cleaned = raw.strip()
    if not cleaned or cleaned == "None":
        return None
    if POSTAL_RE.match(cleaned):
        return cleaned
    return None


def normalize_legal_form(code: str) -> LegalForm:
    return LEGAL_FORM_MAP.get(code.strip(), LegalForm.OTHER)


def normalize_status(raw: str, liquidation_date: Any) -> CompanyStatus:
    if liquidation_date is not None and normalize_date(liquidation_date) is not None:
        return CompanyStatus.LIQUIDATED
    return CompanyStatus.ACTIVE


def normalize_name(raw: str) -> str:
    return raw.strip() if raw and raw.strip() and raw.strip() != "None" else ""


def normalize_address(raw: str) -> str:
    return raw.strip() if raw and raw.strip() and raw.strip() != "None" else ""


def parse_founders(founders_str: str) -> list[dict[str, str]]:
    """Parse comma-separated founder entries into structured dicts.

    Format: "Name1 (100,00%), Name2 (50,00%)" or "Name1 (IDNP1), Name2 (IDNP2)"
    Handles European decimal commas inside parentheses (e.g., "100,00%").
    Extracts ownership percentage when present (not 13-digit IDNP).
    """
    if not founders_str or founders_str == "None":
        return []

    results = []
    parts = _split_outside_parens(founders_str)

    for part in parts:
        # Check for 13-digit IDNP
        idnp_match = _IDNP_RE.search(part)
        idnp = idnp_match.group(1) if idnp_match else None

        # Extract ownership percentage: "(100,00%)" or "(50%)"
        pct_match = re.search(r"\((\d{1,3}(?:[,.]\d{1,2})?)%\)$", part)
        ownership_pct = None
        if pct_match:
            pct_str = pct_match.group(1).replace(",", ".")
            try:
                ownership_pct = float(pct_str)
            except ValueError:
                pass

        # Strip the trailing parenthetical (IDNP or percentage)
        name = re.sub(r"\s*\([^)]*\)\s*$", "", part).strip()

        if name:
            entry: dict[str, Any] = {"name": name, "idnp": idnp}
            if ownership_pct is not None:
                entry["ownership_percentage"] = ownership_pct
            results.append(entry)

    return results


def parse_directors(directors_str: str) -> list[dict[str, str]]:
    """Parse director entries — same format as founders."""
    return parse_founders(directors_str)


def raw_row_to_company(raw: dict[str, Any]) -> Company:
    """Convert a raw XLSX row dict into a Company entity with provenance metadata."""
    idno = normalize_idno(raw["idno"])
    registration_date = normalize_date(raw["registration_date"])
    name = normalize_name(raw["full_name"])
    legal_form = normalize_legal_form(raw["legal_form_code"])
    address = normalize_address(raw["address"])
    cuatm = raw["cuatm"].strip() if raw.get("cuatm") and raw["cuatm"].strip() != "None" else None
    caem_desc = (
        raw.get("activities_licensed", "").strip()
        if raw.get("activities_licensed") and raw["activities_licensed"].strip() != "None"
        else None
    )

    status = normalize_status(raw.get("legal_form_code", ""), raw.get("liquidation_date"))

    founders = parse_founders(raw.get("founders", ""))
    directors = parse_directors(raw.get("directors", ""))

    provenance = {
        "idno": FieldProvenance("idno", idno, DataSource.CKAN_BULK),
        "name_ro": FieldProvenance("name_ro", name, DataSource.CKAN_BULK),
        "registration_date": FieldProvenance(
            "registration_date", registration_date, DataSource.CKAN_BULK
        ),
        "status": FieldProvenance("status", status, DataSource.CKAN_BULK),
        "legal_form": FieldProvenance("legal_form", legal_form, DataSource.CKAN_BULK),
        "legal_address": FieldProvenance("legal_address", address, DataSource.CKAN_BULK),
        "cuatm": FieldProvenance("cuatm", cuatm, DataSource.CKAN_BULK),
        "caem_description": FieldProvenance("caem_description", caem_desc, DataSource.CKAN_BULK),
    }

    company = Company(
        idno=idno,
        name_ro=name,
        name_ru="",
        registration_date=registration_date,
        status=status,
        legal_form=legal_form,
        legal_address=address,
        postal_code=normalize_postal_code(raw.get("postal_code", "")),
        caem=None,
        caem_description=caem_desc,
        cuatm=cuatm,
        founder_count=len(founders),
        director_count=len(directors),
        metadata={
            "provenance": {k: v.to_dict() for k, v in provenance.items()},
            "founders": founders,
            "directors": directors,
            "activities_unlicensed": raw.get("activities_unlicensed", ""),
            "sync_source": "ckan_bulk",
        },
    )

    return company


# ── Business category classification ──────────────────────────────────────────

EURO_TO_MDL = 20

THRESHOLDS = {
    "micro": {"max_employees": 10, "max_turnover": 2_000_000 * EURO_TO_MDL, "max_assets": 2_000_000 * EURO_TO_MDL},
    "small": {"max_employees": 50, "max_turnover": 10_000_000 * EURO_TO_MDL, "max_assets": 10_000_000 * EURO_TO_MDL},
    "medium": {"max_employees": 250, "max_turnover": 50_000_000 * EURO_TO_MDL, "max_assets": 43_000_000 * EURO_TO_MDL},
}


def classify_business_category(
    employees_count: int | None,
    revenue: float | None,
    total_assets: float | None,
) -> str | None:
    """Classify company size based on employee count and financial data.

    Returns one of: 'micro', 'small', 'medium', 'large', or None if insufficient data.
    """
    if employees_count is None and revenue is None and total_assets is None:
        return None

    emp = employees_count or 0
    rev = revenue or 0
    assets = total_assets or 0

    if emp >= 250 or rev > THRESHOLDS["medium"]["max_turnover"]:
        return "large"

    if emp < 250 and rev <= THRESHOLDS["medium"]["max_turnover"]:
        if rev <= THRESHOLDS["medium"]["max_turnover"] and assets <= THRESHOLDS["medium"]["max_assets"]:
            if emp < 50 and rev <= THRESHOLDS["small"]["max_turnover"]:
                if emp < 10 and rev <= THRESHOLDS["micro"]["max_turnover"]:
                    return "micro"
                return "small"
            return "medium"

    if employees_count is not None or revenue is not None:
        return "medium"

    return None


def business_category_label(category: str | None) -> str | None:
    """Convert category code to display label."""
    labels = {
        "micro": "Micro",
        "small": "Small",
        "medium": "Medium",
        "large": "Large",
    }
    return labels.get(category) if category else None
