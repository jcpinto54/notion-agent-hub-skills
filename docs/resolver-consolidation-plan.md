# Agent Hub Resolver Consolidation Plan

## Summary

Reduce the number of globally visible Agent Hub skills while preserving the existing workflows. The public entry point should be `manage-agent-hub-issues`, with detailed workflow knowledge kept reachable behind that resolver.

This plan is documentation only. It does not change installed skills, scripts, or local Codex configuration.

## Goals

- Make `manage-agent-hub-issues` the primary public resolver for Agent Hub work.
- Keep setup, creation, listing, claiming, updating, review, audit, iteration, and sync workflows available.
- Reduce Codex initial skill-list pressure by avoiding many always-visible Agent Hub leaf skills.
- Preserve direct helper scripts and existing test coverage.

## Proposed Public Surface

Keep visible:

- `manage-agent-hub-issues`: resolver and shared operating policy.
- 
- Optionally `sync-agent-hub-skills`: only if local skill publishing remains a frequent explicit maintenance task.

Everything else should be reachable through resolver references or disabled locally after consolidation.

## Implementation Direction

1. Move detailed leaf-skill instructions into resolver-owned references.
   - Suggested layout: `skills/manage-agent-hub-issues/references/`.
   - One reference per workflow family: setup, create, list, claim, update, review, audit, iterate, sync.
2. Update `manage-agent-hub-issues/SKILL.md`.
   - Keep frontmatter concise and trigger-focused.
   - Route user intent to the relevant reference.
   - Keep shared schema, claim, dependency, review, and durability rules in one place.
3. Preserve helper scripts.
   - Claim, list, setup, and sync scripts should remain available from stable paths or be moved with explicit path updates.
   - Avoid duplicating script usage snippets across references.
4. Decide the installation strategy during implementation.
   - Preferred durable option: stop installing leaf workflows as separate visible skills.
   - Local-only fallback: keep leaf skills on disk and disable them in `~/.codex/config.toml`.
5. Update README usage docs.
   - Explain that users should invoke `manage-agent-hub-issues` for Agent Hub work.
   - List the routed capabilities without presenting each as a separately discoverable skill.

## Validation

- Run existing tests:

```bash
pytest
```

- Verify skill metadata after any skill-file restructuring.
- Confirm `manage-agent-hub-issues` can route these smoke scenarios:
  - Create a new Agent Hub issue.
  - List ready issues.
  - Claim work.
  - Submit progress or review evidence.
  - Review an `In Review` issue.
  - Audit workspace hygiene.
  - Sync local skills back to the repo.
- Confirm Codex-visible Agent Hub skill count is reduced after install or local disablement.

## Acceptance Criteria

- Agent Hub workflows remain reachable without relying on chat memory.
- The resolver contains enough routing detail for a fresh agent to choose the right workflow reference.
- Existing tests pass.
- No workflow knowledge is deleted without being moved into a resolver reference.
- Codex initial skill-list usage is lower than before.

## Non-Goals

- Do not change external database schema.
- Do not change claim, review, or dependency semantics.
- Do not remove helper scripts unless their callers are updated and tested.
- Do not make VACCO plugin changes in this repo.
