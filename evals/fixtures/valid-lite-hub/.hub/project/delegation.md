# Delegation Rules

## Core Rule

The main agent is an orchestrator, not an executor.

## Main Agent Responsibilities

Route work, run deterministic commands, and collect evidence.

## Subagent Responsibilities

Read required files, stay in scope, verify changes, and report evidence.

## Handoff Contract

Every handoff includes objective, scope, out-of-scope, required files, commands, evidence, and stop conditions.

## Evidence Requirements

Return files changed, commands run, results, blockers, and residual risks.

## Stop Conditions

Stop on scope conflict, unsafe writes, or unrelated failures that block validation.

## Exceptions

Only lightweight coordination may stay in the main context.
