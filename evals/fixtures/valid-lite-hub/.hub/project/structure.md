# Structure

## Repo Map

`.hub/project` stores guidance, `.hub/issues` stores work, `.hub/changes` stores packets.

## Boundaries

Runtime claims stay under `.hub/runtime`.

## Entry Points

The future `agent-hub` CLI owns audit and analyze commands.

## Extension Points

New diagnostics should remain stable and machine-readable.

## Areas To Avoid

Do not hand-edit generated reports.
