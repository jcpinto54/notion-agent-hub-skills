# Agent Hub v3 Workflows

Use these workflows after loading `v3-router-policy.md` when the user asks for a
specific Agent Hub action.

## Init

1. Identify the target repo and project name.
2. Prefer `agent-hub init --repo <repo> --project-name <name>`.
3. Verify the v3 layout exists: `.hub/config.yml`, `.hub/state.yml`,
   `.hub/project/`, `.hub/changes/`, `.hub/issues/`, `.hub/decisions/`,
   `.hub/reports/`, `.hub/artifacts/`, and `.hub/.gitignore`.
4. Run `agent-hub state refresh` when available.
5. If the v3 CLI is unavailable, use the current init compatibility script only
   for the layout it supports and report any missing v3 paths as assumptions.
6. Use legacy Notion setup only when the user explicitly asks for an existing
   Notion hub or credential setup.

## Create Or Link Work

Use deterministic commands for every structure or frontmatter mutation:

```bash
agent-hub change create
agent-hub issue create
agent-hub change link-issue
agent-hub change archive
agent-hub issue add-dependency
agent-hub issue remove-dependency
```

For implementation issues, ensure the body has:

- context
- scope
- out of scope
- observable done criteria
- verification strategy
- regression target or explicit automated-test exception
- first test path, expected initial failure, and final verification commands
- dependencies and open questions

If the request is vague, run `spec-agent-hub-issue` before creating claimable
work. If the work has multiple independent done states, split it into child
issues and link dependencies.

## Claim

Use:

```bash
agent-hub claim acquire
agent-hub claim check
agent-hub claim renew
agent-hub claim release
```

Claim only ready work. Refuse or send back issues with unresolved dependencies,
external blockers, unclear verification strategy, active claims, or missing
regression plan.

For repo-changing work, the successful claim must be followed by branch/worktree
setup before files are edited. Record base branch, branch, and worktree path
through the deterministic command surface.

## Work And Update

Delegate substantive implementation, research, QA, audit, or docs drafting to a
bounded subagent. The handoff must include required files, permitted edits,
validation, evidence, and stop conditions.

For implementation:

1. Create or identify the failing regression test/eval first.
2. Run it and capture the initial failing result.
3. Implement the smallest scoped fix.
4. Run focused verification, then broader checks appropriate to risk.
5. Append activity and evidence with deterministic commands:

```bash
agent-hub issue append-activity
agent-hub issue add-evidence
```

Do not rewrite the full issue file to record progress. Append through the command
surface or a compatibility append script.

## Submit For Review

Before `In Progress -> In Review`, require:

- completed done criteria
- final verification result
- commit SHA
- pushed branch
- PR URL
- regression evidence or explicit exception
- risks and skipped checks

Use:

```bash
agent-hub issue set-status
agent-hub claim release
```

Prefer release mode semantics that atomically clear the work claim and preserve
review evidence.

## Review

Claim review first. Review the durable issue/change record, PR, commit, linked
artifacts, and command output rather than chat memory.

Pass only when evidence covers:

- done criteria
- scope and out-of-scope boundaries
- dependency state
- regression/TDD requirement or exception
- final verification
- repo metadata for repo-changing work

Fail or send back when evidence is missing, criteria are unmet, dependencies are
unresolved, or skipped checks are not justified. Use deterministic commands to
append review findings, set status, and release the review claim.

## Merged PR Sync

If an implementation PR is merged outside the Agent Hub review flow while its
issue remains `In Review`, sync GitHub merge state before dependency analysis:

```bash
agent-hub state sync-merged-prs --change <change-slug>
```

The command inspects `In Review` issues with GitHub `PR URL` metadata. It uses
`gh pr view` first and falls back to `GITHUB_TOKEN` or `GH_TOKEN` for the GitHub
REST API. Only confirmed merged PRs move to `Completed`; open, closed-unmerged,
inaccessible, malformed, or missing PR URLs are left unchanged and reported as
diagnostics.

## Audit And Analyze

Use audit for workspace and issue health:

```bash
agent-hub audit hub
agent-hub audit issue <issue-id>
```

Audit should flag missing required files, malformed frontmatter, stale claims,
dangling dependencies, vague issues, blocked work, missing evidence, review-ready
work without PR/commit/test data, missing TDD strategy, and malformed runtime
claims. Reports go to `.hub/reports/latest-audit.json` and
`.hub/reports/latest-audit.md`.

Use analyze for change packets:

```bash
agent-hub analyze change <change-slug>
```

Analyze should check proposal/design/tasks alignment, task-to-issue coverage,
issue-to-change links, independent claimability, checklist completion, evidence
coverage, and review risks. Reports go to `.hub/reports/latest-analysis.json`
and `.hub/reports/latest-analysis.md`.

Diagnostics should have stable codes, severities, targets, messages, and
recommendations so tests and evals can match them.

## Iterate And Delegate

Use `iterate-agent-hub-work` for one subagent-first iteration.

1. List ready work through the deterministic listing/readiness command.
2. Cap the batch, normally at 10 or fewer issues.
3. Spawn one bounded subagent per issue.
4. Each subagent claims its own issue. The parent does not claim on their behalf.
5. Do not reinterpret readiness after the command returns rows; send unclear work
   back to spec/audit instead.
6. Return spawned agent IDs, issue IDs, and expected evidence. Do not wait unless
   the user explicitly asked for a synchronous iteration.
