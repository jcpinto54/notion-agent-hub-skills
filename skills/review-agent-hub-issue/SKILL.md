---
name: review-agent-hub-issue
description: Independent review gate for Agent Hub issues before completion. Use when a user asks to review, verify, approve, complete, close, accept, reject, send back, or quality-check an Agent Hub issue in In Review, including code, docs, QA, research, decisions, handoffs, and PR-backed work.
---

# Review Agent Hub Issue

Review durable evidence, not chat memory. Before reviewing, claim the issue for review with `claim-agent-hub-issue`.

## Workflow

1. Locate the issue by link, title, or recent listing.
2. Claim review:

```bash
python3 <repo>/skills/manage-agent-hub-issues/scripts/agent_hub.py claim acquire \
  --purpose review \
  --issue '<issue>' \
  --owner '<reviewer-name>'
```

3. Fetch the full issue body, properties, dependencies, PR, commit, checks, and linked artifacts.
4. Verify completion criteria, evidence, skipped checks, risks, and follow-ups.
5. Decide pass, fail, or abandon.
6. Append the review entry through `agent-hub issue append-activity` or `agent-hub issue add-evidence` for repo-native hubs. Use Notion MCP only for legacy Notion hubs.
7. Release the review claim with the matching mode through the deterministic claim command.
8. Fetch the issue again and report final status, verification, dependency impact, and follow-ups.

## Pass Criteria

Pass only when all are true:

- The issue body explains the work without chat context.
- Stated scope and acceptance criteria are satisfied or explicitly out of scope.
- Evidence supports claims: PR, commit, commands, screenshots, links, logs, or concrete observations.
- Dependencies are completed or explicitly waived.
- Risks and skipped checks are recorded.
- Follow-up work is created, linked, or deliberately deferred with rationale.

Append:

```md
### Status change: In Review -> Completed
Date:
Reviewer:
Review type:
Reviewed:
Verification:
Dependencies:
Follow-ups:
Risks / skipped checks:
Final outcome:
```

Then release:

```bash
python3 <repo>/skills/manage-agent-hub-issues/scripts/agent_hub.py claim release --issue '<issue>' --claim-id '<claim-id>' --mode review-pass
```

## Fail Criteria

Fail when durable evidence is missing, acceptance criteria are not met, checks are unjustifiably skipped, dependencies are unresolved, or required follow-ups are not tracked.

Append:

```md
### Status change: In Review -> In Progress
Date:
Reviewer:
Review type:
Reviewed:
Reason sent back:
Required fixes:
Dependencies:
Evidence:
Recommended next step:
```

Then release:

```bash
python3 <repo>/skills/manage-agent-hub-issues/scripts/agent_hub.py claim release --issue '<issue>' --claim-id '<claim-id>' --mode review-fail
```

The release sets `Owner = Unassigned` unless you pass an explicit owner.

## Abandon Review

If review cannot be completed, append why and release with `review-abandon`. Leave `Status = In Review` so another reviewer can claim it.

## Task-Type Checks

- Code/refactor: inspect diff or PR, run targeted tests/build/lint where practical, check authorization, data integrity, trust boundaries, and regressions.
- Research/audit/architecture: verify the report is self-contained, evidence-backed, ranked, and actionable.
- QA/browser/design: verify repro steps, screenshots, console/network behavior, responsive states, and ranked findings.
- Decision/open question: verify a durable answer, rationale, alternatives, owner, and downstream work.
- Docs/planning/handoff: verify accuracy, assumptions, non-goals, dependencies, and next steps.
