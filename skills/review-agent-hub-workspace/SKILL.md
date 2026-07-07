---
name: review-agent-hub-workspace
description: Audit Agent Hub workspace organization and issue hygiene. Use when a user asks to review, audit, clean up, diagnose, or report on a Agent Hub board for stale claims, missing dependencies, bad blockers, missing PR metadata, vague issues, or unhealthy In Review items.
---

# Review Agent Hub Workspace

Audit the hub without automatically rewriting dependencies or statuses unless the user explicitly asks for fixes.

## Workflow

1. Use `list-agent-hub-issues` with JSON output for the hub data source.
2. Fetch issue bodies and linked artifacts only for rows that need inspection.
3. Review all non-completed issues for hygiene problems.
4. Produce a report with severity, affected issues, evidence, and recommended fixes.
5. Ask before applying dependency rewrites, claim releases, or status changes.

## Checks

- Missing or incorrect `Depends On` for sequenced work.
- `Blockers` that should be dependencies on hub issues.
- Dependencies that are actually external blockers.
- Stale unexpired or expired claims.
- `In Review` items without review claim, PR URL, commit SHA, linked artifact, or reviewer instructions.
- Repo-changing issues missing `Base Branch`, `Branch`, `Worktree Path`, `Commit SHA`, or `PR URL`.
- `In Progress` issues without active matching claim.
- Vague titles, summaries, or issue bodies missing acceptance criteria and next steps.
- Completed prerequisites that should unblock ready work.
- Downstream `Blocks` relationships that no longer match `Depends On`.

## Report Format

```md
## Agent Hub Workspace Audit

Health:

### Findings
| Severity | Issue | Problem | Evidence | Recommended fix |
|---|---|---|---|---|

### Ready Work

### Stale Claims

### Dependency Fixes To Consider

### In Review Risks

### Recommended Next Actions
```

Do not mark issues completed from a workspace audit. Use `review-agent-hub-issue` for completion decisions.

