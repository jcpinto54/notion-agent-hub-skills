---
name: create-agent-hub-issue
description: Create Notion Agent Hub issues, follow-ups, decisions, open questions, and handoffs. Use when a user asks to add, file, create, record, split, or sequence durable work items in an Agent Hub database.
---

# Create Agent Hub Issue

Use Notion MCP for creation. No direct API script is needed for v1 because issue content requires judgment and rich page-body writing.

## Workflow

1. Locate the `Issues / Activities` database from a provided hub URL or by searching Notion.
2. Fetch the schema and adapt only obvious property mappings.
3. Write a durable page body with the reason the issue exists, scope, acceptance criteria or expected output, dependencies, and first next step.
4. Set obvious dependency relations before saving when ordering is clear.
5. Create the item and fetch it back to verify properties and body.

## Defaults

- `Status`: `Not Started`
- `Owner`: `Unassigned`
- `Priority`: `P2` unless urgency is clear
- `Type`: choose from the schema; use `Decision`, `Open Question`, or `Handoff` when appropriate
- `Blockers`: empty unless the blocker is external to the hub
- `Depends On`: prerequisite hub issues, not generic blockers
- `Dependency Notes`: rationale for any dependency, parallel work allowed, or explicit override

## Durable Body Template

```md
## Context

## Scope

## Acceptance Criteria
- [ ]

## Dependencies

## Evidence / Links

## Activity Log

### Created
Date:
Agent:
Reason:
Next step:
```

For follow-ups created during review, link the source issue and set `Depends On` or `Blocks` so downstream tracking reflects the sequencing.

