# Design

## Approach

Run future deterministic commands from fixture cwd and compare diagnostics.

## Data Flow

Fixture `.hub` input produces report JSON under `.hub/reports`.

## Interfaces

`agent-hub audit hub`, `agent-hub audit issue`, and `agent-hub analyze change`.

## Migration Notes

Existing v2 scripts are not modified by this fixture.

## Failure Modes

Missing CLI, missing reports, or missing diagnostics fail the eval.

## Alternatives Rejected

External eval frameworks are deferred.
