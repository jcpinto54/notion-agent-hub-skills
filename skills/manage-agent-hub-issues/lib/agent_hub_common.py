#!/usr/bin/env python3
"""Shared helpers for Agent Hub direct Notion API scripts."""

from __future__ import annotations

import json
import os
import re
import stat
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any


GLOBAL_ENV_PATH = Path.home() / ".codex" / "agent-hub" / ".env"
DEFAULT_ENV_PATH = GLOBAL_ENV_PATH
REPO_ENV_NAME = ".agent-hub.local"
DEFAULT_VERSION = "2026-03-11"
TOKEN_KEY = "NOTION_AGENT_HUB_TOKEN"
DATA_SOURCE_KEY = "NOTION_AGENT_HUB_DATA_SOURCE_ID"
PAGE_URL_KEY = "NOTION_AGENT_HUB_PAGE_URL"
STATUS_ORDER = ["Not Started", "In Progress", "In Review", "Completed"]
PRIORITY_ORDER = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
UNASSIGNED = {"", "unassigned", "none", "n/a"}


class NotionApiError(RuntimeError):
    pass


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


def format_env(values: dict[str, str]) -> str:
    ordered = [TOKEN_KEY, DATA_SOURCE_KEY, PAGE_URL_KEY]
    lines = []
    for key in ordered:
        if values.get(key):
            lines.append(f"{key}={values[key]}")
    for key in sorted(values):
        if key not in ordered and values[key]:
            lines.append(f"{key}={values[key]}")
    return "\n".join(lines).rstrip() + "\n"


def write_env(path: Path, values: dict[str, str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = read_env(path)
    existing.update({key: value for key, value in values.items() if value})
    path.write_text(format_env(existing), encoding="utf-8")
    path.chmod(stat.S_IRUSR | stat.S_IWUSR)


def validate_mode(path: Path) -> None:
    if not path.exists():
        return
    mode = stat.S_IMODE(path.stat().st_mode)
    if mode != 0o600:
        path.chmod(0o600)


def find_repo_root(start: Path | None = None) -> Path | None:
    current = (start or Path.cwd()).resolve()
    for candidate in [current, *current.parents]:
        if (candidate / ".git").exists():
            return candidate
    return None


def repo_env_path(start: Path | None = None) -> Path | None:
    root = find_repo_root(start)
    return root / REPO_ENV_NAME if root else None


def config_path(
    env_path: Path | None = None,
    repo_local: bool = False,
    global_config: bool = False,
) -> Path:
    if env_path:
        return env_path.expanduser()
    if global_config:
        return GLOBAL_ENV_PATH
    root_path = repo_env_path()
    if repo_local and not root_path:
        raise RuntimeError("--repo-local was requested, but no git repository was found.")
    if repo_local:
        return root_path
    return root_path if root_path else GLOBAL_ENV_PATH


def load_config(path: Path | None = None) -> dict[str, str]:
    values = read_env(GLOBAL_ENV_PATH)
    repo_path = repo_env_path()
    if repo_path:
        values.update(read_env(repo_path))
    if path and path not in {GLOBAL_ENV_PATH, repo_path}:
        values.update(read_env(path))
    values.update({key: value for key, value in os.environ.items() if value})
    return values


def load_env(path: Path | None = None) -> None:
    for key, value in load_config(path).items():
        os.environ.setdefault(key, value)


def compact_id(value: str) -> str:
    match = re.search(r"([0-9a-fA-F]{32})", value.replace("-", ""))
    if not match:
        return value
    raw = match.group(1).lower()
    return f"{raw[0:8]}-{raw[8:12]}-{raw[12:16]}-{raw[16:20]}-{raw[20:32]}"


def rich_plain_text(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return "".join(part.get("plain_text", "") for part in value if isinstance(part, dict))
    if isinstance(value, dict):
        for key in ("plain_text", "name"):
            if value.get(key):
                return str(value[key])
        if value.get("title"):
            return rich_plain_text(value["title"])
        if value.get("rich_text"):
            return rich_plain_text(value["rich_text"])
    return ""


def object_title(payload: dict[str, Any]) -> str:
    for key in ("title", "name"):
        text = rich_plain_text(payload.get(key))
        if text:
            return text
    return ""


class NotionClient:
    def __init__(self, token: str, version: str = DEFAULT_VERSION) -> None:
        self.token = token
        self.version = version

    def request(self, method: str, path: str, body: dict[str, Any] | None = None) -> dict[str, Any]:
        data = json.dumps(body).encode("utf-8") if body is not None else None
        request = urllib.request.Request(
            f"https://api.notion.com/v1{path}",
            data=data,
            method=method,
            headers={
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
                "Notion-Version": self.version,
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise NotionApiError(f"Notion API {method} {path} failed: HTTP {exc.code}: {detail}") from exc
        except urllib.error.URLError as exc:
            raise NotionApiError(f"Notion API {method} {path} failed: {exc}") from exc

    def search(self, query: str, page_size: int = 20) -> dict[str, Any]:
        body: dict[str, Any] = {"page_size": page_size}
        if query:
            body["query"] = query
        return self.request("POST", "/search", body)

    def retrieve_data_source(self, data_source_id: str) -> dict[str, Any]:
        return self.request("GET", f"/data_sources/{compact_id(data_source_id)}")

    def query_data_source_once(self, data_source_id: str, page_size: int = 1) -> dict[str, Any]:
        return self.request(
            "POST",
            f"/data_sources/{compact_id(data_source_id)}/query",
            {"page_size": page_size},
        )

    def query_data_source(self, data_source_id: str, page_size: int = 100) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        start_cursor: str | None = None
        while True:
            body: dict[str, Any] = {"page_size": page_size}
            if start_cursor:
                body["start_cursor"] = start_cursor
            payload = self.request("POST", f"/data_sources/{compact_id(data_source_id)}/query", body)
            results.extend(payload.get("results", []))
            if not payload.get("has_more"):
                return results
            start_cursor = payload.get("next_cursor")

    def retrieve_database(self, database_id: str) -> dict[str, Any]:
        return self.request("GET", f"/databases/{compact_id(database_id)}")

    def retrieve_page(self, page_id: str) -> dict[str, Any]:
        return self.request("GET", f"/pages/{compact_id(page_id)}")

    def get_page(self, page_id: str) -> dict[str, Any]:
        return self.retrieve_page(page_id)

    def update_page(self, page_id: str, properties: dict[str, Any]) -> dict[str, Any]:
        return self.request("PATCH", f"/pages/{compact_id(page_id)}", {"properties": properties})

    def block_children(self, block_id: str) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        start_cursor: str | None = None
        while True:
            query = "?page_size=100"
            if start_cursor:
                query += "&start_cursor=" + urllib.parse.quote(start_cursor)
            payload = self.request("GET", f"/blocks/{compact_id(block_id)}/children{query}")
            results.extend(payload.get("results", []))
            if not payload.get("has_more"):
                return results
            start_cursor = payload.get("next_cursor")


def rich_text(value: str) -> dict[str, Any]:
    return {"rich_text": [{"type": "text", "text": {"content": value}}]} if value else {"rich_text": []}


def select_or_status(value: str, current: dict[str, Any] | None) -> dict[str, Any]:
    prop_type = (current or {}).get("type")
    if prop_type == "status":
        return {"status": {"name": value}}
    return {"select": {"name": value}}


def date_prop(value: datetime | None) -> dict[str, Any]:
    return {"date": {"start": value.isoformat().replace("+00:00", "Z")} if value else None}


def url_or_rich_text(value: str, current: dict[str, Any] | None) -> dict[str, Any]:
    if (current or {}).get("type") == "url":
        return {"url": value or None}
    return rich_text(value)


def prop_text(prop: dict[str, Any] | None) -> str:
    if not prop:
        return ""
    kind = prop.get("type")
    if kind == "title":
        return "".join(part.get("plain_text", "") for part in prop.get("title", []))
    if kind == "rich_text":
        return "".join(part.get("plain_text", "") for part in prop.get("rich_text", []))
    if kind == "select":
        return (prop.get("select") or {}).get("name", "")
    if kind == "status":
        return (prop.get("status") or {}).get("name", "")
    if kind == "url":
        return prop.get("url") or ""
    if kind == "date":
        return (prop.get("date") or {}).get("start", "")
    if kind == "created_time":
        return prop.get("created_time", "")
    if kind == "last_edited_time":
        return prop.get("last_edited_time", "")
    if kind == "people":
        return ", ".join(person.get("name", "") for person in prop.get("people", []))
    if kind == "relation":
        return ", ".join(item.get("id", "") for item in prop.get("relation", []))
    return ""


def prop_relation_ids(prop: dict[str, Any] | None) -> list[str]:
    if not prop or prop.get("type") != "relation":
        return []
    return [item["id"] for item in prop.get("relation", []) if item.get("id")]


def parse_notion_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def prop_datetime(prop: dict[str, Any] | None) -> datetime | None:
    return parse_notion_datetime(prop_text(prop))


def is_unassigned(owner: str) -> bool:
    return owner.strip().lower() in UNASSIGNED
