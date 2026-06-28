---
id: "hub-viewer-kanban-ui"
title: "Implement read-only Kanban board UI"
status: "Completed"
type: "Feature"
priority: "P1"
owner: "codex-reviewer"
area: ""
summary: ""
blockers: ""
dependency_notes: ""
change: "readonly-kanban-viewer"
depends_on: ["hub-viewer-data-api"]
blocks: ["hub-viewer-smoke-tests"]
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
- Do not implement authentication, remote hosting, Notion sync, or live reload.
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

## Activity Log

### Dogfood Seed
Created during Agent Hub v3 dogfood bootstrap. Next step is a subagent spec pass that defines the board columns, card fields, no-write boundary, first failing tests, and Playwright verification.

### Spec tightened
Date: 2026-06-28
Agent: Codex orchestrator
Summary: Applied bounded read-only Kanban UI spec through issue set-spec.
Evidence: .hub/artifacts/hub-viewer-kanban-ui/spec.md

### Claimed for work
Date: 2026-06-28T10:50:16.688812Z
Agent: codex-orchestrator
Claim ID: hub-viewer-kanban-ui-work-20260628
Branch: codex/agent-hub-v3-repo-native
Worktree Path: /Users/jcpinto/git/notion-agent-hub-skills

### Regression-first UI implementation
First failing result: python3 -m unittest tests.test_hub_viewer_static failed before viewer files and sample state existed.
Final focused result: python3 -m unittest tests.test_hub_viewer_static tests.test_file_hub_backend tests.test_agent_hub_v3 passed, 25 tests OK.
Browser result: in-app browser loaded http://localhost:8765 with title Agent Hub Viewer, console errors/warnings empty, 3 cards rendered, all six columns present, clicking hub-viewer-kanban-ui updated the detail tray.
Mobile result: viewport 390x780 rendered 3 cards and six columns with body scrollWidth equal to clientWidth; board overflow-x is auto.
Screenshots: /tmp/agent-hub-viewer-desktop.png and /tmp/agent-hub-viewer-mobile.png.
Touched: skills/list-agent-hub-issues/viewer/*; tests/test_hub_viewer_static.py; skills/list-agent-hub-issues/SKILL.md; README.md.

### Status change: In Progress -> In Review
Date: 2026-06-28
Agent: codex-orchestrator
Implemented: dependency-free read-only static Kanban viewer consuming dashboard JSON.
Touched: skills/list-agent-hub-issues/viewer/index.html; styles.css; app.js; hub-state.sample.json; .gitignore; tests/test_hub_viewer_static.py; skills/list-agent-hub-issues/SKILL.md; README.md.
Checks run: python3 -m unittest discover -s tests; python3 evals/run_evals.py; skill metadata validation; git diff --check; Browser/IAB desktop and mobile smoke.
Artifacts: PR https://github.com/jcpinto54/notion-agent-hub-skills/pull/1; commit b93175ac9f7f1e8792c0bc8bd2c6191c724c7bc9.
Risks / skipped checks: no permanent Playwright suite added; browser smoke was manual through Browser/IAB.
Reviewer should verify: read-only controls, schema consumption, cards/columns, detail tray, responsive behavior, and dependency-free source.

### Released claim (submitted)
Date: 2026-06-28T10:50:16.902617Z
Claim ID: hub-viewer-kanban-ui-work-20260628
Mode: submitted
Status: In Review
Owner: Unassigned

### Claimed for review
Date: 2026-06-28T10:53:40.107136Z
Agent: codex-reviewer
Claim ID: hub-viewer-kanban-ui-review-20260628
Branch: codex/agent-hub-v3-repo-native
Worktree Path: /Users/jcpinto/git/notion-agent-hub-skills

### Review verification
Command: python3 -m unittest tests.test_hub_viewer_static
Result: passed, 2 tests OK
Command: Browser/IAB desktop smoke at http://localhost:8765
Result: passed, title Agent Hub Viewer, console clean, 3 cards, six columns, detail tray updates on card click
Command: Browser/IAB mobile smoke at 390x780
Result: passed, 3 cards, six columns, body scrollWidth equals clientWidth, board overflow-x auto
Review source inspection: no external CDN, write controls, or persistence paths found

### Status change: In Review -> Completed
Date: 2026-06-28
Reviewer: codex-reviewer
Review type: independent static viewer and browser QA review
Reviewed: issue spec, viewer source, static tests, README/list skill docs, browser screenshots
Verification: static tests passed; read-only source and browser behavior verified
Dependencies: hub-viewer-data-api completed
Follow-ups: permanent Playwright suite deliberately deferred to future version
Risks / skipped checks: no cross-browser matrix; Browser/IAB Chromium smoke only
Final outcome: PASS

### Released claim (review-pass)
Date: 2026-06-28T10:53:40.334308Z
Claim ID: hub-viewer-kanban-ui-review-20260628
Mode: review-pass
Status: Completed
Owner: codex-reviewer
