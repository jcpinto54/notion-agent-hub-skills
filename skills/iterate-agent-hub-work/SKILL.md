---
name: iterate-agent-hub-work
description: Orchestrate one Agent Hub work iteration by listing ready issues with list-agent-hub-issues, spawning up to 10 subagents, and returning their agent IDs without waiting for completion.
---

# Iterate Agent Hub Work

Use this skill to start one bounded Agent Hub iteration. This skill is orchestration-only: it does not define readiness, claim, review, stale-claim, or completion policy.

## Canonical Responsibilities

- `list-agent-hub-issues` owns readiness and ordering.
- `claim-agent-hub-issue` owns claim/refusal and worktree rules.
- `update-agent-hub-issue` owns durable progress and PR metadata.
- `review-agent-hub-issue` owns completion decisions.

## Workflow

1. Ensure the hub data source is known. If not, use `list-agent-hub-issues` guidance to locate the `Issues / Activities` data source.
2. Run the canonical ready-issue listing, capped at 10:

```bash
python3 ~/.codex/skills/list-agent-hub-issues/scripts/agent_hub_list.py \
  --data-source-id '<hub-data-source-id-or-url>' \
  --readiness Ready \
  --format json \
  --limit 10
```

3. For each returned JSON row, spawn one subagent with `multi_agent_v1.spawn_agent`.
4. Do not wait for completion. Return the issue title, issue URL, status, and spawned agent ID for each subagent.

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
- Use $claim-agent-hub-issue first. Do not work without a successful claim.
- If Status is Not Started, claim purpose is work. After claim succeeds, create or verify the required git worktree exactly as $claim-agent-hub-issue instructs before editing files.
- If Status is In Review, claim purpose is review. After claim succeeds, create a clean review worktree from the PR evidence exactly as $claim-agent-hub-issue instructs before reviewing.
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
