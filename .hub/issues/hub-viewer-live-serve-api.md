---
id: "hub-viewer-live-serve-api"
title: "Add read-only dashboard serve API"
status: "In Progress"
type: "Feature"
priority: "P1"
owner: "Codex"
area: ""
summary: ""
blockers: ""
dependency_notes: ""
change: "hub-viewer-live-updates"
depends_on: ["hub-viewer-live-snapshot-cache"]
blocks: ["hub-viewer-live-client", "hub-viewer-live-regression-docs"]
claim:
  id: "work-ee84560d-7ae8-465b-b090-383e7b66ca99"
  purpose: "work"
  owner: "Codex"
  claimed_at: "2026-07-03T15:49:13.790405Z"
  expires_at: "2026-07-03T17:49:13.790405Z"
  machine: "Joaos-MacBook-Pro.local"
base_branch: "codex/agent-hub-v3-repo-native"
branch: "codex/hub-viewer-live-serve-api"
worktree_path: "/Users/jcpinto/git/agent-hub-skills-hub-viewer-live-serve-api"
commit_sha: ""
pr_url: ""
related_links: ""
external_url: ""
---
## Context

After backend live snapshot helpers exist, Agent Hub needs a local command that serves the existing viewer and current dashboard state without requiring repeated dashboard export commands.

## Scope

- Add agent-hub dashboard serve to the CLI with local bind defaults of 127.0.0.1 and a configurable port.
- Serve existing static viewer files from skills/list-agent-hub-issues/viewer/.
- Expose GET /api/state with dashboard schema version 3, live revision metadata, and Cache-Control: no-store.
- Expose GET /api/events using server-sent events for revision notifications.
- Expose GET /healthz for smoke checks.
- Reject POST, PUT, PATCH, and DELETE requests with 405.
- Keep the server implementation dependency-free with Python stdlib only.

## Out Of Scope

- No viewer live-mode client changes in this issue.
- No browser write APIs or mutation endpoints.
- No WebSocket, Node, Vite, React, CDN, auth, hosting, or external sync work.

## Done Criteria

- [ ] CLI parser accepts dashboard serve options without breaking dashboard export.
- [ ] Local server returns valid /api/state JSON for a temp hub.
- [ ] SSE endpoint emits a revision notification when backend source changes.
- [ ] Mutation HTTP methods are rejected.
- [ ] Static viewer files are served from the existing viewer directory.

## Verification Strategy

### Regression Target

The live dashboard needs a read-only local API surface that exposes current backend snapshots while refusing mutation paths.

### Test Plan

- [ ] Unit: python3 -m unittest tests.test_agent_hub_v3
- [ ] Integration: server smoke against a temp hub for /, /api/state, /api/events, and /healthz
- [ ] Manual / inspection: verify POST/PUT/PATCH/DELETE return 405

### First Test

Path: tests/test_agent_hub_v3.py::AgentHubV3CliTests.test_dashboard_serve_exposes_read_only_state_api
Expected initial result: fails before dashboard serve and its state endpoint exist
Reason this proves the regression or requirement: it locks the public CLI/API shape and read-only behavior before implementation

### Final Verification

Commands: python3 -m unittest tests.test_file_hub_backend tests.test_agent_hub_v3
Expected result: focused live backend and CLI/server tests pass

### Untestable Surface

None beyond browser visual fidelity, which must be covered by desktop and mobile smoke evidence where the issue touches UI.

## Assumptions

- The serve command is local-first and not a hosted product surface.
- SSE is preferred for lightweight updates, with client polling fallback implemented separately.

## Dependencies

- hub-viewer-live-snapshot-cache must provide revision-aware read-only state helpers.

## Open Questions

None.

## Activity Log

### Claimed for work
Date: 2026-07-03T15:49:13.790405Z
Agent: Codex
Claim ID: work-ee84560d-7ae8-465b-b090-383e7b66ca99
Branch: codex/hub-viewer-live-serve-api
Worktree Path: /Users/jcpinto/git/agent-hub-skills-hub-viewer-live-serve-api
