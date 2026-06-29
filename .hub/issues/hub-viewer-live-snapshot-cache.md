---
id: "hub-viewer-live-snapshot-cache"
title: "Add live dashboard snapshot cache and revision metadata"
status: "In Review"
type: "Feature"
priority: "P1"
owner: "Unassigned"
area: ""
summary: ""
blockers: ""
dependency_notes: ""
change: "hub-viewer-live-updates"
depends_on: []
blocks: ["hub-viewer-live-serve-api", "hub-viewer-live-regression-docs"]
claim: {}
base_branch: "codex/agent-hub-v3-repo-native"
branch: "codex/hub-viewer-live-snapshot-cache"
worktree_path: "/Users/jcpinto/git/notion-agent-hub-skills-hub-viewer-live-snapshot-cache"
commit_sha: "0003f87c3d2c88517e10316397a086d96c70ff87"
pr_url: "https://github.com/jcpinto54/notion-agent-hub-skills/pull/2"
related_links: ""
notion_url: ""
---
## Context

The viewer currently depends on manually exported hub-state.json snapshots. Live serving needs a backend-owned way to detect current .hub source state, recompute dashboard snapshots, and expose stable revision metadata without writing reports or frontend-derived hub logic.

## Scope

- Add pure backend helpers for dashboard source fingerprinting across .hub/config.yml, .hub/issues/*.md, .hub/changes/**, and .hub/runtime/claims.json.
- Add a live snapshot state object that returns dashboard_snapshot output plus revision or ETag metadata.
- Recompute snapshots only through the existing dashboard_snapshot source-of-truth path.
- Prove recompute behavior when an issue file changes through deterministic hub writes.
- Prove read-only invariants for .hub/state.yml, .hub/reports/*, and generated viewer state files.

## Out Of Scope

- No HTTP server or browser code in this issue.
- No audit_hub or analyze_change calls in the live loop because those write reports.
- No browser-side .hub parsing or duplicated readiness/diagnostic rules.

## Done Criteria

- [ ] Backend live snapshot helpers return schema version 3 dashboard data plus revision metadata.
- [ ] A deterministic issue/status change updates the live revision and dashboard payload.
- [ ] Snapshot recompute does not write .hub/state.yml, .hub/reports/*, or viewer hub-state.json.
- [ ] Existing dashboard export behavior remains unchanged.

## Verification Strategy

### Regression Target

The live viewer must observe current .hub state through backend snapshot recomputation instead of stale exported JSON.

### Test Plan

- [ ] Unit: python3 -m unittest tests.test_file_hub_backend
- [ ] Integration: python3 -m unittest tests.test_agent_hub_v3
- [ ] Manual / inspection: compare file mtimes for .hub/state.yml and .hub/reports/* before and after live snapshot reads.

### First Test

Path: tests/test_file_hub_backend.py::FileHubBackendTests.test_dashboard_live_state_recomputes_after_issue_file_change_without_writes
Expected initial result: fails before live snapshot cache helpers exist
Reason this proves the regression or requirement: it proves current .hub file changes are reflected without relying on manual dashboard export or writing reports

### Final Verification

Commands: python3 -m unittest tests.test_file_hub_backend tests.test_agent_hub_v3
Expected result: focused backend and CLI tests pass, including read-only live snapshot invariants

### Untestable Surface

None beyond browser visual fidelity, which must be covered by desktop and mobile smoke evidence where the issue touches UI.

## Assumptions

- Polling or SSE layers can consume the same revision helper later.
- Small personal repos can use simple fingerprinting before a more complex watcher is justified.

## Dependencies

None.

## Open Questions

None.

## Activity Log

### Claimed for work
Date: 2026-06-28T22:05:07.687083Z
Agent: Codex
Claim ID: work-97bae0e5-eaac-4efc-9759-0564a91dca50
Branch: codex/hub-viewer-live-snapshot-cache
Worktree Path: /Users/jcpinto/git/notion-agent-hub-skills-hub-viewer-live-snapshot-cache

### Progress
Date: 2026-06-28T22:09:40.762222Z
Agent: Codex
Summary: Added failing-first backend regression for live dashboard snapshots, then implemented a read-only DashboardLiveSnapshotCache that fingerprints .hub source files and reuses dashboard_snapshot for schema v3 payloads with revision metadata.
Evidence: tests/test_file_hub_backend.py; skills/manage-agent-hub-issues/lib/file_hub_common.py; initial targeted test failed because DashboardLiveSnapshotCache was missing.
Verification: python3 -m unittest tests.test_file_hub_backend.FileHubBackendTests.test_dashboard_live_state_recomputes_after_issue_file_change_without_writes -> OK; python3 -m unittest tests.test_file_hub_backend -> OK; python3 -m unittest tests.test_agent_hub_v3 -> OK.
Risks / skipped checks: No HTTP/server/client surface touched. Packet files were copied into the isolated worktree because the claimed issue existed only as untracked caller-worktree Hub metadata.
Next step: Run final combined verification, commit, push, open PR, submit issue to review, and release the claim.

### Status change: In Progress -> In Review
Date: 2026-06-28T22:11:20.580699Z
Agent: Codex
Summary: Implemented live dashboard snapshot cache and revision metadata for backend file hubs.
Evidence: Commit: 0003f87c3d2c88517e10316397a086d96c70ff87; PR: https://github.com/jcpinto54/notion-agent-hub-skills/pull/2; files: skills/manage-agent-hub-issues/lib/file_hub_common.py, tests/test_file_hub_backend.py, .hub/issues/hub-viewer-live-snapshot-cache.md, .hub/changes/hub-viewer-live-updates/.
Verification: python3 -m unittest tests.test_file_hub_backend tests.test_agent_hub_v3 -> OK (24 tests).
Risks / skipped checks: No server/client/API surface included by design. Live helper returns dashboard schema v3 payload with added revision metadata; dashboard export remains unchanged.
Next step: Reviewer should verify cache invalidation on .hub source changes and read-only invariants for state, reports, and viewer hub-state files.

### Released claim (submitted)
Date: 2026-06-28T22:11:20.631335Z
Claim ID: work-97bae0e5-eaac-4efc-9759-0564a91dca50
Mode: submitted
Status: In Review
Owner: Unassigned
