---
name: create-backlog-epics
description: "Survey codebase, read specs, and present the EPIC slicing approach for user approval. Phase 1 of 4 in the create-backlog sequence."
category: planning
disable-model-invocation: false
---

# Create Backlog — Phase 1: EPIC Slicing Approach

Survey the codebase and specification, then present the proposed EPIC decomposition for user approval. This is phase 1 of the [create-backlog sequence](../create-backlog/SKILL.md#operational-sequence). Story format, composition rules, and the done check live in the [parent skill](../create-backlog/SKILL.md).

## Step 0 — Survey the codebase (ground truth)

This step is the foundation — everything that follows is a delta from what it finds.

Follow the technical concerns in `docs/agent-context.md` to locate source directories, test roots, and infrastructure paths. Read the existing codebase at those paths. Inventory what exists: tables, routes, models, views, migrations, tests, configuration, scripts. Note which capabilities already work, which are partially built, and which are absent. This inventory is the departure point for every EPIC and every story.

**Completion**: a concrete inventory of existing artifacts relevant to the spec scope, structured so each item can be referenced as status quo in later stories.

## Step 1 — Propose EPIC groupings (delta from code to spec)

Read `docs/spec/scope-map.md` and the `.feature` files under `docs/spec/` (factory-canonical). Read `docs/agent-context.md` and follow all concern sections — domain concerns carry the project vocabulary and supplementary specs; technical concerns carry architecture views and conventions; cross-cutting concerns define Epic 0 (foundational must-haves). Follow each concern's `Read:` paths to discover what the project has documented.

Compare the spec target against the codebase inventory from Step 0. The gap — what the spec requires that the code does not yet do — is the work to decompose. Group related gaps into EPICs, each a coherent slice developable and demonstrable independently. Capabilities that already exist in the code are not stories; they are status quo.

If context files exist and Epic 0 stories are already in the backlog (created by the `capture-context` completeness sweep), identify the final Epic 0 story (the last one chronologically). Feature EPICs depend on Epic 0 completion.

## Step 1.5a — EPIC-level slice table

**Glossary source:** follow the domain concerns in `docs/agent-context.md` to locate the project glossary (typically the arc42 glossary or CONTEXT.md). When a capability or boundary name uses domain jargon, parenthesise a plain-English gloss on first use in the table (e.g. "DispatchLedger (YAML file tracking story status)").

**Demo vocabulary:** the demo sentence must use only terms already glossed or self-evident. If the demo names a concept the reader hasn't met, gloss it inline or restructure the sentence.

**Boundary vocabulary:** derive boundary names from the project's architecture. Follow the technical concerns in `docs/agent-context.md` to locate architecture views (Structurizr DSL, building-block views, deployment views). Use the project's own component and container names (e.g. `IngestPipeline`, `APIGateway`, `EventBus`), not generic layer labels like "backend" or "database."

For each EPIC, write one row. Each row names the user-visible outcome the EPIC delivers, the system boundaries it crosses, and a one-sentence demo.

| #   | EPIC outcome (what a person can do after) | Boundaries crossed | Demo sentence |
| --- | ----------------------------------------- | ------------------ | ------------- |

**Title convention:** The EPIC outcome column and every story title use an active verb phrase — what a person or system *does*, not what a thing *is*. "Activate a Domain with an immutable timezone", not "Domain activation with immutable timezone." This applies to the `title:` frontmatter, the `# ` heading, and the EPIC outcome column.

**Gate:** every EPIC row must cross at least two system boundaries and have a concrete, showable demo. An EPIC that groups work by layer rather than by capability must be recut.

## Quality gate

Before presenting, review the slice table through two lenses:

**Junior Clarity checklist:**

1. Every domain term, protocol concept, and component name is glossed on first use in the table (parenthetical plain-English explanation).
2. Demo sentences use only glossed or self-evident terms.
3. Narrative text avoids dense chains of component names — save DSL identifiers for the Boundaries column.

If any item fails, revise before presenting.

**Senior Acceptance:** Would a senior hand this decomposition to the team without a follow-up conversation? Is each EPIC bounded, demo-able, and free of ambiguity? If not, recut. Additionally: can each demo sentence be read as a concrete acceptance criterion without referencing internal implementation details that only exist in the architecture DSL?

Present the table to the user for confirmation.

## This skill ends here

The EPIC slicing approach is delivered. **Do not write `backlog/epics.md` yet.** The user confirms or adjusts the approach, then invokes the next skill: [`create-backlog-write-epics`](../create-backlog-write-epics/SKILL.md).
