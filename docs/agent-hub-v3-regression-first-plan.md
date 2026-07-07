# Agent Hub v3 Regression-First Implementation Plan

This file is the durable handoff for a fresh agent. Assume the fresh agent has no
conversation context beyond this document and the repository contents.

## Prime Directive

Work on branch:

```bash
codex/agent-hub-v3-repo-native
```

The main agent is an orchestrator, not an executor. Keep the main context clean.
All substantive work must be delegated to bounded subagents, including:

- research
- implementation
- testing
- audit
- analysis
- review
- documentation drafting
- skill critique
- QA and browser verification

The orchestrator may directly do only lightweight coordination:

- inspect enough repository state to route work
- create short handoffs
- run deterministic commands
- collect subagent outputs
- update durable files with the final agreed result
- run final validation commands

If a task requires sustained reasoning, code changes, review, or research, spawn
a subagent. Do not let the main context become the place where the real work is
performed.

## Goal

Move Agent Hub from the current v2 hybrid framework to Agent Hub v3:

- `.hub/` is the only source of truth for repo work.
- external services are not part of the recommended workflow.
- Deterministic scripts own all `.hub` mutations.
- Skills become thin routers, policy guides, and references.
- Implementation work is TDD-first and regression-first.
- Agent behavior is evaluated with repeatable local evals.
- A simple read-only web dashboard may be added later, but only after schemas,
  state, reports, and deterministic commands stabilize.

No v3 behavior may be implemented without a failing deterministic test, fixture
eval, or agentic scenario eval first.

## Current Repository Snapshot

Repository:

```text
/Users/jcpinto/git/agent-hub-skills
```

Current v2 characteristics:

- `README.md` describes Agent Hub v2 as hybrid and repo-native by default.
- Existing `.hub` target layout currently includes:
  - `.hub/config.yml`
  - `.hub/issues/`
  - `.hub/decisions/`
  - `.hub/artifacts/`
  - `.hub/runtime/`
- `skills/manage-agent-hub-issues/lib/file_hub_common.py` contains the shared
  file backend helpers.
- Existing scripts support init, create issue, list, claim, and append activity.
- Existing tests include `tests/test_file_hub_backend.py` plus file-backed
  list and claim tests.
- `docs/resolver-consolidation-plan.md` already proposes making
  `manage-agent-hub-issues` the primary resolver and reducing visible leaf
  skill clutter.

Do not assume any hidden conversation context. Re-read the repository before
editing.

## Non-Negotiable Working Rules

1. Create or switch to `codex/agent-hub-v3-repo-native` before implementing.
2. Preserve user changes. Do not revert unrelated files.
3. Use deterministic scripts for `.hub` writes whenever a script exists.
4. Do not manually edit `.hub` structure from skill instructions when a helper
   command can do it.
5. Add tests and eval fixtures before implementing new v3 behavior.
6. Confirm new tests/evals fail for missing functionality before coding.
7. Keep skills lean. Put detailed workflows in references loaded only when
   needed.
8. Delegate substantive work to subagents.
9. Run the full validation suite before finalizing.

## Target `.hub` Layout

Agent Hub v3 target layout:

```text
.hub/
  config.yml
  state.yml
  .gitignore

  project/
    principles.md
    product.md
    tech.md
    structure.md
    standards-index.md
    delegation.md

  changes/
    <change-slug>/
      change.yml
      proposal.md
      shape.md
      design.md
      tasks.md
      checklist.md
      evidence.md
      review.md

  issues/
    <issue-id>.md

  decisions/
    <yyyy-mm-dd-slug>.md

  reports/
    latest-audit.json
    latest-audit.md
    latest-analysis.json
    latest-analysis.md

  artifacts/
    <issue-id>/
      <small-evidence-files>

  runtime/
    claims.json
```

`.hub/.gitignore` must keep runtime local:

```gitignore
runtime/
```

## Mental Model

### `project/`

Stable repo guidance. These files are read selectively by agents.

- `principles.md`: quality bar, TDD policy, review rules, security posture,
  non-negotiables, and tradeoffs.
- `product.md`: purpose, users, outcomes, non-goals, success signals.
- `tech.md`: stack, package manager, test/build commands, environment notes.
- `structure.md`: repo map, boundaries, entry points, extension points, areas
  to avoid.
- `standards-index.md`: index of deeper standards and when to read them.
- `delegation.md`: subagent-first operating policy, handoff contract, evidence
  requirements, and stop conditions.

### `changes/`

Change packets for larger initiatives. A change packet explains the parent
story: why it exists, what it changes, design direction, task breakdown,
evidence, and review.

Small work may skip a change packet and use only one issue. Larger or risky work
should have a change packet linked to one or more issues.

### `issues/`

Claimable execution units. One issue should be small enough for one subagent to
claim, implement, verify, and submit for independent review.

### `reports/`

Generated audit and analysis output. Humans, the dashboard, and orchestrators
read these files to decide next actions.

### `artifacts/`

Compact evidence only: command outputs, summaries, screenshots, logs, benchmark
snippets, links, and review attachments. Avoid committing large binaries by
default.

### `runtime/`

Gitignored local live state, especially claim locks.

## Deterministic Write Policy

Skills are not the write engine. Scripts are the write engine.

The model may generate bounded Markdown content, for example:

- proposal text
- design notes
- done criteria
- verification strategy
- review findings
- research summary

But deterministic scripts must own:

- layout initialization
- frontmatter parsing and writing
- dependency add/remove
- issue/change linking
- status transitions
- claim acquire/check/renew/release
- activity appends
- evidence appends
- report generation
- state refresh
- archive moves

This rule exists to reduce context pollution, avoid malformed YAML/Markdown, and
make behavior regression-testable.

## Target CLI Surface

Create or consolidate an `agent-hub` CLI backed by shared Python library code.
It may initially wrap existing scripts, but the public behavior should converge
around one command surface.

Required commands:

```bash
agent-hub init
agent-hub state refresh

agent-hub change create
agent-hub change link-issue
agent-hub change archive

agent-hub issue create
agent-hub issue add-dependency
agent-hub issue remove-dependency
agent-hub issue set-status
agent-hub issue append-activity
agent-hub issue add-evidence

agent-hub claim acquire
agent-hub claim check
agent-hub claim renew
agent-hub claim release

agent-hub audit hub
agent-hub audit issue <issue-id>
agent-hub analyze change <change-slug>
```

Recommended implementation path:

1. Add shared library functions under `skills/manage-agent-hub-issues/lib/`.
2. Add a CLI script such as
   `skills/manage-agent-hub-issues/scripts/agent_hub.py`.
3. Keep older scripts working by delegating to the shared library or CLI.
4. Update skills to call the deterministic command surface.

## Target `.hub/config.yml`

Default v3 config shape:

```yaml
version: 3
source_of_truth: file
project: "Project Name"

cli:
  strict_writes: true
  preserve_unknown_frontmatter: true

agents:
  enabled: false
  runner: codex
  command: codex
  require_subagent_for_tasks: true

audit:
  tdd_required_for_implementation: true
  e2e_required_for_ui: true
  stale_claim_minutes: 120

dashboard:
  enabled: false
  mode: read-only
```

Agent invocation from scripts is optional for the first v3 implementation. The
first pass should define the config and prompt assembly contract, but should not
require scripts to launch agents.

## Issue File Shape

Issue files remain Markdown with frontmatter. Add `change` and stronger
verification sections.

```md
---
id: issue-id
title: "Issue title"
status: Not Started
type: Feature
priority: P2
owner: Unassigned
change: change-slug
depends_on: []
blocks: []
claim: {}
base_branch: ""
branch: ""
worktree_path: ""
commit_sha: ""
pr_url: ""
related_links: ""
---

## Context

## Scope

## Out Of Scope

## Done Criteria

- [ ] Observable criterion

## Verification Strategy

### Regression Target

### Test Plan

- [ ] Unit:
- [ ] Integration:
- [ ] E2E / Playwright:
- [ ] Manual / inspection:

### First Test

Path:
Expected initial result:
Reason this proves the regression or requirement:

### Final Verification

Commands:
Expected result:

### Untestable Surface

## Assumptions

## Dependencies

## Open Questions

## Activity Log
```

Implementation issues must not be considered ready unless the verification
strategy is present or an explicit automated-test exception is recorded.

## Change Packet File Shapes

`change.yml`:

```yaml
id: change-slug
title: "Human title"
status: Draft
priority: P2
owner: Unassigned

issues:
  - issue-id-1
  - issue-id-2

depends_on: []
blocks: []

created_at: "2026-06-26T00:00:00Z"
updated_at: "2026-06-26T00:00:00Z"
```

`proposal.md`:

```md
# Proposal

## Why

## What Changes

## Out Of Scope

## Success Criteria

## Risks
```

`shape.md`:

```md
# Shape

## User Intent

## Constraints

## Options Considered

## Decisions

## References

## Open Questions
```

`design.md`:

```md
# Design

## Approach

## Data Flow

## Interfaces

## Migration Notes

## Failure Modes

## Alternatives Rejected
```

`tasks.md`:

```md
# Tasks

## Dependency Graph

## Issues

- [ ] issue-id-1 - Short title
- [ ] issue-id-2 - Short title

## Parallelization Notes

## Blockers
```

`checklist.md`:

```md
# Checklist

## Spec Quality

- [ ] Scope is clear
- [ ] Out of scope is explicit
- [ ] Done criteria are observable
- [ ] Verification strategy exists

## TDD Readiness

- [ ] First regression test is identified
- [ ] Expected initial failure is defined
- [ ] Final verification commands are listed
- [ ] E2E smoke check is included or explicitly waived

## Implementation Readiness

- [ ] Issues are independently claimable
- [ ] Dependencies are explicit
- [ ] Risky areas have review notes
```

`evidence.md`:

```md
# Evidence

## Commits

## Pull Requests

## Test Runs

## E2E / Playwright Runs

## Screenshots Or Logs

## Notes
```

`review.md`:

```md
# Review

## Review Status

## Findings

## Verification Performed

## Regression Coverage

## Residual Risks

## Decision
```

## Project Guidance Template Requirements

`principles.md` must include:

```md
# Principles

## Quality Bar

## TDD And Regression Policy

## Review Rules

## Security And Safety

## Non-Negotiables

## Tradeoffs
```

`delegation.md` must include:

```md
# Delegation Rules

## Core Rule

The main agent is an orchestrator, not an executor.

## Main Agent Responsibilities

## Subagent Responsibilities

## Handoff Contract

## Evidence Requirements

## Stop Conditions

## Exceptions
```

## TDD And Regression Policy

Implementation work must define verification before coding.

For bug fixes and behavior changes, agents must add or update a regression test
before implementation. The activity log must record the initial failing result,
or explain why a failing automated test was not practical.

For user-facing workflows, final verification should include Playwright or an
equivalent browser automation smoke check when feasible.

Review cannot pass unless evidence includes:

- done criteria coverage
- test path or explicit exception
- focused command output
- final verification result
- PR and commit evidence for repo-changing work

## Audit And Analyze Semantics

Implement these scopes separately.

### `agent-hub audit hub`

Checks workspace health:

- missing required files
- invalid frontmatter
- stale claims
- dangling dependencies
- orphaned issues
- blocked work
- missing evidence
- review-ready work without PR/commit/test data
- missing TDD strategy
- malformed runtime claims

Writes:

```text
.hub/reports/latest-audit.json
.hub/reports/latest-audit.md
```

### `agent-hub audit issue <issue-id>`

Checks one issue:

- clear scope
- explicit out-of-scope
- observable done criteria
- verification strategy
- first-test evidence or explicit exception
- dependency validity
- claim state
- implementation evidence
- review readiness

### `agent-hub analyze change <change-slug>`

Checks change packet consistency:

- proposal/design/tasks alignment
- task-to-issue coverage
- issue-to-change links
- independent claimability
- checklist completion
- evidence coverage
- review risks

Writes:

```text
.hub/reports/latest-analysis.json
.hub/reports/latest-analysis.md
```

## Expected Diagnostic Style

Diagnostics should be machine-readable and stable enough for evals.

Recommended JSON object:

```json
{
  "code": "implementation_missing_first_test",
  "severity": "error",
  "target": ".hub/issues/add-dashboard.md",
  "message": "Implementation issue has no First Test recorded.",
  "recommendation": "Add a regression test path and expected initial failing result before claim."
}
```

Use severity values:

- `error`: blocks claim, review, or completion
- `warning`: does not block but should be fixed
- `info`: advisory

## Regression-First Implementation Order

Follow this sequence. Do not skip the failing-test step.

### Phase 0: Orchestrator Setup

Main agent:

1. Confirm branch.
2. Read this file.
3. Read only the minimum current repo files needed to plan handoffs:
   - `README.md`
   - `skills/manage-agent-hub-issues/SKILL.md`
   - `skills/manage-agent-hub-issues/lib/file_hub_common.py`
   - existing tests under `tests/`
4. Spawn a test-planning subagent.

### Phase 1: Failing Deterministic Tests

Spawn a subagent to add tests first.

Required test coverage:

- v3 hub layout initialization
- guidance template creation
- `state.yml` creation and refresh
- change packet creation
- issue linking to change packet
- issue dependency add/remove
- strict status transitions
- activity append-only behavior
- evidence append-only behavior
- claim lifecycle
- audit hub diagnostics
- audit issue diagnostics
- analyze change diagnostics

The subagent must run the tests and report which new tests fail because v3
functionality does not exist yet.

### Phase 2: Failing Fixture Evals

Spawn a subagent to create eval fixtures and expected diagnostics.

Required fixture directories:

```text
evals/
  fixtures/
    valid-lite-hub/
    missing-guidance/
    stale-claim/
    vague-issue/
    missing-tdd/
    broken-change-packet/
    review-ready-no-evidence/
    dangling-dependency/
    malformed-frontmatter/
  expected/
  scenarios/
  reports/
```

Expected outputs should use exact or subset diagnostic matching.

The eval runner should be local and simple at first. Do not add Promptfoo,
Inspect, or another external framework unless the user explicitly requests it.

### Phase 3: Failing Agentic Scenario Evals

Spawn a subagent to create scenario evals for skill behavior.

Required scenarios:

- resolver routes mutations to deterministic commands
- resolver refuses to manually edit `.hub` structure
- resolver delegates substantive tasks to subagents
- implementation handoff includes TDD requirements
- subagent handoff includes required files, scope, out-of-scope, expected output,
  evidence requirements, and stop conditions
- review gate rejects missing regression evidence
- audit/analyze recommendations are stable and actionable

Recommended scenario file shape:

```yaml
id: add_dependency
prompt: "Make issue api-client depend on auth-contract."
expected:
  command: "agent-hub issue add-dependency"
  args:
    issue: "api-client"
    depends_on: "auth-contract"
must_not:
  - "manual_edit_issue_file"
  - "rewrite_full_markdown"
```

### Phase 4: Deterministic Implementation

Only after new tests and evals fail for missing v3 behavior, spawn bounded
implementation subagents.

Suggested implementation subagents:

1. `v3-layout-init`
   - Implements v3 layout and guidance templates.
   - Makes init tests pass.
2. `v3-change-issue-model`
   - Implements change packets, issue links, dependency commands.
   - Makes change and issue tests pass.
3. `v3-state-claims-evidence`
   - Implements state refresh, claims, activity, evidence append behavior.
   - Makes state and lifecycle tests pass.
4. `v3-audit-analyze`
   - Implements audit hub, audit issue, analyze change.
   - Makes fixture diagnostics pass.
5. `v3-cli-compat`
   - Builds or consolidates the `agent-hub` CLI and keeps old scripts working
     or clearly deprecated.

Each subagent must:

- read this file
- read only relevant code and tests
- make a focused change
- run focused tests
- report exact files changed and commands run

### Phase 5: Skill Updates

Spawn a skill-update subagent.

Required skill behavior:

- `manage-agent-hub-issues` becomes the primary visible resolver.
- Detailed workflows move into `skills/manage-agent-hub-issues/references/`.
- Skill body stays lean.
- Resolver policy says:
  - `.hub` is canonical
  - external services are outside the repo-native source of truth
  - deterministic scripts own `.hub` mutations
  - main agent is orchestrator-only
  - subagents perform substantive work
  - implementation is TDD-first
  - audit/analyze gates readiness and review quality
- Leaf skills either call scripts or defer to resolver references.
- Skill metadata remains valid.

### Phase 6: Independent Review

Spawn at least two review subagents:

1. Deterministic reviewer:
   - Reviews CLI/library behavior and tests.
   - Looks for unsafe writes, malformed frontmatter, broken compatibility,
     missing validations, and weak diagnostics.
2. Skill/eval reviewer:
   - Reviews skills and scenario evals.
   - Checks that skills do not encourage manual `.hub` edits.
   - Checks subagent-first and TDD-first policies are explicit.

Review findings must be fixed or explicitly documented as residual risks.

### Phase 7: Final Validation

Run:

```bash
python3 -m unittest discover -s tests
python3 <eval-runner>
for skill in skills/*; do
  python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py "$skill"
done
```

If `pytest` is the repo standard by then, run that too. Current README uses:

```bash
python3 -m unittest discover -s tests
```

## Subagent Handoff Contract

Every subagent prompt must include:

- task objective
- scope
- out-of-scope
- required files to read
- permitted files to edit
- required commands to run
- evidence requirements
- expected output format
- stop conditions

Implementation handoffs must also include:

- failing tests or evals to satisfy
- TDD policy
- regression evidence requirements
- final verification commands

Generic handoff skeleton:

```text
You are a bounded Agent Hub v3 subagent.

Read first:
- docs/agent-hub-v3-regression-first-plan.md
- <specific test files>
- <specific implementation files>

Objective:
<one sentence>

Scope:
<specific allowed changes>

Out of scope:
<specific forbidden changes>

Required behavior:
<exact behavior/tests/evals>

Validation:
Run:
<commands>

Evidence to return:
- files changed
- commands run
- failing-before or passing-after evidence
- blockers
- residual risks

Stop if:
- requirements conflict
- unrelated dirty files block safe edits
- tests fail for reasons outside your scope
```

## Eval Strategy

Use three grading styles.

### Exact Match

Use for stable script JSON where ordering and fields are intentionally fixed.

### Subset Match

Use for diagnostics because additional warnings may be added over time.

### Rubric Match

Use for agentic behavior:

- Did the resolver choose the deterministic command?
- Did it avoid manual file rewrites?
- Did it delegate substantive work?
- Did the handoff include required files?
- Did it include TDD and evidence requirements?
- Did review reject missing regression evidence?

## Completion Criteria

The work is complete only when:

- v3 layout is initialized by deterministic command
- deterministic CLI supports required v3 operations
- `.hub` writes are script-managed
- audit/analyze generate JSON and Markdown reports
- TDD-first policy is encoded in templates and audits
- subagent-first policy is encoded in templates and skills
- external services are removed from the recommended workflow
- deterministic tests pass
- fixture evals pass
- agentic scenario evals pass
- skill validation passes
- README or docs explain the v3 model

## Important Non-Goals For First v3 Pass

- Do not build the dashboard until schemas and reports stabilize.
- Do not require script-driven agent invocation yet.
- Do not add external eval frameworks yet.
- Do not commit large binary artifacts by default.
- Do not remove compatibility behavior unless replacement docs and tests are ready, or the user explicitly approves removal.

## Final Report Expected From Implementing Agent

The final response after implementation should include:

- branch name
- summary of v3 behavior implemented
- tests and evals added
- validation commands run
- any removed-backend status
- residual risks
- files changed at a high level

Keep the report concise. The durable details should live in tests, evals, and
docs, not in chat.
