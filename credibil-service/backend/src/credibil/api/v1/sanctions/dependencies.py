from __future__ import annotations

from typing import TYPE_CHECKING

from credibil.config import get_settings
from credibil.infrastructure.sanctions.sdn_provider import SDNProvider

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator


async def get_sdn_provider() -> AsyncGenerator[SDNProvider, None]:
    settings = get_settings()
    if not settings.sdn_api_key:
        raise ValueError("CREDIBIL_SDN_API_KEY not configured")
    provider = SDNProvider(api_key=settings.sdn_api_key, base_url=settings.sdn_api_url)
    try:
        yield provider
    finally:
        await provider.close()
