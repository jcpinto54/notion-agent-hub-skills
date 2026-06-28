#!/usr/bin/env python3
"""Deterministic repo-native Agent Hub v3 CLI."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

COMMON_LIB = Path(__file__).resolve().parents[1] / "lib"
sys.path.insert(0, str(COMMON_LIB))

from agent_hub_common import STATUS_ORDER, find_repo_root  # noqa: E402
import file_hub_common as file_hub  # noqa: E402


def repo_root_from_arg(path: Path) -> Path:
    candidate = path.expanduser().resolve()
    if candidate.name == file_hub.HUB_DIR_NAME and (candidate / file_hub.CONFIG_NAME).exists():
        return candidate.parent
    if (candidate / file_hub.HUB_DIR_NAME / file_hub.CONFIG_NAME).exists():
        return candidate
    return find_repo_root(candidate) or candidate


def hub_from_args(args: argparse.Namespace) -> Path:
    return repo_root_from_arg(args.repo) / file_hub.HUB_DIR_NAME


def print_json(payload: Any) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path.cwd(), help="Repository root.")
    commands = parser.add_subparsers(dest="command", required=True)

    init = commands.add_parser("init", help="Initialize .hub layout.")
    init.add_argument("--project-name")

    state = commands.add_parser("state", help="State operations.")
    state_sub = state.add_subparsers(dest="state_command", required=True)
    state_sub.add_parser("refresh", help="Refresh .hub/state.yml.")

    change = commands.add_parser("change", help="Change packet operations.")
    change_sub = change.add_subparsers(dest="change_command", required=True)
    create_change = change_sub.add_parser("create")
    create_change.add_argument("--slug", required=True)
    create_change.add_argument("--title", required=True)
    create_change.add_argument("--priority", default="P2", choices=["P0", "P1", "P2", "P3"])
    create_change.add_argument("--owner", default="Unassigned")
    link_issue = change_sub.add_parser("link-issue")
    link_issue.add_argument("--change", required=True)
    link_issue.add_argument("--issue", required=True)
    archive_change = change_sub.add_parser("archive")
    archive_change.add_argument("--change", required=True)

    issue = commands.add_parser("issue", help="Issue operations.")
    issue_sub = issue.add_subparsers(dest="issue_command", required=True)
    create_issue = issue_sub.add_parser("create")
    create_issue.add_argument("--id", dest="issue_id")
    create_issue.add_argument("--title", required=True)
    create_issue.add_argument("--type", default="Feature")
    create_issue.add_argument("--priority", default="P2", choices=["P0", "P1", "P2", "P3"])
    create_issue.add_argument("--change", default="")
    add_dep = issue_sub.add_parser("add-dependency")
    add_dep.add_argument("--issue", required=True)
    add_dep.add_argument("--depends-on", required=True)
    remove_dep = issue_sub.add_parser("remove-dependency")
    remove_dep.add_argument("--issue", required=True)
    remove_dep.add_argument("--depends-on", required=True)
    set_status = issue_sub.add_parser("set-status")
    set_status.add_argument("--issue", required=True)
    set_status.add_argument("--status", required=True, choices=STATUS_ORDER)
    set_status.add_argument("--reason", default="")
    append_activity = issue_sub.add_parser("append-activity")
    append_activity.add_argument("--issue", required=True)
    append_activity.add_argument("--heading", default="Progress")
    append_activity.add_argument("--line", action="append", default=[])
    add_evidence = issue_sub.add_parser("add-evidence")
    add_evidence.add_argument("--issue", required=True)
    add_evidence.add_argument("--heading", default="Evidence")
    add_evidence.add_argument("--line", action="append", default=[])
    set_spec = issue_sub.add_parser("set-spec")
    set_spec.add_argument("--issue", required=True)
    set_spec.add_argument("--spec-file", type=Path, required=True)

    dashboard = commands.add_parser("dashboard", help="Read-only dashboard operations.")
    dashboard_sub = dashboard.add_subparsers(dest="dashboard_command", required=True)
    dashboard_export = dashboard_sub.add_parser("export")
    dashboard_export.add_argument("--change", default="")
    dashboard_export.add_argument("--output", type=Path)

    claim = commands.add_parser("claim", help="Claim operations.")
    claim_sub = claim.add_subparsers(dest="claim_command", required=True)
    acquire = claim_sub.add_parser("acquire")
    acquire.add_argument("--issue", required=True)
    acquire.add_argument("--purpose", default="work", choices=["work", "review"])
    acquire.add_argument("--owner", required=True)
    acquire.add_argument("--claim-id", required=True)
    acquire.add_argument("--ttl-minutes", type=int, default=120)
    acquire.add_argument("--base-branch", default="")
    acquire.add_argument("--branch", default="")
    acquire.add_argument("--worktree-path", default="")
    acquire.add_argument("--allow-missing-artifacts", action="store_true")
    check = claim_sub.add_parser("check")
    check.add_argument("--issue", required=True)
    check.add_argument("--claim-id", default="")
    renew = claim_sub.add_parser("renew")
    renew.add_argument("--issue", required=True)
    renew.add_argument("--claim-id", required=True)
    renew.add_argument("--ttl-minutes", type=int, default=120)
    release = claim_sub.add_parser("release")
    release.add_argument("--issue", required=True)
    release.add_argument("--claim-id", required=True)
    release.add_argument("--mode", required=True)
    release.add_argument("--owner", default="")
    release.add_argument("--blocker", default="")
    release.add_argument("--commit-sha", default="")
    release.add_argument("--pr-url", default="")

    audit = commands.add_parser("audit", help="Audit operations.")
    audit_sub = audit.add_subparsers(dest="audit_command", required=True)
    audit_sub.add_parser("hub")
    audit_issue = audit_sub.add_parser("issue")
    audit_issue.add_argument("issue")

    analyze = commands.add_parser("analyze", help="Analyze operations.")
    analyze_sub = analyze.add_subparsers(dest="analyze_command", required=True)
    analyze_change = analyze_sub.add_parser("change")
    analyze_change.add_argument("change")

    scenario = commands.add_parser("scenario", help="Scenario eval operations.")
    scenario_sub = scenario.add_subparsers(dest="scenario_command", required=True)
    scenario_eval = scenario_sub.add_parser("eval")
    scenario_eval.add_argument("scenario_path", type=Path)

    return parser


def run(args: argparse.Namespace) -> Any:
    root = repo_root_from_arg(args.repo)
    if args.command == "init":
        hub = file_hub.create_hub(root, args.project_name)
        return {"ok": True, "hub": str(hub)}

    hub = hub_from_args(args)

    if args.command == "state" and args.state_command == "refresh":
        return file_hub.refresh_state(hub)

    if args.command == "change":
        if args.change_command == "create":
            path = file_hub.create_change_packet(
                hub, args.slug, args.title, priority=args.priority, owner=args.owner
            )
            return {"ok": True, "change": args.slug, "path": str(path)}
        if args.change_command == "link-issue":
            return file_hub.link_issue_to_change(hub, args.change, args.issue)
        if args.change_command == "archive":
            data = file_hub.load_change(hub, args.change)
            data["status"] = "Archived"
            data["updated_at"] = file_hub.isoformat(file_hub.now_utc())
            file_hub.write_change(hub, args.change, data)
            return {"ok": True, "change": args.change, "status": "Archived"}

    if args.command == "issue":
        if args.issue_command == "create":
            created = file_hub.create_issue_file(
                hub,
                args.title,
                args.issue_id,
                issue_type=args.type,
                priority=args.priority,
                change=args.change,
            )
            if args.change:
                file_hub.link_issue_to_change(hub, args.change, created.id)
            return {"ok": True, "issue": created.id, "path": str(created.path)}
        if args.issue_command == "add-dependency":
            return file_hub.add_issue_dependency(hub, args.issue, args.depends_on)
        if args.issue_command == "remove-dependency":
            return file_hub.remove_issue_dependency(hub, args.issue, args.depends_on)
        if args.issue_command == "set-status":
            return file_hub.set_issue_status(hub, args.issue, args.status, args.reason)
        if args.issue_command == "append-activity":
            return file_hub.append_issue_activity(hub, args.issue, args.heading, args.line)
        if args.issue_command == "add-evidence":
            return file_hub.add_issue_evidence(hub, args.issue, args.heading, args.line)
        if args.issue_command == "set-spec":
            return file_hub.set_issue_spec(hub, args.issue, args.spec_file)

    if args.command == "dashboard" and args.dashboard_command == "export":
        snapshot = file_hub.dashboard_snapshot(hub, change=args.change)
        if args.output:
            output_path = args.output.expanduser()
            file_hub.atomic_write(
                output_path,
                json.dumps(snapshot, indent=2, sort_keys=True) + "\n",
            )
            return {"ok": True, "output": str(output_path), "summary": snapshot["summary"]}
        return snapshot

    if args.command == "claim":
        issue = file_hub.issue_by_id(hub, args.issue)
        if args.claim_command == "acquire":
            return file_hub.claim_issue(
                hub,
                issue,
                args.purpose,
                args.owner,
                args.ttl_minutes,
                args.claim_id,
                base_branch=args.base_branch,
                branch=args.branch,
                worktree_path=args.worktree_path,
                allow_missing_artifacts=args.allow_missing_artifacts,
            )
        if args.claim_command == "check":
            return file_hub.check_issue(hub, issue, args.claim_id)
        if args.claim_command == "renew":
            return file_hub.renew_issue(hub, issue, args.claim_id, args.ttl_minutes)
        if args.claim_command == "release":
            return file_hub.release_issue(
                hub,
                issue,
                args.claim_id,
                args.mode,
                owner=args.owner,
                blocker=args.blocker,
                commit_sha=args.commit_sha,
                pr_url=args.pr_url,
            )

    if args.command == "audit":
        if args.audit_command == "hub":
            return file_hub.audit_hub(hub)
        if args.audit_command == "issue":
            return file_hub.audit_issue(hub, args.issue)

    if args.command == "analyze" and args.analyze_command == "change":
        return file_hub.analyze_change(hub, args.change)

    if args.command == "scenario" and args.scenario_command == "eval":
        eval_root = Path(__file__).resolve().parents[3] / "evals"
        sys.path.insert(0, str(eval_root))
        from scenario_adapter import evaluate_scenario  # type: ignore  # noqa: PLC0415

        scenario = json.loads(args.scenario_path.read_text(encoding="utf-8"))
        fixture = scenario.get("fixture", "")
        fixture_dir = eval_root / "fixtures" / str(fixture)
        return evaluate_scenario(
            scenario=scenario,
            scenario_path=args.scenario_path,
            fixture_dir=fixture_dir,
            repo_root=eval_root.parent,
            eval_root=eval_root,
        )

    raise RuntimeError("Unsupported command.")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        print_json(run(args))
        return 0
    except Exception as exc:  # noqa: BLE001 - CLI should render deterministic failures.
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
