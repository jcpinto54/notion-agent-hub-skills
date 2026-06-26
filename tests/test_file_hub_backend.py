from __future__ import annotations

import importlib.util
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from datetime import datetime, timedelta, timezone
from io import StringIO
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COMMON_LIB = ROOT / "skills/manage-agent-hub-issues/lib"
sys.path.insert(0, str(COMMON_LIB))

import file_hub_common as file_hub  # noqa: E402

LIST_PATH = ROOT / "skills/list-agent-hub-issues/scripts/agent_hub_list.py"
CLAIM_PATH = ROOT / "skills/claim-agent-hub-issue/scripts/agent_hub_claim.py"
INIT_PATH = ROOT / "skills/init-agent-hub/scripts/init_file_hub.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


list_mod = load_module("agent_hub_list_file_tests", LIST_PATH)
claim_mod = load_module("agent_hub_claim_file_tests", CLAIM_PATH)
init_mod = load_module("init_file_hub_tests", INIT_PATH)


class FileHubBackendTests(unittest.TestCase):
    def make_repo(self):
        temp = tempfile.TemporaryDirectory()
        root = Path(temp.name)
        (root / ".git").mkdir()
        hub = file_hub.create_hub(root, "Test Project")
        return temp, root, hub

    def test_parse_and_write_issue_frontmatter(self):
        temp, _, hub = self.make_repo()
        self.addCleanup(temp.cleanup)

        issue = file_hub.create_issue_file(hub, "Add file backend", "hub-file-backend")
        loaded = file_hub.issue_by_id(hub, "hub-file-backend")

        self.assertEqual(loaded.id, "hub-file-backend")
        self.assertEqual(loaded.title, "Add file backend")
        self.assertEqual(loaded.status, "Not Started")
        self.assertIn("## Activity Log", loaded.body)

        loaded.status = "In Progress"
        loaded.depends_on = ["dependency"]
        loaded.write()
        reloaded = file_hub.issue_by_id(hub, "hub-file-backend")
        self.assertEqual(reloaded.status, "In Progress")
        self.assertEqual(reloaded.depends_on, ["dependency"])

    def test_readiness_from_dependencies_blockers_and_claims(self):
        temp, _, hub = self.make_repo()
        self.addCleanup(temp.cleanup)

        dep = file_hub.create_issue_file(hub, "Dependency", "dep")
        dep.status = "Completed"
        dep.write()
        ready = file_hub.create_issue_file(hub, "Ready", "ready")
        ready.depends_on = ["dep"]
        ready.write()
        blocked = file_hub.create_issue_file(hub, "Blocked", "blocked")
        blocked.blockers = "Waiting for credentials"
        blocked.write()
        claimed = file_hub.create_issue_file(hub, "Claimed", "claimed")
        claimed.claim = {
            "id": "work-other",
            "expires_at": (datetime.now(timezone.utc) + timedelta(minutes=10))
            .isoformat()
            .replace("+00:00", "Z"),
        }
        claimed.write()

        issues = file_hub.load_issues(hub)
        by_id = {issue.id: issue for issue in issues}

        self.assertEqual(file_hub.readiness(by_id["ready"], by_id), ("Ready", ""))
        self.assertEqual(file_hub.readiness(by_id["blocked"], by_id)[0], "Blocked")
        self.assertEqual(file_hub.readiness(by_id["claimed"], by_id)[0], "Blocked")

    def test_claim_refusal_success_release_and_runtime_locking(self):
        temp, _, hub = self.make_repo()
        self.addCleanup(temp.cleanup)

        dep = file_hub.create_issue_file(hub, "Dependency", "dep")
        dep.status = "In Progress"
        dep.write()
        waiting = file_hub.create_issue_file(hub, "Waiting", "waiting")
        waiting.depends_on = ["dep"]
        waiting.write()

        with self.assertRaises(RuntimeError):
            file_hub.claim_issue(hub, waiting, "work", "Codex", 120, "work-waiting")

        dep.status = "Completed"
        dep.write()
        waiting = file_hub.issue_by_id(hub, "waiting")
        result = file_hub.claim_issue(
            hub,
            waiting,
            "work",
            "Codex",
            120,
            "work-waiting",
            base_branch="main",
            branch="codex/waiting",
            worktree_path="/tmp/waiting",
        )
        self.assertEqual(result["status"], "In Progress")
        runtime = json.loads((hub / "runtime/claims.json").read_text(encoding="utf-8"))
        self.assertEqual(runtime["waiting"]["id"], "work-waiting")

        with self.assertRaises(RuntimeError):
            file_hub.claim_issue(
                hub,
                file_hub.issue_by_id(hub, "waiting"),
                "work",
                "Other",
                120,
                "work-other",
            )

        released = file_hub.release_issue(
            hub,
            file_hub.issue_by_id(hub, "waiting"),
            "work-waiting",
            "submitted",
            pr_url="https://github.com/o/r/pull/1",
            commit_sha="abc123",
        )
        self.assertEqual(released["status"], "In Review")
        self.assertEqual(file_hub.load_runtime_claims(hub), {})

    def test_append_activity_is_append_only(self):
        temp, _, hub = self.make_repo()
        self.addCleanup(temp.cleanup)

        issue = file_hub.create_issue_file(hub, "Evidence", "evidence")
        issue.append_activity("Progress", ["Date: 2026-06-26T00:00:00Z", "Summary: first"])
        issue.append_activity("Review", ["Date: 2026-06-26T01:00:00Z", "Summary: second"])
        text = issue.path.read_text(encoding="utf-8")

        self.assertLess(text.index("### Progress"), text.index("### Review"))
        self.assertIn("Summary: first", text)
        self.assertIn("Summary: second", text)

    def test_list_and_claim_scripts_auto_detect_file_backend(self):
        temp, root, hub = self.make_repo()
        self.addCleanup(temp.cleanup)

        file_hub.create_issue_file(hub, "Ready from script", "ready-script")
        cwd = Path.cwd()
        try:
            os.chdir(root)
            with redirect_stdout(StringIO()):
                list_rc = list_mod.main(["--format", "json", "--readiness", "Ready"])
            self.assertEqual(list_rc, 0)
            with redirect_stdout(StringIO()):
                claim_rc = claim_mod.main(
                    [
                        "claim",
                        "--page-id",
                        "ready-script",
                        "--purpose",
                        "work",
                        "--owner",
                        "Codex",
                        "--claim-id",
                        "work-script",
                    ]
                )
            self.assertEqual(claim_rc, 0)
        finally:
            os.chdir(cwd)

    def test_init_script_creates_repo_native_layout(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        (root / ".git").mkdir()

        with redirect_stdout(StringIO()):
            rc = init_mod.main(["--repo", str(root), "--project-name", "Script Project"])

        self.assertEqual(rc, 0)
        self.assertTrue((root / ".hub/config.yml").exists())
        self.assertTrue((root / ".hub/issues").is_dir())
        self.assertTrue((root / ".hub/decisions").is_dir())
        self.assertTrue((root / ".hub/artifacts").is_dir())
        self.assertEqual((root / ".hub/.gitignore").read_text(encoding="utf-8"), "runtime/\n")


if __name__ == "__main__":
    unittest.main()
