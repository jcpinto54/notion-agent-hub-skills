#!/usr/bin/env python3
"""Configure local Agent Hub Notion credentials and default hub metadata."""

from __future__ import annotations

import argparse
import getpass
import os
import sys
from pathlib import Path
from typing import Any

COMMON_LIB = Path(__file__).resolve().parents[2] / "manage-agent-hub-issues" / "lib"
sys.path.insert(0, str(COMMON_LIB))

from agent_hub_common import (  # noqa: E402
    DATA_SOURCE_KEY,
    DEFAULT_VERSION,
    PAGE_URL_KEY,
    TOKEN_KEY,
    NotionApiError,
    NotionClient,
    compact_id,
    config_path as shared_config_path,
    load_config,
    object_title,
    validate_mode,
    write_env,
)


class SetupError(RuntimeError):
    pass


def config_path(args: argparse.Namespace) -> Path:
    try:
        return shared_config_path(
            env_path=args.env_path,
            repo_local=args.repo_local,
            global_config=args.global_config,
        )
    except RuntimeError as exc:
        raise SetupError(str(exc)) from exc


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
    except NotionApiError:
        client.query_data_source_once(data_source_id, page_size=1)
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
        values = load_config(path)
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
    except (SetupError, NotionApiError) as exc:
        raise SystemExit(str(exc)) from exc


if __name__ == "__main__":
    raise SystemExit(main())
