from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace


ROOT = Path(__file__).resolve().parents[1]
COMMON_LIB = ROOT / "skills/manage-agent-hub-issues/lib"
LIST_PATH = ROOT / "skills/list-agent-hub-issues/scripts/agent_hub_list.py"
sys.path.insert(0, str(COMMON_LIB))

import file_hub_common as file_hub  # noqa: E402


def load_module():
    spec = importlib.util.spec_from_file_location("agent_hub_list", LIST_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules["agent_hub_list"] = module
    spec.loader.exec_module(module)
    return module


list_mod = load_module()


class AgentHubListTests(unittest.TestCase):
    def make_repo(self):
        temp = tempfile.TemporaryDirectory()
        root = Path(temp.name)
        (root / ".git").mkdir()
        hub = file_hub.create_hub(root, "List Project")
        self.addCleanup(temp.cleanup)
        return hub

    def file_args(self, hub: Path, **overrides):
        defaults = {
            "hub_root": hub,
            "change": None,
            "status": None,
            "owner": None,
            "priority": None,
            "type": None,
            "area": None,
            "readiness": None,
        }
        defaults.update(overrides)
        return SimpleNamespace(**defaults)

    def issue(self, hub: Path, issue_id: str, title: str, **overrides):
        issue = file_hub.create_issue_file(hub, title, issue_id)
        for key, value in overrides.items():
            setattr(issue, key, value)
        issue.write()
        return file_hub.issue_by_id(hub, issue_id)

    def test_grouping_priority_sorting_and_markdown_counts(self):
        hub = self.make_repo()
        self.issue(hub, "p2-old", "P2 old", priority="P2")
        self.issue(hub, "p0-newer", "P0 newer", priority="P0")
        self.issue(hub, "review", "Review", status="In Review")

        rows, by_id = list_mod.load_file_rows(self.file_args(hub))
        output = list_mod.markdown(rows, by_id, 30)

        self.assertIn("Not Started `2`", output)
        self.assertIn("In Review `1`", output)
        self.assertLess(output.index("P0 newer"), output.index("P2 old"))

    def test_readiness_uses_dependency_status_without_n_plus_one(self):
        hub = self.make_repo()
        dep = self.issue(hub, "dep", "Dependency", status="Completed")
        ready = self.issue(hub, "ready", "Ready issue", depends_on=[dep.id])
        blocked_dep = self.issue(hub, "blocked-dep", "Blocked dependency", status="In Progress")
        blocked = self.issue(hub, "blocked", "Blocked issue", depends_on=[blocked_dep.id])
        issues = [dep, ready, blocked_dep, blocked]
        by_id = {issue.id: issue for issue in issues}

        self.assertEqual(file_hub.readiness(by_id["ready"], by_id), ("Ready", ""))
        label, reason = file_hub.readiness(by_id["blocked"], by_id)
        self.assertEqual(label, "Blocked")
        self.assertIn("Blocked dependency", reason)

    def test_filters_and_expired_claim_readiness(self):
        hub = self.make_repo()
        now = datetime.now(timezone.utc)
        self.issue(
            hub,
            "expired",
            "Expired claim",
            claim={
                "id": "work-old",
                "owner": "Codex",
                "purpose": "work",
                "expires_at": (now - timedelta(minutes=1)).isoformat(),
            },
        )
        self.issue(
            hub,
            "active",
            "Active claim",
            claim={
                "id": "work-new",
                "owner": "Codex",
                "purpose": "work",
                "expires_at": (now + timedelta(minutes=30)).isoformat(),
            },
        )

        rows, by_id = list_mod.load_file_rows(self.file_args(hub, readiness="Ready"))
        self.assertEqual([issue.title for issue, _, _ in rows], ["Expired claim"])
        json_output = list_mod.json_rows(rows, by_id)
        self.assertIn("work-old", json_output)

    def test_json_output_honors_limit_without_recomputing_readiness(self):
        hub = self.make_repo()
        self.issue(hub, "ready-1", "Ready 1", priority="P0")
        self.issue(hub, "ready-2", "Ready 2", priority="P1")
        self.issue(hub, "ready-3", "Ready 3", status="In Review", priority="P2")

        rows, by_id = list_mod.load_file_rows(self.file_args(hub, readiness="Ready"))
        json_output = list_mod.json_rows(rows, by_id, limit=2)

        self.assertIn("Ready 1", json_output)
        self.assertIn("Ready 2", json_output)
        self.assertNotIn("Ready 3", json_output)

    def test_file_backend_change_filter_and_json_change_field(self):
        hub = self.make_repo()
        file_hub.create_change_packet(hub, "first-change", "First Change")
        file_hub.create_change_packet(hub, "second-change", "Second Change")
        first = file_hub.create_issue_file(hub, "First issue", "first-issue")
        second = file_hub.create_issue_file(hub, "Second issue", "second-issue")
        file_hub.link_issue_to_change(hub, "first-change", first.id)
        file_hub.link_issue_to_change(hub, "second-change", second.id)

        rows, by_id = list_mod.load_file_rows(
            self.file_args(hub, change="first-change", readiness="Ready")
        )

        self.assertEqual([issue.id for issue, _, _ in rows], ["first-issue"])
        payload = json.loads(list_mod.json_rows(rows, by_id))
        self.assertEqual(payload[0]["change"], "first-change")

    def test_file_backend_missing_change_filter_fails_clearly(self):
        hub = self.make_repo()

        with self.assertRaises(SystemExit) as raised:
            list_mod.load_file_rows(self.file_args(hub, change="missing-change"))

        self.assertIn("No change packet found", str(raised.exception))


if __name__ == "__main__":
    unittest.main()
