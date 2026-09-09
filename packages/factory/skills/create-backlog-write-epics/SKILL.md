---
name: create-backlog-write-epics
description: "Write backlog/epics.md from the approved EPIC slicing approach. Phase 2 of 4 in the create-backlog sequence."
category: planning
disable-model-invocation: false
---

# Create Backlog — Phase 2: Write EPICs

Write `backlog/epics.md` from the approved EPIC slicing approach. This is phase 2 of the [create-backlog sequence](../create-backlog/SKILL.md#operational-sequence). Story format, composition rules, and the done check live in the [parent skill](../create-backlog/SKILL.md).

Write for an international Team whose members have English as a common, but not as a native language.

**Prerequisite:** the EPIC-level slice table has been approved by the user (output of [`create-backlog-epics`](../create-backlog-epics/SKILL.md)).

## Step 1 — Write backlog/epics.md

Follow the concern sections in `docs/agent-context.md` to locate domain vocabulary, supplementary specs, and architecture views relevant to each EPIC. Use concern `Read:` paths — not hardcoded file paths — to discover project-native knowledge.

Document every confirmed EPIC in `backlog/epics.md` with:

- Actor goals
- Demo (what a person can show after shipping the EPIC)
- Scope
- Dependencies on other EPICs
- Boundaries (system boundaries the EPIC crosses)
- Size / story count estimate
- Building-block inventory listing each anticipated story with its capacity tier, day-range estimate, and Goal (one sentence of concrete behavior). The Goal seeds the story's Goal section in Phase 4. For each block, note what already exists in the codebase (files, modules, tests) and what the story adds or changes.

**Domain Rules subsection:** Each EPIC gains a Domain Rules subsection listing the invariants that govern the EPIC's stories as a bullet list. These invariants capture the business or technical rules that constrain how stories within the EPIC behave. This subsection seeds each story's Domain Rule section in Phase 4.

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
6. The building-block inventory includes a Goal column with one sentence of concrete behavior for each anticipated story.
7. Each EPIC has a Domain Rules subsection that lists the invariants governing its stories.

If any item fails, revise before presenting.

**Senior Acceptance:** Would a senior hand this EPIC breakdown to the team without a follow-up conversation? Is the scope bounded, the demo concrete, and the dependency chain clear? If not, revise. Additionally: the demo steps, when read as a manual test, exercise the EPIC's core scenario end-to-end without referencing internal implementation details that only exist in the architecture DSL.

Present `backlog/epics.md` to the user for confirmation.

## This skill ends here

The EPIC artifact is written. **Do not proceed to story-level slicing.** The user confirms or adjusts `backlog/epics.md`, then invokes the next skill in the sequence: the testability probe (phase 2.5).

## Next: Invoke testability-probe

Before proceeding to story slicing (phase 3), invoke [`testability-probe`](../testability-probe/SKILL.md) to assess each EPIC's testability and resolve contract ownership backlog-wide. The probe writes a testability paragraph and ownership table per EPIC into `backlog/epics.md` — catching untestable scoping before stories are cut and ensuring every traced contract has exactly one test owner. This step is mandatory; skipping it lets planning proceed without the gate that catches scoping defects.
