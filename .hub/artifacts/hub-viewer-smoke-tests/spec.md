# Add Regression And Browser Smoke Coverage For Hub Viewer

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
