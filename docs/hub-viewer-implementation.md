# Read-Only Agent Hub Viewer Implementation

The Agent Hub viewer is a dependency-free, static Kanban dashboard for a
repo-native `.hub/` directory. It is intentionally read-only: the backend exports
a JSON snapshot, and the browser renders that snapshot without parsing Markdown,
calling external services, or writing hub state.

## Architecture

The durable source of truth is the target repository's `.hub/` directory.
Issues live in `.hub/issues/*.md`, change packets live under `.hub/changes/`,
and local runtime claim state lives under `.hub/runtime/`.

The implementation boundary is:

- `.hub` source files are read by the Agent Hub backend.
- `dashboard_snapshot(hub_path, change="")` builds an in-memory dashboard model.
- `agent-hub dashboard export` serializes that model as JSON to stdout or an
  explicit output file.
- `skills/list-agent-hub-issues/viewer/` serves static HTML, CSS, and JavaScript.
- The browser fetches `hub-state.json` by default, or a `?data=<url>` override,
  and renders local UI state only.

The viewer has no package manager, build step, external CDN, auth layer, or
hosting integration. A generated `hub-state.json` is local runtime output, not
committed source.

## Dashboard Snapshot Contract

The exported snapshot is schema version `3` and mode `read-only`. It includes:

- generated timestamp and hub metadata such as project, source of truth, and
  dashboard mode
- optional change filter
- six columns: `Needs Spec`, `Ready`, `In Progress`, `In Review`, `Completed`,
  and `Blocked`
- top-level diagnostics and summary counts
- issue cards with id, title, status, type, priority, owner, change, area,
  summary, path, dependencies, blockers, readiness, diagnostics, done criteria,
  and verification snippets

Passing `--change <slug>` creates a change-specific snapshot and refuses missing
change slugs. Omitting the change filter exports a whole-hub snapshot.

## Core Concepts

A hub is the repo-owned `.hub/` workspace that stores project state.

An issue is a Markdown record with frontmatter and structured sections for
scope, criteria, verification, dependencies, ownership, and activity.

A change packet groups related issues under `.hub/changes/<slug>/` and lets the
dashboard focus on one coherent initiative.

A dashboard snapshot is the read-only JSON view of hub state that the browser
can render safely.

Columns are derived from status, readiness, and spec diagnostics. Spec problems
go to `Needs Spec`; ready unstarted work goes to `Ready`; active lifecycle
statuses map to their matching columns; unresolved readiness goes to `Blocked`.

Diagnostics are backend-computed audit findings. They are rendered as health
counts and chips, but the viewer does not create or repair them.

Readiness is backend-computed from issue status, ownership, blockers, claims,
and dependency state. The browser only filters and displays the result.

Evidence and spec snippets come from issue sections such as done criteria,
first test, and final verification. They are included so a reviewer can inspect
the work context without opening every Markdown file.

## Current Capabilities

- Read-only Kanban board for an exported hub snapshot.
- Change, priority, owner, and hide-completed filters.
- Detail panel for the selected issue.
- Audit health and readiness summary metrics.
- Bundled sample fallback when the requested snapshot is unavailable.
- `?data=<url>` override for alternate snapshots.
- Whole-hub snapshots and change-specific snapshots.
- Local static serving with tools such as Python `http.server`.

At a high level, generate a dashboard export for a target repo, write it to the
viewer directory as `hub-state.json` or serve it elsewhere, then open the static
viewer in a browser.

## Explicit Limitations And Non-Goals

- No realtime updates yet.
- No browser-side `.hub` parsing.
- No writes, mutations, status changes, issue creation, claims, or releases.
- No external services dependency or external sync.
- No authentication, hosted service, routing server, or package manager.
- No committed generated dashboard state.
- No persistent browser settings or user-specific dashboard state.
- No live server/watch mode in the current implementation.

## Next Likely Step

The right next enhancement is a local `dashboard serve` command that recomputes
or watches `.hub` and serves `/api/state`. That would keep the current read-only
browser boundary while removing the manual snapshot export step.
