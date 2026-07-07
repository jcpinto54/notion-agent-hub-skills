---
id: "hub-viewer-card-tag-overflow"
title: "Prevent long board tags from overflowing cards"
status: "In Progress"
type: "Bug"
priority: "P1"
owner: "Codex"
area: ""
summary: ""
blockers: ""
dependency_notes: ""
change: "hub-viewer-board-polish"
depends_on: []
blocks: []
claim:
  id: "work-dca4d4ef-2e16-4754-8c29-d4b728c41f1c"
  purpose: "work"
  owner: "Codex"
  claimed_at: "2026-07-03T16:49:37.578164Z"
  expires_at: "2026-07-03T18:49:37.578164Z"
  machine: "Joaos-MacBook-Pro.local"
base_branch: "codex/agent-hub-v3-repo-native"
branch: "codex/hub-viewer-card-tag-overflow"
worktree_path: "/Users/jcpinto/git/notion-agent-hub-skills/.worktrees/hub-viewer-card-tag-overflow"
commit_sha: ""
pr_url: ""
related_links: ""
notion_url: ""
external_url: ""
---
## Context

The Agent Hub viewer Kanban board can overflow horizontally when a card contains a long tag, diagnostic code, or change identifier. The screenshot shows a long red diagnostic chip extending out of an `In Review` card and overlapping the adjacent `Completed` column.

Cards must contain their own content. Long tokens should wrap, truncate, or otherwise remain inside the card boundary without pushing into neighboring columns.

## Scope

- Update the existing board card styles and markup in `skills/list-agent-hub-issues/viewer/`.
- Ensure long issue IDs, change IDs, dependency text, readiness reasons, diagnostic chips, and other tag-like fields stay within the card.
- Prefer CSS constraints such as `min-width: 0`, `max-width: 100%`, `overflow-wrap`, `word-break` where appropriate, and stable chip/card sizing.
- Preserve useful readability for normal-length tags and diagnostics.
- Add regression coverage for at least one deliberately long tag/diagnostic value.
- Verify desktop and mobile board rendering against the overflow case shown in the screenshot.

## Out Of Scope

- Do not remove diagnostic chips or hide important issue metadata entirely.
- Do not widen columns globally as the only fix.
- Do not add a build system, external dependencies, or framework migration.
- Do not alter issue/change data semantics to shorten values at the source.

## Done Criteria

- [ ] Long diagnostic/readiness/change chips stay inside their card and do not overlap neighboring columns.
- [ ] Long issue IDs and title-like metadata stay inside the card or are clipped/wrapped with an accessible title/label if truncation is used.
- [ ] The fix works in all board columns, including `In Review` next to `Completed`.
- [ ] The board does not gain page-level horizontal overflow from long card content on mobile.
- [ ] A regression fixture or sample dashboard state includes a long tag/diagnostic token representative of the screenshot.
- [ ] Browser smoke captures desktop and mobile evidence showing no card-to-column overlap.

## Verification Strategy

### Regression Target

A long tag or diagnostic token rendered inside a Kanban card must not escape the card boundary or overlap the next column.

### Test Plan

- [ ] Unit/static: add or update `tests/test_hub_viewer_static.py` to require the CSS/fixture contract for wrapping long board chips.
- [ ] Integration: use a dashboard fixture or sample state containing a long diagnostic such as `review_ready_missing_regression_evidence`.
- [ ] E2E / Playwright: render the board, locate the long chip/card, and assert its bounding box remains within the card and column bounds.
- [ ] Manual / inspection: compare the screenshot scenario on desktop and mobile to confirm the overlap is gone.

### First Test

Path: `tests/test_hub_viewer_static.py`
Expected initial result: a new focused assertion fails because the current viewer does not yet lock long chip/card overflow behavior.
Reason this proves the regression or requirement: it reproduces the class of layout failure from the screenshot with a stable fixture or CSS contract.

### Final Verification

Commands: `python3 -m unittest tests.test_hub_viewer_static`; plus browser smoke against a dashboard state containing a long diagnostic/tag token.
Expected result: focused tests pass, browser console is clean, and visual/bounding-box checks show the long tag remains inside its card.

### Untestable Surface

Exact truncation versus wrapping aesthetics should be checked by screenshot review because several acceptable visual treatments can satisfy the containment requirement.

## Assumptions

- The long overflowing label in the screenshot is rendered as a card chip or chip-like metadata element in the static viewer.
- The fix can be done in the viewer layer without changing dashboard export data.

## Dependencies

None.

## Open Questions

- Should diagnostic chips wrap to multiple lines, truncate with tooltip/title, or use a compact code display for very long values?

## Activity Log

### Claimed for work
Date: 2026-07-03T16:49:37.578164Z
Agent: Codex
Claim ID: work-dca4d4ef-2e16-4754-8c29-d4b728c41f1c
Branch: codex/hub-viewer-card-tag-overflow
Worktree Path: /Users/jcpinto/git/notion-agent-hub-skills/.worktrees/hub-viewer-card-tag-overflow
