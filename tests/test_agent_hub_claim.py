from __future__ import annotations

import importlib.util
import sys
import unittest
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace


ROOT = Path(__file__).resolve().parents[1]
CLAIM_PATH = ROOT / "skills/claim-agent-hub-issue/scripts/agent_hub_claim.py"


def load_module():
    spec = importlib.util.spec_from_file_location("agent_hub_claim", CLAIM_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules["agent_hub_claim"] = module
    spec.loader.exec_module(module)
    return module


claim_mod = load_module()


def rich_text(value: str):
    return {"type": "rich_text", "rich_text": [{"plain_text": value}] if value else []}


def select(value: str):
    return {"type": "select", "select": {"name": value} if value else None}


def url(value: str):
    return {"type": "url", "url": value or None}


def date_prop(value: datetime | None):
    return {
        "type": "date",
        "date": {"start": value.isoformat().replace("+00:00", "Z")} if value else None,
    }


def relation(*ids: str):
    return {"type": "relation", "relation": [{"id": item} for item in ids]}


def page(
    page_id: str = "issue",
    status: str = "Not Started",
    owner: str = "Unassigned",
    blockers: str = "",
    depends_on: tuple[str, ...] = (),
    claim_id: str = "",
    claim_expires_at: datetime | None = None,
    pr_url: str = "",
    commit_sha: str = "",
):
    return {
        "id": page_id,
        "properties": {
            "Title": {"type": "title", "title": [{"plain_text": page_id}]},
            "Status": select(status),
            "Owner": rich_text(owner),
            "Blockers": rich_text(blockers),
            "Dependency Notes": rich_text(""),
            "Depends On": relation(*depends_on),
            "Claim ID": rich_text(claim_id),
            "Claimed At": date_prop(None),
            "Claim Expires At": date_prop(claim_expires_at),
            "Base Branch": rich_text(""),
            "Branch": rich_text(""),
            "Worktree Path": rich_text(""),
            "Commit SHA": rich_text(commit_sha),
            "PR URL": url(pr_url),
            "Related Links": rich_text(""),
        },
    }


class FakeClient:
    def __init__(self, pages, mismatch_claim: str | None = None):
        self.pages = {item["id"]: deepcopy(item) for item in pages}
        self.mismatch_claim = mismatch_claim

    def get_page(self, page_id: str):
        return deepcopy(self.pages[page_id])

    def query_data_source(self, data_source_id: str):
        return [deepcopy(item) for item in self.pages.values()]

    def update_page(self, page_id: str, properties):
        target = self.pages[page_id]["properties"]
        for name, value in properties.items():
            current_type = target[name]["type"]
            if current_type == "select":
                target[name] = {"type": "select", "select": value.get("select")}
            elif current_type == "status":
                target[name] = {"type": "status", "status": value.get("status")}
            elif current_type == "rich_text":
                parts = []
                for part in value.get("rich_text", []):
                    text = part.get("plain_text") or (part.get("text") or {}).get("content", "")
                    parts.append({"plain_text": text})
                target[name] = {"type": "rich_text", "rich_text": parts}
            elif current_type == "date":
                target[name] = {"type": "date", "date": value.get("date")}
            elif current_type == "url":
                target[name] = {"type": "url", "url": value.get("url")}
        if self.mismatch_claim:
            target["Claim ID"] = rich_text(self.mismatch_claim)
            self.mismatch_claim = None
        return deepcopy(self.pages[page_id])


def claim_args(**overrides):
    values = {
        "page_id": "issue",
        "data_source_id": "source",
        "purpose": "work",
        "owner": "Codex",
        "ttl_minutes": 120,
        "claim_id": "work-test",
        "base_branch": None,
        "branch": None,
        "worktree_path": None,
        "allow_missing_artifacts": False,
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def release_args(**overrides):
    values = {
        "page_id": "issue",
        "claim_id": "work-test",
        "mode": "handoff",
        "owner": None,
        "blocker": None,
        "commit_sha": None,
        "pr_url": None,
    }
    values.update(overrides)
    return SimpleNamespace(**values)


class AgentHubClaimTests(unittest.TestCase):
    def test_successful_work_claim(self):
        client = FakeClient([page()])
        result = claim_mod.command_claim(client, claim_args())
        self.assertTrue(result["ok"])
        self.assertEqual(result["status"], "In Progress")
        self.assertEqual(result["claim_id"], "work-test")

    def test_dependency_refusal(self):
        client = FakeClient([page(depends_on=("dep",)), page("dep", status="In Progress")])
        with self.assertRaises(SystemExit):
            claim_mod.command_claim(client, claim_args())

    def test_active_claim_refusal(self):
        future = datetime.now(timezone.utc) + timedelta(minutes=30)
        client = FakeClient([page(claim_id="work-other", claim_expires_at=future)])
        with self.assertRaises(SystemExit):
            claim_mod.command_claim(client, claim_args())

    def test_expired_claim_reclaim(self):
        past = datetime.now(timezone.utc) - timedelta(minutes=30)
        client = FakeClient([page(claim_id="work-old", claim_expires_at=past)])
        result = claim_mod.command_claim(client, claim_args())
        self.assertEqual(result["claim_id"], "work-test")

    def test_successful_review_claim(self):
        client = FakeClient([page(status="In Review", pr_url="https://github.com/o/r/pull/1")])
        result = claim_mod.command_claim(
            client, claim_args(purpose="review", claim_id="review-test", owner="Reviewer")
        )
        self.assertEqual(result["status"], "In Review")
        self.assertEqual(result["claim_id"], "review-test")

    def test_review_claim_refused_when_not_in_review(self):
        client = FakeClient([page(status="In Progress", pr_url="https://github.com/o/r/pull/1")])
        with self.assertRaises(SystemExit):
            claim_mod.command_claim(client, claim_args(purpose="review", claim_id="review-test"))

    def test_release_work_handoff_and_submitted(self):
        client = FakeClient([page(status="In Progress", claim_id="work-test")])
        handoff = claim_mod.command_release(client, release_args(mode="handoff"))
        self.assertEqual(handoff["status"], "In Progress")
        self.assertEqual(handoff["claim_id"], "")

        client = FakeClient([page(status="In Progress", claim_id="work-test")])
        submitted = claim_mod.command_release(
            client,
            release_args(
                mode="submitted",
                pr_url="https://github.com/o/r/pull/2",
                commit_sha="abc123",
            ),
        )
        self.assertEqual(submitted["status"], "In Review")

    def test_release_review_modes(self):
        client = FakeClient([page(status="In Review", claim_id="review-test")])
        passed = claim_mod.command_release(
            client, release_args(claim_id="review-test", mode="review-pass")
        )
        self.assertEqual(passed["status"], "Completed")

        client = FakeClient([page(status="In Review", claim_id="review-test")])
        failed = claim_mod.command_release(
            client, release_args(claim_id="review-test", mode="review-fail")
        )
        self.assertEqual(failed["status"], "In Progress")

        client = FakeClient([page(status="In Review", claim_id="review-test")])
        abandoned = claim_mod.command_release(
            client, release_args(claim_id="review-test", mode="review-abandon")
        )
        self.assertEqual(abandoned["status"], "In Review")

    def test_immediate_refetch_mismatch_failure(self):
        client = FakeClient([page()], mismatch_claim="stolen")
        with self.assertRaises(SystemExit):
            claim_mod.command_claim(client, claim_args())


if __name__ == "__main__":
    unittest.main()
