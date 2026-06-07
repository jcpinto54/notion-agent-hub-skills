---
name: set-agent-hub-api-key
description: Configure local credentials for reusable Agent Hub Notion API scripts. Use when a user asks to set up, validate, rotate, store, or troubleshoot the NOTION_AGENT_HUB_TOKEN used by list-agent-hub-issues or claim-agent-hub-issue.
---

# Set Agent Hub API Key

Configure the local token file used by direct Notion API helper scripts. This skill does not create or modify hub issues.

## Workflow

1. Get the Notion integration token from the user, `NOTION_AGENT_HUB_TOKEN`, or an existing `~/.codex/agent-hub/.env`.
2. Run:

```bash
python3 <skill-dir>/scripts/set_agent_hub_api_key.py --token '<token>'
```

3. If the user only wants validation, run:

```bash
python3 <skill-dir>/scripts/set_agent_hub_api_key.py --check-only
```

4. Confirm that the script reports success. It writes `~/.codex/agent-hub/.env`, enforces file mode `600`, and runs a harmless Notion search auth check.

## Notes

- Never print the token back to the user.
- If auth fails, ask the user to verify the Notion integration token and that the relevant hub pages/databases are shared with the integration.
- Direct Notion API scripts read `NOTION_AGENT_HUB_TOKEN` first, then fall back to `NOTION_TOKEN`.

