---
name: list-agent-hub-issues
description: Read-only Agent Hub listing and readiness automation. Use when a user asks to list, enumerate, show, count, filter, summarize, export, or find ready-to-start Notion Agent Hub issues, including dependency-aware readiness, board views, Markdown tables, or JSON output.
---

# List Agent Hub Issues

Use the bundled direct Notion API script for read-only listing.

## Workflow

1. Ensure credentials exist. If not, use `set-agent-hub-api-key`.
2. Get the Notion data source ID or URL for the hub `Issues / Activities` database.
3. Run:

```bash
python3 <skill-dir>/scripts/agent_hub_list.py --data-source-id '<data-source-id-or-url>'
```

4. Add filters as needed:

```bash
python3 <skill-dir>/scripts/agent_hub_list.py --data-source-id '<id>' --readiness Ready
python3 <skill-dir>/scripts/agent_hub_list.py --data-source-id '<id>' --status 'In Review'
python3 <skill-dir>/scripts/agent_hub_list.py --data-source-id '<id>' --format json
```

## What The Script Computes

- Groups by status in order: `Not Started`, `In Progress`, `In Review`, `Completed`.
- Sorts by priority `P0` to `P3`, then newest update first.
- Computes readiness from status, owner, blockers, active claim, and dependency statuses.
- Uses one data source query for dependency status lookup, avoiding N+1 dependency fetches for normal hubs.
- Flags expired and active claims through `Claim ID` and `Claim Expires At`.

## Safety

- Do not create, update, delete, claim, or release anything with this skill.
- If the user asks to modify a listed issue, switch to the appropriate create, claim, update, or review skill.
- Issue numbers in the Markdown output are per-response references only. Do not persist them.

