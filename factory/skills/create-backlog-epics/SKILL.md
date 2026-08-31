---
name: create-backlog-epics
description: "Survey codebase, read specs, and present the EPIC slicing approach for user approval. Phase 1 of 4 in the create-backlog sequence."
category: planning
disable-model-invocation: false
---

# Create Backlog — Phase 1: EPIC Slicing Approach

Survey the codebase and specification, then present the proposed EPIC decomposition for user approval. This is phase 1 of the [create-backlog sequence](../create-backlog/SKILL.md#operational-sequence). Story format, composition rules, and the done check live in the [parent skill](../create-backlog/SKILL.md).

## Step 0 — Survey the codebase skeleton

Before decomposing, read the existing codebase. List what exists: tables, routes, models, views, migrations, tests. This is the departure point — every story steps forward from here.

**Completion**: a concrete inventory of existing artifacts relevant to the spec scope.

## Step 1 — Propose EPIC groupings

Read `docs/spec/actor-goal-list.md` and `docs/spec/use_cases/`. Read `docs/CONTEXT.md` if it exists — use the project's domain vocabulary. Read `docs/charter/*.md` if charter files exist — the charter defines Epic 0 (foundational must-haves).

Group related User Goals into EPICs — each a coherent slice developable and demonstrable independently.

If charter files exist and Epic 0 stories are already in the backlog (created by the `capture-charter` completeness sweep), identify the final Epic 0 story (the last one chronologically). Feature EPICs depend on Epic 0 completion.

## Step 1.5a — EPIC-level slice table

**Glossary source:** read `docs/arc42/12_glossary.md` if it exists, otherwise `docs/CONTEXT.md`. When a capability or boundary name uses domain jargon, parenthesise a plain-English gloss on first use in the table (e.g. "DispatchLedger (YAML file tracking story status)").

**Boundary vocabulary:** derive boundary names from the project's architecture — components, containers, and deployment nodes in `docs/arc42/architecture.dsl` or the arc42 building-block and deployment views. Use the project's own names (e.g. `IngestPipeline`, `APIGateway`, `EventBus`), not generic layer labels like "backend" or "database."

For each EPIC, write one row. Each row names the user-visible outcome the EPIC delivers, the system boundaries it crosses, and a one-sentence demo.

| #   | EPIC outcome (what a person can do after) | Boundaries crossed | Demo sentence |
| --- | ----------------------------------------- | ------------------ | ------------- |

**Title convention:** The EPIC outcome column and every story title use an active verb phrase — what a person or system *does*, not what a thing *is*. "Activate a Domain with an immutable timezone", not "Domain activation with immutable timezone." This applies to the `title:` frontmatter, the `# ` heading, and the EPIC outcome column.

**Gate:** every EPIC row must cross at least two system boundaries and have a concrete, showable demo. An EPIC that groups work by layer rather than by capability must be recut.

## Quality gate

Before presenting, review the slice table through two lenses:

**Junior Clarity:** Can a junior developer read this table and understand what each EPIC delivers, which parts of the system it touches, and what "done" looks like? If not, the EPIC description is underspecified.

**Senior Acceptance:** Would a senior hand this decomposition to the team without a follow-up conversation? Is each EPIC bounded, demo-able, and free of ambiguity? If not, recut.

Present the table to the user for confirmation.

## This skill ends here

The EPIC slicing approach is delivered. **Do not write `backlog/epics.md` yet.** The user confirms or adjusts the approach, then invokes the next skill: [`create-backlog-write-epics`](../create-backlog-write-epics/SKILL.md).
