"""Extract founders and directors from company metadata into persons and relationships.

Properly handles:
- Ownership percentage suffixes like "(100" appended to names
- Percentage fragment entries like "00%)" that are split across array elements
- European decimal format: "Name (100,00%)" where comma is decimal separator
- Company names masquerading as founders (S.R.L., S.A., etc.)
- Person deduplication via normalized full name

Run with:
    docker compose exec api python -m scripts.extract_persons --force
"""
from __future__ import annotations

import argparse
import asyncio
import logging
import re
import uuid
from datetime import datetime, timezone

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from credibil.config import get_settings

logger = logging.getLogger(__name__)

BATCH = 5000

# Company/legal entity indicators
_COMPANY_KEYWORDS = [
    "S.R.L.", "S.A.", "SRL", "S.A", "Societatea", "Întreprinderea",
    "Company", "Enterprises", "GROUP", "GRUP", "HOLDING", "Banca",
    "FIRMA", "Asociatia", "Fondul", "Ministerul", "Agentia",
    "SIRL", "LTD", "LLC", "GmbH", "BANK", "CORPORATION",
    "UNIUNEA", "ASOCIAȚIA", "FUNDATIA", "COOPERATIVA",
]


def _reassemble_entries(entries: list[dict]) -> list[dict]:
    """Reassemble split founder entries and extract ownership percentages.

    The CKAN XLSX sometimes splits entries due to European decimal commas:
      ["MÎRCA MIHAIL (100", "00%)"] → should be "MÎRCA MIHAIL" with 100%

    Also handles cases where ownership_percentage is already parsed correctly.
    """
    result = []
    i = 0

    while i < len(entries):
        entry = entries[i]
        name = entry.get("name", "")

        # If entry already has ownership_percentage, keep as-is
        if "ownership_percentage" in entry:
            result.append(entry)
            i += 1
            continue

        # Check if name ends with truncated percentage: "(100", "(50", "(33", etc.
        pct_prefix_match = re.search(r"\s*\((\d{1,3})$", name)
        if pct_prefix_match and i + 1 < len(entries):
            next_entry = entries[i + 1]
            next_name = next_entry.get("name", "")
            # Check if next entry is the remainder: "00%)", "100%)", etc.
            pct_remainder_match = re.match(r"^(\d{1,3}%?\)?)$", next_name)
            if pct_remainder_match:
                # Reassemble: strip "(100" from name, build full percentage
                clean_name = name[: pct_prefix_match.start()].strip()
                pct_digits = pct_prefix_match.group(1)  # e.g. "10"
                remainder = next_name  # e.g. "00%)"

                # Strip the % and ) from remainder to get decimal digits
                decimal_part = remainder.replace("%)", "").replace(")", "")  # e.g. "00"
                # Build: "10" + "." + "00" = "10.00" → 10.0%
                full_pct_str = pct_digits + "." + decimal_part if decimal_part else pct_digits
                ownership_pct = _parse_assembled_percentage(full_pct_str)

                if clean_name:
                    reassembled = {"name": clean_name, "idnp": entry.get("idnp")}
                    if ownership_pct is not None:
                        reassembled["ownership_percentage"] = ownership_pct
                    result.append(reassembled)
                i += 2
                continue

        # Check if entry is just a standalone percentage fragment: "00%)", "50%)", etc.
        if re.match(r"^\d{1,3}%?\)?$", name):
            # Standalone fragment with no preceding name — skip
            i += 1
            continue

        result.append(entry)
        i += 1

    return result


def _parse_assembled_percentage(raw: str) -> float | None:
    """Parse an assembled percentage string into a float.

    Input is now in "X.YY" format (with decimal point), e.g.:
      "10.00" → 10.0
      "100.00" → 100.0
      "1.00" → 1.0
      "25.19" → 25.19
    """
    raw = raw.strip().rstrip("%").strip()
    if not raw:
        return None

    try:
        val = float(raw)
    except ValueError:
        return None

    if 0 < val <= 100:
        return val

    return None


def _extract_director_role(raw_name: str) -> str | None:
    """Extract role from director name like 'NAME [Administrator]'."""
    m = re.search(r"\[([^\]]+)\]\s*$", raw_name)
    return m.group(1).strip() if m else None


def _clean_name(raw: str) -> str | None:
    """Clean a raw name from metadata. Returns None if not a valid person name."""
    name = raw.strip()
    name = re.sub(r"\s+", " ", name)

    if len(name) < 3:
        return None

    # Strip role suffixes: [Administrator], [Director], etc.
    name = re.sub(r"\s*\[.*?\]\s*$", "", name, flags=re.IGNORECASE)

    # Strip ownership percentage suffix: "(100%)", "(50%)", "(33,33%)", "(100"
    name = re.sub(r"\s*\(\d{1,3}(?:[,.]\d{1,2})?%?\)?$", "", name)

    name = name.strip()
    if len(name) < 3:
        return None

    return name


def _is_person_name(name: str) -> bool:
    """Heuristic: is this a person name (not a company)?"""
    if not name or len(name) < 3:
        return False

    name_upper = name.upper()
    for kw in _COMPANY_KEYWORDS:
        if kw.upper() in name_upper:
            return False

    words = name.split()
    if len(words) < 2:
        return False

    if name.replace(" ", "").isdigit():
        return False

    return True


def _normalize_name(name: str) -> str:
    """Normalize name for deduplication: lowercase, trim, collapse whitespace, NFKD."""
    import unicodedata

    name = name.lower().strip()
    name = re.sub(r"\s+", " ", name)
    nfkd = unicodedata.normalize("NFKD", name)
    name = "".join(c for c in nfkd if unicodedata.category(c) != "Mn")
    return name


def _extract_ownership_from_name(name: str) -> float | None:
    """Try to extract ownership percentage from a raw name string.

    Handles:
      "MÎRCA MIHAIL (100%)"     → 100.0
      "PORCESCO TIMOFEI (100%)"  → 100.0
      "Name (50,00%)"            → 50.0
      "Name (25.5%)"             → 25.5
      "Name"                     → None
    """
    m = re.search(r"\((\d{1,3}(?:[,.]\d{1,2})?)%\)$", name)
    if not m:
        return None
    pct_str = m.group(1).replace(",", ".")
    try:
        return float(pct_str)
    except ValueError:
        return None


async def run(force: bool = False) -> None:
    settings = get_settings()
    engine = create_async_engine(settings.database_url, pool_pre_ping=True)
    factory = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    async with factory() as session:
        if not force:
            result = await session.execute(text("SELECT count(*) FROM company_relationships"))
            existing_rels = result.scalar()
            if existing_rels > 0:
                logger.info("Relationships already populated (%d records). Use --force to rebuild.", existing_rels)
                await engine.dispose()
                return

        if force:
            logger.info("Force mode: clearing existing persons and relationships...")
            await session.execute(text("DELETE FROM company_relationships"))
            await session.execute(text("DELETE FROM persons"))
            await session.commit()
            logger.info("Cleared existing data.")

        result = await session.execute(
            text("""
                SELECT idno, metadata->'founders' as founders, metadata->'directors' as directors
                FROM companies
                WHERE metadata->'founders' IS NOT NULL
                   OR metadata->'directors' IS NOT NULL
            """)
        )
        rows = result.fetchall()
        logger.info("Processing %d companies...", len(rows))

        person_map: dict[str, dict] = {}
        relationships: list[dict] = []

        skipped_companies = 0
        skipped_fragments = 0
        skipped_short = 0

        for idno, founders_raw, directors_raw in rows:
            for rel_type, entries in [("founder", founders_raw), ("director", directors_raw)]:
                if not entries:
                    continue

                # Reassemble split entries first
                entries = _reassemble_entries(entries)

                for entry in entries:
                    raw = entry.get("name", "") if isinstance(entry, dict) else ""
                    ownership_pct = entry.get("ownership_percentage") if isinstance(entry, dict) else None

                    # Extract director role before cleaning name
                    director_role = None
                    if rel_type == "director":
                        director_role = _extract_director_role(raw)

                    # If no ownership from reassembly, try extracting from name
                    if ownership_pct is None:
                        ownership_pct = _extract_ownership_from_name(raw)

                    cleaned = _clean_name(raw)
                    if cleaned is None:
                        skipped_fragments += 1
                        continue
                    if not _is_person_name(cleaned):
                        skipped_companies += 1
                        continue
                    if len(cleaned) < 3:
                        skipped_short += 1
                        continue

                    norm = _normalize_name(cleaned)

                    if norm not in person_map:
                        person_map[norm] = {
                            "id": uuid.uuid4(),
                            "display_name": cleaned,
                        }

                    pid = person_map[norm]["id"]

                    # Build metadata for the relationship
                    rel_metadata = {"source": "ckan_bulk"}
                    if director_role:
                        rel_metadata["role"] = director_role

                    relationships.append({
                        "person_id": pid,
                        "company_idno": idno,
                        "relationship_type": rel_type,
                        "ownership_percentage": ownership_pct,
                        "metadata": rel_metadata,
                    })

        logger.info(
            "Extracted %d unique persons, %d relationships "
            "(skipped: %d company names, %d fragments, %d short)",
            len(person_map), len(relationships),
            skipped_companies, skipped_fragments, skipped_short,
        )

        # Count ownership data
        with_pct = sum(1 for r in relationships if r.get("ownership_percentage") is not None)
        logger.info("Relationships with ownership percentage: %d / %d", with_pct, len(relationships))

        # Count director roles
        role_counts: dict[str, int] = {}
        for r in relationships:
            if r["relationship_type"] == "director":
                role = r.get("metadata", {}).get("role", "unknown")
                role_counts[role] = role_counts.get(role, 0) + 1
        if role_counts:
            logger.info("Director roles: %s", dict(sorted(role_counts.items(), key=lambda x: -x[1])))

        now = datetime.now(timezone.utc)
        if person_map:
            person_rows = [
                {
                    "id": p["id"],
                    "full_name": p["display_name"],
                    "person_type": "natural",
                    "created_at": now,
                    "updated_at": now,
                }
                for p in person_map.values()
            ]
            for i in range(0, len(person_rows), BATCH):
                batch = person_rows[i : i + BATCH]
                await session.execute(
                    text("""
                        INSERT INTO persons (id, full_name, person_type, metadata, created_at, updated_at)
                        VALUES (:id, :full_name, :person_type, '{}'::jsonb, :created_at, :updated_at)
                    """),
                    batch,
                )
            await session.commit()
            logger.info("Inserted %d persons", len(person_rows))

        if relationships:
            import json
            rel_rows = [
                {
                    "id": uuid.uuid4(),
                    "person_id": r["person_id"],
                    "company_idno": r["company_idno"],
                    "relationship_type": r["relationship_type"],
                    "ownership_percentage": r.get("ownership_percentage"),
                    "is_active": True,
                    "metadata": json.dumps(r.get("metadata", {"source": "ckan_bulk"})),
                    "created_at": now,
                    "updated_at": now,
                }
                for r in relationships
            ]
            for i in range(0, len(rel_rows), BATCH):
                batch = rel_rows[i : i + BATCH]
                await session.execute(
                    text("""
                        INSERT INTO company_relationships
                            (id, person_id, company_idno, relationship_type,
                             ownership_percentage, is_active, metadata, created_at, updated_at)
                        VALUES (:id, :person_id, :company_idno, :relationship_type,
                                :ownership_percentage, :is_active,
                                CAST(:metadata AS jsonb), :created_at, :updated_at)
                    """),
                    batch,
                )
                if (i + BATCH) % 50000 == 0:
                    await session.commit()
                    logger.info("Inserted %d/%d relationships", min(i + BATCH, len(rel_rows)), len(rel_rows))

            await session.commit()
            logger.info("Inserted %d relationships", len(rel_rows))

        # Update founder_count and director_count in companies table
        # based on actual extracted relationships (fixes inflated counts from raw metadata)
        logger.info("Updating founder_count and director_count from extracted relationships...")
        await session.execute(text("""
            UPDATE companies SET founder_count = sub.cnt
            FROM (
                SELECT company_idno, COUNT(*) as cnt
                FROM company_relationships
                WHERE relationship_type = 'founder'
                GROUP BY company_idno
            ) sub
            WHERE companies.idno = sub.company_idno
        """))
        await session.execute(text("""
            UPDATE companies SET director_count = sub.cnt
            FROM (
                SELECT company_idno, COUNT(*) as cnt
                FROM company_relationships
                WHERE relationship_type = 'director'
                GROUP BY company_idno
            ) sub
            WHERE companies.idno = sub.company_idno
        """))
        # Set to 0 for companies with no relationships
        await session.execute(text("""
            UPDATE companies SET founder_count = 0
            WHERE founder_count > 0
            AND NOT EXISTS (
                SELECT 1 FROM company_relationships
                WHERE company_idno = companies.idno AND relationship_type = 'founder'
            )
        """))
        await session.execute(text("""
            UPDATE companies SET director_count = 0
            WHERE director_count > 0
            AND NOT EXISTS (
                SELECT 1 FROM company_relationships
                WHERE company_idno = companies.idno AND relationship_type = 'director'
            )
        """))
        await session.commit()
        logger.info("Updated founder_count and director_count.")

    await engine.dispose()
    logger.info("Extraction complete!")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true", help="Rebuild relationships from scratch")
    args = parser.parse_args()
    asyncio.run(run(force=args.force))
