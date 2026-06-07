---
name: sync-agent-hub-skills
description: Sync installed local Agent Hub Codex skills back to their backing git repository, validate them, commit the changes, and push. Use when the user asks to publish, commit, push, back up, or synchronize local Agent Hub skills with the repo.
---

# Sync Agent Hub Skills

Use the bundled script to copy installed Agent Hub skills into the backing repo, validate them, commit, and push.

## Workflow

1. Discover the backing repository. Do not hardcode it. Prefer an explicit repo the user named; otherwise inspect likely git repositories, remotes, and `skills/*/SKILL.md` files until you identify the Agent Hub skills repo.
2. Verify the discovered repo contains the Agent Hub skills suite under `skills/`.
3. Run:

```bash
python3 <skill-dir>/scripts/agent_hub_sync_skills.py --repo-dir '<discovered-repo-path>'
```

Optional flags:

```bash
python3 <skill-dir>/scripts/agent_hub_sync_skills.py --repo-dir '<repo>' --no-push
python3 <skill-dir>/scripts/agent_hub_sync_skills.py --repo-dir '<repo>' --commit-message 'Sync Agent Hub skills'
```

## What The Script Does

- Copies only known Agent Hub skills from `~/.codex/skills` into `<repo>/skills`.
- Refuses to run when the destination repo is dirty before sync.
- Refuses repo/local drift when a tracked skill file exists in the repo but is missing locally.
- Excludes generated files such as `__pycache__`, `*.pyc`, `.DS_Store`, and editor temp files.
- Runs unit tests, skill metadata validation, and Python syntax compilation.
- Commits changed skill files and pushes the current branch to `origin` unless `--no-push` is used.

## Safety

- Do not sync unrelated local skills into this repo.
- Do not use this skill if the destination repo cannot be confidently identified.
- If the script reports drift or a dirty repo, stop and show the user the exact reason.
