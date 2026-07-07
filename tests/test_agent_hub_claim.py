from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COMMON_LIB = ROOT / "skills/manage-agent-hub-issues/lib"
CLAIM_PATH = ROOT / "skills/claim-agent-hub-issue/scripts/agent_hub_claim.py"
sys.path.insert(0, str(COMMON_LIB))

import file_hub_common as file_hub  # noqa: E402


def load_module():
    spec = importlib.util.spec_from_file_location("agent_hub_claim", CLAIM_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules["agent_hub_claim"] = module
    spec.loader.exec_module(module)
    return module


claim_mod = load_module()


class AgentHubClaimTests(unittest.TestCase):
    def make_repo(self):
        temp = tempfile.TemporaryDirectory()
        root = Path(temp.name)
        (root / ".git").mkdir()
        hub = file_hub.create_hub(root, "Claim Project")
        self.addCleanup(temp.cleanup)
        return hub

    def run_claim(self, *args: str):
        stdout = StringIO()
        with redirect_stdout(stdout):
            rc = claim_mod.main(list(args))
        return rc, json.loads(stdout.getvalue())

    def test_successful_work_claim(self):
        hub = self.make_repo()
        file_hub.create_issue_file(hub, "Issue", "issue")

        rc, result = self.run_claim(
            "--hub-root",
            str(hub),
            "claim",
            "--page-id",
            "issue",
            "--purpose",
            "work",
            "--owner",
            "Codex",
            "--claim-id",
            "work-test",
        )

        self.assertEqual(rc, 0)
        self.assertEqual(result["status"], "In Progress")
        self.assertEqual(result["claim_id"], "work-test")

    def test_dependency_refusal(self):
        hub = self.make_repo()
        dep = file_hub.create_issue_file(hub, "Dependency", "dep")
        dep.status = "In Progress"
        dep.write()
        issue = file_hub.create_issue_file(hub, "Issue", "issue")
        issue.depends_on = ["dep"]
        issue.write()

        with self.assertRaises(SystemExit):
            self.run_claim(
                "--hub-root",
                str(hub),
                "claim",
                "--page-id",
                "issue",
                "--purpose",
                "work",
                "--owner",
                "Codex",
            )

    def test_release_work_handoff_and_submitted(self):
        hub = self.make_repo()
        file_hub.create_issue_file(hub, "Issue", "issue")
        self.run_claim(
            "--hub-root",
            str(hub),
            "claim",
            "--page-id",
            "issue",
            "--purpose",
            "work",
            "--owner",
            "Codex",
            "--claim-id",
            "work-test",
        )

        _, handoff = self.run_claim(
            "--hub-root",
            str(hub),
            "release",
            "--page-id",
            "issue",
            "--claim-id",
            "work-test",
            "--mode",
            "handoff",
        )
        self.assertEqual(handoff["status"], "In Progress")
        self.assertEqual(handoff["claim_id"], "")

        issue = file_hub.issue_by_id(hub, "issue")
        issue.claim = {"id": "work-test", "owner": "Codex", "purpose": "work"}
        issue.status = "In Progress"
        issue.write()
        _, submitted = self.run_claim(
            "--hub-root",
            str(hub),
            "release",
            "--page-id",
            "issue",
            "--claim-id",
            "work-test",
            "--mode",
            "submitted",
            "--pr-url",
            "https://github.com/o/r/pull/2",
            "--commit-sha",
            "abc123",
        )
        self.assertEqual(submitted["status"], "In Review")

    def test_release_review_modes(self):
        hub = self.make_repo()
        issue = file_hub.create_issue_file(hub, "Issue", "issue")
        issue.status = "In Review"
        issue.claim = {"id": "review-test", "owner": "Reviewer", "purpose": "review"}
        issue.write()

        _, passed = self.run_claim(
            "--hub-root",
            str(hub),
            "release",
            "--page-id",
            "issue",
            "--claim-id",
            "review-test",
            "--mode",
            "review-pass",
        )
        self.assertEqual(passed["status"], "Completed")


if __name__ == "__main__":
    unittest.main()
