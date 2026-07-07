---
id: "hub-viewer-board-detail-footer"
title: "Keep board issue detail footer pinned and minimizable"
status: "In Progress"
type: "Feature"
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
  id: "work-af217faa-fff6-4d6e-b846-c30027da2c7d"
  purpose: "work"
  owner: "Codex"
  claimed_at: "2026-07-03T16:50:42.677888Z"
  expires_at: "2026-07-03T18:50:42.677888Z"
  machine: "Joaos-MacBook-Pro.local"
base_branch: "codex/agent-hub-v3-repo-native"
branch: "codex/hub-viewer-board-detail-footer"
worktree_path: "/Users/jcpinto/.config/superpowers/worktrees/notion-agent-hub-skills/hub-viewer-board-detail-footer"
commit_sha: ""
pr_url: ""
related_links: ""
notion_url: ""
external_url: ""
---
## Context

The Agent Hub viewer Kanban board currently places the selected issue information tray at the end of the webpage. On a tall or horizontally scrollable board this makes issue details feel disconnected from the selected card and forces users to scroll away from the board to read the issue information.

This follow-up improves the existing read-only board experience by keeping the issue detail footer attached to the viewport. The footer should sit over the board at the bottom of the screen, remain available while the board scrolls, and support a minimized state so it does not permanently consume vertical space.

## Scope

- Update the existing dependency-free board viewer UI in `skills/list-agent-hub-issues/viewer/`.
- Render the selected issue detail area as a viewport-pinned footer or bottom tray over the board.
- Add an accessible minimize/restore control for the detail footer.
- Preserve read-only behavior: the footer must not add mutation, claim, or status controls.
- Ensure the pinned footer works with horizontal board scrolling and does not obscure essential controls without a way to minimize it.
- Ensure desktop and mobile layouts remain usable with the footer expanded and minimized.
- Record focused verification evidence with screenshots or browser smoke details.

## Out Of Scope

- Do not redesign the full Kanban board visual system.
- Do not add persistence for the minimized state unless it already follows an existing local UI-state pattern.
- Do not add backend changes, issue mutation, claim controls, authentication, or remote hosting.
- Do not change the dashboard JSON contract unless the existing UI cannot represent the selected issue without it.

## Done Criteria

- [ ] Selecting an issue shows its details in a footer/tray pinned to the bottom of the viewport rather than after the board content.
- [ ] The footer remains visible while the page or board scrolls vertically and while the board scrolls horizontally.
- [ ] A minimize/restore control is available, keyboard accessible, and visually clear.
- [ ] The minimized state leaves the board usable and provides a clear path to restore the selected issue details.
- [ ] The footer does not cover top navigation, filter controls, or selected cards in a way that prevents normal board use.
- [ ] Desktop and mobile browser smoke checks verify expanded and minimized states without incoherent overlap or body overflow.
- [ ] Regression coverage locks the pinned/minimized footer behavior or the DOM/CSS contract that supports it.

## Verification Strategy

### Regression Target

The selected issue detail surface must be viewport-pinned and minimizable, not rendered only after the board content.

### Test Plan

- [ ] Unit/static: add or update a focused test in `tests/test_hub_viewer_static.py` that asserts the viewer exposes a pinned/minimizable detail footer contract.
- [ ] Integration: export or serve dashboard state with enough issues to make board scrolling meaningful.
- [ ] E2E / Playwright: load the viewer, select an issue, verify the footer is fixed/sticky at the viewport bottom, minimize it, restore it, and repeat on mobile.
- [ ] Manual / inspection: inspect desktop and mobile screenshots for overlap, clipping, and readable selected issue details.

### First Test

Path: `tests/test_hub_viewer_static.py`
Expected initial result: a new focused assertion fails because the detail footer is not yet encoded as a viewport-pinned, minimizable UI surface.
Reason this proves the regression or requirement: it prevents the detail surface from quietly returning to an end-of-page tray with no minimize affordance.

### Final Verification

Commands: `python3 -m unittest tests.test_hub_viewer_static`; plus browser smoke against `python3 skills/manage-agent-hub-issues/scripts/agent_hub.py dashboard serve --change hub-viewer-board-polish`
Expected result: focused tests pass, browser console is clean, and desktop/mobile smoke confirms expanded and minimized footer states.

### Untestable Surface

Exact visual polish and whether the footer feels intrusive require screenshot inspection in addition to automated checks.

## Assumptions

- The selected issue detail surface is implemented in the existing static viewer files.
- The board remains read-only and local-state-only.

## Dependencies

None.

## Open Questions

- Should the minimized state remember its value across reloads, or should it reset to expanded when the viewer loads?

## Activity Log

### Claimed for work
Date: 2026-07-03T16:50:42.677888Z
Agent: Codex
Claim ID: work-af217faa-fff6-4d6e-b846-c30027da2c7d
Branch: codex/hub-viewer-board-detail-footer
Worktree Path: /Users/jcpinto/.config/superpowers/worktrees/notion-agent-hub-skills/hub-viewer-board-detail-footer
