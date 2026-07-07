---
id: "hub-viewer-live-regression-docs"
title: "Document and verify live dashboard workflow"
status: "Not Started"
type: "Task"
priority: "P2"
owner: "Unassigned"
area: ""
summary: ""
blockers: ""
dependency_notes: ""
change: "hub-viewer-live-updates"
depends_on: ["hub-viewer-live-snapshot-cache", "hub-viewer-live-serve-api", "hub-viewer-live-client"]
blocks: []
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

The live dashboard should be documented and regression-protected after the backend, server, and client pieces exist, so future agents can use it without rediscovering the workflow.

## Scope

- Update README with the dashboard serve workflow and clarify when to use export versus serve.
- Update the list-agent-hub-issues skill docs with live mode usage and read-only constraints.
- Update docs/hub-viewer-implementation.md with live architecture and static compatibility.
- Update tests or eval fixtures that assert viewer docs and sample behavior.
- Run desktop and mobile browser smoke against live mode and capture durable evidence.

## Out Of Scope

- No new live server features beyond documentation and verification fixes.
- No write controls, hosted deployment, auth, or external sync documentation except as explicit non-goals.

## Done Criteria

- [ ] Docs explain dashboard serve, /api/state, live refresh, and static fallback.
- [ ] Regression checks cover live and static viewer expectations.
- [ ] Browser smoke evidence verifies live refresh on desktop and mobile.
- [ ] Full unit/eval/skill validation passes or skipped checks are justified.

## Verification Strategy

### Regression Target

Documentation and fixture expectations must prevent future regressions back to manual-only export behavior.

### Test Plan

- [ ] Unit/static: python3 -m unittest tests.test_hub_viewer_static
- [ ] Full unit: python3 -m unittest discover -s tests
- [ ] Evals: python3 evals/run_evals.py
- [ ] Skill validation: quick_validate.py for skills/*
- [ ] Browser: desktop and mobile live-mode smoke

### First Test

Path: docs/live-dashboard-workflow assertion or tests/test_hub_viewer_static.py::HubViewerStaticTests.test_live_dashboard_docs_are_present
Expected initial result: fails before docs mention dashboard serve and live mode expectations
Reason this proves the regression or requirement: it prevents shipping live behavior without agent-usable instructions

### Final Verification

Commands: python3 -m unittest discover -s tests && python3 evals/run_evals.py
Expected result: all deterministic tests and evals pass, plus browser smoke evidence is recorded

### Untestable Surface

None beyond browser visual fidelity, which must be covered by desktop and mobile smoke evidence where the issue touches UI.

## Assumptions

- This issue runs after implementation issues so docs describe actual command behavior.
- Generated hub-state.json remains ignored and uncommitted.

## Dependencies

- All other hub-viewer-live-updates issues must be complete.

## Open Questions

None.

## Activity Log
