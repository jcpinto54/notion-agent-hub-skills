# agent-hub-skills

Reusable Codex skills for coordinating multi-agent work in a Notion Agent Hub.

The suite keeps automation intentionally small:

- `set-agent-hub-api-key` validates and stores `NOTION_AGENT_HUB_TOKEN`.
- `list-agent-hub-issues` lists hub issues and computes readiness through the Notion API.
- `claim-agent-hub-issue` manages optimistic ownership leases for work and review.
- The remaining skills guide creation, updates, review decisions, and workspace hygiene through Notion MCP and durable issue records.

## Install

After publishing this repository to GitHub, install the skills with Codex's `skill-installer`:

```bash
python3 ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo jcpinto54/notion-agent-hub-skills \
  --path skills/set-agent-hub-api-key \
  --path skills/manage-agent-hub-issues \
  --path skills/init-agent-hub \
  --path skills/create-agent-hub-issue \
  --path skills/list-agent-hub-issues \
  --path skills/claim-agent-hub-issue \
  --path skills/update-agent-hub-issue \
  --path skills/review-agent-hub-issue \
  --path skills/review-agent-hub-workspace
```

Restart Codex after installing.

## Development

Run unit tests:

```bash
python3 -m unittest discover -s tests
```

Validate skill metadata:

```bash
for skill in skills/*; do
  python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py "$skill"
done
```
