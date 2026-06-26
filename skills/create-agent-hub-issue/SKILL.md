---
name: create-agent-hub-issue
description: Create repo-native `.hub` Agent Hub issues or legacy Notion issues, follow-ups, decisions, open questions, and handoffs. Use when a user asks to add, file, create, record, split, or sequence durable work items in an Agent Hub.
---

# Create Agent Hub Issue

For repo work, create `.hub/issues/<issue-id>.md` as the canonical durable record. Use Notion MCP only for legacy hubs or optional mirror pages.

## Workflow

1. If `.hub/config.yml` exists, write a repo-native issue. Otherwise use the configured legacy Notion `Issues / Activities` data source.
2. Write a durable body with the reason the issue exists, scope, acceptance criteria or expected output, dependencies, and first next step.
3. Set obvious dependencies before saving when ordering is clear.
4. Create the item and fetch/read it back to verify metadata and body.

For repo-native creation, use:

```bash
python3 <skill-dir>/scripts/create_file_issue.py '<title>' --id '<issue-id>' --type Feature --priority P2
```

Then edit the generated issue body as needed.

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
