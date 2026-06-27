---
id: ready-implementation
title: "Add deterministic eval runner"
status: Not Started
type: Feature
priority: P2
owner: Unassigned
change: eval-contract
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

Agent Hub v3 needs repeatable local evals.

## Scope

Add a stdlib runner for fixture and scenario evals.

## Out Of Scope

Do not implement audit or analyze behavior in this fixture.

## Done Criteria

- [ ] Runner discovers all expected fixture diagnostics.
- [ ] Runner writes a JSON and Markdown report.

## Verification Strategy

### Regression Target

Missing v3 audit and analyze implementation should fail evals clearly.

### Test Plan

- [ ] Unit: `python3 evals/run_evals.py`
- [ ] Integration: Fixture audit commands run from fixture cwd.
- [ ] E2E / Playwright: Waived because this is a local CLI eval.
- [ ] Manual / inspection: Inspect `evals/reports/latest-eval-report.json`.

### First Test

Path: `evals/run_evals.py`
Expected initial result: Fails because the v3 deterministic CLI or library is missing.
Reason this proves the regression or requirement: The eval harness must detect absent v3 audit and scenario behavior before implementation.

### Final Verification

Commands: `python3 evals/run_evals.py`
Expected result: Passes once the v3 deterministic CLI and scenario evaluator exist.

### Untestable Surface

None.

## Assumptions

The future CLI is named `agent-hub` or `skills/manage-agent-hub-issues/scripts/agent_hub.py`.

## Dependencies

None.

## Open Questions

None.

## Activity Log

- 2026-06-26: Fixture created for eval harness validation.
