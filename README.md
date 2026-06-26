# agent-hub-skills

Reusable Codex skills for coordinating multi-agent work in an Agent Hub.

Agent Hub v2 is hybrid and repo-native by default:

- `.hub/` in each target project repository is the canonical durable store for specs, activity logs, decisions, evidence, and review notes.
- Notion is optional as a personal dashboard/index or as a legacy backend for existing hubs.
- Helper scripts default to `--backend auto`, which selects `.hub/config.yml` when present and otherwise falls back to Notion configuration.

The suite keeps automation intentionally small:

- `dry-mece` provides generic DRY and MECE reasoning context for code, planning, research, docs, and skill design.
- `init-agent-hub` creates repo-native `.hub` directories or legacy Notion hubs.
- `setup-agent-hub` validates and stores legacy Notion Agent Hub configuration.
- `list-agent-hub-issues` lists hub issues and computes readiness from `.hub` or Notion.
- `spec-agent-hub-issue` turns raw ideas or rough issues into agent-ready specs before parallel execution.
- `claim-agent-hub-issue` manages optimistic ownership leases for work and review using `.hub/runtime/claims.json` or Notion claim fields.
- `iterate-agent-hub-work` spawns subagents for one ready-issue iteration without redefining readiness or claim rules.
- `sync-agent-hub-skills` copies installed Agent Hub skills back to the repo, validates, commits, and pushes.
- The remaining skills guide creation, updates, review decisions, and workspace hygiene through `.hub` files or legacy Notion records.

## Repo-Native Hub Layout

Initialize a target repository:

```bash
python3 skills/init-agent-hub/scripts/init_file_hub.py --repo /path/to/repo --project-name "Project"
```

This creates:

```text
.hub/
├── config.yml
├── .gitignore
├── issues/
├── decisions/
├── artifacts/
└── runtime/      # gitignored live locks
```

Create a file-backed issue:

```bash
python3 skills/create-agent-hub-issue/scripts/create_file_issue.py \
  "Add hybrid file backend" --id add-hybrid-file-backend
```

List ready work:

```bash
python3 skills/list-agent-hub-issues/scripts/agent_hub_list.py --backend file --readiness Ready
```

Claim work:

```bash
python3 skills/claim-agent-hub-issue/scripts/agent_hub_claim.py claim \
  --backend file \
  --page-id add-hybrid-file-backend \
  --purpose work \
  --owner Codex
```

## Parallel Agent Workflow

Parallel execution is only useful after issues are small, clear, and independently verifiable. Use `spec-agent-hub-issue` before `iterate-agent-hub-work` to turn raw ideas into ready issues or split work that is too broad for one agent.

```mermaid
flowchart TD
    A["Raw idea, dictation, or rough issue"] --> B["spec-agent-hub-issue"]
    B --> C{"Spec gate result"}
    C -->|Ready| D["Status: Not Started / ready for pickup"]
    C -->|Revise| B
    C -->|Decompose| E["dry-mece decomposition"]
    E --> F["create-agent-hub-issue child issues"]
    F --> B
    D --> G["iterate-agent-hub-work"]
    G --> H["list-agent-hub-issues --readiness Ready"]
    H --> I["Spawn up to 10 subagents"]
    I --> J["Each subagent uses claim-agent-hub-issue"]
    J --> K["Implement and update evidence"]
    K --> L["review-agent-hub-issue"]
    L --> M{"Review result"}
    M -->|Pass| N["Completed"]
    M -->|Fail| O["In Progress"]
    O --> J
```

The spec gate uses fresh-context checks before an issue can enter the parallel queue:

```mermaid
flowchart TD
    A["Draft spec"] --> B["Critic subagent reviews full spec"]
    B --> C{"Findings?"}
    C -->|"No findings or accepted residual risk"| D["Write Done Summary"]
    C -->|"Ambiguity or missing criteria"| E["Revise spec"]
    C -->|"Multiple independent done states"| F["Decompose issue"]
    E --> B
    D --> G["Reconstruction subagent receives only Done Summary"]
    G --> H{"Matches Done Criteria?"}
    H -->|Yes| I["Spec Ready"]
    H -->|"Gaps, additions, or questions"| D
    F --> J["Create child issues"]
    J --> K["Run spec-agent-hub-issue on each child"]
```

## Install

After publishing this repository to GitHub, install the skills with Codex's `skill-installer`:

```bash
python3 ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo jcpinto54/notion-agent-hub-skills \
  --path \
  skills/dry-mece \
  skills/setup-agent-hub \
  skills/manage-agent-hub-issues \
  skills/init-agent-hub \
  skills/create-agent-hub-issue \
  skills/spec-agent-hub-issue \
  skills/list-agent-hub-issues \
  skills/claim-agent-hub-issue \
  skills/iterate-agent-hub-work \
  skills/update-agent-hub-issue \
  skills/review-agent-hub-issue \
  skills/review-agent-hub-workspace \
  skills/sync-agent-hub-skills
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
