---
id: "hub-app-multi-instance-runtime"
title: "Support multiple simultaneous Agent Hub app instances"
status: "Not Started"
type: "Feature"
priority: "P1"
owner: "Unassigned"
area: ""
summary: ""
blockers: ""
dependency_notes: ""
change: ""
depends_on: []
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

The new `run-agent-hub-app` skill starts the local read-only Agent Hub viewer by exporting a snapshot into the installed viewer directory. That works for one active dashboard, but it is not prepared for multiple hub apps at the same time because all runs share the same `hub-state.json` target and a single viewer URL can silently switch to the most recently exported repo.

Users need to run dashboards for multiple repos or change packets concurrently without one app overwriting another app's state.

## Scope

- Update `skills/run-agent-hub-app/scripts/run_agent_hub_app.py` so each launched hub app instance has an isolated runtime snapshot path.
- Derive a stable per-instance runtime directory from repo path plus optional change slug, stored under the target repo's `.hub/runtime/agent-hub-app/`.
- Serve each app with a URL that points the static viewer at that specific snapshot, for example through the viewer's existing `?data=` support or an equivalent per-instance static serving strategy.
- Ensure two different repos, or the same repo with two different `--change` values, can be open simultaneously without sharing dashboard state.
- Keep the viewer read-only and continue to reuse the existing static viewer files instead of introducing a build step.
- Preserve the existing single-hub default behavior for users who only run one app.
- Update skill docs and README guidance to describe multi-instance behavior and the returned URL.

## Out Of Scope

- Browser-side editing or mutation of `.hub` state.
- Replacing the static viewer with a frontend framework or build pipeline.
- Implementing the live update API/client work owned by the other `hub-viewer-live-updates` issues.
- Cross-machine hosting or public network binding.

## Done Criteria

- [ ] Running the app for repo A and repo B creates distinct snapshot files and distinct usable URLs.
- [ ] Running the app for the same repo with two different `--change` values creates distinct snapshot files and distinct usable URLs.
- [ ] Existing `--port` behavior still avoids unrelated occupied ports and reuses an existing matching app only when it is safe for that exact repo/change instance.
- [ ] Generated runtime snapshots and server metadata remain under ignored runtime paths, not tracked source files.
- [ ] The viewer still loads the default single-instance flow and static sample fallback.
- [ ] Documentation explains that concurrent apps are supported and how the returned URL maps to an isolated snapshot.

## Verification Strategy

### Regression Target

The runner must stop writing all launches to the shared installed viewer `hub-state.json` and must stop treating any existing viewer server on the requested port as interchangeable across repos or change filters.

### Test Plan

- [ ] Unit: add focused tests for runtime snapshot path derivation, per-instance URL generation, and safe reuse semantics.
- [ ] Integration: run the runner twice with different repo/change inputs and assert both exported snapshots remain distinct and reachable.
- [ ] E2E / Playwright: optional browser smoke that opens two returned URLs and verifies each page shows the expected repo/change metadata.
- [ ] Manual / inspection: verify `git status --ignored` shows generated snapshots under ignored runtime state.

### First Test

Path: tests/test_run_agent_hub_app.py::RunAgentHubAppTests.test_concurrent_apps_use_isolated_snapshots_and_urls
Expected initial result: fails because the current runner writes every export to the shared installed viewer `hub-state.json` and returns a shared URL.
Reason this proves the regression or requirement: it directly captures the multi-instance bug by requiring two launched hub apps to keep separate data sources.

### Final Verification

Commands: python3 -m unittest tests.test_run_agent_hub_app tests.test_hub_viewer_static
Expected result: runner tests and existing static viewer tests pass; manual smoke can open two returned URLs without state crossover.

### Untestable Surface

None expected. If browser smoke is skipped, record the reason and include the deterministic URL/snapshot assertions as evidence.

## Assumptions

- The static viewer's existing `?data=` support can load an isolated snapshot URL served by the same local HTTP process.
- The installed skill set remains the source of viewer assets, while target repos own their runtime state.

## Dependencies

- Related to `hub-viewer-live-updates`, but should remain independently claimable if it only changes the launcher/runtime snapshot strategy.
- Coordinate with `hub-viewer-live-serve-api` if that work introduces a local API server that can provide a cleaner per-instance data URL.

## Open Questions

- Should reuse semantics prefer one server per repo/change, or one static server with multiple `?data=` snapshot URLs?
- Should the runner expose a `--new-instance` flag to force a fresh port even when an equivalent app instance already exists?

## Activity Log
