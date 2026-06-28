# Define Read-Only Hub Viewer Data Contract

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
