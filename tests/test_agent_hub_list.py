from __future__ import annotations

import importlib.util
import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace


ROOT = Path(__file__).resolve().parents[1]
LIST_PATH = ROOT / "skills/list-agent-hub-issues/scripts/agent_hub_list.py"


def load_module():
    spec = importlib.util.spec_from_file_location("agent_hub_list", LIST_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules["agent_hub_list"] = module
    spec.loader.exec_module(module)
    return module


list_mod = load_module()


def rich_text(value: str):
    return {"type": "rich_text", "rich_text": [{"plain_text": value}] if value else []}


def select(value: str):
    return {"type": "select", "select": {"name": value} if value else None}


def date_prop(value: datetime | None):
    return {
        "type": "date",
        "date": {"start": value.isoformat().replace("+00:00", "Z")} if value else None,
    }


def relation(*ids: str):
    return {"type": "relation", "relation": [{"id": item} for item in ids]}


def page(
    page_id: str,
    title: str,
    status: str,
    priority: str = "P2",
    owner: str = "Unassigned",
    blockers: str = "",
    depends_on: tuple[str, ...] = (),
    updated_at: str = "2026-06-01T00:00:00Z",
    claim_id: str = "",
    claim_expires_at: datetime | None = None,
):
    return {
        "id": page_id,
        "url": f"https://notion.so/{page_id.replace('-', '')}",
        "last_edited_time": updated_at,
        "properties": {
            "Title": {"type": "title", "title": [{"plain_text": title}]},
            "Status": select(status),
            "Owner": rich_text(owner),
            "Priority": select(priority),
            "Type": select("Feature"),
            "Area": rich_text("Core"),
            "Summary": rich_text("summary"),
            "Blockers": rich_text(blockers),
            "Depends On": relation(*depends_on),
            "Blocks": relation(),
            "Dependency Notes": rich_text(""),
            "Updated At": {"type": "last_edited_time", "last_edited_time": updated_at},
            "Claim ID": rich_text(claim_id),
            "Claim Expires At": date_prop(claim_expires_at),
        },
    }


class AgentHubListTests(unittest.TestCase):
    def test_grouping_priority_sorting_and_markdown_counts(self):
        pages = [
            page("a", "P2 old", "Not Started", "P2", updated_at="2026-06-01T00:00:00Z"),
            page("b", "P0 newer", "Not Started", "P0", updated_at="2026-06-02T00:00:00Z"),
            page("c", "Review", "In Review", "P1", updated_at="2026-06-03T00:00:00Z"),
        ]
        issues = [list_mod.Issue.from_page(item) for item in pages]
        issues.sort(key=list_mod.issue_sort_key)
        self.assertEqual([issue.title for issue in issues], ["P0 newer", "P2 old", "Review"])
        by_id = {issue.id: issue for issue in issues}
        args = SimpleNamespace(
            status=None, owner=None, priority=None, type=None, area=None, readiness=None
        )
        rows = list_mod.apply_filters(issues, by_id, args)
        output = list_mod.markdown(rows, by_id, 30)
        self.assertIn("Not Started `2`", output)
        self.assertIn("In Review `1`", output)
        self.assertLess(output.index("P0 newer"), output.index("P2 old"))

    def test_readiness_uses_dependency_status_without_n_plus_one(self):
        dep = page("dep", "Dependency", "Completed")
        ready = page("ready", "Ready issue", "Not Started", depends_on=("dep",))
        blocked_dep = page("blocked-dep", "Blocked dependency", "In Progress")
        blocked = page("blocked", "Blocked issue", "Not Started", depends_on=("blocked-dep",))
        issues = [list_mod.Issue.from_page(item) for item in [dep, ready, blocked_dep, blocked]]
        by_id = {issue.id: issue for issue in issues}
        self.assertEqual(list_mod.readiness(by_id["ready"], by_id), ("Ready", ""))
        label, reason = list_mod.readiness(by_id["blocked"], by_id)
        self.assertEqual(label, "Blocked")
        self.assertIn("Blocked dependency", reason)

    def test_filters_and_expired_claim_readiness(self):
        now = datetime.now(timezone.utc)
        expired = page(
            "expired",
            "Expired claim",
            "Not Started",
            claim_id="work-old",
            claim_expires_at=now - timedelta(minutes=1),
        )
        active = page(
            "active",
            "Active claim",
            "Not Started",
            claim_id="work-new",
            claim_expires_at=now + timedelta(minutes=30),
        )
        issues = [list_mod.Issue.from_page(item) for item in [expired, active]]
        by_id = {issue.id: issue for issue in issues}
        args = SimpleNamespace(
            status=None, owner=None, priority=None, type=None, area=None, readiness="Ready"
        )
        rows = list_mod.apply_filters(issues, by_id, args)
        self.assertEqual([issue.title for issue, _, _ in rows], ["Expired claim"])
        json_output = list_mod.json_rows(rows, by_id)
        self.assertIn("work-old", json_output)

    def test_json_output_honors_limit_without_recomputing_readiness(self):
        pages = [
            page("ready-1", "Ready 1", "Not Started", "P0", updated_at="2026-06-03T00:00:00Z"),
            page("ready-2", "Ready 2", "Not Started", "P1", updated_at="2026-06-02T00:00:00Z"),
            page("ready-3", "Ready 3", "In Review", "P2", updated_at="2026-06-01T00:00:00Z"),
        ]
        issues = [list_mod.Issue.from_page(item) for item in pages]
        issues.sort(key=list_mod.issue_sort_key)
        by_id = {issue.id: issue for issue in issues}
        args = SimpleNamespace(
            status=None, owner=None, priority=None, type=None, area=None, readiness="Ready"
        )
        rows = list_mod.apply_filters(issues, by_id, args)

        json_output = list_mod.json_rows(rows, by_id, limit=2)

        self.assertIn("Ready 1", json_output)
        self.assertIn("Ready 2", json_output)
        self.assertNotIn("Ready 3", json_output)


if __name__ == "__main__":
    unittest.main()
