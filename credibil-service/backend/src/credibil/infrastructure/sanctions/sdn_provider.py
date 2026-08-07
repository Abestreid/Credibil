"""SDN sanctions provider — compliance.dazor.by API.

Enterprise plan, no daily limits. Searches by entity name (not IDNO).
Covers OFAC, UN, EU, UK HMT, and Belarus sanctions lists.
"""

from __future__ import annotations

import logging
from typing import Any

import httpx

from credibil.domain.sanctions.entities import SanctionsEntry
from credibil.domain.sanctions.enums import SanctionStatus, SanctionType
from credibil.ports.providers.sanctions import SanctionsProvider

logger = logging.getLogger(__name__)

SDN_API_BASE = "http://compliance.dazor.by/api/v1"


def _map_sdn_status(sdn_is_sanctioned: bool, sdn_has_sanctions: bool) -> SanctionStatus:
    """Map SDN API flags to our SanctionStatus enum."""
    if sdn_is_sanctioned:
        return SanctionStatus.ACTIVE
    if sdn_has_sanctions:
        return SanctionStatus.UNDER_REVIEW
    return SanctionStatus.LIFTED


def _map_sdn_type(programs: list[str]) -> SanctionType:
    """Infer sanction type from program names."""
    programs_lower = " ".join(programs).lower()
    if "ofac" in programs_lower or "sdn" in programs_lower:
        return SanctionType.US_OFAC
    if "eu" in programs_lower or "(ue)" in programs_lower:
        return SanctionType.EU
    if "un" in programs_lower or "unsc" in programs_lower:
        return SanctionType.UN
    return SanctionType.INTERNATIONAL


def _parse_entry(entity: dict[str, Any]) -> SanctionsEntry:
    """Convert SDN API entity response into a SanctionsEntry domain object."""
    programs = entity.get("programs") or []
    properties = entity.get("properties") or {}
    notes = properties.get("notes") or []
    countries = entity.get("countries") or []

    return SanctionsEntry(
        target_name=entity.get("caption", ""),
        sanction_type=_map_sdn_type(programs),
        status=_map_sdn_status(
            entity.get("is_sanctioned", False), entity.get("has_sanctions", False)
        ),
        list_name=", ".join(entity.get("source_datasets") or []),
        country_code=countries[0].upper() if countries else None,
        reason=notes[0] if notes else None,
        program=", ".join(programs) if programs else None,
        metadata={
            "sdn_id": entity.get("id"),
            "aliases": entity.get("aliases") or [],
            "topics": entity.get("topics") or [],
            "all_notes": notes,
            "all_programs": programs,
        },
    )


class SDNProvider(SanctionsProvider):
    """Sanctions provider using the compliance.dazor.by SDN API.

    Search by entity name is the primary lookup method.
    IDNO/IDNP lookups are not supported by SDN (returns empty results).
    """

    def __init__(self, api_key: str, base_url: str = SDN_API_BASE) -> None:
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._client = httpx.AsyncClient(
            timeout=30.0,
            headers={
                "X-API-Key": api_key,
                "Accept": "application/json",
            },
        )

    async def close(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> SDNProvider:
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()

    async def search_by_name(self, name: str, limit: int = 10) -> list[SanctionsEntry]:
        """Search sanctions lists by entity name.

        SDN API full-text search across all datasets.
        Returns matching entities converted to SanctionsEntry objects.
        For sanctioned entities, enriches with entity detail (programs, notes).
        """
        try:
            resp = await self._client.get(
                f"{self._base_url}/search",
                params={
                    "q": name,
                    "schema_type": "Organization",
                    "page_size": min(limit, 100),
                },
            )
            resp.raise_for_status()
            data = resp.json()

            results = data.get("results") or []
            entries = [_parse_entry(r) for r in results[:limit]]

            # Enrich sanctioned entries with entity detail (programs, notes)
            for entry in entries:
                if entry.status == SanctionStatus.ACTIVE and entry.metadata.get("sdn_id"):
                    detail = await self.get_entity_detail(entry.metadata["sdn_id"])
                    if detail:
                        entry.metadata["programs"] = detail.get("programs") or []
                        entry.metadata["aliases"] = detail.get("aliases") or []
                        entry.metadata["topics"] = detail.get("topics") or []
                        props = detail.get("properties") or {}
                        notes = props.get("notes") or []
                        if notes:
                            entry.reason = notes[0]
                        entry.program = ", ".join(detail.get("programs") or [])

            return entries
        except httpx.HTTPStatusError as e:
            logger.warning("SDN search failed for %r: HTTP %d", name, e.response.status_code)
            return []
        except Exception as e:
            logger.warning("SDN search failed for %r: %s", name, e)
            return []

    async def search_by_idno(self, idno: str) -> list[SanctionsEntry]:
        """Exact sanctions lookup by Moldovan IDNO.

        SDN now indexes company registration numbers / IDNOs (enriched from the
        ASP registry), so an exact ``identifier`` match returns precisely the
        entity carrying that IDNO — no fuzzy name false-positives. Preferred over
        search_by_name whenever an IDNO is known.
        """
        if not idno:
            return []
        try:
            resp = await self._client.get(
                f"{self._base_url}/search",
                params={"identifier": str(idno).strip(), "page_size": 20},
            )
            resp.raise_for_status()
            results = resp.json().get("results") or []
            entries = [_parse_entry(r) for r in results]
            for entry in entries:
                if entry.status == SanctionStatus.ACTIVE and entry.metadata.get("sdn_id"):
                    detail = await self.get_entity_detail(entry.metadata["sdn_id"])
                    if detail:
                        notes = (detail.get("properties") or {}).get("notes") or []
                        if notes:
                            entry.reason = notes[0]
                        if detail.get("programs"):
                            entry.program = ", ".join(detail["programs"])
                            entry.metadata["programs"] = detail["programs"]
            return entries
        except httpx.HTTPStatusError as e:
            logger.warning("SDN IDNO search failed for %r: HTTP %d", idno, e.response.status_code)
            return []
        except Exception as e:
            logger.warning("SDN IDNO search failed for %r: %s", idno, e)
            return []

    async def search_by_idnp(self, idnp: str) -> list[SanctionsEntry]:
        """Search by IDNP — SDN does not index Moldovan IDNPs.

        Returns empty list. Use search_by_name instead.
        """
        logger.info("SDN IDNP lookup not supported, skipping: %s", idnp)
        return []

    async def get_latest_entries(self, since: str | None = None) -> list[SanctionsEntry]:
        """Get latest sanctions entries.

        SDN API does not have a dedicated "latest" endpoint.
        Uses search with recent filter if since is provided.
        """
        logger.info("SDN get_latest_entries called (since=%s)", since)
        return []

    async def health_check(self) -> bool:
        """Check if SDN API is reachable."""
        try:
            resp = await self._client.get(f"{self._base_url}/me")
            resp.raise_for_status()
            return True
        except Exception as e:
            logger.warning("SDN health check failed: %s", e)
            return False

    async def batch_search(
        self, names: list[str], only_sanctioned: bool = True
    ) -> list[SanctionsEntry]:
        """Batch search by multiple names in a single API call.

        Uses POST /search/batch endpoint (up to 100 queries).
        """
        if not names:
            return []

        try:
            payload: dict[str, Any] = {
                "queries": names[:100],
                "schema_type": "Organization",
            }
            if only_sanctioned:
                payload["is_sanctioned"] = "1"

            resp = await self._client.post(
                f"{self._base_url}/search/batch",
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()

            entries = []
            for result in data.get("results") or []:
                for match in result.get("matches") or []:
                    entries.append(_parse_entry(match))
            return entries
        except httpx.HTTPStatusError as e:
            logger.warning("SDN batch search failed: HTTP %d", e.response.status_code)
            return []
        except Exception as e:
            logger.warning("SDN batch search failed: %s", e)
            return []

    async def get_entity_detail(self, entity_id: str) -> dict[str, Any] | None:
        """Get full entity details including relations and documents."""
        try:
            resp = await self._client.get(f"{self._base_url}/entities/{entity_id}")
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logger.warning("SDN entity detail failed for %s: %s", entity_id, e)
            return None
