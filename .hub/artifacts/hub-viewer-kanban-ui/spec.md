# Implement Read-Only Kanban Board UI

## Context

Agent Hub needs a small visual surface for humans and agents to inspect `.hub`
state without opening many Markdown files. The first version should be a
dependency-free, read-only Kanban viewer that consumes the exported dashboard
JSON and makes issue readiness, diagnostics, dependencies, and verification
context scannable.

## Scope

- Add a static viewer under `skills/list-agent-hub-issues/viewer/`.
- Render a top bar with project, source, generated timestamp, and issue count.
- Render a left rail with change selector, audit health counts, readiness
  summary, priority filter, owner filter, and hide-completed toggle.
- Render six Kanban columns: `Needs Spec`, `Ready`, `In Progress`, `In Review`,
  `Completed`, and `Blocked`.
- Render issue cards with id, title, priority, owner, readiness, dependencies,
  blockers/reasons, change, and diagnostic chips.
- Render a selected issue detail tray with summary, done criteria, verification,
  and diagnostics.
- Support `hub-state.json` by default, `?data=<url>` for alternate snapshots,
  and bundled sample-state fallback.
- Document how agents export state and serve the viewer.

## Out Of Scope

- Do not add write controls, status mutation, issue creation, claim actions, or
  browser-side `.hub` parsing.
- Do not add Node, Vite, React, shadcn, package managers, or external CDNs.
- Do not implement authentication, remote hosting, external sync, or live reload.
- Do not persist filters or create user-specific settings.

## Done Criteria

- [ ] The viewer opens as the first screen and shows the actual Kanban board,
  not a landing page.
- [ ] The viewer renders all six columns from dashboard JSON and preserves empty
  states.
- [ ] Filtering by change, priority, owner, and hide-completed updates only local
  read-only UI state.
- [ ] Clicking an issue card updates the detail tray without navigation or
  mutation.
- [ ] Static regression tests prove the viewer files exist, stay dependency-free,
  and ship a sample state matching the dashboard contract.
- [ ] Browser QA verifies desktop rendering, console health, detail interaction,
  and mobile layout without body overflow.

## Verification Strategy

### Regression Target

The static viewer must render the Agent Hub dashboard contract without external
dependencies or browser-side mutation paths.

### Test Plan

- [ ] Unit: `python3 -m unittest tests.test_hub_viewer_static`
- [ ] Integration: `python3 skills/manage-agent-hub-issues/scripts/agent_hub.py dashboard export --change readonly-kanban-viewer --output skills/list-agent-hub-issues/viewer/hub-state.json`
- [ ] E2E / Playwright: in-app browser loads `http://localhost:8765`, verifies
  console health, cards, columns, selected detail update, and mobile layout.
- [ ] Manual / inspection: visually inspect desktop and mobile screenshots for
  overlap, clipping, and read-only controls.

### First Test

Path: tests/test_hub_viewer_static.py::HubViewerStaticTests.test_static_viewer_files_exist_and_stay_dependency_free
Expected initial result: fails before the static viewer files exist
Reason this proves the regression or requirement: it locks the no-build, no-external-dependency delivery model for the viewer UI.

### Final Verification

Commands: python3 -m unittest tests.test_hub_viewer_static tests.test_file_hub_backend tests.test_agent_hub_v3
Expected result: all focused viewer, backend, and CLI tests pass

### Untestable Surface

Visual fidelity is verified with browser screenshots rather than a pixel-perfect
automated assertion.

## Assumptions

- The viewer is served locally with Python `http.server` or another static-file
  server.
- `hub-state.json` is generated and gitignored; committed source includes only
  app files and `hub-state.sample.json`.

## Dependencies

- `hub-viewer-data-api` provides the exported dashboard JSON contract.

## Open Questions

None.
