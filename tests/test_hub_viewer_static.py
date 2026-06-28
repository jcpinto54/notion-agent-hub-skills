from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VIEWER_DIR = ROOT / "skills/list-agent-hub-issues/viewer"


class HubViewerStaticTests(unittest.TestCase):
    def test_static_viewer_files_exist_and_stay_dependency_free(self):
        expected = {
            "index.html",
            "styles.css",
            "app.js",
            "hub-state.sample.json",
        }
        missing = [name for name in sorted(expected) if not (VIEWER_DIR / name).exists()]
        self.assertEqual(missing, [])

        html = (VIEWER_DIR / "index.html").read_text(encoding="utf-8")
        script = (VIEWER_DIR / "app.js").read_text(encoding="utf-8")
        for external_marker in ["https://", "http://", "npm", "unpkg", "cdn."]:
            self.assertNotIn(external_marker, html)
            self.assertNotIn(external_marker, script)

    def test_sample_state_matches_dashboard_contract(self):
        payload = json.loads((VIEWER_DIR / "hub-state.sample.json").read_text(encoding="utf-8"))

        self.assertEqual(payload["version"], "3")
        self.assertEqual(payload["mode"], "read-only")
        self.assertEqual(
            [column["id"] for column in payload["columns"]],
            ["needs-spec", "ready", "in-progress", "in-review", "completed", "blocked"],
        )
        cards = [card for column in payload["columns"] for card in column["issues"]]
        self.assertTrue(cards)
        required_card_keys = {
            "id",
            "title",
            "status",
            "priority",
            "owner",
            "change",
            "depends_on",
            "blocks",
            "readiness",
            "diagnostics",
            "done_criteria",
            "verification",
        }
        for card in cards:
            self.assertEqual(sorted(required_card_keys.difference(card)), [])
            self.assertIn("state", card["readiness"])
            self.assertIn("first_test", card["verification"])
            self.assertIn("final_verification", card["verification"])


if __name__ == "__main__":
    unittest.main()
