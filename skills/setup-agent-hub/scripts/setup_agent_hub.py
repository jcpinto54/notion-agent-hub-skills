#!/usr/bin/env python3
"""Configure local Agent Hub Notion credentials and default hub metadata."""

from __future__ import annotations

import argparse
import getpass
import json
import os
import re
import stat
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


GLOBAL_ENV_PATH = Path.home() / ".codex" / "agent-hub" / ".env"
REPO_ENV_NAME = ".agent-hub.local"
DEFAULT_VERSION = "2026-03-11"
TOKEN_KEY = "NOTION_AGENT_HUB_TOKEN"
DATA_SOURCE_KEY = "NOTION_AGENT_HUB_DATA_SOURCE_ID"
PAGE_URL_KEY = "NOTION_AGENT_HUB_PAGE_URL"


class SetupError(RuntimeError):
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


def config_path(args: argparse.Namespace) -> Path:
    if args.env_path:
        return args.env_path.expanduser()
    if args.global_config:
        return GLOBAL_ENV_PATH
    if args.repo_local:
        root_path = repo_env_path()
        if not root_path:
            raise SetupError("--repo-local was requested, but no git repository was found.")
        return root_path
    root_path = repo_env_path()
    return root_path if root_path else GLOBAL_ENV_PATH


def merged_config(target_path: Path | None = None) -> dict[str, str]:
    values = read_env(GLOBAL_ENV_PATH)
    repo_path = repo_env_path()
    if repo_path:
        values.update(read_env(repo_path))
    if target_path and target_path not in {GLOBAL_ENV_PATH, repo_path}:
        values.update(read_env(target_path))
    values.update({key: value for key, value in os.environ.items() if value})
    return values


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
            raise SetupError(f"Notion API {method} {path} failed: HTTP {exc.code}: {detail}") from exc
        except urllib.error.URLError as exc:
            raise SetupError(f"Notion API {method} {path} failed: {exc}") from exc

    def search(self, query: str, page_size: int = 20) -> dict[str, Any]:
        body: dict[str, Any] = {"page_size": page_size}
        if query:
            body["query"] = query
        return self.request("POST", "/search", body)

    def retrieve_data_source(self, data_source_id: str) -> dict[str, Any]:
        return self.request("GET", f"/data_sources/{compact_id(data_source_id)}")

    def query_data_source(self, data_source_id: str, page_size: int = 1) -> dict[str, Any]:
        return self.request(
            "POST",
            f"/data_sources/{compact_id(data_source_id)}/query",
            {"page_size": page_size},
        )

    def retrieve_database(self, database_id: str) -> dict[str, Any]:
        return self.request("GET", f"/databases/{compact_id(database_id)}")

    def retrieve_page(self, page_id: str) -> dict[str, Any]:
        return self.request("GET", f"/pages/{compact_id(page_id)}")

    def block_children(self, block_id: str) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        start_cursor: str | None = None
        while True:
            query = f"?page_size=100"
            if start_cursor:
                query += "&start_cursor=" + urllib.parse.quote(start_cursor)
            payload = self.request("GET", f"/blocks/{compact_id(block_id)}/children{query}")
            results.extend(payload.get("results", []))
            if not payload.get("has_more"):
                return results
            start_cursor = payload.get("next_cursor")


def notion_search_check(client: NotionClient) -> None:
    client.search("", page_size=1)


def is_issues_data_source(payload: dict[str, Any]) -> bool:
    title = object_title(payload).strip().lower()
    return title in {"issues / activities", "issues", "activities"}


def data_source_record(payload: dict[str, Any]) -> dict[str, str]:
    data_source_id = payload.get("id") or payload.get("data_source_id") or ""
    url = payload.get("url") or payload.get("public_url") or ""
    title = object_title(payload)
    return {"id": compact_id(data_source_id), "url": url, "title": title}


def validate_data_source(client: NotionClient, value: str) -> dict[str, str]:
    data_source_id = compact_id(value)
    try:
        payload = client.retrieve_data_source(data_source_id)
        record = data_source_record(payload)
        if not record["id"]:
            record["id"] = data_source_id
        return record
    except SetupError:
        client.query_data_source(data_source_id, page_size=1)
        return {"id": data_source_id, "url": value if value.startswith("http") else "", "title": ""}


def candidates_from_database(database: dict[str, Any]) -> list[dict[str, str]]:
    candidates: list[dict[str, str]] = []
    for item in database.get("data_sources", []) or []:
        if not isinstance(item, dict):
            continue
        record = data_source_record(item)
        if record["id"]:
            candidates.append(record)
    return candidates


def discover_from_database(client: NotionClient, database_id: str) -> list[dict[str, str]]:
    database = client.retrieve_database(database_id)
    candidates = candidates_from_database(database)
    issues = [candidate for candidate in candidates if candidate["title"].strip().lower() == "issues / activities"]
    return issues or candidates


def discover_from_page(client: NotionClient, page_id: str) -> list[dict[str, str]]:
    client.retrieve_page(page_id)
    candidates: list[dict[str, str]] = []
    for block in client.block_children(page_id):
        block_type = block.get("type", "")
        if block_type == "child_database":
            title = rich_plain_text((block.get("child_database") or {}).get("title"))
            if title.strip().lower() == "issues / activities":
                candidates.extend(discover_from_database(client, block.get("id", "")))
        elif "data_source" in block_type:
            record = data_source_record(block.get(block_type) or block)
            if record["id"] and record["title"].strip().lower() == "issues / activities":
                candidates.append(record)
    return candidates


def discover_from_url(client: NotionClient, value: str) -> list[dict[str, str]]:
    raw_id = compact_id(value)
    attempts = [
        lambda: [validate_data_source(client, raw_id)],
        lambda: discover_from_database(client, raw_id),
        lambda: discover_from_page(client, raw_id),
    ]
    errors = []
    for attempt in attempts:
        try:
            candidates = attempt()
            issues = [candidate for candidate in candidates if candidate["title"].strip().lower() == "issues / activities"]
            if issues:
                return issues
            if candidates:
                return candidates
        except SetupError as exc:
            errors.append(str(exc))
    raise SetupError("Could not discover an Agent Hub data source from the supplied URL or ID.")


def unique_candidates(candidates: list[dict[str, str]]) -> list[dict[str, str]]:
    seen: set[str] = set()
    unique: list[dict[str, str]] = []
    for candidate in candidates:
        candidate_id = candidate.get("id", "")
        if not candidate_id or candidate_id in seen:
            continue
        seen.add(candidate_id)
        unique.append(candidate)
    return unique


def search_agent_hubs(client: NotionClient) -> list[dict[str, str]]:
    candidates: list[dict[str, str]] = []
    for query in ("Agent Hub", "Issues / Activities"):
        payload = client.search(query, page_size=25)
        for result in payload.get("results", []):
            object_type = result.get("object")
            try:
                if object_type == "data_source" and is_issues_data_source(result):
                    candidates.append(data_source_record(result))
                elif object_type == "database":
                    candidates.extend(discover_from_database(client, result.get("id", "")))
                elif object_type == "page":
                    title = object_title(result)
                    if "agent hub" in title.lower() or query == "Issues / Activities":
                        candidates.extend(discover_from_page(client, result.get("id", "")))
            except SetupError:
                continue
    issues = [candidate for candidate in candidates if candidate["title"].strip().lower() == "issues / activities"]
    return unique_candidates(issues or candidates)


def choose_single(candidates: list[dict[str, str]]) -> dict[str, str]:
    candidates = unique_candidates(candidates)
    if not candidates:
        raise SetupError("No Agent Hub Issues / Activities data source was found.")
    if len(candidates) == 1:
        return candidates[0]
    lines = ["Multiple Agent Hub data sources were found; rerun with --data-source-id or --hub-url:"]
    for candidate in candidates:
        title = candidate.get("title") or "(untitled)"
        url = candidate.get("url") or candidate.get("id")
        lines.append(f"- {title}: {url}")
    raise SetupError("\n".join(lines))


def resolve_data_source(client: NotionClient, args: argparse.Namespace, values: dict[str, str]) -> dict[str, str] | None:
    if args.data_source_id:
        return validate_data_source(client, args.data_source_id)
    if args.hub_url:
        return choose_single(discover_from_url(client, args.hub_url))
    existing = values.get(DATA_SOURCE_KEY)
    if existing:
        return validate_data_source(client, existing)
    if args.check_only:
        return None
    return choose_single(search_agent_hubs(client))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env-path", type=Path)
    parser.add_argument("--token", default=os.environ.get(TOKEN_KEY))
    parser.add_argument("--hub-url")
    parser.add_argument("--data-source-id")
    parser.add_argument("--repo-local", action="store_true")
    parser.add_argument("--global", dest="global_config", action="store_true")
    parser.add_argument("--notion-version", default=os.environ.get("NOTION_VERSION", DEFAULT_VERSION))
    parser.add_argument("--check-only", action="store_true")
    parser.add_argument("--no-prompt", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.repo_local and args.global_config:
        raise SystemExit("Choose only one of --repo-local or --global.")

    try:
        path = config_path(args)
        values = merged_config(path)
        token = args.token or values.get(TOKEN_KEY) or values.get("NOTION_TOKEN")
        if not token and not args.check_only and not args.no_prompt and sys.stdin.isatty():
            token = getpass.getpass("Notion Agent Hub token: ").strip()
        if not token:
            raise SetupError("Missing token. Set NOTION_AGENT_HUB_TOKEN or pass --token before running setup.")

        client = NotionClient(token, args.notion_version)
        notion_search_check(client)
        data_source = resolve_data_source(client, args, values)

        updates = {TOKEN_KEY: token}
        if data_source:
            updates[DATA_SOURCE_KEY] = data_source["id"]
        if args.hub_url:
            updates[PAGE_URL_KEY] = args.hub_url

        if not args.check_only:
            write_env(path, updates)
        validate_mode(path)

        configured = f" and data source {updates[DATA_SOURCE_KEY]}" if updates.get(DATA_SOURCE_KEY) else ""
        action = "validated" if args.check_only else "configured"
        print(f"OK: {action} Agent Hub Notion token{configured} using {path}")
        return 0
    except SetupError as exc:
        raise SystemExit(str(exc)) from exc


if __name__ == "__main__":
    raise SystemExit(main())
