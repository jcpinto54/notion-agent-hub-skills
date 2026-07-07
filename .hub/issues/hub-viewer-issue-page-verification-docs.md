---
id: "hub-viewer-issue-page-verification-docs"
title: "Document and verify read-only Issue page"
status: "Not Started"
type: "Task"
priority: "P1"
owner: "Unassigned"
area: ""
summary: ""
blockers: ""
dependency_notes: ""
change: "readonly-issue-viewer"
depends_on: ["hub-viewer-issue-page-ui"]
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

The Issue page needs sample data, docs, and browser evidence so future agents understand that it is a read-only inspection surface backed by dashboard snapshots.

## Scope

- Update bundled sample JSON with representative issue detail fields.
- Update static tests for issue detail contract and view behavior.
- Update README and docs/hub-viewer-implementation.md with Issue page purpose and non-goals.
- Run desktop and mobile browser smoke for Board to Issue navigation.
- Record final validation evidence through Agent Hub activity/evidence commands during implementation.

## Out Of Scope

- No new Issue page features beyond fixture/docs/test alignment.
- No live server, Audit page, or browser mutation work.

## Done Criteria

- [ ] Sample fallback renders a useful Issue page.
- [ ] Docs explain Issue page data ownership and read-only limits.
- [ ] Tests cover detail payload shape and dependency-free viewer constraints.
- [ ] Browser smoke evidence covers selected issue rendering on desktop and mobile.

## Verification Strategy

### Regression Target

Fixtures and docs must keep the Issue page contract stable and agent-usable.

### Test Plan

- [ ] Unit/static: python3 -m unittest tests.test_hub_viewer_static
- [ ] Full unit: python3 -m unittest discover -s tests
- [ ] Evals: python3 evals/run_evals.py when implementation is complete
- [ ] Browser: desktop/mobile Issue page smoke

### First Test

Path: tests/test_hub_viewer_static.py::HubViewerStaticTests.test_sample_state_includes_issue_detail_payload
Expected initial result: fails before sample state and docs include Issue page detail data
Reason this proves the regression or requirement: it protects the sample fallback and documentation from drifting away from the Issue page contract

### Final Verification

Commands: python3 -m unittest discover -s tests && python3 evals/run_evals.py
Expected result: all deterministic tests and evals pass, plus Issue page browser smoke evidence is recorded

### Untestable Surface

None beyond browser visual fidelity, which must be covered by desktop and mobile smoke evidence where the issue touches UI.

## Assumptions

- This issue is last because it documents actual implemented behavior.

## Dependencies

- hub-viewer-issue-page-ui must be complete.

## Open Questions

None.

## Activity Log
