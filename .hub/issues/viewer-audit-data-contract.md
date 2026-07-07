---
id: "viewer-audit-data-contract"
title: "Add audit and analysis data to dashboard snapshots"
status: "Not Started"
type: "Feature"
priority: "P1"
owner: "Unassigned"
area: ""
summary: ""
blockers: ""
dependency_notes: ""
change: "viewer-audit-page"
depends_on: []
blocks: ["viewer-audit-nav-shell", "viewer-audit-diagnostics-renderer", "viewer-audit-docs-fixtures"]
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

The Audit page needs canonical diagnostic data, but the browser must not duplicate audit rules. Dashboard snapshots should include pure non-writing report payloads based on the same backend logic used by audit hub, audit issue, and analyze change.

## Scope

- Refactor audit/analyze builders so dashboard_snapshot can include report-shaped diagnostics without writing .hub/reports.
- Add reports.audit diagnostics and summary to dashboard snapshots.
- When a change filter is supplied, add reports.analysis diagnostics and summary for that change.
- Preserve existing top-level diagnostics and issue card diagnostics for board compatibility.
- Prove dashboard export does not write latest-audit or latest-analysis reports.

## Out Of Scope

- No Audit page UI in this issue.
- No new diagnostic rules unless needed to expose existing canonical output.
- No browser-side audit, YAML, Markdown, or .hub parsing logic.

## Done Criteria

- [ ] Dashboard snapshot includes stable reports.audit fields.
- [ ] Change-filtered dashboard snapshot includes stable reports.analysis fields.
- [ ] Report diagnostics use canonical code, severity, target, message, and recommendation fields.
- [ ] Snapshot generation remains read-only for .hub/reports.

## Verification Strategy

### Regression Target

The Audit view must render backend-owned diagnostics from the dashboard payload without invoking report-writing audit commands.

### Test Plan

- [ ] Unit: python3 -m unittest tests.test_file_hub_backend
- [ ] Integration: python3 -m unittest tests.test_agent_hub_v3
- [ ] Manual / inspection: compare .hub/reports mtimes before and after dashboard export

### First Test

Path: tests/test_file_hub_backend.py::FileHubBackendTests.test_dashboard_snapshot_includes_reports_without_writing_audit_files
Expected initial result: fails before dashboard snapshots include reports.audit and reports.analysis payloads
Reason this proves the regression or requirement: it locks the read-only data contract for the Audit page and prevents browser rule duplication

### Final Verification

Commands: python3 -m unittest tests.test_file_hub_backend tests.test_agent_hub_v3
Expected result: focused backend and CLI tests pass, including non-writing report payload assertions

### Untestable Surface

None beyond browser visual fidelity, which must be covered by desktop and mobile smoke evidence where the issue touches UI.

## Assumptions

- Dashboard export remains read-only; audit hub and analyze change remain the commands that write reports.

## Dependencies

None.

## Open Questions

None.

## Activity Log
