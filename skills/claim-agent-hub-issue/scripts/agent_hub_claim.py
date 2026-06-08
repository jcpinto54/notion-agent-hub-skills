#!/usr/bin/env python3
"""Claim, check, renew, and release Agent Hub ownership leases."""

from __future__ import annotations

import argparse
import json
import os
import sys
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

WORK_RELEASE_MODES = {"abandon", "handoff", "blocked", "submitted"}
REVIEW_RELEASE_MODES = {"review-pass", "review-fail", "review-abandon"}

COMMON_LIB = Path(__file__).resolve().parents[2] / "manage-agent-hub-issues" / "lib"
sys.path.insert(0, str(COMMON_LIB))

from agent_hub_common import (  # noqa: E402
    DATA_SOURCE_KEY,
    DEFAULT_VERSION,
    TOKEN_KEY,
    NotionClient,
    date_prop,
    is_unassigned,
    load_config,
    prop_datetime,
    prop_relation_ids,
    prop_text,
    rich_text,
    select_or_status,
    url_or_rich_text,
)


@dataclass
class Issue:
    id: str
    title: str
    status: str
    owner: str
    blockers: str
    dependency_notes: str
    depends_on: list[str]
    claim_id: str
    claim_expires_at: datetime | None
    commit_sha: str
    pr_url: str
    related_links: str
    props: dict[str, Any]

    @classmethod
    def from_page(cls, page: dict[str, Any]) -> "Issue":
        props = page.get("properties", {})
        return cls(
            id=page.get("id", ""),
            title=prop_text(props.get("Title")) or "(Untitled)",
            status=prop_text(props.get("Status")),
            owner=prop_text(props.get("Owner")),
            blockers=prop_text(props.get("Blockers")),
            dependency_notes=prop_text(props.get("Dependency Notes")),
            depends_on=prop_relation_ids(props.get("Depends On")),
            claim_id=prop_text(props.get("Claim ID")),
            claim_expires_at=prop_datetime(props.get("Claim Expires At")),
            commit_sha=prop_text(props.get("Commit SHA")),
            pr_url=prop_text(props.get("PR URL")),
            related_links=prop_text(props.get("Related Links")),
            props=props,
        )


def active_claim(issue: Issue, now: datetime | None = None) -> bool:
    if not issue.claim_id:
        return False
    if not issue.claim_expires_at:
        return True
    now = now or datetime.now(timezone.utc)
    return issue.claim_expires_at > now


def load_issue_statuses(client: NotionClient, data_source_id: str | None) -> dict[str, str]:
    if not data_source_id:
        return {}
    statuses: dict[str, str] = {}
    for page in client.query_data_source(data_source_id):
        props = page.get("properties", {})
        statuses[page.get("id", "")] = prop_text(props.get("Status"))
    return statuses


def dependency_failures(issue: Issue, statuses: dict[str, str]) -> list[str]:
    failures: list[str] = []
    for dep_id in issue.depends_on:
        status = statuses.get(dep_id)
        if status != "Completed":
            failures.append(f"{dep_id} ({status or 'unknown'})")
    return failures


def has_waiver(issue: Issue) -> bool:
    text = issue.dependency_notes.lower()
    return "waive" in text or "override" in text


def set_if_present(props: dict[str, Any], name: str, value: dict[str, Any], updates: dict[str, Any]) -> None:
    if name in props:
        updates[name] = value


def build_claim_updates(
    issue: Issue,
    args: argparse.Namespace,
    claim_id: str,
    claimed_at: datetime,
    expires_at: datetime,
) -> dict[str, Any]:
    updates: dict[str, Any] = {
        "Status": select_or_status("In Progress" if args.purpose == "work" else "In Review", issue.props.get("Status")),
        "Owner": rich_text(args.owner),
        "Claim ID": rich_text(claim_id),
        "Claimed At": date_prop(claimed_at),
        "Claim Expires At": date_prop(expires_at),
    }
    set_if_present(issue.props, "Base Branch", rich_text(args.base_branch or ""), updates)
    set_if_present(issue.props, "Branch", rich_text(args.branch or ""), updates)
    set_if_present(issue.props, "Worktree Path", rich_text(args.worktree_path or ""), updates)
    return {key: value for key, value in updates.items() if key in issue.props or key in {"Status", "Owner"}}


def require_claimable(issue: Issue, args: argparse.Namespace, statuses: dict[str, str]) -> None:
    if active_claim(issue):
        raise SystemExit(
            f"Refusing claim: active claim {issue.claim_id} expires at "
            f"{issue.claim_expires_at.isoformat() if issue.claim_expires_at else 'unknown'}."
        )
    if args.purpose == "work":
        if issue.status != "Not Started":
            raise SystemExit(f"Refusing work claim: status is {issue.status!r}, expected 'Not Started'.")
        if issue.owner and not is_unassigned(issue.owner):
            raise SystemExit(f"Refusing work claim: owner is already {issue.owner!r}.")
        if issue.blockers:
            raise SystemExit(f"Refusing work claim: Blockers is not empty: {issue.blockers}")
        failures = dependency_failures(issue, statuses)
        if failures:
            raise SystemExit("Refusing work claim: dependencies are not completed: " + ", ".join(failures))
    else:
        if issue.status != "In Review":
            raise SystemExit(f"Refusing review claim: status is {issue.status!r}, expected 'In Review'.")
        failures = dependency_failures(issue, statuses)
        if failures and not has_waiver(issue):
            raise SystemExit("Refusing review claim: prerequisites incomplete: " + ", ".join(failures))
        if not args.allow_missing_artifacts and not (
            issue.pr_url or issue.commit_sha or issue.related_links
        ):
            raise SystemExit(
                "Refusing review claim: issue lacks PR URL, Commit SHA, or Related Links evidence."
            )


def command_claim(client: NotionClient, args: argparse.Namespace) -> dict[str, Any]:
    page = client.get_page(args.page_id)
    issue = Issue.from_page(page)
    statuses = load_issue_statuses(client, args.data_source_id)
    require_claimable(issue, args, statuses)

    claimed_at = datetime.now(timezone.utc)
    expires_at = claimed_at + timedelta(minutes=args.ttl_minutes)
    claim_id = args.claim_id or f"{args.purpose}-{uuid.uuid4()}"
    updates = build_claim_updates(issue, args, claim_id, claimed_at, expires_at)
    client.update_page(args.page_id, updates)
    refetched = Issue.from_page(client.get_page(args.page_id))
    if refetched.claim_id != claim_id:
        raise SystemExit(
            f"Optimistic claim verification failed: expected {claim_id}, found {refetched.claim_id!r}."
        )
    return {
        "ok": True,
        "action": "claim",
        "purpose": args.purpose,
        "page_id": refetched.id,
        "title": refetched.title,
        "status": refetched.status,
        "owner": refetched.owner,
        "claim_id": refetched.claim_id,
        "claim_expires_at": refetched.claim_expires_at.isoformat()
        if refetched.claim_expires_at
        else "",
    }


def require_matching_claim(issue: Issue, claim_id: str) -> None:
    if not issue.claim_id:
        raise SystemExit("No active claim is recorded on this issue.")
    if issue.claim_id != claim_id:
        raise SystemExit(f"Claim mismatch: issue has {issue.claim_id!r}, got {claim_id!r}.")


def command_check(client: NotionClient, args: argparse.Namespace) -> dict[str, Any]:
    issue = Issue.from_page(client.get_page(args.page_id))
    if args.claim_id:
        require_matching_claim(issue, args.claim_id)
    return {
        "ok": True,
        "action": "check",
        "page_id": issue.id,
        "title": issue.title,
        "status": issue.status,
        "owner": issue.owner,
        "claim_id": issue.claim_id,
        "active": active_claim(issue),
        "claim_expires_at": issue.claim_expires_at.isoformat() if issue.claim_expires_at else "",
    }


def command_renew(client: NotionClient, args: argparse.Namespace) -> dict[str, Any]:
    issue = Issue.from_page(client.get_page(args.page_id))
    require_matching_claim(issue, args.claim_id)
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=args.ttl_minutes)
    client.update_page(args.page_id, {"Claim Expires At": date_prop(expires_at)})
    refetched = Issue.from_page(client.get_page(args.page_id))
    require_matching_claim(refetched, args.claim_id)
    return {
        "ok": True,
        "action": "renew",
        "page_id": refetched.id,
        "claim_id": refetched.claim_id,
        "claim_expires_at": refetched.claim_expires_at.isoformat()
        if refetched.claim_expires_at
        else "",
    }


def release_updates(issue: Issue, args: argparse.Namespace) -> dict[str, Any]:
    updates: dict[str, Any] = {
        "Claim ID": rich_text(""),
        "Claimed At": date_prop(None),
        "Claim Expires At": date_prop(None),
    }
    if args.mode == "abandon":
        repo_work_exists = bool(issue.commit_sha or issue.pr_url or prop_text(issue.props.get("Branch")))
        updates["Status"] = select_or_status(
            "In Progress" if repo_work_exists else "Not Started", issue.props.get("Status")
        )
        updates["Owner"] = rich_text(args.owner or ("Unassigned" if not repo_work_exists else issue.owner))
    elif args.mode == "handoff":
        updates["Status"] = select_or_status("In Progress", issue.props.get("Status"))
        updates["Owner"] = rich_text(args.owner or "Unassigned")
    elif args.mode == "blocked":
        updates["Status"] = select_or_status("In Progress", issue.props.get("Status"))
        if args.blocker and "Blockers" in issue.props:
            updates["Blockers"] = rich_text(args.blocker)
        if args.owner:
            updates["Owner"] = rich_text(args.owner)
    elif args.mode == "submitted":
        if not issue.pr_url and not args.pr_url:
            raise SystemExit("Refusing submitted release: PR URL is required.")
        updates["Status"] = select_or_status("In Review", issue.props.get("Status"))
        updates["Owner"] = rich_text(args.owner or "Unassigned")
        if args.commit_sha and "Commit SHA" in issue.props:
            updates["Commit SHA"] = rich_text(args.commit_sha)
        if args.pr_url and "PR URL" in issue.props:
            updates["PR URL"] = url_or_rich_text(args.pr_url, issue.props.get("PR URL"))
    elif args.mode == "review-pass":
        updates["Status"] = select_or_status("Completed", issue.props.get("Status"))
        updates["Owner"] = rich_text(args.owner or issue.owner)
    elif args.mode == "review-fail":
        updates["Status"] = select_or_status("In Progress", issue.props.get("Status"))
        updates["Owner"] = rich_text(args.owner or "Unassigned")
    elif args.mode == "review-abandon":
        updates["Status"] = select_or_status("In Review", issue.props.get("Status"))
        updates["Owner"] = rich_text(args.owner or "Unassigned")
    else:
        raise SystemExit(f"Unsupported release mode: {args.mode}")
    return {key: value for key, value in updates.items() if key in issue.props or key in {"Status", "Owner"}}


def command_release(client: NotionClient, args: argparse.Namespace) -> dict[str, Any]:
    issue = Issue.from_page(client.get_page(args.page_id))
    require_matching_claim(issue, args.claim_id)
    if args.mode in WORK_RELEASE_MODES and issue.status != "In Progress":
        raise SystemExit(f"Refusing work release from status {issue.status!r}; expected 'In Progress'.")
    if args.mode in REVIEW_RELEASE_MODES and issue.status != "In Review":
        raise SystemExit(f"Refusing review release from status {issue.status!r}; expected 'In Review'.")
    updates = release_updates(issue, args)
    client.update_page(args.page_id, updates)
    refetched = Issue.from_page(client.get_page(args.page_id))
    if refetched.claim_id:
        raise SystemExit(f"Release verification failed: claim still present as {refetched.claim_id!r}.")
    return {
        "ok": True,
        "action": "release",
        "mode": args.mode,
        "page_id": refetched.id,
        "title": refetched.title,
        "status": refetched.status,
        "owner": refetched.owner,
        "claim_id": refetched.claim_id,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env-path", type=Path)
    parser.add_argument("--notion-version", default=os.environ.get("NOTION_VERSION", DEFAULT_VERSION))
    subparsers = parser.add_subparsers(dest="command", required=True)

    claim = subparsers.add_parser("claim")
    claim.add_argument("--page-id", required=True)
    claim.add_argument(
        "--data-source-id",
        help=f"Notion data source ID or URL. Defaults to {DATA_SOURCE_KEY} from Agent Hub config.",
    )
    claim.add_argument("--purpose", choices=["work", "review"], required=True)
    claim.add_argument("--owner", required=True)
    claim.add_argument("--ttl-minutes", type=int, default=120)
    claim.add_argument("--claim-id")
    claim.add_argument("--base-branch")
    claim.add_argument("--branch")
    claim.add_argument("--worktree-path")
    claim.add_argument("--allow-missing-artifacts", action="store_true")

    check = subparsers.add_parser("check")
    check.add_argument("--page-id", required=True)
    check.add_argument("--claim-id")

    renew = subparsers.add_parser("renew")
    renew.add_argument("--page-id", required=True)
    renew.add_argument("--claim-id", required=True)
    renew.add_argument("--ttl-minutes", type=int, default=120)

    release = subparsers.add_parser("release")
    release.add_argument("--page-id", required=True)
    release.add_argument("--claim-id", required=True)
    release.add_argument(
        "--mode",
        choices=sorted(WORK_RELEASE_MODES | REVIEW_RELEASE_MODES),
        required=True,
    )
    release.add_argument("--owner")
    release.add_argument("--blocker")
    release.add_argument("--commit-sha")
    release.add_argument("--pr-url")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    values = load_config(args.env_path)
    token = values.get(TOKEN_KEY) or values.get("NOTION_TOKEN")
    if not token:
        raise SystemExit("Missing NOTION_AGENT_HUB_TOKEN. Run setup-agent-hub first.")
    if args.command == "claim" and not args.data_source_id:
        args.data_source_id = values.get(DATA_SOURCE_KEY)

    client = NotionClient(token, args.notion_version)
    if args.command == "claim":
        result = command_claim(client, args)
    elif args.command == "check":
        result = command_check(client, args)
    elif args.command == "renew":
        result = command_renew(client, args)
    elif args.command == "release":
        result = command_release(client, args)
    else:
        raise SystemExit(f"Unknown command: {args.command}")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
