---
id: stale-worker
title: "Finish abandoned implementation"
status: In Progress
type: Feature
priority: P2
owner: Codex
change: ""
depends_on: []
blocks: []
claim:
  owner: "Codex"
  purpose: "work"
  claimed_at: "2026-06-25T08:00:00Z"
  expires_at: "2026-06-25T10:00:00Z"
base_branch: "main"
branch: "codex/stale-worker"
worktree_path: "/tmp/stale-worker"
commit_sha: ""
pr_url: ""
related_links: ""
---

## Context

This issue has an expired local claim.

## Scope

Finish the implementation.

## Out Of Scope

Do not change unrelated issues.

## Done Criteria

- [ ] Claim state is refreshed or released.

## Verification Strategy

### Regression Target

Expired claims must block fresh work until resolved.

### Test Plan

- [ ] Unit: Audit reports stale claim.
- [ ] Integration: Claim lifecycle command releases stale claim.
- [ ] E2E / Playwright: Waived for CLI-only state.
- [ ] Manual / inspection: Inspect `.hub/runtime/claims.json`.

### First Test

Path: `evals/fixtures/stale-claim`
Expected initial result: Audit reports `stale_claim`.
Reason this proves the regression or requirement: It verifies claim expiry is evaluated deterministically.

### Final Verification

Commands: `agent-hub audit hub`
Expected result: No stale claim diagnostic after release.

### Untestable Surface

None.

## Assumptions

The stale threshold is 120 minutes.

## Dependencies

None.

## Open Questions

None.

## Activity Log

- 2026-06-25T08:00:00Z: Codex claimed work.
