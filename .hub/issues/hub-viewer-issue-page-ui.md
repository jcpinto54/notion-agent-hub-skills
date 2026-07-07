---
id: "hub-viewer-issue-page-ui"
title: "Render read-only Issue page UI"
status: "Not Started"
type: "Feature"
priority: "P1"
owner: "Unassigned"
area: ""
summary: ""
blockers: ""
dependency_notes: ""
change: "readonly-issue-viewer"
depends_on: ["hub-viewer-issue-detail-contract", "hub-viewer-issue-nav-state"]
blocks: ["hub-viewer-issue-page-verification-docs"]
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

After detail data and navigation exist, the Issue page should become the focused single-issue reading surface for specs, verification, dependencies, evidence, and per-issue health.

## Scope

- Render an issue picker or list based on the loaded dashboard payload.
- Render selected issue metadata: id, title, status, type, priority, owner, change, readiness, and path.
- Render spec sections from detail: context, scope, out of scope, assumptions, dependencies, and open questions.
- Render blockers, depends_on, blocks, diagnostics, done criteria, first test, and final verification.
- Render compact latest activity or evidence snippets if included by the backend.
- Keep layout responsive on desktop and mobile without overlap.

## Out Of Scope

- No editing or deterministic command execution from the browser.
- No Audit hub-wide diagnostics page work.
- No live server or refresh work.
- No frontend Markdown parsing or external dependencies.

## Done Criteria

- [ ] Issue page displays selected issue spec and verification fields from snapshot JSON.
- [ ] Issue selector changes local selection only.
- [ ] Missing optional details render clear empty states.
- [ ] No mutation controls appear in the Issue page.
- [ ] Desktop and mobile browser smoke pass without console errors or layout overflow.

## Verification Strategy

### Regression Target

Users and agents need a focused issue inspection page that reads backend-exported detail data only.

### Test Plan

- [ ] Unit/static: python3 -m unittest tests.test_hub_viewer_static
- [ ] Browser: select card, click I, verify title/status/done criteria/verification render
- [ ] Browser mobile: Issue page has no overflow or clipped controls

### First Test

Path: browser smoke fixture: select a board card, click I, and expect the same issue title, status, done criteria, and final verification command
Expected initial result: fails before the Issue page renderer exists
Reason this proves the regression or requirement: it verifies the end-user workflow and selected issue preservation

### Final Verification

Commands: python3 -m unittest tests.test_hub_viewer_static tests.test_file_hub_backend tests.test_agent_hub_v3
Expected result: focused tests pass and browser smoke confirms read-only Issue page behavior

### Untestable Surface

None beyond browser visual fidelity, which must be covered by desktop and mobile smoke evidence where the issue touches UI.

## Assumptions

- The Issue page can reuse existing detail tray styles if they remain clear and responsive.

## Dependencies

- hub-viewer-issue-detail-contract and hub-viewer-issue-nav-state must be complete.

## Open Questions

None.

## Activity Log
