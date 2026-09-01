---
name: create-backlog-write-epics
description: "Write backlog/epics.md from the approved EPIC slicing approach. Phase 2 of 4 in the create-backlog sequence."
category: planning
disable-model-invocation: false
---

# Create Backlog — Phase 2: Write EPICs

Write `backlog/epics.md` from the approved EPIC slicing approach. This is phase 2 of the [create-backlog sequence](../create-backlog/SKILL.md#operational-sequence). Story format, composition rules, and the done check live in the [parent skill](../create-backlog/SKILL.md).

**Prerequisite:** the EPIC-level slice table has been approved by the user (output of [`create-backlog-epics`](../create-backlog-epics/SKILL.md)).

## Step 1 — Write backlog/epics.md

Document every confirmed EPIC in `backlog/epics.md` with:

- Actor goals
- Demo (what a person can show after shipping the EPIC)
- Scope
- Dependencies on other EPICs
- Boundaries (system boundaries the EPIC crosses)
- Size / story count estimate
- Building-block inventory listing each anticipated story with its capacity tier and day-range estimate

Every User Goal from the actor-goal list must belong to exactly one EPIC.

If charter files exist and Epic 0 stories are already in the backlog (created by the `capture-charter` completeness sweep), record Epic 0 in `epics.md` and note that feature EPICs depend on its completion. Feature stories derived from the charter's Feature List shall depend on the final Epic 0 story via `deps:`.

Format via `factory/scripts/mdformat --number backlog/epics.md` per [markdown-formatting.md](../../rulebooks/conventions/markdown-formatting.md).

## Quality gate

Before presenting, review `backlog/epics.md` through two lenses:

**Junior Clarity:** Can a junior developer read each EPIC section and understand what it delivers, what its boundaries are, and roughly how many stories it contains? If not, the EPIC is underspecified.

**Senior Acceptance:** Would a senior hand this EPIC breakdown to the team without a follow-up conversation? Is the scope bounded, the demo concrete, and the dependency chain clear? If not, revise.

Present `backlog/epics.md` to the user for confirmation.

## This skill ends here

The EPIC artifact is written. **Do not proceed to story-level slicing.** The user confirms or adjusts `backlog/epics.md`, then invokes the next skill: [`create-backlog-story-slices`](../create-backlog-story-slices/SKILL.md).

## Optional: Invoke test-design

Before proceeding to step 3, you may invoke [`test-design`](../test-design/SKILL.md) to enrich the epics with test scenarios from the `.feature` contracts. The test-design skill designs failure scenarios that prescribe the developer-agent's TDD RED phase — without it, each developer-agent invents its own tests, often defaulting to obvious happy-path coverage that proves nothing about the behavioral invariants the specification intended. By contrast, test-design output ensures every test traces to a contract and every contract has one clear owner.
