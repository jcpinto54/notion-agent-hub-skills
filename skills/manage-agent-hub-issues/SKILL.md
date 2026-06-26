---
name: manage-agent-hub-issues
description: Router and shared standards for Agent Hub issue workflows, including repo-native `.hub` orchestration and legacy Notion hubs. Use when a user asks to initialize, create, plan, spec, classify, list, claim, update, release, submit, review, audit, iterate, or coordinate Agent Hub issues, or when the right specialized Agent Hub skill is unclear.
---

# Manage Agent Hub Issues

Use this skill as the coordination router. For repo work, treat `.hub/` in the target repository as the canonical durable source of truth. Use Notion only as an optional personal dashboard or legacy backend unless the user explicitly asks for Notion-first coordination.

Prefer the specialized workflow that matches the requested action:

- Create repo-native or Notion hub: `init-agent-hub`
- Create issue, decision, open question, follow-up, or handoff: `create-agent-hub-issue`
- Tighten vague or oversized work: `spec-agent-hub-issue`
- List or find ready work: `list-agent-hub-issues`
- Spawn subagents for one ready-work iteration: `iterate-agent-hub-work`
- Claim work: `claim-agent-hub-issue`
- Progress, block, handoff, release, or submit work for review: `update-agent-hub-issue`
- Review one `In Review` issue: `review-agent-hub-issue`
- Audit workspace hygiene: `review-agent-hub-workspace`
- Configure Agent Hub token and data source: `setup-agent-hub`

## Backend Rule

- Use `.hub/config.yml` when it exists. The helper scripts default to `--backend auto`, which selects `file` before Notion.
- Use `--backend file` for repo-native hubs and `--backend notion` for legacy Notion hubs.
- Read `.hub/issues/*.md` before relying on Notion summaries. Notion mirrors may be stale or intentionally partial.
- Store durable specs, activity logs, review notes, PR evidence, and compact artifacts in `.hub`.
- Keep `.hub/runtime/` gitignored. It is for live local locks such as active claim metadata.

## Core Rules

- Treat the `.hub` issue file or legacy Notion issue page body as the durable work record. Chat context is not durable.
- Use dependencies before claiming: `Depends On` is for prerequisite hub issues; `Blockers` is for external blockers.
- Do not claim work unless dependencies are completed, blockers are empty, owner is empty or `Unassigned`, and no unexpired claim exists.
- Use worktree isolation for repo-changing issues. Record `Base Branch`, `Branch`, and `Worktree Path` when repo work is expected.
- Do not move repo-tracked work to `In Review` without a commit, push, normal PR, `Commit SHA`, and `PR URL`.
- Completion is a review decision. Use `review-agent-hub-issue` for `In Review -> Completed`.
- Release stale, abandoned, submitted, passed, or failed claims through the claim script rather than manually clearing claim fields.

## Repo-Native Schema

Repo-native issues live at `.hub/issues/<issue-id>.md` with YAML frontmatter and a Markdown body. Use these frontmatter fields:

- `id`, `title`, `status`, `type`, `priority`, `owner`
- `area`, `summary`, `blockers`, `dependency_notes`
- `depends_on`, `blocks`
- `claim`
- `base_branch`, `branch`, `worktree_path`
- `commit_sha`, `pr_url`, `related_links`, `notion_url`

The body should keep context, scope, done criteria, verification steps, assumptions, dependencies, open questions, and append-only activity log entries.

## Legacy Notion Schema

Use these properties when present:

- `Status`: `Not Started`, `In Progress`, `In Review`, `Completed`
- `Owner`: free text; use `Unassigned` when available
- `Priority`: `P0`, `P1`, `P2`, `P3`
- `Type`: `Bug`, `Feature`, `Research`, `Refactor`, `Docs`, `Ops`, `Decision`, `Open Question`, `Handoff`
- `Depends On`, `Blocks`, `Dependency Notes`
- `Claim ID`, `Claimed At`, `Claim Expires At`
- `Base Branch`, `Branch`, `Worktree Path`, `Commit SHA`, `PR URL`
- `Summary`, `Blockers`, `Related Links`, `Created At`, `Updated At`

If a legacy hub lacks claim or repo metadata fields, use `init-agent-hub` guidance to add them with Notion MCP before relying on direct scripts.
