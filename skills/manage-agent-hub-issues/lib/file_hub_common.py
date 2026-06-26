#!/usr/bin/env python3
"""Repo-native Agent Hub helpers for .hub issue files."""

from __future__ import annotations

import json
import re
import socket
import tempfile
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from agent_hub_common import PRIORITY_ORDER, STATUS_ORDER, find_repo_root, is_unassigned


HUB_DIR_NAME = ".hub"
CONFIG_NAME = "config.yml"
RUNTIME_DIR = "runtime"
CLAIMS_NAME = "claims.json"
ISSUES_DIR = "issues"
DECISIONS_DIR = "decisions"
ARTIFACTS_DIR = "artifacts"


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def isoformat(value: datetime | None) -> str:
    return value.isoformat().replace("+00:00", "Z") if value else ""


def parse_datetime(value: Any) -> datetime | None:
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    if not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def repo_hub_path(start: Path | None = None) -> Path | None:
    root = find_repo_root(start)
    if not root:
        return None
    hub = root / HUB_DIR_NAME
    return hub if (hub / CONFIG_NAME).exists() else None


def resolve_hub_path(start: Path | None = None, hub_root: Path | None = None) -> Path:
    if hub_root:
        return hub_root.expanduser().resolve()
    hub = repo_hub_path(start)
    if not hub:
        raise RuntimeError("No .hub/config.yml found. Run init-agent-hub for a repo-native hub.")
    return hub


def has_file_hub(start: Path | None = None, hub_root: Path | None = None) -> bool:
    try:
        return (resolve_hub_path(start, hub_root) / CONFIG_NAME).exists()
    except RuntimeError:
        return False


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return slug or "issue"


def parse_scalar(value: str) -> Any:
    value = value.strip()
    if value in {"", "null", "None"}:
        return "" if value == "" else None
    if value in {"[]", "{}"}:
        return [] if value == "[]" else {}
    if value in {"true", "false"}:
        return value == "true"
    if value.startswith(('"', "'")):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value.strip("'\"")
    if value.startswith("[") or value.startswith("{"):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value
    return value


def parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, text
    raw = text[4:end].splitlines()
    body = text[end + 5 :]
    data: dict[str, Any] = {}
    current_key: str | None = None
    for line in raw:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if not line.startswith(" ") and ":" in line:
            key, value = line.split(":", 1)
            current_key = key.strip()
            value = value.strip()
            data[current_key] = parse_scalar(value) if value else {}
            continue
        if current_key and line.startswith("  ") and ":" in line:
            if not isinstance(data.get(current_key), dict):
                data[current_key] = {}
            key, value = line.strip().split(":", 1)
            data[current_key][key.strip()] = parse_scalar(value)
            continue
        if current_key and line.startswith("  - "):
            if not isinstance(data.get(current_key), list):
                data[current_key] = []
            data[current_key].append(parse_scalar(line[4:]))
    return data, body


def format_scalar(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (list, dict)):
        return json.dumps(value, sort_keys=True)
    return json.dumps(str(value))


def dump_frontmatter(data: dict[str, Any]) -> str:
    lines = ["---"]
    for key, value in data.items():
        if isinstance(value, dict):
            if not value:
                lines.append(f"{key}: {{}}")
            else:
                lines.append(f"{key}:")
                for sub_key, sub_value in value.items():
                    lines.append(f"  {sub_key}: {format_scalar(sub_value)}")
        else:
            lines.append(f"{key}: {format_scalar(value)}")
    lines.append("---")
    return "\n".join(lines) + "\n"


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=path.parent, delete=False
    ) as handle:
        handle.write(text)
        temp_name = handle.name
    Path(temp_name).replace(path)


def normalize_list(value: Any) -> list[str]:
    if value is None or value == "":
        return []
    if isinstance(value, list):
        return [str(item) for item in value if str(item)]
    return [str(value)]


@dataclass
class FileHubIssue:
    id: str
    path: Path
    body: str
    title: str = ""
    status: str = "Not Started"
    owner: str = "Unassigned"
    priority: str = "P2"
    type: str = "Feature"
    area: str = ""
    summary: str = ""
    blockers: str = ""
    dependency_notes: str = ""
    depends_on: list[str] = field(default_factory=list)
    blocks: list[str] = field(default_factory=list)
    claim: dict[str, Any] = field(default_factory=dict)
    base_branch: str = ""
    branch: str = ""
    worktree_path: str = ""
    commit_sha: str = ""
    pr_url: str = ""
    related_links: str = ""
    notion_url: str = ""
    updated_at: datetime | None = None

    @classmethod
    def from_path(cls, path: Path) -> "FileHubIssue":
        data, body = parse_frontmatter(path.read_text(encoding="utf-8"))
        stat = path.stat()
        issue_id = str(data.get("id") or path.stem)
        return cls(
            id=issue_id,
            path=path,
            body=body,
            title=str(data.get("title") or issue_id),
            status=str(data.get("status") or "Not Started"),
            owner=str(data.get("owner") or "Unassigned"),
            priority=str(data.get("priority") or "P2"),
            type=str(data.get("type") or "Feature"),
            area=str(data.get("area") or ""),
            summary=str(data.get("summary") or ""),
            blockers=str(data.get("blockers") or ""),
            dependency_notes=str(data.get("dependency_notes") or ""),
            depends_on=normalize_list(data.get("depends_on")),
            blocks=normalize_list(data.get("blocks")),
            claim=data.get("claim") if isinstance(data.get("claim"), dict) else {},
            base_branch=str(data.get("base_branch") or ""),
            branch=str(data.get("branch") or ""),
            worktree_path=str(data.get("worktree_path") or ""),
            commit_sha=str(data.get("commit_sha") or ""),
            pr_url=str(data.get("pr_url") or ""),
            related_links=str(data.get("related_links") or ""),
            notion_url=str(data.get("notion_url") or ""),
            updated_at=datetime.fromtimestamp(stat.st_mtime, timezone.utc),
        )

    @property
    def url(self) -> str:
        return str(self.path)

    @property
    def claim_id(self) -> str:
        return str(self.claim.get("id") or "")

    @property
    def claim_expires_at(self) -> datetime | None:
        return parse_datetime(self.claim.get("expires_at"))

    def to_frontmatter(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "status": self.status,
            "type": self.type,
            "priority": self.priority,
            "owner": self.owner,
            "area": self.area,
            "summary": self.summary,
            "blockers": self.blockers,
            "dependency_notes": self.dependency_notes,
            "depends_on": self.depends_on,
            "blocks": self.blocks,
            "claim": self.claim,
            "base_branch": self.base_branch,
            "branch": self.branch,
            "worktree_path": self.worktree_path,
            "commit_sha": self.commit_sha,
            "pr_url": self.pr_url,
            "related_links": self.related_links,
            "notion_url": self.notion_url,
        }

    def write(self) -> None:
        atomic_write(self.path, dump_frontmatter(self.to_frontmatter()) + self.body.lstrip("\n"))

    def append_activity(self, heading: str, lines: list[str]) -> None:
        body = self.body.rstrip() + "\n\n"
        body += f"### {heading}\n"
        body += "\n".join(lines).rstrip() + "\n"
        self.body = body
        self.write()


def load_config(hub_path: Path) -> dict[str, Any]:
    config_path = hub_path / CONFIG_NAME
    if not config_path.exists():
        return {}
    data, body = parse_frontmatter("---\n" + config_path.read_text(encoding="utf-8") + "\n---\n")
    return data or {"raw": body}


def load_issues(hub_path: Path) -> list[FileHubIssue]:
    issues_dir = hub_path / ISSUES_DIR
    if not issues_dir.exists():
        return []
    return [FileHubIssue.from_path(path) for path in sorted(issues_dir.glob("*.md"))]


def issue_by_id(hub_path: Path, issue_id_or_path: str) -> FileHubIssue:
    candidate = Path(issue_id_or_path).expanduser()
    if candidate.exists():
        return FileHubIssue.from_path(candidate)
    issues = load_issues(hub_path)
    by_id = {issue.id: issue for issue in issues}
    if issue_id_or_path in by_id:
        return by_id[issue_id_or_path]
    for issue in issues:
        if issue.path.stem == issue_id_or_path:
            return issue
    raise RuntimeError(f"No .hub issue found for {issue_id_or_path!r}.")


def active_claim(issue: FileHubIssue, runtime_claim: dict[str, Any] | None = None) -> bool:
    claim = runtime_claim or issue.claim
    claim_id = str(claim.get("id") or "")
    if not claim_id:
        return False
    expires_at = parse_datetime(claim.get("expires_at"))
    if not expires_at:
        return True
    return expires_at > now_utc()


def readiness(issue: FileHubIssue, by_id: dict[str, FileHubIssue]) -> tuple[str, str]:
    if issue.status == "In Review":
        reasons: list[str] = []
        if issue.owner and not is_unassigned(issue.owner):
            reasons.append(f"owned by {issue.owner}")
        if active_claim(issue):
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
    if active_claim(issue):
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


def issue_sort_key(issue: FileHubIssue) -> tuple[int, int, float]:
    status_index = (
        STATUS_ORDER.index(issue.status) if issue.status in STATUS_ORDER else len(STATUS_ORDER)
    )
    priority_index = PRIORITY_ORDER.get(issue.priority, 99)
    updated = issue.updated_at.timestamp() if issue.updated_at else 0
    return (status_index, priority_index, -updated)


def runtime_claims_path(hub_path: Path) -> Path:
    return hub_path / RUNTIME_DIR / CLAIMS_NAME


def load_runtime_claims(hub_path: Path) -> dict[str, Any]:
    path = runtime_claims_path(hub_path)
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8") or "{}")


def write_runtime_claims(hub_path: Path, claims: dict[str, Any]) -> None:
    path = runtime_claims_path(hub_path)
    atomic_write(path, json.dumps(claims, indent=2, sort_keys=True) + "\n")


def current_runtime_claim(hub_path: Path, issue_id: str) -> dict[str, Any] | None:
    claim = load_runtime_claims(hub_path).get(issue_id)
    if isinstance(claim, dict) and active_claim_placeholder(claim):
        return claim
    return None


def active_claim_placeholder(claim: dict[str, Any]) -> bool:
    if not claim.get("id"):
        return False
    expires_at = parse_datetime(claim.get("expires_at"))
    return True if not expires_at else expires_at > now_utc()


def dependency_failures(issue: FileHubIssue, by_id: dict[str, FileHubIssue]) -> list[str]:
    failures: list[str] = []
    for dep_id in issue.depends_on:
        dep = by_id.get(dep_id)
        if not dep or dep.status != "Completed":
            failures.append(f"{dep_id} ({dep.status if dep else 'unknown'})")
    return failures


def has_waiver(issue: FileHubIssue) -> bool:
    text = issue.dependency_notes.lower()
    return "waive" in text or "override" in text


def create_hub(root: Path, project_name: str | None = None) -> Path:
    root = root.expanduser().resolve()
    hub = root / HUB_DIR_NAME
    (hub / ISSUES_DIR).mkdir(parents=True, exist_ok=True)
    (hub / DECISIONS_DIR).mkdir(parents=True, exist_ok=True)
    (hub / ARTIFACTS_DIR).mkdir(parents=True, exist_ok=True)
    (hub / RUNTIME_DIR).mkdir(parents=True, exist_ok=True)
    if not (hub / ".gitignore").exists():
        (hub / ".gitignore").write_text("runtime/\n", encoding="utf-8")
    if not (hub / CONFIG_NAME).exists():
        name = project_name or root.name
        config = {
            "version": "2",
            "project": name,
            "canonical_store": "file",
            "notion_mirror": {
                "enabled": False,
                "data_source_id": "",
                "page_url": "",
            },
        }
        atomic_write(hub / CONFIG_NAME, dump_frontmatter(config).strip("-\n") + "\n")
    return hub


def create_issue_file(
    hub_path: Path,
    title: str,
    issue_id: str | None = None,
    issue_type: str = "Feature",
    priority: str = "P2",
) -> FileHubIssue:
    issue_id = issue_id or slugify(title)
    path = hub_path / ISSUES_DIR / f"{issue_id}.md"
    if path.exists():
        raise RuntimeError(f"Issue already exists: {path}")
    issue = FileHubIssue(
        id=issue_id,
        path=path,
        title=title,
        type=issue_type,
        priority=priority,
        body="""## Context

## Scope

## Done Criteria
- [ ]

## Verification Steps
1.

## Assumptions

## Dependencies

## Open Questions

## Activity Log
""",
    )
    issue.write()
    return issue


def claim_issue(
    hub_path: Path,
    issue: FileHubIssue,
    purpose: str,
    owner: str,
    ttl_minutes: int,
    claim_id: str,
    base_branch: str = "",
    branch: str = "",
    worktree_path: str = "",
    allow_missing_artifacts: bool = False,
) -> dict[str, Any]:
    issues = load_issues(hub_path)
    by_id = {item.id: item for item in issues}
    runtime_claim = current_runtime_claim(hub_path, issue.id)
    if runtime_claim:
        raise RuntimeError(
            f"Refusing claim: active runtime claim {runtime_claim.get('id')}."
        )
    if active_claim(issue):
        raise RuntimeError(f"Refusing claim: active issue claim {issue.claim_id}.")
    failures = dependency_failures(issue, by_id)
    if purpose == "work":
        if issue.status != "Not Started":
            raise RuntimeError(f"Refusing work claim: status is {issue.status!r}.")
        if issue.owner and not is_unassigned(issue.owner):
            raise RuntimeError(f"Refusing work claim: owner is already {issue.owner!r}.")
        if issue.blockers:
            raise RuntimeError(f"Refusing work claim: Blockers is not empty: {issue.blockers}")
        if failures:
            raise RuntimeError(
                "Refusing work claim: dependencies are not completed: " + ", ".join(failures)
            )
        issue.status = "In Progress"
    else:
        if issue.status != "In Review":
            raise RuntimeError(f"Refusing review claim: status is {issue.status!r}.")
        if failures and not has_waiver(issue):
            raise RuntimeError(
                "Refusing review claim: prerequisites incomplete: " + ", ".join(failures)
            )
        if not allow_missing_artifacts and not (
            issue.pr_url or issue.commit_sha or issue.related_links
        ):
            raise RuntimeError(
                "Refusing review claim: issue lacks PR URL, Commit SHA, or Related Links evidence."
            )
    claimed_at = now_utc()
    expires_at = claimed_at + timedelta(minutes=ttl_minutes)
    claim = {
        "id": claim_id,
        "purpose": purpose,
        "owner": owner,
        "claimed_at": isoformat(claimed_at),
        "expires_at": isoformat(expires_at),
        "machine": socket.gethostname(),
    }
    issue.owner = owner
    issue.claim = claim
    issue.base_branch = base_branch or issue.base_branch
    issue.branch = branch or issue.branch
    issue.worktree_path = worktree_path or issue.worktree_path
    claims = load_runtime_claims(hub_path)
    claims[issue.id] = claim
    write_runtime_claims(hub_path, claims)
    issue.append_activity(
        f"Claimed for {purpose}",
        [
            f"Date: {isoformat(claimed_at)}",
            f"Agent: {owner}",
            f"Claim ID: {claim_id}",
            f"Branch: {issue.branch or '-'}",
            f"Worktree Path: {issue.worktree_path or '-'}",
        ],
    )
    refetched = issue_by_id(hub_path, issue.id)
    runtime_refetched = current_runtime_claim(hub_path, issue.id) or {}
    if refetched.claim_id != claim_id or runtime_refetched.get("id") != claim_id:
        raise RuntimeError("Optimistic file claim verification failed.")
    return {
        "ok": True,
        "action": "claim",
        "purpose": purpose,
        "page_id": refetched.id,
        "title": refetched.title,
        "status": refetched.status,
        "owner": refetched.owner,
        "claim_id": refetched.claim_id,
        "claim_expires_at": isoformat(refetched.claim_expires_at),
        "backend": "file",
    }


def check_issue(hub_path: Path, issue: FileHubIssue, claim_id: str = "") -> dict[str, Any]:
    runtime_claim = current_runtime_claim(hub_path, issue.id)
    active = active_claim(issue, runtime_claim)
    current_id = str((runtime_claim or issue.claim).get("id") or "")
    if claim_id and current_id != claim_id:
        raise RuntimeError(f"Claim mismatch: issue has {current_id!r}, got {claim_id!r}.")
    return {
        "ok": True,
        "action": "check",
        "page_id": issue.id,
        "title": issue.title,
        "status": issue.status,
        "owner": issue.owner,
        "claim_id": current_id,
        "active": active,
        "claim_expires_at": str((runtime_claim or issue.claim).get("expires_at") or ""),
        "backend": "file",
    }


def renew_issue(
    hub_path: Path, issue: FileHubIssue, claim_id: str, ttl_minutes: int
) -> dict[str, Any]:
    check_issue(hub_path, issue, claim_id)
    expires_at = now_utc() + timedelta(minutes=ttl_minutes)
    issue.claim["expires_at"] = isoformat(expires_at)
    claims = load_runtime_claims(hub_path)
    claims.setdefault(issue.id, issue.claim)
    claims[issue.id]["expires_at"] = isoformat(expires_at)
    write_runtime_claims(hub_path, claims)
    issue.write()
    return {
        "ok": True,
        "action": "renew",
        "page_id": issue.id,
        "claim_id": claim_id,
        "claim_expires_at": isoformat(expires_at),
        "backend": "file",
    }


def release_issue(
    hub_path: Path,
    issue: FileHubIssue,
    claim_id: str,
    mode: str,
    owner: str = "",
    blocker: str = "",
    commit_sha: str = "",
    pr_url: str = "",
) -> dict[str, Any]:
    check_issue(hub_path, issue, claim_id)
    if mode in {"abandon", "handoff", "blocked", "submitted"} and issue.status != "In Progress":
        raise RuntimeError(
            f"Refusing work release from status {issue.status!r}; expected 'In Progress'."
        )
    if mode in {"review-pass", "review-fail", "review-abandon"} and issue.status != "In Review":
        raise RuntimeError(
            f"Refusing review release from status {issue.status!r}; expected 'In Review'."
        )
    if mode == "abandon":
        repo_work_exists = bool(issue.commit_sha or issue.pr_url or issue.branch)
        issue.status = "In Progress" if repo_work_exists else "Not Started"
        issue.owner = owner or ("Unassigned" if not repo_work_exists else issue.owner)
    elif mode == "handoff":
        issue.status = "In Progress"
        issue.owner = owner or "Unassigned"
    elif mode == "blocked":
        issue.status = "In Progress"
        issue.blockers = blocker or issue.blockers
        if owner:
            issue.owner = owner
    elif mode == "submitted":
        if not issue.pr_url and not pr_url:
            raise RuntimeError("Refusing submitted release: PR URL is required.")
        issue.status = "In Review"
        issue.owner = owner or "Unassigned"
        issue.commit_sha = commit_sha or issue.commit_sha
        issue.pr_url = pr_url or issue.pr_url
    elif mode == "review-pass":
        issue.status = "Completed"
        issue.owner = owner or issue.owner
    elif mode == "review-fail":
        issue.status = "In Progress"
        issue.owner = owner or "Unassigned"
    elif mode == "review-abandon":
        issue.status = "In Review"
        issue.owner = owner or "Unassigned"
    else:
        raise RuntimeError(f"Unsupported release mode: {mode}")
    claims = load_runtime_claims(hub_path)
    claims.pop(issue.id, None)
    write_runtime_claims(hub_path, claims)
    issue.claim = {}
    issue.append_activity(
        f"Released claim ({mode})",
        [
            f"Date: {isoformat(now_utc())}",
            f"Claim ID: {claim_id}",
            f"Mode: {mode}",
            f"Status: {issue.status}",
            f"Owner: {issue.owner}",
        ],
    )
    refetched = issue_by_id(hub_path, issue.id)
    if current_runtime_claim(hub_path, issue.id) or refetched.claim_id:
        raise RuntimeError("Release verification failed: claim still present.")
    return {
        "ok": True,
        "action": "release",
        "mode": mode,
        "page_id": refetched.id,
        "title": refetched.title,
        "status": refetched.status,
        "owner": refetched.owner,
        "claim_id": refetched.claim_id,
        "backend": "file",
    }
