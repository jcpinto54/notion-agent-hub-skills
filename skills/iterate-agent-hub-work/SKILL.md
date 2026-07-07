---
name: iterate-agent-hub-work
description: Orchestrate one single Agent Hub work iteration by listing ready issues with list-agent-hub-issues, spawning up to 10 subagents, and returning their agent IDs without waiting for completion. Use run-agent-hub-loop instead when the user asks to keep operating on a change packet until blocked, complete, or budget exhausted.
---

# Iterate Agent Hub Work

Use this skill to start one bounded Agent Hub iteration. This is a one-wave
primitive: it lists ready work, spawns subagents, and returns their IDs without
waiting for completion.

Use `run-agent-hub-loop` when the user asks to keep running a packet, operate
until blocked, include automatic review, or respect wave/time budgets.

## Canonical Responsibilities

- `spec-agent-hub-issue` owns execution-readiness, spec critique, done criteria, and decomposition before issues enter the parallel queue.
- `list-agent-hub-issues` owns readiness and ordering.
- `claim-agent-hub-issue` owns claim/refusal and worktree rules.
- `update-agent-hub-issue` owns durable progress and PR metadata.
- `review-agent-hub-issue` owns completion decisions.

## Workflow

1. Ensure Agent Hub setup exists. If not, use `init-agent-hub`.
2. Confirm that work entering this iteration has already passed `spec-agent-hub-issue` or is otherwise clearly scoped with observable done criteria. If an issue is vague, too broad, or missing verification steps, do not reinterpret it here; run `spec-agent-hub-issue` first.
3. Run the canonical ready-issue listing, capped at 10:

```bash
python3 ~/.codex/skills/list-agent-hub-issues/scripts/agent_hub_list.py \
  --readiness Ready \
  --format json \
  --limit 10
```

For a packet-scoped one-wave iteration, pass the change filter through the
listing command:

```bash
python3 ~/.codex/skills/list-agent-hub-issues/scripts/agent_hub_list.py \
  --backend file \
  --change '<change-slug>' \
  --readiness Ready \
  --format json \
  --limit 10
```

4. For each returned JSON row, spawn one subagent with `multi_agent_v1.spawn_agent`.
5. Do not wait for completion. Return the issue title, issue URL, status, and spawned agent ID for each subagent.

If the listing returns no rows, report that no ready Agent Hub issues were found.

## Subagent Prompt Template

Use this prompt for each spawned subagent, filling in the row values exactly:

```text
Use the Agent Hub skills to work this issue end to end.

Issue:
- Title: <title>
- URL: <url>
- Page ID: <id>
- Status: <status>
- Priority: <priority>

Rules:
- This issue should already be execution-ready. If the issue body is too vague to identify scope, done criteria, or verification steps, stop and report that it needs $spec-agent-hub-issue before implementation.
- Use $claim-agent-hub-issue first. Do not work without a successful claim.
- If Status is Not Started, claim purpose is work.
- If Status is In Review, claim purpose is review.
- After claiming, follow $claim-agent-hub-issue for the required worktree or review worktree setup before touching repo files.
- Use $update-agent-hub-issue for durable progress, blockers, PR metadata, or handoff notes.
- Use $review-agent-hub-issue for review completion decisions.
- If the claim is refused, stop and report the refusal reason. Do not bypass claim or readiness rules.
- If repo work is completed, commit, push, open a normal PR, update the issue with evidence, and release the claim using the proper mode.
```

## Safety

- Spawn at most 10 subagents per iteration.
- Do not reinterpret or filter readiness beyond the JSON rows returned by `list-agent-hub-issues`.
- Do not claim issues in the parent orchestrator; each subagent claims its own issue.
- Do not spawn duplicate agents for the same issue in one iteration.
