#!/usr/bin/env python3
"""Store and validate the Notion token used by Agent Hub scripts."""

from __future__ import annotations

import argparse
import getpass
import json
import os
import stat
import sys
import urllib.error
import urllib.request
from pathlib import Path


DEFAULT_ENV_PATH = Path.home() / ".codex" / "agent-hub" / ".env"
DEFAULT_VERSION = "2026-03-11"


def read_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip("'\"")
    return values


def write_env(path: Path, token: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"NOTION_AGENT_HUB_TOKEN={token}\n", encoding="utf-8")
    path.chmod(stat.S_IRUSR | stat.S_IWUSR)


def validate_mode(path: Path) -> None:
    mode = stat.S_IMODE(path.stat().st_mode)
    if mode != 0o600:
        path.chmod(0o600)


def notion_search_check(token: str, notion_version: str) -> dict[str, object]:
    body = json.dumps({"page_size": 1}).encode("utf-8")
    request = urllib.request.Request(
        "https://api.notion.com/v1/search",
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Notion-Version": notion_version,
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"Notion auth check failed: HTTP {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise SystemExit(f"Notion auth check failed: {exc}") from exc


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env-path", type=Path, default=DEFAULT_ENV_PATH)
    parser.add_argument("--token", default=os.environ.get("NOTION_AGENT_HUB_TOKEN"))
    parser.add_argument("--notion-version", default=os.environ.get("NOTION_VERSION", DEFAULT_VERSION))
    parser.add_argument("--check-only", action="store_true")
    parser.add_argument("--no-prompt", action="store_true")
    args = parser.parse_args(argv)

    token = args.token
    values = read_env(args.env_path)
    if not token:
        token = values.get("NOTION_AGENT_HUB_TOKEN")
    if not token and not args.check_only and not args.no_prompt and sys.stdin.isatty():
        token = getpass.getpass("Notion Agent Hub token: ").strip()
    if not token:
        raise SystemExit(
            "Missing token. Set NOTION_AGENT_HUB_TOKEN or pass --token before running setup."
        )

    if not args.check_only:
        write_env(args.env_path, token)
    if not args.env_path.exists():
        raise SystemExit(f"Missing env file: {args.env_path}")
    validate_mode(args.env_path)
    notion_search_check(token, args.notion_version)

    print(f"OK: validated Notion token and secured {args.env_path} with mode 600")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

