---
name: create-backlog-epics
description: "Survey codebase, read specs, and present the EPIC slicing approach for user approval. Phase 1 of 4 in the create-backlog sequence."
category: planning
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

Each EPIC is a vertical slice — it starts where the user touches the system, passes through the logic that decides, and ends where the result is stored or shown. Every EPIC must be demo-able: a person performs an action and sees the outcome without depending on a later EPIC.

For each EPIC, write one row. Each row names what the user can do after, the path the action takes through the system, and a one-sentence demo.

| #   | What the user can do after | Path through the system | Demo sentence |
| --- | -------------------------- | ----------------------- | ------------- |

**Outcome column:** use an active verb phrase — what a person *does*, not what a thing *is*. "Activate a domain with an immutable timezone", not "Domain activation with immutable timezone." This applies to the `title:` frontmatter, the `# ` heading, and the outcome column.

**Path column:** trace the vertical from entry point to persistence. Name three things in order: (1) what the user touches (command, menu option, skill invocation), (2) what decides or transforms (engine, validator, evaluator), (3) where the result lands (state file, index, report, screen output). Use the project's own component names, not generic labels. Two components inside the same step do not count as two entries in the path.

**Gate — each rule is a hard pass/fail:**

1. Every EPIC row traces a path from user entry through decision logic to a stored or shown result, and has a concrete, showable demo.
2. The path must cross at least two distinct steps — an entry point and a decision step in the same module do not count. An EPIC whose path stays inside one layer (engine-only, persistence-only) is a horizontal, not a vertical — recut it.
3. A person must be able to use this EPIC's result without any later EPIC. Test: "Can someone do the demo with only this EPIC built?" If the answer is no, the EPIC is incomplete.
4. An EPIC that groups work by layer rather than by use case must be recut.
5. If the proposed EPICs form a fully serial dependency chain (each depends on the previous, no parallelism), flag this as likely horizontal slicing. Revisit whether thin vertical slices — each delivering one end-to-end use case — are possible before presenting.

## Quality gate

Read [writing-quality-gates.md](../../rulebooks/conventions/writing-quality-gates.md) now and hold every rule as a writing constraint. Compose every slice-table row with all four gates active — no row reaches terminal output or a file until it passes. Revise any row that fails before presenting.

Present the table to the user for confirmation.

## This skill ends here

The EPIC slicing approach is delivered. **Do not write `backlog/epics.md` yet.** The user confirms or adjusts the approach, then invokes the next skill: [`create-backlog-write-epics`](../create-backlog-write-epics/SKILL.md).
