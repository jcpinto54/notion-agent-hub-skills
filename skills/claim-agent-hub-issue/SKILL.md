---
name: claim-agent-hub-issue
description: Claim, check, renew, or release Agent Hub ownership leases for implementation work or review work. Use when a user asks to claim ready work, claim review, renew a claim, release abandoned or submitted work, or clear passed/failed review ownership in a Notion Agent Hub.
---

# Claim Agent Hub Issue

Use the bundled direct Notion API script for ownership leases. The script writes only status, owner, claim fields, and optional repo metadata properties.

## Claim Work

Run:

```bash
python3 <skill-dir>/scripts/agent_hub_claim.py claim \
  --purpose work \
  --page-id '<issue-page-id-or-url>' \
  --data-source-id '<hub-data-source-id-or-url>' \
  --owner '<agent-name>' \
  --base-branch '<base>' \
  --branch '<branch>' \
  --worktree-path '<path>'
```

The script refuses the claim unless:

- `Status = Not Started`
- `Owner` is empty, `Unassigned`, or equivalent
- `Blockers` is empty
- all `Depends On` issues are `Completed`
- no unexpired claim exists

After the script succeeds, create the branch/worktree if repo work is expected and record any missing metadata through `update-agent-hub-issue`.

## Claim Review

Run:

```bash
python3 <skill-dir>/scripts/agent_hub_claim.py claim \
  --purpose review \
  --page-id '<issue-page-id-or-url>' \
  --data-source-id '<hub-data-source-id-or-url>' \
  --owner '<reviewer-name>'
```

The script refuses review unless:

- `Status = In Review`
- no unexpired claim exists
- dependencies are completed or explicitly waived in `Dependency Notes`
- the issue has durable artifact evidence in `PR URL`, `Commit SHA`, or `Related Links`

Use `--allow-missing-artifacts` only when the issue type is intentionally non-repo/non-artifact and the page body itself is sufficient.

## Check Or Renew

```bash
python3 <skill-dir>/scripts/agent_hub_claim.py check --page-id '<issue>' --claim-id '<claim-id>'
python3 <skill-dir>/scripts/agent_hub_claim.py renew --page-id '<issue>' --claim-id '<claim-id>' --ttl-minutes 120
```

## Release Modes

```bash
python3 <skill-dir>/scripts/agent_hub_claim.py release --page-id '<issue>' --claim-id '<claim-id>' --mode submitted --pr-url '<url>' --commit-sha '<sha>'
python3 <skill-dir>/scripts/agent_hub_claim.py release --page-id '<issue>' --claim-id '<claim-id>' --mode review-pass
python3 <skill-dir>/scripts/agent_hub_claim.py release --page-id '<issue>' --claim-id '<claim-id>' --mode review-fail
```

Supported modes:

- `abandon`: release work claim; return to `Not Started` only when no repo metadata exists.
- `handoff`: release work claim; keep `In Progress`; owner defaults to `Unassigned`.
- `blocked`: release work claim and optionally write `Blockers`.
- `submitted`: release work claim after PR exists; set `In Review`.
- `review-pass`: release review claim after moving to `Completed`.
- `review-fail`: release review claim after moving back to `In Progress`.
- `review-abandon`: release review claim and leave `In Review`.

## Optimistic Locking

Every claim writes a unique `Claim ID`, immediately refetches the page, and succeeds only if the claim ID still matches. If verification fails, stop and inspect the issue manually.

