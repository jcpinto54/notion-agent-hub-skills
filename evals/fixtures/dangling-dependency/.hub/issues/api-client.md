---
id: api-client
title: "Build API client"
status: Not Started
type: Feature
priority: P2
owner: Unassigned
change: ""
depends_on:
  - missing-auth-contract
blocks: []
claim: {}
base_branch: ""
branch: ""
worktree_path: ""
commit_sha: ""
pr_url: ""
related_links: ""
---

## Context

The API client depends on an auth contract issue that does not exist.

## Scope

Build the API client after dependencies are valid.

## Out Of Scope

Do not create the auth contract implicitly.

## Done Criteria

- [ ] Dependency graph is valid before claiming.

## Verification Strategy

### Regression Target

Dangling dependencies must be reported.

### Test Plan

- [ ] Unit: Audit detects missing dependency issue.
- [ ] Integration: Claim refuses work with missing dependency.
- [ ] E2E / Playwright: Waived for CLI-only dependency graph.
- [ ] Manual / inspection: Inspect `.hub/issues`.

### First Test

Path: `evals/fixtures/dangling-dependency`
Expected initial result: Audit reports `dangling_dependency`.
Reason this proves the regression or requirement: Claimability depends on a valid graph.

### Final Verification

Commands: `agent-hub audit hub`
Expected result: No dangling dependency diagnostics.

### Untestable Surface

None.

## Assumptions

Dependencies reference issue IDs.

## Dependencies

- missing-auth-contract

## Open Questions

None.

## Activity Log
