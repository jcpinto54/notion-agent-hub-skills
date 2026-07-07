#!/usr/bin/env python3
"""Shared helpers for Agent Hub scripts."""

from __future__ import annotations

from pathlib import Path


STATUS_ORDER = ["Not Started", "In Progress", "In Review", "Completed"]
PRIORITY_ORDER = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
UNASSIGNED = {"", "unassigned", "none", "n/a"}


def find_repo_root(start: Path | None = None) -> Path | None:
    current = (start or Path.cwd()).resolve()
    for candidate in [current, *current.parents]:
        if (candidate / ".git").exists():
            return candidate
    return None


def is_unassigned(owner: str) -> bool:
    return owner.strip().lower() in UNASSIGNED
