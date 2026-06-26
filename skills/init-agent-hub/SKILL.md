---
name: init-agent-hub
description: Create a reusable Agent Hub for a software project, preferably as a repo-native `.hub` directory with optional Notion mirroring, or as a legacy Notion Agent Hub when requested. Use when a user asks to initialize or set up an agent coordination hub, shared task board, AI agent issue tracker, or workspace for multi-agent ownership, dependency, review, and handoff workflows.
---

# Init Agent Hub

Prefer a repo-native `.hub` unless the user explicitly asks for Notion-first setup. The repo-native hub is the canonical store for repo work; Notion is an optional personal dashboard/index.

## Repo-Native Workflow

1. Determine the target repository root.
2. Run:

```bash
python3 <skill-dir>/scripts/init_file_hub.py --repo '<repo-path>' --project-name '<Project Name>'
```

3. Verify these paths exist:
   - `.hub/config.yml`
   - `.hub/issues/`
   - `.hub/decisions/`
   - `.hub/artifacts/`
   - `.hub/.gitignore` containing `runtime/`
4. If the user gave an initial task, create the first issue through `create-agent-hub-issue` or pass `--seed-issue`.
5. Report the `.hub` path and remind the user that Notion mirroring is optional.

## Repo-Native Layout

```text
.hub/
├── config.yml
├── .gitignore
├── issues/
├── decisions/
├── artifacts/
└── runtime/      # gitignored active locks and local state
```

`config.yml` should set `canonical_store: file` and `notion_mirror.enabled: false` by default.

## Legacy Notion Workflow

Create a Notion root page with one inline `Issues / Activities` database only when the user requests Notion-first setup or is maintaining an existing Notion hub. Use Notion MCP for page, database, schema, and view creation. Do not use the direct Notion API scripts for initialization or migrations.

## Workflow

1. Determine the project name from the request or current repository basename.
2. Create a page titled `<Project Name> Agent Hub`.
3. Add the operating guidelines below.
4. Create an inline database titled `Issues / Activities`.
5. Add the base schema and then the self-relation dependency fields.
6. Add the views below.
7. Fetch the page and database to verify the inline database, schema, and views.
8. Return the hub page URL, data source/database URL, and a concise summary.

## Page Content

```md
# Purpose
This page is the coordination hub for <Project Name>. Humans and AI agents use it to claim work, log progress, record blockers, hand off tasks, submit work for review, and keep durable communication attached to specific work items.

# Agent Operating Guidelines
- Use the database below as the living source of truth.
- Write durable issue bodies. A future agent must be able to resume from Notion without chat context.
- Use `Depends On` for prerequisite hub issues and `Blocks` for the reverse relation.
- Use `Blockers` only for external blockers such as credentials, access, unclear decisions, or broken infrastructure.
- Claim work before starting. Do not claim if dependencies are incomplete, blockers exist, owner is assigned, or a claim is active.
- Isolate repo work in a branch/worktree and record `Base Branch`, `Branch`, and `Worktree Path`.
- Move repo-tracked work to `In Review` only after commit, push, PR, `Commit SHA`, and `PR URL` are recorded.
- Claim review before reviewing an `In Review` item.
- Move work to `Completed` only after review passes.
- Send failed reviews back to `In Progress` with required fixes and claim release.

# Activity Log Standard
Every status change must append a task-specific activity-log entry covering scope, evidence, verification, risks, and next step.
```

## Database Schema

Use these properties:

- `Title`: title
- `Status`: select/status values `Not Started`, `In Progress`, `In Review`, `Completed`
- `Owner`: rich text
- `Priority`: select values `P0`, `P1`, `P2`, `P3`
- `Type`: select values `Bug`, `Feature`, `Research`, `Refactor`, `Docs`, `Ops`, `Decision`, `Open Question`, `Handoff`
- `Area`: rich text
- `Summary`: rich text
- `Blockers`: rich text
- `Dependency Notes`: rich text
- `Depends On`: self-relation to prerequisite issues
- `Blocks`: reverse relation
- `Claim ID`: rich text
- `Claimed At`: date
- `Claim Expires At`: date
- `Base Branch`: rich text
- `Branch`: rich text
- `Worktree Path`: rich text
- `Commit SHA`: rich text
- `PR URL`: URL or rich text
- `Related Links`: rich text
- `Created At`: created time
- `Updated At`: last edited time

## Views

- `Board`: board grouped by `Status`; show owner, priority, type, dependencies, blockers, branch, PR URL, and claim expiry.
- `Ready To Start`: table filtered to `Status = Not Started`; show owner, priority, dependencies, blockers, and claim expiry.
- `In Review`: table filtered to `Status = In Review`; show PR URL, commit SHA, owner, claim expiry, and dependencies.
- `Recent Updates`: table sorted by `Updated At` descending.
- `By Type`: board grouped by `Type`.
