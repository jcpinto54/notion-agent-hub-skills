---
name: manage-agent-hub-issues
description: Router and shared standards for Notion Agent Hub issue workflows. Use when a user asks to create, list, claim, update, release, submit, review, audit, or coordinate Agent Hub issues, or when the right specialized Agent Hub skill is unclear.
---

# Manage Agent Hub Issues

Use this skill as the coordination router. Prefer the specialized skill that matches the requested action:

- Create hub: `init-agent-hub`
- Create issue, decision, open question, follow-up, or handoff: `create-agent-hub-issue`
- List or find ready work: `list-agent-hub-issues`
- Claim work: `claim-agent-hub-issue`
- Progress, block, handoff, release, or submit work for review: `update-agent-hub-issue`
- Review one `In Review` issue: `review-agent-hub-issue`
- Audit workspace hygiene: `review-agent-hub-workspace`
- Configure Agent Hub token and data source: `setup-agent-hub`

## Core Rules

- Treat the Notion issue page body as the durable work record. Chat context is not durable.
- Use dependencies before claiming: `Depends On` is for prerequisite hub issues; `Blockers` is for external blockers.
- Do not claim work unless dependencies are completed, blockers are empty, owner is empty or `Unassigned`, and no unexpired claim exists.
- Use worktree isolation for repo-changing issues. Record `Base Branch`, `Branch`, and `Worktree Path` when repo work is expected.
- Do not move repo-tracked work to `In Review` without a commit, push, normal PR, `Commit SHA`, and `PR URL`.
- Completion is a review decision. Use `review-agent-hub-issue` for `In Review -> Completed`.
- Release stale, abandoned, submitted, passed, or failed claims through the claim script rather than manually clearing claim fields.

## Shared Schema

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
