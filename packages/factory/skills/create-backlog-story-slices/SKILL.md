---
name: create-backlog-story-slices
description: "Read confirmed backlog/epics.md, sketch story-level slice tables per EPIC, and present them for user approval. Phase 3 of 4 in the create-backlog sequence."
category: planning
---

# Create Backlog — Phase 3: Story Slicing Approach

Sketch story-level slice tables for each confirmed EPIC and present them for user approval. This is phase 3 of the [create-backlog sequence](../create-backlog/SKILL.md#operational-sequence). Story format, composition rules, and the done check live in the [parent skill](../create-backlog/SKILL.md).

**Prerequisite:** `backlog/epics.md` exists and has been confirmed by the user (output of [`create-backlog-write-epics`](../create-backlog-write-epics/SKILL.md)).

## Step 1.5b — Story-level slice table (per EPIC)

Follow the concern sections in `docs/agent-context.md` to locate domain vocabulary, architecture views, and project conventions relevant to each EPIC. For each EPIC, revisit the codebase inventory from Phase 1 — identify which files, modules, and tests already exist that the EPIC's stories will extend or modify. Each story slice is a step forward from this concrete base, not from an aspirational architecture.

**Glossary source:** follow the domain concerns in `docs/agent-context.md` to locate the project glossary. When a capability or boundary name uses domain jargon, parenthesise a plain-English gloss on first use in the table.

**Boundary vocabulary:** derive boundary names from the project's architecture. Follow the technical concerns in `docs/agent-context.md` to locate architecture views. Use the project's own component and container names, not generic layer labels.

For each confirmed EPIC, sketch a table of candidate stories. Each row names an actor-visible capability, the entry point, the outcome, and a demo that uses the shipped interface.

| #   | Capability | Actor / consumer | Trigger or entry point | Observable outcome | Production path | Demo |
| --- | ---------- | ---------------- | ---------------------- | ------------------ | --------------- | ---- |

**Capability column:** active verb phrase — this becomes the story title. "Start a workstream and select any cycle", not "Workstream creation and cycle selection."

**Actor / consumer column:** the person, agent, or external system that initiates or consumes the capability.

**Production path column:** trace the path from trigger to outcome through the system's own component names. Name the entry point, the deciding component, and where the result lands.

**Goal derivation:** the combination of Actor, Trigger, Outcome, and Path seeds the story's Goal section in Phase 4.

If a candidate row has no named actor or external consumer, no supported entry point, or no externally observable outcome, it is not a story — fold it into the first row that needs it as a line item.

**Gate:** every row must satisfy all of the following:

1. It names an actor or external consumer, a supported entry point or trigger, and an externally observable outcome or rejection.
2. It implements the complete path through every boundary required for that outcome.
3. The demo must use the shipped interface, not source inspection, direct invocation of internals, database inspection, or a test suite. Tests verify a story; test output is not the capability the story delivers.
4. **Isolation check:** assume only the current baseline, declared dependencies, and this candidate story are shipped. Can the named actor complete the demo through a supported interface? If not, merge or recut the story.

**Story count:** the EPIC's size estimate is an estimate, never a target. Preserve natural capability seams even when the resulting count differs. Do not split an end-to-end capability into incomplete implementation units to match the estimate. If Phase 3 produces a different count, explain the variance and update `backlog/epics.md` (the building-block inventory and size field) after stakeholder confirmation.

## Quality gate

Read [writing-quality-gates.md](../../rulebooks/conventions/writing-quality-gates.md) now and hold every rule as a writing constraint. Compose every slice-table row with all four gates active — no row reaches terminal output or a file until it passes. Revise any row that fails before presenting.

Present the tables to the user for confirmation.

## This skill ends here

The story slicing approach is delivered. **Do not write story files yet.** The user confirms or adjusts the slices, then invokes the next skill: [`create-backlog-stories`](../create-backlog-stories/SKILL.md).
