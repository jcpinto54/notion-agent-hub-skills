---
name: list-agent-hub-issues
description: Read-only Agent Hub listing and readiness automation. Use when a user asks to list, enumerate, show, count, filter, summarize, export, or find ready-to-start Notion Agent Hub issues, including dependency-aware readiness, board views, Markdown tables, or JSON output.
---

# List Agent Hub Issues

Use the bundled direct Notion API script for read-only listing.

## Workflow

1. Ensure Agent Hub setup exists. If not, use `setup-agent-hub`.
2. Run the list script. It reads the default `Issues / Activities` data source from repo `.agent-hub.local`, then `~/.codex/agent-hub/.env`.
3. Run:

```bash
python3 <skill-dir>/scripts/agent_hub_list.py
```

4. Add filters or a one-off data source override as needed:

```bash
python3 <skill-dir>/scripts/agent_hub_list.py --readiness Ready
python3 <skill-dir>/scripts/agent_hub_list.py --status 'In Review'
python3 <skill-dir>/scripts/agent_hub_list.py --format json
python3 <skill-dir>/scripts/agent_hub_list.py --data-source-id '<id>'
```

## What The Script Computes

- Renders three Markdown boards by default, in order: `Eligible (Not Started)`, `Eligible (In Review)`, and `Blocked`.
- Shows each listed issue's current status in the board output.
- Treats unblocked, unowned `Not Started` issues as implementation pickup candidates.
- Treats unowned `In Review` issues without an active claim as review pickup candidates.
- Includes completed issue count in the summary.
- Groups and counts statuses in order: `Not Started`, `In Progress`, `In Review`, `Completed`.
- Sorts by priority `P0` to `P3`, then newest update first.
- Computes `Not Started` readiness from owner, blockers, active claim, and dependency statuses.
- Computes `In Review` readiness from owner and active claim.
- Uses one data source query for dependency status lookup, avoiding N+1 dependency fetches for normal hubs.
- Flags expired and active claims through `Claim ID` and `Claim Expires At`.

## Safety

- Do not create, update, delete, claim, or release anything with this skill.
- Do not spawn subagents with this skill. Use `iterate-agent-hub-work` for bounded subagent orchestration.
- If the user asks to modify a listed issue, switch to the appropriate create, claim, update, or review skill.
- Issue numbers in the Markdown output are per-response references only. Do not persist them.
