#!/usr/bin/env python3
"""List Notion Agent Hub issues and compute dependency-aware readiness."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_ENV_PATH = Path.home() / ".codex" / "agent-hub" / ".env"
REPO_ENV_NAME = ".agent-hub.local"
DEFAULT_VERSION = "2026-03-11"
TOKEN_KEY = "NOTION_AGENT_HUB_TOKEN"
DATA_SOURCE_KEY = "NOTION_AGENT_HUB_DATA_SOURCE_ID"
STATUS_ORDER = ["Not Started", "In Progress", "In Review", "Completed"]
PRIORITY_ORDER = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
UNASSIGNED = {"", "unassigned", "none", "n/a"}


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


def find_repo_root(start: Path | None = None) -> Path | None:
    current = (start or Path.cwd()).resolve()
    for candidate in [current, *current.parents]:
        if (candidate / ".git").exists():
            return candidate
    return None


def repo_env_path(start: Path | None = None) -> Path | None:
    root = find_repo_root(start)
    return root / REPO_ENV_NAME if root else None


def load_config(path: Path | None = None) -> dict[str, str]:
    values = read_env(DEFAULT_ENV_PATH)
    repo_path = repo_env_path()
    if repo_path:
        values.update(read_env(repo_path))
    if path:
        values.update(read_env(path))
    values.update({key: value for key, value in os.environ.items() if value})
    return values


def load_env(path: Path = DEFAULT_ENV_PATH) -> None:
    for key, value in load_config(path).items():
        os.environ.setdefault(key, value)


def compact_id(value: str) -> str:
    match = re.search(r"([0-9a-fA-F]{32})", value.replace("-", ""))
    if not match:
        return value
    raw = match.group(1).lower()
    return f"{raw[0:8]}-{raw[8:12]}-{raw[12:16]}-{raw[16:20]}-{raw[20:32]}"


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
            raise RuntimeError(f"Notion API {method} {path} failed: HTTP {exc.code}: {detail}") from exc

    def query_data_source(self, data_source_id: str) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        start_cursor: str | None = None
        while True:
            body: dict[str, Any] = {"page_size": 100}
            if start_cursor:
                body["start_cursor"] = start_cursor
            payload = self.request("POST", f"/data_sources/{compact_id(data_source_id)}/query", body)
            results.extend(payload.get("results", []))
            if not payload.get("has_more"):
                return results
            start_cursor = payload.get("next_cursor")


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


def prop_datetime(prop: dict[str, Any] | None) -> datetime | None:
    text = prop_text(prop)
    if not text:
        return None
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None


@dataclass
class Issue:
    id: str
    url: str
    title: str
    status: str
    owner: str
    priority: str
    type: str
    area: str
    summary: str
    blockers: str
    dependency_notes: str
    depends_on: list[str]
    blocks: list[str]
    updated_at: datetime | None
    claim_id: str
    claim_expires_at: datetime | None

    @classmethod
    def from_page(cls, page: dict[str, Any]) -> "Issue":
        props = page.get("properties", {})
        return cls(
            id=page.get("id", ""),
            url=page.get("url", ""),
            title=prop_text(props.get("Title")) or "(Untitled)",
            status=prop_text(props.get("Status")) or "-",
            owner=prop_text(props.get("Owner")),
            priority=prop_text(props.get("Priority")),
            type=prop_text(props.get("Type")),
            area=prop_text(props.get("Area")),
            summary=prop_text(props.get("Summary")),
            blockers=prop_text(props.get("Blockers")),
            dependency_notes=prop_text(props.get("Dependency Notes")),
            depends_on=prop_relation_ids(props.get("Depends On")),
            blocks=prop_relation_ids(props.get("Blocks")),
            updated_at=prop_datetime(props.get("Updated At")) or page_last_edited(page),
            claim_id=prop_text(props.get("Claim ID")),
            claim_expires_at=prop_datetime(props.get("Claim Expires At")),
        )


def page_last_edited(page: dict[str, Any]) -> datetime | None:
    value = page.get("last_edited_time")
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def is_unassigned(owner: str) -> bool:
    return owner.strip().lower() in UNASSIGNED


def has_active_claim(issue: Issue, now: datetime | None = None) -> bool:
    if not issue.claim_id:
        return False
    if not issue.claim_expires_at:
        return True
    now = now or datetime.now(timezone.utc)
    return issue.claim_expires_at > now


def readiness(issue: Issue, by_id: dict[str, Issue]) -> tuple[str, str]:
    if issue.status == "In Review":
        reasons: list[str] = []
        if issue.owner and not is_unassigned(issue.owner):
            reasons.append(f"owned by {issue.owner}")
        if has_active_claim(issue):
            reasons.append("active claim")
        if reasons:
            return "Blocked", "; ".join(reasons)
        return "Ready", "ready for review"
    if issue.status != "Not Started":
        return "-", ""
    reasons: list[str] = []
    if issue.owner and not is_unassigned(issue.owner):
        reasons.append(f"owned by {issue.owner}")
    if issue.blockers:
        reasons.append("external blocker")
    if has_active_claim(issue):
        reasons.append("active claim")
    unknown_deps: list[str] = []
    incomplete_deps: list[str] = []
    for dep_id in issue.depends_on:
        dep = by_id.get(dep_id)
        if not dep:
            unknown_deps.append(dep_id)
        elif dep.status != "Completed":
            incomplete_deps.append(dep.title)
    if unknown_deps:
        return "Unknown", "dependency status unavailable"
    if incomplete_deps:
        reasons.append("waiting on " + ", ".join(incomplete_deps))
    if reasons:
        return "Blocked", "; ".join(reasons)
    return "Ready", ""


def issue_sort_key(issue: Issue) -> tuple[int, int, float]:
    status_index = STATUS_ORDER.index(issue.status) if issue.status in STATUS_ORDER else len(STATUS_ORDER)
    priority_index = PRIORITY_ORDER.get(issue.priority, 99)
    updated = issue.updated_at.timestamp() if issue.updated_at else 0
    return (status_index, priority_index, -updated)


def apply_filters(
    issues: list[Issue], by_id: dict[str, Issue], args: argparse.Namespace
) -> list[tuple[Issue, str, str]]:
    rows: list[tuple[Issue, str, str]] = []
    for issue in issues:
        ready, reason = readiness(issue, by_id)
        if args.status and issue.status != args.status:
            continue
        if args.owner and args.owner.lower() not in issue.owner.lower():
            continue
        if args.priority and issue.priority != args.priority:
            continue
        if args.type and issue.type != args.type:
            continue
        if args.area and args.area.lower() not in issue.area.lower():
            continue
        if args.readiness and ready.lower() != args.readiness.lower():
            continue
        rows.append((issue, ready, reason))
    return rows


def short(value: str, limit: int = 48) -> str:
    value = " ".join(value.split())
    if not value:
        return "-"
    return value if len(value) <= limit else value[: limit - 1].rstrip() + "..."


def dependency_titles(ids: list[str], by_id: dict[str, Issue]) -> str:
    if not ids:
        return "-"
    return ", ".join(short(by_id.get(item_id).title if item_id in by_id else item_id, 28) for item_id in ids)


def render_board(
    lines: list[str],
    title: str,
    rows: list[tuple[Issue, str, str]],
    by_id: dict[str, Issue],
    start_number: int,
) -> int:
    lines.append(f"### {title}")
    if not rows:
        lines.append("No issues.")
        lines.append("")
        return start_number

    lines.append("| # | Issue | Status | Owner | Priority | Type | Depends On | Reason |")
    lines.append("|---|---|---|---|---|---|---|---|")
    number = start_number
    for issue, ready, reason in rows:
        title_text = short(issue.title, 56)
        linked = f"[{title_text}]({issue.url})" if issue.url else title_text
        reason_text = issue.blockers or reason or ready
        lines.append(
            f"| {number} | {linked} | {short(issue.status, 18)} | {short(issue.owner)} | "
            f"{short(issue.priority, 12)} | {short(issue.type, 18)} | "
            f"{dependency_titles(issue.depends_on, by_id)} | {short(reason_text, 44)} |"
        )
        number += 1
    lines.append("")
    return number


def markdown(rows: list[tuple[Issue, str, str]], by_id: dict[str, Issue], limit: int) -> str:
    counts = {status: 0 for status in STATUS_ORDER}
    for issue, _, _ in rows:
        if issue.status in counts:
            counts[issue.status] += 1

    eligible_not_started_rows = [row for row in rows if row[0].status == "Not Started" and row[1] == "Ready"]
    eligible_in_review_rows = [row for row in rows if row[0].status == "In Review" and row[1] == "Ready"]
    blocked_rows = [row for row in rows if row[1] in {"Blocked", "Unknown"}]
    eligible_not_started_visible = eligible_not_started_rows[:limit]
    eligible_in_review_visible = eligible_in_review_rows[:limit]
    blocked_visible = blocked_rows[:limit]
    lines = ["## Agent Hub Issues", ""]
    lines.append(
        "Counts: "
        + " | ".join(f"{status} `{counts[status]}`" for status in STATUS_ORDER)
    )
    lines.append("")
    lines.append(
        f"Eligible to pick up: Not Started `{len(eligible_not_started_rows)}` | "
        f"In Review `{len(eligible_in_review_rows)}` | "
        f"Blocked: `{len(blocked_rows)}` | Completed: `{counts['Completed']}`"
    )
    lines.append("")

    number = 1
    number = render_board(lines, "Eligible (Not Started)", eligible_not_started_visible, by_id, number)
    number = render_board(lines, "Eligible (In Review)", eligible_in_review_visible, by_id, number)
    number = render_board(lines, "Blocked", blocked_visible, by_id, number)

    if len(eligible_not_started_rows) > limit:
        lines.append(
            f"Showing {limit} of {len(eligible_not_started_rows)} eligible Not Started issues. "
            "Increase --limit to see more."
        )
    if len(eligible_in_review_rows) > limit:
        lines.append(
            f"Showing {limit} of {len(eligible_in_review_rows)} eligible In Review issues. "
            "Increase --limit to see more."
        )
    if len(blocked_rows) > limit:
        lines.append(
            f"Showing {limit} of {len(blocked_rows)} blocked issues. Increase --limit to see more."
        )
    eligible_total = len(eligible_not_started_rows) + len(eligible_in_review_rows)
    if eligible_total > 10:
        lines.append("Subagent pickup is capped at 10 eligible issues in one pass.")
    lines.append("")
    lines.append(
        "Do you want to spawn subagents for the eligible issues (up to 10), or explore the completed issues?"
    )
    return "\n".join(lines).rstrip() + "\n"


def json_rows(rows: list[tuple[Issue, str, str]], by_id: dict[str, Issue], limit: int | None = None) -> str:
    payload = []
    visible_rows = rows[:limit] if limit is not None else rows
    for issue, ready, reason in visible_rows:
        payload.append(
            {
                "id": issue.id,
                "url": issue.url,
                "title": issue.title,
                "status": issue.status,
                "owner": issue.owner,
                "priority": issue.priority,
                "type": issue.type,
                "area": issue.area,
                "summary": issue.summary,
                "blockers": issue.blockers,
                "depends_on": [
                    {"id": dep_id, "title": by_id[dep_id].title if dep_id in by_id else None}
                    for dep_id in issue.depends_on
                ],
                "blocks": [
                    {"id": block_id, "title": by_id[block_id].title if block_id in by_id else None}
                    for block_id in issue.blocks
                ],
                "readiness": ready,
                "readiness_reason": reason,
                "claim_id": issue.claim_id,
                "claim_expires_at": issue.claim_expires_at.isoformat()
                if issue.claim_expires_at
                else "",
                "updated_at": issue.updated_at.isoformat() if issue.updated_at else "",
            }
        )
    return json.dumps(payload, indent=2, sort_keys=True)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data-source-id",
        "--source",
        help=f"Notion data source ID or URL. Defaults to {DATA_SOURCE_KEY} from Agent Hub config.",
    )
    parser.add_argument("--status", choices=STATUS_ORDER)
    parser.add_argument("--owner")
    parser.add_argument("--priority", choices=["P0", "P1", "P2", "P3"])
    parser.add_argument("--type")
    parser.add_argument("--area")
    parser.add_argument("--readiness", choices=["Ready", "Blocked", "Unknown"])
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    parser.add_argument("--limit", type=int, default=30)
    parser.add_argument("--notion-version", default=os.environ.get("NOTION_VERSION", DEFAULT_VERSION))
    parser.add_argument("--env-path", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    values = load_config(args.env_path)
    token = values.get(TOKEN_KEY) or values.get("NOTION_TOKEN")
    if not token:
        raise SystemExit("Missing NOTION_AGENT_HUB_TOKEN. Run setup-agent-hub first.")
    data_source_id = args.data_source_id or values.get(DATA_SOURCE_KEY)
    if not data_source_id:
        raise SystemExit(
            f"Missing data source. Run setup-agent-hub or pass --data-source-id."
        )

    client = NotionClient(token, args.notion_version)
    pages = client.query_data_source(data_source_id)
    issues = [Issue.from_page(page) for page in pages]
    issues.sort(key=issue_sort_key)
    by_id = {issue.id: issue for issue in issues}
    rows = apply_filters(issues, by_id, args)

    if args.format == "json":
        print(json_rows(rows, by_id, args.limit))
    else:
        print(markdown(rows, by_id, args.limit))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
