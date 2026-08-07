from __future__ import annotations

import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)

CKAN_BASE_URL = "https://dataset.gov.md"
CKAN_DATASET_ID = "a1f38191-f35c-4180-8d80-297851a08f60"
CKAN_API_URL = f"{CKAN_BASE_URL}/api/3/action"


class CKANMetadata:
    """Fetches metadata about the CKAN dataset (latest resource, checksums, etc.)."""

    def __init__(self, dataset_id: str = CKAN_DATASET_ID) -> None:
        self._dataset_id = dataset_id
        self._client = httpx.AsyncClient(timeout=30.0)

    async def close(self) -> None:
        await self._client.aclose()

    async def get_package_info(self) -> dict[str, Any]:
        """Fetch full package metadata from CKAN API."""
        url = f"{CKAN_API_URL}/package_show"
        resp = await self._client.get(url, params={"id": self._dataset_id})
        resp.raise_for_status()
        data = resp.json()
        if not data.get("success"):
            raise RuntimeError(f"CKAN API error: {data}")
        return data["result"]

    async def get_latest_resource(self) -> dict[str, Any]:
        """Get the most recent XLSX resource from the dataset."""
        pkg = await self.get_package_info()
        resources = [r for r in pkg.get("resources", []) if r.get("format") == "XLSX"]
        if not resources:
            raise RuntimeError(f"No XLSX resource found in dataset {self._dataset_id}")
        resources.sort(key=lambda r: r.get("created", ""), reverse=True)
        return resources[0]

    async def get_download_url(self) -> str:
        """Build the direct download URL for the latest XLSX."""
        resource = await self.get_latest_resource()
        resource_id = resource["id"]
        filename = resource.get("name", "data.xlsx")
        return (
            f"{CKAN_BASE_URL}/dataset/{self._dataset_id}/resource/{resource_id}/download/{filename}"
        )

    async def get_resource_checksum(self) -> str | None:
        """Get MD5 checksum of latest resource if available."""
        resource = await self.get_latest_resource()
        return resource.get("checksum")

    async def health_check(self) -> bool:
        """Verify CKAN API is reachable."""
        try:
            url = f"{CKAN_API_URL}/status_show"
            resp = await self._client.get(url)
            resp.raise_for_status()
            return resp.json().get("success", False)
        except Exception:
            return False
