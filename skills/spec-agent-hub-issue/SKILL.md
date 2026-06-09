---
name: spec-agent-hub-issue
description: Turn raw ideas, dictation, or rough Agent Hub issues into precise, agent-ready specs with observable done criteria before claim or parallel execution; use when an issue needs specification, critique, decomposition, or readiness validation.
---

# Spec Agent Hub Issue

Use this skill before `claim-agent-hub-issue` or `iterate-agent-hub-work` when an issue is vague, missing acceptance criteria, or likely too large for one agent.

The core rule: if "done" cannot be stated clearly and reconstructed by a fresh context, the issue is not ready for parallel execution.

## Gateway Results

| Result | Condition | Next step |
|---|---|---|
| Ready | Done Summary passes the reconstruction test | Mark the issue ready for claim or iteration |
| Revise | Scope or criteria are ambiguous but single-purpose | Tighten the spec and re-run critique |
| Decompose | The issue contains multiple independent done states | Use `dry-mece`, then create child issues |

## Workflow

1. Capture the raw input as dictation, notes, or an existing issue body.
2. Rewrite it into the Spec Template below. Mark unknowns as `[UNKNOWN - needs clarification]`.
3. Make every Done Criteria item binary and observable.
4. Spawn one critic subagent with only the draft spec:

```text
You are a skeptical senior engineer doing a cold spec review.
You have NOT been part of writing this spec.

Your only job is to find flaws. Look for:
- Ambiguous terms such as "improve", "clean up", or "make it better"
- Missing out-of-scope boundaries
- Untestable or subjective done criteria
- Silent assumptions about environment, data, access, or dependencies
- Done criteria that belong to different concerns, owners, or lifecycles

Return a numbered list of findings only.
Do not suggest fixes. Do not praise the spec.
If you find no flaws, return exactly: "No findings."

Spec to review:
<paste full spec draft>
```

5. If the critic identifies multiple independent done states, stop tightening and decompose the issue with `dry-mece`.
6. Otherwise, revise the spec until critic findings are resolved or limited to explicitly accepted residual risks.
7. Write a two-sentence Done Summary that states the output, verification method, and out-of-scope boundary.
8. Spawn one reconstruction subagent with only the Done Summary:

```text
You are a new engineer who just joined the project.
You have ONLY this task summary. Nothing else.

Summary: "<Done Summary>"

Based solely on this summary:
1. List every acceptance criterion you would use to verify the work is done.
2. List any term or boundary you would need to ask a clarifying question about.

Be specific. If the summary is ambiguous, flag the ambiguity instead of assuming.
```

9. Compare the reconstruction against the spec:
   - Every Done Criteria item must be inferable from the summary.
   - No reconstructed criterion may be absent from the spec.
   - No clarifying questions may remain.
10. If the reconstruction fails, revise the Done Summary and repeat the reconstruction test.
11. If the reconstruction passes, update or create the Agent Hub issue with the final spec and make it eligible for the normal ready/claim workflow.

## Decomposition

Use decomposition when the issue resists a clear Done Summary because it contains multiple independent outcomes. Split by owner, lifecycle, repository area, verification method, risk, or dependency order.

For each child issue:

1. Create a separate issue using `create-agent-hub-issue`.
2. Link dependencies where sequencing is required.
3. Run `spec-agent-hub-issue` on the child before it can be claimed.
4. Keep the parent issue as the durable record of intent.

## Spec Template

```md
## Done Summary
<!-- Two sentences max. Fill this after the reconstruction test passes. -->

## Context
<!-- Why this exists and what problem it solves. -->

## Scope
<!-- What is explicitly included. -->

## Out of Scope
<!-- What the agent must not touch, change, or assume. -->

## Done Criteria
<!-- Binary, observable checks. -->
- [ ] <observable check>
- [ ] <observable check>

## Verification Steps
<!-- Prefer tests, commands, or explicit file/state checks. -->
1. <step> -> expected result
2. <step> -> expected result

## Assumptions

## Dependencies

## Open Questions

## Activity Log

### Specced
Date:
Agent:
Critique rounds:
Critiques resolved:
Residual risks:
Decomposed from:
```

## Criteria Guide

| Weak | Strong |
|---|---|
| Fix the bug | A test reproducing the bug exists and passes |
| Add validation | Invalid inputs X, Y, and Z return error E |
| Refactor the module | Existing tests pass before and after; no public API is added |
| Make it faster | P95 latency is below 200 ms on benchmark B |
| Clean up docs | Required sections exist and the docs build exits 0 |
