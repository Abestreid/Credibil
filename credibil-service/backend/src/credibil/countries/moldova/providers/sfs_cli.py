#!/usr/bin/env python3
"""CLI to manage SFS cookies for automated tax debt checks.

Usage:
  # Export cookies from browser (paste JSON array of cookie objects)
  python -m credibil.countries.moldova.providers.sfs_cli export

  # Export from a JSON file
  python -m credibil.countries.moldova.providers.sfs_cli export --file cookies.json

  # Check if cookies are valid
  python -m credibil.countries.moldova.providers.sfs_cli status

  # Test SFS access with current cookies
  python -m credibil.countries.moldova.providers.sfs_cli test --idno 1002600000010
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from credibil.countries.moldova.providers.sfs_cookies import (
    DEFAULT_COOKIE_PATH,
    cookies_valid,
    load_cookies,
    save_cookies,
)
from credibil.countries.moldova.providers.sfs_provider import SFSProvider

SFS_COOKIE_EXPORT_PATH = Path("/app/backend/sfs_cookies.json")


def cmd_export(args: argparse.Namespace) -> None:
    """Export cookies from a file or stdin."""
    source = args.file
    if source:
        path = Path(source)
        if not path.exists():
            print(f"File not found: {source}")
            sys.exit(1)
        raw = path.read_text()
    else:
        print("Paste JSON array of cookies (from browser DevTools), then Ctrl+D:")
        raw = sys.stdin.read()

    try:
        cookies = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}")
        sys.exit(1)

    if not isinstance(cookies, list):
        print("Expected a JSON array of cookie objects")
        sys.exit(1)

    save_cookies(cookies)
    print(f"Saved {len(cookies)} cookies to {SFS_COOKIE_EXPORT_PATH}")
    if cookies_valid(cookies):
        print("✓ Required cookies present (cf_clearance, session)")
    else:
        names = {c["name"] for c in cookies}
        missing = {"cf_clearance", "serviciul_fiscal_de_stat_session"} - names
        print(f"⚠ Missing required cookies: {missing}")
        print("Make sure you exported cookies after visiting and solving the Cloudflare challenge on sfs.md")

    # Print expiry info
    for c in cookies:
        if c["name"] == "cf_clearance":
            expiry = c.get("expiry") or c.get("expires")
            if expiry:
                import datetime
                dt = datetime.datetime.fromtimestamp(int(expiry))
                print(f"  cf_clearance expires: {dt}")


def cmd_status(args: argparse.Namespace) -> None:
    """Check if cookies are loaded and valid."""
    cookies = load_cookies()
    if not cookies:
        print("No SFS cookies found.")
        print(f"Run: python -m credibil.countries.moldova.providers.sfs_cli export")
        sys.exit(1)

    print(f"Found {len(cookies)} cookies:")
    for c in cookies:
        print(f"  {c['name']}: {c['value'][:20]}...")
    print()

    if cookies_valid(cookies):
        print("✓ All required cookies present")
    else:
        names = {c["name"] for c in cookies}
        missing = {"cf_clearance", "serviciul_fiscal_de_stat_session"} - names
        print(f"⚠ Missing: {missing}")


def cmd_test(args: argparse.Namespace) -> None:
    """Test SFS access with current cookies."""
    import asyncio

    provider = SFSProvider()
    result = asyncio.run(provider.fetch_tax_debt(args.idno))

    print(f"IDNO: {result.idno}")
    print(f"Error: {result.error}")
    print(f"Has debt: {result.has_debt}")
    print(f"Total: {result.total_amount}")
    print(f"Details: {result.debt_details}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Manage SFS cookies")
    sub = parser.add_subparsers(dest="command", required=True)

    p_export = sub.add_parser("export", help="Export cookies")
    p_export.add_argument("--file", "-f", help="JSON file with cookies (reads from stdin if omitted)")

    sub.add_parser("status", help="Check cookie status")

    p_test = sub.add_parser("test", help="Test SFS access")
    p_test.add_argument("--idno", required=True, help="IDNO to check")

    args = parser.parse_args()

    if args.command == "export":
        cmd_export(args)
    elif args.command == "status":
        cmd_status(args)
    elif args.command == "test":
        cmd_test(args)


if __name__ == "__main__":
    main()
