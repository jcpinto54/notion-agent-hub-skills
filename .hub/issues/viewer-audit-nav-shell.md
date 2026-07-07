---
id: "viewer-audit-nav-shell"
title: "Wire Audit rail navigation shell"
status: "Not Started"
type: "Feature"
priority: "P1"
owner: "Unassigned"
area: ""
summary: ""
blockers: ""
dependency_notes: ""
change: "viewer-audit-page"
depends_on: ["viewer-audit-data-contract"]
blocks: ["viewer-audit-diagnostics-renderer", "viewer-audit-docs-fixtures"]
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

The left rail already shows an A button, but it is currently a placeholder. The viewer needs explicit read-only view state so Board and Audit can swap without navigation or mutation.

## Scope

- Add addressable rail buttons with view identifiers for Board and Audit.
- Add an Audit view container and keep the Board view container intact.
- Track active view in local JS state and active/pressed button styling.
- Preserve existing board filters and selected issue state when switching views.
- Keep the shell dependency-free and accessible with button labels.

## Out Of Scope

- No diagnostic renderer beyond a minimal empty/loading shell.
- No Issue page wiring in this issue unless shared view-state helpers are tiny and necessary.
- No browser writes or remediation actions.

## Done Criteria

- [ ] Clicking A shows the Audit shell and marks A active.
- [ ] Clicking B returns to the Board and marks B active.
- [ ] No console errors or layout breakage in desktop smoke.
- [ ] Static tests prove view containers and data-view controls exist.

## Verification Strategy

### Regression Target

The rail must become real navigation before Audit diagnostics can be rendered safely.

### Test Plan

- [ ] Unit/static: python3 -m unittest tests.test_hub_viewer_static
- [ ] Browser: local viewer click smoke for B and A rail buttons

### First Test

Path: tests/test_hub_viewer_static.py::HubViewerStaticTests.test_audit_view_shell_exists_and_rail_controls_are_read_only
Expected initial result: fails before index.html and app.js expose an Audit view shell
Reason this proves the regression or requirement: it confirms the A button is no longer a placeholder and remains read-only

### Final Verification

Commands: python3 -m unittest tests.test_hub_viewer_static
Expected result: static tests pass and browser smoke verifies B/A switching without console errors

### Untestable Surface

None beyond browser visual fidelity, which must be covered by desktop and mobile smoke evidence where the issue touches UI.

## Assumptions

- The Audit page will consume the reports data contract in a later dependent issue.

## Dependencies

- viewer-audit-data-contract provides the payload shape the page will later render.

## Open Questions

None.

## Activity Log
