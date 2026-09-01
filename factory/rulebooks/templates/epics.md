---
title: EPICs Document Template
version: 1.0.0
---

# EPICs Document Template

Skeleton for `backlog/epics.md`. Sits between the specification artifacts (scope map, `.feature` files) and the individual story files (`backlog/ST-NNNNNN.md`). The planning agent creates this document in Step 1 of the create-backlog skill; individual stories in Step 2 reference their parent EPIC by the `epic:` frontmatter value matching an EPIC title here.

The same composition discipline governs EPICs and stories: Demo First, Forward from Status Quo, Criteria Are Invariants. An EPIC is a larger vertical slice — if you cannot write its demo, the decomposition is wrong.

## Structure

````markdown
# <Increment or Release> EPICs

<One-paragraph summary of what this increment delivers and the decomposition strategy.>

## Shared Definition of Done

<What "done" means for every story in this increment — test ownership, gate criteria, redaction policy, infrastructure constraints. Shared across all EPICs so individual stories do not repeat it.>

## EPIC 0 -- <Title>

**Actor goals:** <AG-NN references, or "Enables AG-NN; owns no product goal" for foundational work.>

### Demo

<2–4 sentences. What a person can show after this EPIC ships. Concrete values, walkthrough format. Happy path plus one meaningful edge case.>

### Scope

**Status quo:** <what exists before this EPIC — deliverables of depended-on EPICs, or the bare project state for EPIC 0.>
**Adds:** <what this EPIC creates or changes, across all layers.>
**Out of scope:** <what explicitly does not change.>

### Acceptance Criteria

- <falsifiable invariant — "X produces Y", "X never Y", or "when X then Y" (scope-map rule IDs)>

### Presentation

- <One bullet per demonstrable capability or guarantee. Slide-ready — each bullet stands alone.>

### Dependencies

<Other EPICs that must complete first, or "None." The status quo section names what those EPICs deliver.>

### Stories

- [<ST-NNNNNN> <Story title>](ST-NNNNNN.md): <one-line scope>

## EPIC N -- <Title>

<Repeat the EPIC section structure for each subsequent EPIC.>

## Dependency Order

\```text
<ASCII dependency graph showing EPIC-to-EPIC ordering.>
\```

## Coverage

| EPIC | Actor goals | Stories | Priority intent |
| ---: | ----------- | ------: | --------------- |
|    0 | ...         |     ... | ...             |

<Every actor goal from the actor-goal list must appear exactly once. No speculative scope.>

## Unresolved Stakeholder Decisions

<Decisions this backlog intentionally does not invent. Each must be recorded in the specification todo before implementation if still open at backlog confirmation.>
````

## Composition Rules at the EPIC Level

The three story composition rules apply to EPICs with the same force:

### Demo First

Write the EPIC's Demo section before decomposing into stories. If you cannot describe what a person demonstrates after the EPIC ships, the EPIC does not deliver a coherent capability — recut it.

### Forward from Status Quo

State what exists before this EPIC (deliverables of depended-on EPICs, or the bare project for EPIC 0). State what a person can do afterward that they cannot do today. The gap is the EPIC's scope. Each EPIC's deliverables become status quo for every EPIC that depends on it.

### Criteria Are Invariants

Each acceptance criterion is a falsifiable statement. Trace scope-map rule IDs parenthetically. At the EPIC level, criteria describe system-wide guarantees the EPIC establishes — individual story criteria refine these into implementable test assertions.

## Referenced from

- [create-backlog § Step 1](../../skills/create-backlog/SKILL.md#step-1--define-epics-and-identify-epic-0)
- [story.md template](story.md) — `epic:` frontmatter references an EPIC title from this document
