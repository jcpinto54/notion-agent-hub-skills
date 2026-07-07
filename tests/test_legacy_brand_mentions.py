from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN = "no" + "tion"
SKIP_DIRS = {
    ".agents",
    ".claude",
    ".codex",
    ".cursor",
    ".git",
    ".github",
    ".hub",
    ".mypy_cache",
    ".pytest_cache",
    ".tessl",
    ".tessl-plugin",
    ".venv",
    "__pycache__",
}
SKIP_NAMES = {"tessl.json"}


class LegacyBrandMentionTests(unittest.TestCase):
    def test_repository_text_has_no_removed_brand_mentions(self) -> None:
        hits: list[str] = []
        for path in ROOT.rglob("*"):
            relative = path.relative_to(ROOT)
            if relative.parts[:2] == ("evals", "reports"):
                continue
            if any(part in SKIP_DIRS for part in path.parts) or path.name in SKIP_NAMES:
                continue
            if not path.is_file():
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            if FORBIDDEN in text.lower():
                hits.append(str(relative))
        self.assertEqual(hits, [])
