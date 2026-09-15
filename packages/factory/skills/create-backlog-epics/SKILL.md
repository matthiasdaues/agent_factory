______________________________________________________________________

## name: create-backlog-epics description: "Survey user capabilities, map them against the codebase, and present the EPIC slicing approach for user approval. Phase 1 of 4 in the create-backlog sequence." category: planning

# Create Backlog — Phase 1: EPIC Slicing Approach

This skill surveys user capabilities and the codebase, then presents the proposed EPIC decomposition for user approval. It is phase 1 of the [create-backlog sequence](../create-backlog/SKILL.md#operational-sequence). Story format, composition rules, and the done check live in the [parent skill](../create-backlog/SKILL.md).

## Writing constraint

The [writing quality gates](../../rulebooks/conventions/writing-quality-gates.md) are read before composing either table. All four gates apply to every capability row, every EPIC row, and all accompanying terminal prose. No row reaches terminal output until it passes. A failing row is revised before presenting.

## Step 0a — Survey the capability set

The active feature is resolved from the user's request or accepted proposal. Other `.feature` files provide context but do not contribute capability rows unless explicitly included.

The inputs are `docs/spec/scope-map.md` and the active `.feature` file under `docs/spec/` (factory-canonical). `docs/agent-context.md` domain concerns locate the project glossary and vocabulary. Supplementary specifications (state machines, interface contracts, validation models) are not read until Step 0b. Technical concerns, architecture views, and cross-cutting concerns are not read until Step 0b.

The output is a capability table. Each row describes one thing a user can do when this feature is complete. The row names what the person does, through what shipped entry point, and what result they see. Component names do not appear in Person, User action, or Observable result. They may appear in Supporting rules. System roles do not stand in for users. Internal system behaviors support capabilities — they are not capabilities.

Each row carries a stable ID (CAP-01, CAP-02, …). The "Status quo" and "Supporting rules" columns stay empty until Step 0b.

| ID  | Person | Shipped entry point | User action | Observable result | Status quo | Supporting rules |
| --- | ------ | ------------------- | ----------- | ----------------- | ---------- | ---------------- |

The table is incomplete at this point. Step 0b fills the remaining columns before presentation.

**Completion**: a capability table with IDs, person, entry point, action, and result filled in. Status quo and supporting rules are pending.

## Step 0b — Survey the codebase against each capability

The technical concerns and cross-cutting concerns in `docs/agent-context.md` are read now. Technical concerns locate source directories, test roots, and infrastructure paths. Cross-cutting concerns define Epic 0 (foundational must-haves). For each capability row, the relevant codebase determines two columns:

- **Status quo** — "exists," "partial," "absent," or "gap." A capability is "exists" only when its complete specified observable behavior already works. An existing entry point with missing behavior is "partial." A capability is "gap" when an unresolved specification decision prevents a complete slice.
- **Supporting rules** — which specification rules this capability requires and whether each has an existing implementation. Specification rules include engine decisions, adapter behaviors, validator checks, and schema constraints.

Every specification rule in the active feature must be allocated. Rules from contextual features are excluded unless the user included those features. No EPICs are formed while a rule remains unallocated. Each unallocated rule is assigned as supporting or cross-cutting scope, added as a missing capability, or presented as a specification gap. A specification gap does not stop the procedure. The gap is recorded in the capability table with status `gap` and a reference to the unresolved decision. Any EPIC that includes a gap-status capability carries the gap as an open issue in the EPIC table. The EPIC is presented but marked as blocked on that gap.

Capabilities whose status quo is "exists" are not stories. Capabilities marked "partial," "absent," or "gap" enter EPIC grouping.

Steps 0a and 0b run without a pause. The completed capability table is not presented alone — it appears together with the EPIC table as this skill's terminal output.

**Completion**: all columns filled. No unallocated specification rules remain.

## Step 1 — Propose EPIC groupings

An EPIC groups capabilities that form one coherent user journey or deliver one useful outcome. Shared infrastructure does not justify grouping. Unrelated journeys may share an adapter or schema without belonging in the same EPIC. Backend rules from Step 0b are supporting scope. They never seed an EPIC.

An engine, adapter, validator, schema, or migration rule that no user capability owns cannot originate an EPIC. Such a rule is a specification gap.

If context files exist and Epic 0 stories are already in the backlog (created by the `capture-context` completeness sweep), the final Epic 0 story (chronologically last) is identified. Feature EPICs depend on Epic 0 completion.

## Step 1.5a — EPIC-level slice table

**Glossary source:** the project glossary is located through the domain concerns in `docs/agent-context.md` (typically the arc42 glossary or CONTEXT.md). Domain jargon in a capability or boundary name gets a plain-English gloss on first use (e.g. "DispatchLedger (YAML file tracking story status)").

**Demo vocabulary:** the demo sentence uses only terms already glossed or self-evident. An unmet concept is glossed inline or the sentence is restructured.

**Demo verification:** the demo verifies its result through a shipped interface, not by inspecting persistence. The architecture path may end at a state file or database. The demo confirms the result as a user would — reopening a workstream, running a query, or reading terminal output.

**Boundary vocabulary:** boundary names come from the project's architecture views (Structurizr DSL, building-block views, deployment views), located through `docs/agent-context.md` technical concerns. The project's own component and container names apply (e.g. `IngestPipeline`, `APIGateway`, `EventBus`), not generic layer labels.

An EPIC is a vertical slice. It starts where the user touches the system, passes through the logic that decides, and ends where the result is stored or shown. Every EPIC is demo-able: a person performs an action and sees the outcome without depending on a later EPIC.

Each EPIC occupies one row. The row names its source capabilities by ID, its primary backend rules, what the user can do after, the path through the system, and a one-sentence demo.

| #   | Capabilities | Primary backend rules | What the user can do after | Path through the system | Demo sentence | Open issues |
| --- | ------------ | --------------------- | -------------------------- | ----------------------- | ------------- | ----------- |

The Open issues column is empty for an unblocked EPIC. A gap-status capability adds its unresolved-decision reference and marks the EPIC blocked. The blocked row remains provisional until the gap is resolved and the complete vertical slice passes the gates below.

**Outcome column:** an active verb phrase — what a person *does*, not what a thing *is*. "Activate a domain with an immutable timezone", not "Domain activation with immutable timezone." The same phrasing applies to the `title:` frontmatter and the `# ` heading.

**Path column:** a vertical trace from entry point to persistence. Three things appear in order:

1. what the user touches (command, menu option, skill invocation);
2. what decides or transforms (engine, validator, evaluator);
3. where the result lands (state file, index, report, screen output).

The project's own component names apply, not generic labels. Two components inside the same step do not count as two entries.

**Gate — each rule is a hard pass/fail:**

1. Each EPIC traces a path from user entry through decision logic to a stored or shown result. The demo is concrete and showable. Each capability in the EPIC follows the complete user → decision → result path. One valid path does not cover unrelated capabilities.
2. The path crosses at least two distinct steps. An entry point and a decision step in the same module do not count. An EPIC whose path stays inside one layer (engine-only, persistence-only) is a horizontal — recut it.
3. A person can use this EPIC's result without any later EPIC. Test: "Can someone do the demo with only this EPIC built?" A "no" means the EPIC is incomplete.
4. An EPIC that groups work by layer rather than by use case is recut.
5. A fully serial dependency chain (each EPIC depends on the previous, no parallelism) signals horizontal slicing. Thin vertical slices — each delivering one end-to-end use case — are revisited before presenting.
6. A person describes this EPIC's result without naming implementation components. An outcome that only makes sense in terms of engines, adapters, schemas, or validators is an internal rule — recut it. The outcome changes what the person accomplishes. An artifact-health diagnostic is not a capability unless it is a supported product interface.
7. Each EPIC traces back to a user capability in Step 0a, not to a backend rule. Each backend rule has one primary owning EPIC — the journey that first requires it. Cross-cutting rules may constrain other EPICs without duplicating ownership. Unallocated rules are missing capabilities or specification gaps.

**Example — bad vs. good:**

Bad: "Validate the delivery model against versioned schemas" — starts from an internal rule. The outcome names components. No user entry point. Capabilities column is empty — no user origin exists.

| #   | Capabilities | Primary backend rules            | What the user can do after  | Path through the system                            | Demo sentence                                   | Open issues |
| --- | ------------ | -------------------------------- | --------------------------- | -------------------------------------------------- | ----------------------------------------------- | ----------- |
| 1   | —            | Delivery model schema validation | Validate the delivery model | transition-lint → Cycle Model Loader → diagnostics | Run transition-lint and see validation results. | —           |

Good: "Check which cycle the evidence supports and choose the next one" — starts from what the user does. The model validation happens inside. Capabilities and primary rules are traceable.

| #   | Capabilities   | Primary backend rules              | What the user can do after                                      | Path through the system                                                                                                  | Demo sentence                                                                                                            | Open issues |
| --- | -------------- | ---------------------------------- | --------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------ | ----------- |
| 1   | CAP-03, CAP-04 | Readiness evaluation, route guards | Check which cycle the evidence supports and choose the next one | `cycle select` → Readiness Evaluator recommends routes → chosen cycle and evidence appear in workstream state and output | Run `cycle select`, choose REALIZE despite its warning, then reopen the workstream and see REALIZE as its current cycle. | —           |

The completed capability table and the EPIC table are presented together as this skill's terminal output.

## This skill ends here

The EPIC slicing approach is delivered. **`backlog/epics.md` is not written yet.** The user confirms or adjusts the approach, then invokes the next skill: [`create-backlog-write-epics`](../create-backlog-write-epics/SKILL.md).
