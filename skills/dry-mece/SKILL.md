---
name: dry-mece
description: Apply DRY and MECE principles to code, skills, research, planning, documentation, decomposition, reviews, and other reasoning tasks.
---

# DRY and MECE

Use this skill when the user asks for DRY/MECE thinking or when a task would benefit from cleaner decomposition, less duplication, or sharper boundaries.

## Principles

- **DRY**: Do not duplicate source-of-truth logic, definitions, policies, schemas, prompts, or facts. Reuse or reference the canonical owner instead.
- **MECE**: Decompose work into groups that are mutually exclusive and collectively exhaustive: no overlap, no gaps.

## How To Apply

1. Identify the canonical source of truth before adding new logic, docs, or structure.
2. Separate responsibilities by owner, layer, audience, lifecycle, or decision boundary.
3. Remove duplicated rules and replace them with references to the owning source.
4. Check for overlap: if two buckets can own the same thing, redefine the boundary.
5. Check for gaps: every required case should have exactly one home.
6. Prefer small, named abstractions only when they remove real duplication or clarify ownership.

## Output Shape

When useful, summarize with:

```text
Source of truth:
MECE decomposition:
Duplications removed:
Gaps covered:
Residual tradeoffs:
```

Keep the advice domain-neutral. DRY and MECE can apply to implementation, skill design, research synthesis, product plans, review findings, testing strategy, and documentation.
