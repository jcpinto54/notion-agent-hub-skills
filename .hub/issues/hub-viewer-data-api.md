---
id: "hub-viewer-data-api"
title: "Define read-only hub viewer data contract"
status: "Completed"
type: "Feature"
priority: "P1"
owner: "codex-reviewer"
area: ""
summary: ""
blockers: ""
dependency_notes: ""
change: "readonly-kanban-viewer"
depends_on: []
blocks: ["hub-viewer-kanban-ui"]
claim: {}
base_branch: "main"
branch: "codex/agent-hub-v3-repo-native"
worktree_path: "/Users/jcpinto/git/notion-agent-hub-skills"
commit_sha: "b93175ac9f7f1e8792c0bc8bd2c6191c724c7bc9"
pr_url: "https://github.com/jcpinto54/notion-agent-hub-skills/pull/1"
related_links: ""
notion_url: ""
---
## Context

Agent Hub needs a read-only dashboard data contract so a visual Kanban viewer can
render repo-native `.hub` state without parsing Markdown in the browser or
calling Notion. The contract should be deterministic, stable under tests, and
safe to export without refreshing state or writing audit reports.

## Scope

- Add a deterministic `issue set-spec` command so agents can tighten issue
  specs without hand-editing `.hub/issues/*.md`.
- Add a pure `dashboard_snapshot` backend that groups issue cards into
  `Needs Spec`, `Ready`, `In Progress`, `In Review`, `Completed`, and `Blocked`.
- Include snapshot metadata, change filter, hub project/source metadata,
  diagnostics, summary counts, issue card fields, readiness, done criteria, and
  verification snippets.
- Add `agent-hub dashboard export` to print the snapshot as JSON or write it to
  an explicit output path.
- Cover the backend and CLI behavior with regression tests.

## Out Of Scope

- Do not add mutable dashboard operations.
- Do not implement the visual web UI in this issue.
- Do not parse issue Markdown in browser code.
- Do not add Notion sync, authentication, package managers, or external
  dashboard dependencies.

## Done Criteria

- [ ] `issue set-spec` preserves frontmatter and existing activity logs while
  replacing only bounded spec sections from a Markdown draft.
- [ ] `dashboard_snapshot` returns read-only schema version `3`, generated
  timestamp, hub metadata, columns, diagnostics, summary, and card fields.
- [ ] `dashboard export --change <slug>` filters cards to the selected change
  and refuses missing change slugs.
- [ ] Exporting a dashboard snapshot does not write `.hub/state.yml` or
  `.hub/reports/*`.
- [ ] Focused backend and CLI regression tests pass.

## Verification Strategy

### Regression Target

The deterministic backend and CLI must expose a stable read-only JSON contract
and a spec-tightening command before agents can operate the viewer lifecycle.

### Test Plan

- [ ] Unit: `python3 -m unittest tests.test_file_hub_backend tests.test_agent_hub_v3`
- [ ] Integration: `python3 skills/manage-agent-hub-issues/scripts/agent_hub.py dashboard export --change readonly-kanban-viewer`
- [ ] E2E / Playwright: covered by the downstream viewer smoke issue.
- [ ] Manual / inspection: inspect exported JSON for project metadata, columns,
  readiness, diagnostics, and verification fields.

### First Test

Path: tests/test_file_hub_backend.py::FileHubBackendTests.test_set_issue_spec_preserves_frontmatter_replaces_sections_and_clears_diagnostics
Expected initial result: fails before deterministic set-spec and dashboard snapshot support exists
Reason this proves the regression or requirement: it exercises the issue rewrite contract and ensures vague issues can be made claim-ready through the CLI-owned backend.

### Final Verification

Commands: python3 -m unittest tests.test_file_hub_backend tests.test_agent_hub_v3
Expected result: all focused backend and CLI tests pass

### Untestable Surface

None.

## Assumptions

- The dashboard contract is intentionally file-backed and read-only.
- A static viewer or local server can consume the exported JSON separately.

## Dependencies

- Existing Agent Hub v3 issue parsing, audit diagnostics, readiness, and CLI
  parser helpers.

## Open Questions

None.

## Activity Log

### Dogfood Seed
Created during Agent Hub v3 dogfood bootstrap. Audit correctly reports this issue needs spec tightening, first-test definition, and final verification before claim.

### Spec tightened
Date: 2026-06-28
Agent: Codex orchestrator
Summary: Applied bounded data-contract spec through issue set-spec.
Evidence: .hub/artifacts/hub-viewer-data-api/spec.md

### Claimed for work
Date: 2026-06-28T10:43:23.793502Z
Agent: codex-orchestrator
Claim ID: hub-viewer-data-api-work-20260628
Branch: codex/agent-hub-v3-repo-native
Worktree Path: /Users/jcpinto/git/notion-agent-hub-skills

### Regression-first backend implementation
First failing result: python3 -m unittest tests.test_file_hub_backend tests.test_agent_hub_v3 initially failed for missing set_issue_spec, missing dashboard_snapshot, and missing issue set-spec CLI command.
Final focused result: python3 -m unittest tests.test_file_hub_backend tests.test_agent_hub_v3 passed after backend and CLI implementation.
Touched: skills/manage-agent-hub-issues/lib/file_hub_common.py; skills/manage-agent-hub-issues/scripts/agent_hub.py; tests/test_file_hub_backend.py; tests/test_agent_hub_v3.py.
Output contract: dashboard export now includes read-only mode, generated_at, hub metadata, columns, diagnostics, summary, card readiness, done criteria, and verification snippets.

### Status change: In Progress -> In Review
Date: 2026-06-28
Agent: codex-orchestrator
Implemented: deterministic set-spec command and dashboard export snapshot contract.
Touched: skills/manage-agent-hub-issues/lib/file_hub_common.py; skills/manage-agent-hub-issues/scripts/agent_hub.py; tests/test_file_hub_backend.py; tests/test_agent_hub_v3.py; README.md.
Checks run: python3 -m unittest discover -s tests; python3 evals/run_evals.py; skill metadata validation; git diff --check.
Artifacts: PR https://github.com/jcpinto54/notion-agent-hub-skills/pull/1; commit b93175ac9f7f1e8792c0bc8bd2c6191c724c7bc9.
Risks / skipped checks: none for backend data contract; browser QA belongs to dependent smoke issue.
Reviewer should verify: schema fields, deterministic writes, read-only export, and tests.

### Released claim (submitted)
Date: 2026-06-28T10:46:35.751486Z
Claim ID: hub-viewer-data-api-work-20260628
Mode: submitted
Status: In Review
Owner: Unassigned

### Claimed for review
Date: 2026-06-28T10:49:54.908351Z
Agent: codex-reviewer
Claim ID: hub-viewer-data-api-review-20260628
Branch: codex/agent-hub-v3-repo-native
Worktree Path: /Users/jcpinto/git/notion-agent-hub-skills

### Review verification
Command: python3 -m unittest tests.test_file_hub_backend tests.test_agent_hub_v3
Result: passed, 23 tests OK
Command: python3 skills/manage-agent-hub-issues/scripts/agent_hub.py dashboard export --change readonly-kanban-viewer
Result: passed, schema version 3, read-only mode, correct change filter and columns
Command: python3 skills/manage-agent-hub-issues/scripts/agent_hub.py dashboard export --change definitely-missing-change
Result: failed as expected with No change packet found

### Status change: In Review -> Completed
Date: 2026-06-28
Reviewer: codex-reviewer
Review type: independent backend/data-contract review
Reviewed: issue spec, evidence, tests, backend, CLI, README, PR URL, commit SHA
Verification: focused tests passed; export schema and missing-change refusal verified
Dependencies: none
Follow-ups: dependent UI and smoke issues are unblocked by completion
Risks / skipped checks: live GitHub PR metadata was not fetched by the review subagent; local commit and pushed branch evidence were used
Final outcome: PASS

### Released claim (review-pass)
Date: 2026-06-28T10:49:55.142177Z
Claim ID: hub-viewer-data-api-review-20260628
Mode: review-pass
Status: Completed
Owner: codex-reviewer
