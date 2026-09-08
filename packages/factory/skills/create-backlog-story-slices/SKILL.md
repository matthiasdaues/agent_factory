---
name: create-backlog-story-slices
description: "Read confirmed backlog/epics.md, sketch story-level slice tables per EPIC, and present them for user approval. Phase 3 of 4 in the create-backlog sequence."
category: planning
disable-model-invocation: false
---

# Create Backlog — Phase 3: Story Slicing Approach

Sketch story-level slice tables for each confirmed EPIC and present them for user approval. This is phase 3 of the [create-backlog sequence](../create-backlog/SKILL.md#operational-sequence). Story format, composition rules, and the done check live in the [parent skill](../create-backlog/SKILL.md).

**Prerequisite:** `backlog/epics.md` exists and has been confirmed by the user (output of [`create-backlog-write-epics`](../create-backlog-write-epics/SKILL.md)).

## Step 1.5b — Story-level slice table (per EPIC)

Follow the concern sections in `docs/agent-context.md` to locate domain vocabulary, architecture views, and project conventions relevant to each EPIC. For each EPIC, revisit the codebase inventory from Phase 1 — identify which files, modules, and tests already exist that the EPIC's stories will extend or modify. Each story slice is a step forward from this concrete base, not from an aspirational architecture.

**Glossary source:** follow the domain concerns in `docs/agent-context.md` to locate the project glossary. When a capability or boundary name uses domain jargon, parenthesise a plain-English gloss on first use in the table.

**Boundary vocabulary:** derive boundary names from the project's architecture. Follow the technical concerns in `docs/agent-context.md` to locate architecture views. Use the project's own component and container names, not generic layer labels.

For each confirmed EPIC, sketch a table of candidate stories. Each row names a user-visible capability, the system boundaries it crosses, and a one-sentence demo.

| #   | Capability (what a person can do after) | Boundaries crossed | Demo sentence |
| --- | --------------------------------------- | ------------------ | ------------- |

If a candidate row touches only one boundary and delivers nothing a person can demonstrate, it is not a story — fold it into the first row that needs it as a line item.

**Title convention:** The Capability column uses an active verb phrase — this becomes the story title. "Deliver a command and accept it on the Agent", not "Command delivery and Agent acceptance."

**Gate:** every row crosses at least two system boundaries and has a concrete, showable demo.

## Quality gate

Before presenting, review every slice table through two lenses:

**Junior Clarity:** Can a junior developer read each row and understand what capability it delivers, which parts of the system it touches, and what the first test would assert? If not, the slice is underspecified.

**Senior Acceptance:** Would a senior hand these slices to the team without a follow-up conversation? Is each slice bounded, independently demo-able, and free of hidden dependencies? If not, recut.

Present the tables to the user for confirmation.

## This skill ends here

The story slicing approach is delivered. **Do not write story files yet.** The user confirms or adjusts the slices, then invokes the next skill: [`create-backlog-stories`](../create-backlog-stories/SKILL.md).
