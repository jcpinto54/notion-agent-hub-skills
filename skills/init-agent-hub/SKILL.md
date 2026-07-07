---
name: init-agent-hub
description: Create a reusable Agent Hub for a software project as an Agent Hub v3 repo-native `.hub` directory with deterministic file-backed orchestration. Use when a user asks to initialize or set up an agent coordination hub, shared task board, AI agent issue tracker, or workspace for multi-agent ownership, dependency, review, and handoff workflows.
---

# Init Agent Hub

Create an Agent Hub v3 repo-native `.hub`. The repo-native hub is the only durable source of truth for repo work.

## Repo-Native Workflow

1. Determine the target repository root.
2. Prefer the unified v3 CLI:

```bash
python3 <repo>/skills/manage-agent-hub-issues/scripts/agent_hub.py init --repo '<repo-path>' --project-name '<Project Name>'
```

3. If the unified CLI is unavailable, use the compatibility init script:

```bash
python3 <skill-dir>/scripts/init_file_hub.py --repo '<repo-path>' --project-name '<Project Name>'
```

4. Verify these paths exist:
   - `.hub/config.yml`
   - `.hub/state.yml`
   - `.hub/project/`
   - `.hub/changes/`
   - `.hub/issues/`
   - `.hub/decisions/`
   - `.hub/reports/`
   - `.hub/artifacts/`
   - `.hub/.gitignore` containing `runtime/`
5. If the user gave an initial task, create the first issue through the deterministic v3 command surface or `create-agent-hub-issue`.
6. Report the `.hub` path and remind the user that external notes are context only.

## Repo-Native Layout

```text
.hub/
|-- config.yml
|-- state.yml
|-- .gitignore
|-- project/
|-- changes/
|-- issues/
|-- decisions/
|-- reports/
|-- artifacts/
`-- runtime/      # gitignored active locks and local state
```

`config.yml` should set `version: 3`, `source_of_truth: file`, deterministic
strict writes, subagent-first behavior, and read-only dashboard defaults.
