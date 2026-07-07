---
id: "viewer-audit-docs-fixtures"
title: "Document and verify Audit page behavior"
status: "Not Started"
type: "Task"
priority: "P2"
owner: "Unassigned"
area: ""
summary: ""
blockers: ""
dependency_notes: ""
change: "viewer-audit-page"
depends_on: ["viewer-audit-data-contract", "viewer-audit-nav-shell", "viewer-audit-diagnostics-renderer"]
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

The Audit page should be documented and sample-backed so agents understand that it is a read-only diagnostic view powered by backend reports, not a place to fix hub records manually.

## Scope

- Update bundled sample JSON with audit and analysis report diagnostics.
- Update static tests to assert the sample report payload and Audit view expectations.
- Update README and docs/hub-viewer-implementation.md with Audit page purpose and non-goals.
- Add or update browser smoke guidance for desktop and mobile Audit view checks.
- Record final validation evidence through Agent Hub issue activity/evidence commands during implementation.

## Out Of Scope

- No new Audit UI features beyond fixture/docs/test alignment.
- No new diagnostic rules or backend report semantics.

## Done Criteria

- [ ] Sample fallback renders a useful Audit page.
- [ ] Docs explain hub audit versus change analysis sources.
- [ ] Tests cover report payload shape and dependency-free viewer constraints.
- [ ] Browser smoke evidence covers Audit page rendering.

## Verification Strategy

### Regression Target

Fixtures and docs must protect the Audit page contract after implementation.

### Test Plan

- [ ] Unit/static: python3 -m unittest tests.test_hub_viewer_static
- [ ] Full unit: python3 -m unittest discover -s tests
- [ ] Evals: python3 evals/run_evals.py when implementation is complete
- [ ] Browser: desktop/mobile Audit page smoke

### First Test

Path: tests/test_hub_viewer_static.py::HubViewerStaticTests.test_sample_state_includes_audit_report_payload
Expected initial result: fails before sample state and docs include Audit report data
Reason this proves the regression or requirement: it ensures sample fallback and documentation stay aligned with the Audit page contract

### Final Verification

Commands: python3 -m unittest discover -s tests && python3 evals/run_evals.py
Expected result: all deterministic tests and evals pass, plus Audit browser smoke evidence is recorded

### Untestable Surface

None beyond browser visual fidelity, which must be covered by desktop and mobile smoke evidence where the issue touches UI.

## Assumptions

- This issue is last because it documents actual implemented behavior.

## Dependencies

- All other viewer-audit-page issues must be complete.

## Open Questions

None.

## Activity Log
