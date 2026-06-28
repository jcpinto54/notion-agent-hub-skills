---
id: "hub-viewer-smoke-tests"
title: "Add regression and Playwright smoke coverage for hub viewer"
status: "Completed"
type: "Feature"
priority: "P1"
owner: "codex-reviewer"
area: ""
summary: ""
blockers: ""
dependency_notes: ""
change: "readonly-kanban-viewer"
depends_on: ["hub-viewer-kanban-ui"]
blocks: []
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

The read-only Kanban viewer should be protected by deterministic regression
tests and a browser smoke pass so future changes do not silently break the
dashboard contract, dependency-free delivery, card interaction, or responsive
layout.

## Scope

- Add static regression tests for the viewer source files and sample state.
- Run focused backend, CLI, and viewer tests after implementation.
- Export live dogfood `.hub` state to a local ignored `hub-state.json` file for
  browser smoke.
- Serve the viewer locally and verify desktop load, console health, column/card
  rendering, selected detail interaction, and mobile layout.
- Record durable evidence in the Agent Hub issue activity and artifacts.

## Out Of Scope

- Do not add a permanent Playwright test suite or browser dependency to this
  repository in this issue.
- Do not commit generated `hub-state.json`, screenshots, traces, or server logs.
- Do not test mutable dashboard operations because the first viewer is read-only.
- Do not require Notion, Jira, or network services for smoke coverage.

## Done Criteria

- [ ] `tests/test_hub_viewer_static.py` passes and covers viewer source presence,
  dependency-free HTML/JS, sample schema, columns, and required card fields.
- [ ] Focused backend and CLI tests pass after viewer integration.
- [ ] Full unit discovery and current evals pass.
- [ ] Browser smoke verifies desktop page identity, nonblank DOM, console health,
  rendered cards/columns, detail tray interaction, and mobile no-overflow layout.
- [ ] Evidence is appended to the Agent Hub issue through deterministic commands.

## Verification Strategy

### Regression Target

The viewer implementation must remain testable from a fresh checkout without
installing frontend dependencies, while browser smoke proves the exported state
is actually usable.

### Test Plan

- [ ] Unit: `python3 -m unittest tests.test_hub_viewer_static`
- [ ] Integration: `python3 -m unittest tests.test_hub_viewer_static tests.test_file_hub_backend tests.test_agent_hub_v3`
- [ ] E2E / Playwright: Browser/IAB loads the local static server, clicks an
  issue card, and verifies mobile layout with no body overflow.
- [ ] Manual / inspection: visually inspect screenshots captured under `/tmp`.

### First Test

Path: tests/test_hub_viewer_static.py::HubViewerStaticTests.test_sample_state_matches_dashboard_contract
Expected initial result: fails before the viewer sample state and contract assertions exist
Reason this proves the regression or requirement: it protects the static viewer from drifting away from the backend dashboard export schema.

### Final Verification

Commands: python3 -m unittest discover -s tests && python3 evals/run_evals.py
Expected result: all unit tests and scenario evals pass

### Untestable Surface

Cross-browser compatibility beyond the in-app Chromium browser is not covered in
this first read-only version.

## Assumptions

- Browser smoke screenshots are verification artifacts, not source artifacts.
- The generated local `hub-state.json` remains ignored and can be regenerated.

## Dependencies

- `hub-viewer-data-api` provides the snapshot contract.
- `hub-viewer-kanban-ui` provides the static viewer files.

## Open Questions

None.

## Activity Log

### Dogfood Seed
Created during Agent Hub v3 dogfood bootstrap. This issue should remain dependency-waiting until the UI exists, then own regression and browser smoke coverage for the read-only hub viewer.

### Spec tightened
Date: 2026-06-28
Agent: Codex orchestrator
Summary: Applied bounded regression and browser smoke spec through issue set-spec.
Evidence: .hub/artifacts/hub-viewer-smoke-tests/spec.md

### Claimed for work
Date: 2026-06-28T10:54:00.832493Z
Agent: codex-orchestrator
Claim ID: hub-viewer-smoke-tests-work-20260628
Branch: codex/agent-hub-v3-repo-native
Worktree Path: /Users/jcpinto/git/notion-agent-hub-skills

### Regression and browser smoke verification
Command: python3 -m unittest discover -s tests
Result: passed, 49 tests OK
Command: python3 evals/run_evals.py
Result: passed, 16 scenario evals OK
Command: for skill in skills/*; do python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py ""; done
Result: passed, all 13 skills valid
Command: git diff --check
Result: passed, no whitespace errors
Command: Browser/IAB desktop and mobile smoke against http://localhost:8765
Result: passed, page identity/nonblank/console/cards/detail/mobile no-overflow verified

### Status change: In Progress -> In Review
Date: 2026-06-28
Agent: codex-orchestrator
Implemented: static regression tests plus full unit/eval/skill/browser verification evidence for read-only viewer.
Touched: tests/test_hub_viewer_static.py plus validation reports generated outside tracked source.
Checks run: unit discovery; evals; skill metadata validation; diff check; Browser/IAB desktop/mobile smoke.
Artifacts: PR https://github.com/jcpinto54/notion-agent-hub-skills/pull/1; commit b93175ac9f7f1e8792c0bc8bd2c6191c724c7bc9; screenshots /tmp/agent-hub-viewer-desktop.png and /tmp/agent-hub-viewer-mobile.png.
Risks / skipped checks: no committed Playwright suite; Browser/IAB smoke is durable issue evidence only.
Reviewer should verify: validation evidence covers unit, eval, skill metadata, browser desktop/mobile, and no generated artifacts are committed.

### Released claim (submitted)
Date: 2026-06-28T10:54:01.059918Z
Claim ID: hub-viewer-smoke-tests-work-20260628
Mode: submitted
Status: In Review
Owner: Unassigned

### Claimed for review
Date: 2026-06-28T10:56:46.184619Z
Agent: codex-reviewer
Claim ID: hub-viewer-smoke-tests-review-20260628
Branch: codex/agent-hub-v3-repo-native
Worktree Path: /Users/jcpinto/git/notion-agent-hub-skills

### Review verification
Command: python3 -m unittest tests.test_hub_viewer_static
Result: passed, 2 tests OK
Command: python3 -m unittest tests.test_hub_viewer_static tests.test_file_hub_backend tests.test_agent_hub_v3
Result: passed, 25 tests OK
Command: python3 -m unittest discover -s tests
Result: passed, 49 tests OK
Command: git status --short --ignored
Result: generated hub-state.json is ignored; screenshots/logs are not committed; unrelated docs/resolver-consolidation-plan.md remains untracked

### Status change: In Review -> Completed
Date: 2026-06-28
Reviewer: codex-reviewer
Review type: independent regression and browser evidence review
Reviewed: issue spec, static tests, validation evidence, ignored artifact state, dependency statuses
Verification: static, focused, and full tests passed; durable eval and Browser/IAB evidence present
Dependencies: hub-viewer-data-api and hub-viewer-kanban-ui completed
Follow-ups: none required for read-only v1
Risks / skipped checks: evals were not rerun by the review subagent to avoid report churn; orchestrator already ran them successfully
Final outcome: PASS

### Released claim (review-pass)
Date: 2026-06-28T10:56:46.413065Z
Claim ID: hub-viewer-smoke-tests-review-20260628
Mode: review-pass
Status: Completed
Owner: codex-reviewer

### Evidence correction
Command correction: for skill in skills/*; do python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py "$skill"; done
Result: passed, all 13 skills valid
Reason: the earlier activity line was shell-expanded while being appended and rendered the variable as empty.
