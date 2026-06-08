---
name: setup-agent-hub
description: Configure local Agent Hub Notion access and default hub metadata. Use when a user asks to set up, validate, rotate, store, or troubleshoot the Notion token, hub URL, or Issues / Activities data source used by Agent Hub skills.
---

# Setup Agent Hub

Configure the local Agent Hub file used by direct Notion API helper scripts. This skill does not create, update, claim, or release hub issues.

## Workflow

1. Get the Notion integration token from the user, `NOTION_AGENT_HUB_TOKEN`, repo `.agent-hub.local`, or `~/.codex/agent-hub/.env`.
2. Prefer repo-local setup when running inside the project repository.
3. Run setup with a hub URL or data source when available:

```bash
python3 <skill-dir>/scripts/setup_agent_hub.py --token '<token>' --hub-url '<hub-or-database-url>'
python3 <skill-dir>/scripts/setup_agent_hub.py --token '<token>' --data-source-id '<issues-data-source-id-or-url>'
```

4. If no hub URL is known, let setup search Notion for a single unambiguous Agent Hub:

```bash
python3 <skill-dir>/scripts/setup_agent_hub.py --token '<token>'
```

5. If the user only wants validation, run:

```bash
python3 <skill-dir>/scripts/setup_agent_hub.py --check-only
```

6. Confirm that the script reports success. It writes `.agent-hub.local` inside a git repo, otherwise `~/.codex/agent-hub/.env`, enforces file mode `600`, and runs a harmless Notion search auth check.

## Config Values

The setup file is env-style and may contain:

- `NOTION_AGENT_HUB_TOKEN`
- `NOTION_AGENT_HUB_DATA_SOURCE_ID`
- `NOTION_AGENT_HUB_PAGE_URL`

Direct scripts load config in this order: CLI args, process env, repo `.agent-hub.local`, then `~/.codex/agent-hub/.env`.

## Options

- Use `--repo-local` to require repo-local config.
- Use `--global` to write `~/.codex/agent-hub/.env`.
- Use `--env-path <path>` for an explicit config file.
- Use `--data-source-id` to avoid search and validate a known `Issues / Activities` data source.
- Use `--hub-url` to discover the inline `Issues / Activities` data source from a hub page or database.

## Notes

- Never print the token back to the user.
- If auth fails, ask the user to verify the Notion integration token and that the relevant hub pages/databases are shared with the integration.
- If discovery finds multiple hubs, ask the user for the correct hub URL or data source ID.
- Direct Notion API scripts read `NOTION_AGENT_HUB_TOKEN` first, then fall back to `NOTION_TOKEN`.
