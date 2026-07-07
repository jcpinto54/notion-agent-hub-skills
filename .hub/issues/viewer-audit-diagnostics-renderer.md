---
id: "viewer-audit-diagnostics-renderer"
title: "Render read-only audit diagnostics page"
status: "Not Started"
type: "Feature"
priority: "P1"
owner: "Unassigned"
area: ""
summary: ""
blockers: ""
dependency_notes: ""
change: "viewer-audit-page"
depends_on: ["viewer-audit-data-contract", "viewer-audit-nav-shell"]
blocks: ["viewer-audit-docs-fixtures"]
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

After the report payload and Audit shell exist, the Audit page should become the diagnostic cockpit: what is unsafe, stale, vague, blocked, or under-evidenced in the hub or selected change.

## Scope

- Render summary counts for audit and optional change analysis diagnostics.
- Render diagnostic rows with severity, source, code, target, message, and recommendation from the payload.
- Add local read-only filters for severity, source, and diagnostic code.
- Allow diagnostic targets that reference issues to select or link to the matching issue context without mutating state.
- Render useful empty states when no diagnostics exist.
- Ensure mobile layout remains scannable without overlap or body overflow.

## Out Of Scope

- No browser-side severity assignment or recommendation generation.
- No repair buttons, deterministic command execution, or .hub writes.
- No changes to Board column semantics or Issue page detail ownership.

## Done Criteria

- [ ] Audit page renders known diagnostic fixture rows exactly from JSON.
- [ ] Severity/source/code filters update local view only.
- [ ] Counts match payload diagnostics.
- [ ] Diagnostic target interactions do not mutate files or browser state beyond selection/navigation.

## Verification Strategy

### Regression Target

The Audit page must expose canonical diagnostics in a useful triage surface without becoming a mutation UI.

### Test Plan

- [ ] Unit/static: python3 -m unittest tests.test_hub_viewer_static
- [ ] Browser: fixture with audit and analysis diagnostics renders codes and recommendations
- [ ] Browser mobile: Audit page has no text overlap or body overflow

### First Test

Path: browser smoke fixture: click A and expect known diagnostic code, target, message, and recommendation from JSON
Expected initial result: fails before the Audit renderer exists
Reason this proves the regression or requirement: it verifies the page consumes backend diagnostics rather than derived frontend rules

### Final Verification

Commands: python3 -m unittest tests.test_hub_viewer_static tests.test_file_hub_backend tests.test_agent_hub_v3
Expected result: focused static/backend/CLI tests pass and browser smoke confirms Audit rendering

### Untestable Surface

None beyond browser visual fidelity, which must be covered by desktop and mobile smoke evidence where the issue touches UI.

## Assumptions

- The diagnostics payload contains all content required for display.
- Issue target selection can reuse existing selectedId state.

## Dependencies

- viewer-audit-data-contract and viewer-audit-nav-shell must be complete.

## Open Questions

None.

## Activity Log
