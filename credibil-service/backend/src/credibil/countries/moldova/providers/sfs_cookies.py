"""SFS cookie storage - persists Cloudflare-bypassed cookies from the user's real browser.

Cookies are stored in a JSON file. The user extracts cookies from their browser
DevTools after manually visiting SFS and solving the Cloudflare challenge.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

DEFAULT_COOKIE_PATH = Path("/app/backend/sfs_cookies.json")


def load_cookies(path: Path = DEFAULT_COOKIE_PATH) -> list[dict[str, Any]]:
    """Load SFS cookies from JSON file."""
    if not path.exists():
        logger.warning("SFS cookies file not found: %s", path)
        return []
    try:
        data = json.loads(path.read_text())
        logger.info("Loaded %d SFS cookies from %s", len(data), path)
        return data
    except (json.JSONDecodeError, OSError) as e:
        logger.error("Failed to load SFS cookies: %s", e)
        return []


def save_cookies(cookies: list[dict[str, Any]], path: Path = DEFAULT_COOKIE_PATH) -> None:
    """Save cookies to JSON file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(cookies, indent=2))
    logger.info("Saved %d SFS cookies to %s", len(cookies), path)


def cookies_to_dict(cookies: list[dict[str, Any]]) -> dict[str, str]:
    """Convert cookie list to dict for curl_cffi."""
    return {c["name"]: c["value"] for c in cookies}


def cookies_valid(cookies: list[dict[str, Any]]) -> bool:
    """Check if cookies contain required fields."""
    names = {c["name"] for c in cookies}
    required = {"cf_clearance", "serviciul_fiscal_de_stat_session"}
    missing = required - names
    if missing:
        logger.warning("Missing required SFS cookies: %s", missing)
        return False
    return True
