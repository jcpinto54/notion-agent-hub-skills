---
id: "hub-viewer-issue-detail-contract"
title: "Extend dashboard snapshot with issue detail sections"
status: "Not Started"
type: "Feature"
priority: "P1"
owner: "Unassigned"
area: ""
summary: ""
blockers: ""
dependency_notes: ""
change: "readonly-issue-viewer"
depends_on: []
blocks: ["hub-viewer-issue-nav-state", "hub-viewer-issue-page-ui"]
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

The Issue page should show issue specs and evidence without making the browser parse .hub Markdown. The backend must export the detail sections the UI needs from the existing issue body structure.

## Scope

- Add a detail object to each dashboard issue card with backend-parsed sections.
- Include context, scope, out_of_scope, assumptions, dependencies, open_questions, and concise activity or evidence snippets where feasible.
- Reuse existing card metadata, readiness, diagnostics, done_criteria, and verification fields.
- Keep the snapshot schema backward-compatible for existing Board rendering.
- Update sample/contract tests for issue detail fields.

## Out Of Scope

- No Issue page UI in this issue.
- No frontend Markdown parsing.
- No write controls, status changes, claims, or review actions.
- No Audit page or live server work.

## Done Criteria

- [ ] dashboard_snapshot includes detail sections for every issue card.
- [ ] Missing sections produce empty strings or arrays, not browser parsing requirements.
- [ ] Existing dashboard export consumers still work.
- [ ] Backend tests cover detail extraction from a temp issue body.

## Verification Strategy

### Regression Target

The Issue page data must come from backend-owned Markdown section parsing rather than frontend parsing or duplicated .hub rules.

### Test Plan

- [ ] Unit: python3 -m unittest tests.test_file_hub_backend
- [ ] Integration: python3 -m unittest tests.test_agent_hub_v3
- [ ] Static: python3 -m unittest tests.test_hub_viewer_static after sample update

### First Test

Path: tests/test_file_hub_backend.py::FileHubBackendTests.test_dashboard_snapshot_includes_issue_detail_sections
Expected initial result: fails before detail fields are exported from dashboard_snapshot
Reason this proves the regression or requirement: it locks the backend source-of-truth boundary for the Issue page

### Final Verification

Commands: python3 -m unittest tests.test_file_hub_backend tests.test_agent_hub_v3
Expected result: focused backend and CLI tests pass with detail section assertions

### Untestable Surface

None beyond browser visual fidelity, which must be covered by desktop and mobile smoke evidence where the issue touches UI.

## Assumptions

- Only compact text sections are exported; large artifacts remain linked rather than embedded.

## Dependencies

None.

## Open Questions

None.

## Activity Log
