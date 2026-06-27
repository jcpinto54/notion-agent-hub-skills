---
id: api-client
title: "Build API client"
status: Not Started
type: Feature
priority: P2
owner: Unassigned
change: other-change
depends_on: []
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

The API client is listed in `broken-change` but links to a different change.

## Scope

Build the API client.

## Out Of Scope

Do not build the UI shell.

## Done Criteria

- [ ] API client request flow is covered by a test.

## Verification Strategy

### Regression Target

Issue-to-change links must align.

### Test Plan

- [ ] Unit: Analyze reports mismatched change link.
- [ ] Integration: Change packet lists only linked issues.
- [ ] E2E / Playwright: Waived for CLI-only analyze.
- [ ] Manual / inspection: Inspect issue frontmatter.

### First Test

Path: `evals/fixtures/broken-change-packet`
Expected initial result: Analyze reports `issue_change_mismatch`.
Reason this proves the regression or requirement: It prevents orphaned change tasks.

### Final Verification

Commands: `agent-hub analyze change broken-change`
Expected result: No packet consistency diagnostics.

### Untestable Surface

None.

## Assumptions

Issue `change` must equal the containing packet ID.

## Dependencies

None.

## Open Questions

None.

## Activity Log
