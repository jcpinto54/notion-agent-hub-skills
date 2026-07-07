---
id: "hub-viewer-issue-nav-state"
title: "Wire Issue rail navigation state"
status: "Not Started"
type: "Feature"
priority: "P1"
owner: "Unassigned"
area: ""
summary: ""
blockers: ""
dependency_notes: ""
change: "readonly-issue-viewer"
depends_on: ["hub-viewer-issue-detail-contract"]
blocks: ["hub-viewer-issue-page-ui"]
claim: {}
base_branch: ""
branch: ""
worktree_path: ""
commit_sha: ""
pr_url: ""
related_links: ""
external_url: ""
---
## Context

The left rail already shows an I button, but it is currently a placeholder. The viewer needs explicit read-only view state so Board and Issue views can swap while preserving issue selection.

## Scope

- Add addressable rail controls for Board and Issue views.
- Add an Issue view container and active/pressed rail state.
- Preserve selected issue when navigating from a board card to the Issue page.
- Default to the first visible issue when no selected issue exists.
- Keep existing Board behavior intact.

## Out Of Scope

- No Issue detail renderer beyond shell/selection plumbing.
- No Audit page implementation here unless shared view-state helpers are tiny and already present.
- No write controls or browser mutation paths.

## Done Criteria

- [ ] Clicking I opens the Issue shell for the selected issue.
- [ ] Clicking B returns to the Board.
- [ ] Selected issue survives Board to Issue navigation.
- [ ] Static tests prove I is a read-only view control.

## Verification Strategy

### Regression Target

The Issue rail button must become real navigation before detail data can be rendered safely.

### Test Plan

- [ ] Unit/static: python3 -m unittest tests.test_hub_viewer_static
- [ ] Browser: select a card, click I, confirm Issue shell references the same issue

### First Test

Path: tests/test_hub_viewer_static.py::HubViewerStaticTests.test_issue_view_shell_exists_and_rail_control_is_read_only
Expected initial result: fails before index.html and app.js expose Issue view navigation
Reason this proves the regression or requirement: it proves the I rail button is no longer a placeholder and does not add mutation controls

### Final Verification

Commands: python3 -m unittest tests.test_hub_viewer_static
Expected result: static tests pass and browser smoke verifies B/I switching without console errors

### Untestable Surface

None beyond browser visual fidelity, which must be covered by desktop and mobile smoke evidence where the issue touches UI.

## Assumptions

- Issue detail data is available from the previous backend contract issue.

## Dependencies

- hub-viewer-issue-detail-contract must provide issue detail payload fields.

## Open Questions

None.

## Activity Log
