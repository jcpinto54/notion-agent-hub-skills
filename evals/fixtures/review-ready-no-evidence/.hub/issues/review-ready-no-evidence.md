---
id: review-ready-no-evidence
title: "Submit work without evidence"
status: In Review
type: Feature
priority: P1
owner: Codex
change: ""
depends_on: []
blocks: []
claim: {}
base_branch: "main"
branch: "codex/no-evidence"
worktree_path: "/tmp/no-evidence"
commit_sha: ""
pr_url: ""
related_links: ""
---

## Context

This issue was moved to review without regression evidence.

## Scope

Review should reject it.

## Out Of Scope

Do not infer evidence from chat.

## Done Criteria

- [ ] Review gate rejects missing evidence.

## Verification Strategy

### Regression Target

Review-ready work must include test and repo evidence.

### Test Plan

- [ ] Unit: Review audit detects missing evidence.
- [ ] Integration: Review gate refuses completion.
- [ ] E2E / Playwright: Waived for CLI-only review.
- [ ] Manual / inspection: Inspect issue evidence fields.

### First Test

Path: `evals/fixtures/review-ready-no-evidence`
Expected initial result: Audit reports missing review evidence.
Reason this proves the regression or requirement: It prevents review from passing based only on status.

### Final Verification

Commands: `agent-hub audit hub`
Expected result: Review-ready issue has commit, PR, and test evidence.

### Untestable Surface

None.

## Assumptions

Review evidence belongs in issue metadata or evidence sections.

## Dependencies

None.

## Open Questions

None.

## Activity Log

- 2026-06-26: Status moved to In Review without evidence.
