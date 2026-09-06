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

**"Why this EPIC exists" section (required):** Before the Actor Goals, write one paragraph (2–4 sentences) that explains why this capability matters — what cannot happen without it, or what risk it removes. A junior reading the EPIC should understand the motivation before encountering the scope list.

**Demo format:** Write the demo as a numbered step list (not a paragraph). Each step describes one observable action or system response. A junior should be able to walk through the steps as a manual test.

**Term glossing:** On first use within each EPIC, parenthesise a plain-English gloss for every domain term, component name, or protocol concept that a junior developer would not recognise from general programming experience. Examples: "Odate boundary (the wall-clock moment one business day ends and the next begins)", "Return (a message carrying the exit code and terminal evidence)".

**Scope phrasing:** Scope In items must explain what the system does, not just name a component or concept. "Immutable Task Version publication — one atomic transaction that creates the version, records an audit event, supersedes the predecessor, and deletes the consumed draft" beats "Immutable Task Version publication". Scope Out items name what is excluded with enough context to prevent confusion about why.

Every User Goal from the actor-goal list must belong to exactly one EPIC.

If charter files exist and Epic 0 stories are already in the backlog (created by the `capture-charter` completeness sweep), record Epic 0 in `epics.md` and note that feature EPICs depend on its completion. Feature stories derived from the charter's Feature List shall depend on the final Epic 0 story via `deps:`.

Format via `factory/scripts/mdformat --number backlog/epics.md` per [markdown-formatting.md](../../rulebooks/conventions/markdown-formatting.md).

## Quality gate

Before presenting, review `backlog/epics.md` through two lenses:

**Junior Clarity checklist:**

1. Every domain term, protocol concept, and component name is glossed on first use within the EPIC (parenthetical plain-English explanation).
2. The demo is a numbered step list, not a wall paragraph.
3. Each EPIC has a "Why this EPIC exists" section that explains the motivation in plain language.
4. Scope In items describe behaviour ("what the system does"), not just name components.
5. Narrative text avoids dense chains of component names — save DSL identifiers for the Boundaries table.

If any item fails, revise before presenting.

**Senior Acceptance:** Would a senior hand this EPIC breakdown to the team without a follow-up conversation? Is the scope bounded, the demo concrete, and the dependency chain clear? If not, revise. Additionally: the demo steps, when read as a manual test, exercise the EPIC's core scenario end-to-end without referencing internal implementation details that only exist in the architecture DSL.

Present `backlog/epics.md` to the user for confirmation.

## This skill ends here

The EPIC artifact is written. **Do not proceed to story-level slicing.** The user confirms or adjusts `backlog/epics.md`, then invokes the next skill: [`create-backlog-story-slices`](../create-backlog-story-slices/SKILL.md).

## Optional: Invoke test-design

Before proceeding to step 3, you may invoke [`test-design`](../test-design/SKILL.md) to enrich the epics with test scenarios from the `.feature` contracts. The test-design skill designs failure scenarios that prescribe the developer-agent's TDD RED phase — without it, each developer-agent invents its own tests, often defaulting to obvious happy-path coverage that proves nothing about the behavioral invariants the specification intended. By contrast, test-design output ensures every test traces to a contract and every contract has one clear owner.
