---
id: "hub-viewer-live-client"
title: "Add live mode to the static viewer client"
status: "Not Started"
type: "Feature"
priority: "P1"
owner: "Unassigned"
area: ""
summary: ""
blockers: ""
dependency_notes: ""
change: "hub-viewer-live-updates"
depends_on: ["hub-viewer-live-serve-api"]
blocks: ["hub-viewer-live-regression-docs"]
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

The browser currently fetches hub-state.json or a ?data URL once. When served by dashboard serve, it should read current state from the local API and refresh without adding browser-side hub logic or write paths.

## Scope

- Add a live mode entry path, such as ?live=1, that loads /api/state instead of hub-state.json.
- Subscribe to /api/events for revision notifications and refetch /api/state when the revision changes.
- Add conditional polling fallback when SSE is unavailable.
- Preserve selected issue, active filters, and active view across payload refreshes when possible.
- Show generated/live metadata so users can tell the dashboard is connected to live state.
- Preserve static hub-state.json, ?data=<url>, and sample fallback behavior.

## Out Of Scope

- No server implementation in this issue.
- No browser mutation calls or write controls.
- No frontend readiness, audit, or .hub parsing logic.
- No package manager, framework, or external dependency.

## Done Criteria

- [ ] Static tests prove live mode code exists without external dependencies or mutation methods.
- [ ] Live mode fetches /api/state and can refresh from a revision event.
- [ ] Static snapshot mode remains working.
- [ ] Selected issue and filters survive refresh when the issue still exists.

## Verification Strategy

### Regression Target

The viewer must transition from one-shot snapshot loading to live read-only refresh while preserving all current static behavior.

### Test Plan

- [ ] Unit/static: python3 -m unittest tests.test_hub_viewer_static
- [ ] Integration: serve live API and load viewer with ?live=1
- [ ] E2E / Browser: update .hub through deterministic CLI and verify card movement without browser mutation

### First Test

Path: tests/test_hub_viewer_static.py::HubViewerStaticTests.test_viewer_supports_live_mode_without_external_dependencies_or_mutation_methods
Expected initial result: fails before app.js supports live mode and read-only refresh paths
Reason this proves the regression or requirement: it protects the client boundary and prevents introducing write APIs or external dependencies

### Final Verification

Commands: python3 -m unittest tests.test_hub_viewer_static tests.test_file_hub_backend tests.test_agent_hub_v3
Expected result: viewer, backend, and CLI focused tests pass, followed by browser smoke in live mode

### Untestable Surface

None beyond browser visual fidelity, which must be covered by desktop and mobile smoke evidence where the issue touches UI.

## Assumptions

- Live mode is only used when served by dashboard serve or another compatible read-only API.
- Static mode remains the default for plain http.server usage.

## Dependencies

- hub-viewer-live-serve-api must provide /api/state and /api/events.

## Open Questions

None.

## Activity Log
