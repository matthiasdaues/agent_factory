---
name: create-backlog
description: Break specification and architecture into a local backlog of markdown stories — EPICs and User Stories with INVEST criteria and MoSCoW priority.
category: planning
disable-model-invocation: false
---

# Create Backlog

Break the specification and architecture into a prioritised backlog of EPICs and User Stories, written as local markdown files under `backlog/`. The artifact chain is: scope map → `.feature` files → **`backlog/epics.md`** → individual `backlog/ST-NNNN.md` stories. The planning agent creates `epics.md` and the stories; the scope map and `.feature` files are inputs from the specification phase.

Every story is a **tracer bullet** — a **vertical slice** that is independently implementable, traceable to its Use Case, and respects architectural boundaries.

Stories are project artifacts, not entries in an external tracker: one file per story, `backlog/ST-NNNN.md`, with strict frontmatter validated by `factory/scripts/backlog-lint`.

Read `docs/CONTEXT.md` if it exists — use the project's domain vocabulary in story titles and descriptions.

Read `docs/charter/*.md` if charter files exist — the charter defines Epic 0 (foundational must-haves) and concrete implementation names (test framework, deployment target, API framework) to use in story acceptance criteria.

## Story file format

See [story.md template](../../rulebooks/templates/story.md) for the complete frontmatter schema and body structure.

**Key frontmatter fields:**

- `id`: ST-NNNN, zero-padded, unique; matches the filename
- `epic`: The EPIC this story belongs to (references a section in `backlog/epics.md`)
- `title`: What the story delivers
- `tier`: economy | standard | strong (model tier needed)
- `status`: pending | in_progress | review | blocked | done
- `deps`: Story IDs that block this one (optional)
- `traces`: Use Case / ADR / component IDs implemented (optional)
- `outputs`: Files the story produces — **including its test file(s)**, so `premerge-check --scope` covers them without manual widening

EPICs are documented in `backlog/epics.md` — each EPIC section carries actor goals, demo, scope, dependencies, boundaries, size, presentation, and a building-block inventory with capacity estimates. The `epic:` frontmatter value in each story references its parent EPIC by name. MoSCoW priority lives in the prose body (the frontmatter schema is closed; `backlog-lint` rejects unknown fields).

## Story composition rules

Three rules govern how stories are decomposed and written.

### Rule 1: Demo First

Write the Demo section before anything else. Two to four sentences: what a person can show after the story ships. Concrete values, walkthrough format.

**If you cannot write the demo, the story is not demo-able. Recut it.**

Every story delivers a capability a person can demonstrate. Infrastructure — markers, migrations, types, scaffolding — enters as a line item inside the story that needs it.

### Rule 2: Forward from Status Quo

Start every story by stating what exists now — including deliverables of all stories it depends on. End with what a person can do afterward that they cannot do today. The gap is the story's scope.

Chain stories so each one's deliverables become status quo for every story that depends on it. The dependency graph is a chain of accumulating status quos.

Spec rules are traces — evidence of coverage, not the decomposition axis. A story exists because it delivers a capability, not because a rule needs coverage.

**MUST NOT** decompose by layer. One story for types, one for schema, one for service, one for API, one for UI is horizontal decomposition — it produces stories that individually deliver nothing showable and violates the vertical-slice gate. Each story **MUST** cross all system boundaries its capability requires. Infrastructure (identity types, schema scaffolding, test markers, pre-commit fixes) enters as a line item inside the story that first uses it, never as a standalone story — unless the story belongs to Epic 0 (charter-derived foundational setup).

### Rule 3: Criteria Are Invariants

Each acceptance criterion is a falsifiable statement a test can prove or disprove:

- "X produces Y" (positive invariant)
- "X never Y" (negative invariant)
- "When X, then Y" (boundary condition)

Trace the scope-map rule parenthetically. Do not specify test paths, framework choices, or implementation approach.

## Step 0 — Survey the codebase skeleton

Before decomposing, read the existing codebase. List what exists: tables, routes, models, views, migrations, tests. This is the departure point — every story steps forward from here.

**Completion**: a concrete inventory of existing artifacts relevant to the spec scope.

## Step 1 — Define EPICs and identify Epic 0

Read `docs/spec/actor-goal-list.md` and `docs/spec/use_cases/`. Group related User Goals into EPICs — each a coherent slice developable and demonstrable independently. Document every EPIC in `backlog/epics.md` with: actor goals, demo, scope, dependencies, boundaries, size/story count, presentation (bullet summary of what shipping the EPIC proves), and a building-block inventory listing each story with its capacity tier and day-range estimate.

If charter files exist and Epic 0 stories are already in the backlog (created by the `capture-charter` completeness sweep), identify the final Epic 0 story (the last one chronologically). Feature stories derived from the charter's Feature List shall depend on this final Epic 0 story via `deps:` — ensuring foundational work completes before feature implementation begins.

**Completion**: every User Goal belongs to exactly one EPIC (an `epic:` value). If Epic 0 stories exist, feature stories carry appropriate `deps:` on the final Epic 0 story.

## Step 1.5 — Sketch vertical slices

Before writing any story files, sketch slice tables that force the vertical decomposition axis. This step has two sub-steps — EPIC-level slices first, then story-level slices per EPIC. Both use the same table format and the same gate.

**Glossary source:** read `docs/arc42/12_glossary.md` if it exists, otherwise `docs/CONTEXT.md`. When a capability or boundary name uses domain jargon, parenthesise a plain-English gloss on first use in the table (e.g. "DispatchLedger (YAML file tracking story status)").

**Boundary vocabulary:** derive boundary names from the project's architecture — components, containers, and deployment nodes in `docs/arc42/architecture.dsl` or the arc42 building-block and deployment views. Use the project's own names (e.g. `IngestPipeline`, `APIGateway`, `EventBus`), not generic layer labels like "backend" or "database."

### Step 1.5a — EPIC-level slice table

For each EPIC, write one row. Each row names the user-visible outcome the EPIC delivers, the system boundaries it crosses, and a one-sentence demo.

| #   | EPIC outcome (what a person can do after) | Boundaries crossed | Demo sentence |
| --- | ----------------------------------------- | ------------------ | ------------- |

**Gate:** every EPIC row must cross at least two system boundaries and have a concrete, showable demo. An EPIC that groups work by layer rather than by capability must be recut.

Present the table to the user for confirmation before proceeding to Step 1.5b.

### Step 1.5b — Story-level slice table (per EPIC)

For each confirmed EPIC, sketch a table of candidate stories before writing story files. Each row names a user-visible capability, the system boundaries it crosses, and a one-sentence demo.

| #   | Capability (what a person can do after) | Boundaries crossed | Demo sentence |
| --- | --------------------------------------- | ------------------ | ------------- |

If a candidate row touches only one boundary and delivers nothing a person can demonstrate, it is not a story — fold it into the first row that needs it as a line item.

**Gate:** every row crosses at least two system boundaries and has a concrete, showable demo. Present the table to the user for confirmation before proceeding to Step 2.

**Completion**: confirmed EPIC-level and story-level slice tables. Every slice crosses system boundaries and is independently demo-able.

## Step 2 — Break EPICs into User Stories

For each EPIC, create `backlog/ST-NNNN.md` stories meeting **INVEST** — particularly: Independent (dependencies explicit in `deps`), Small (one implementation session), Testable (acceptance criteria as falsifiable invariants).

Apply the **story composition rules**: write the Demo section first (Rule 1), define scope as a step forward from the status quo of depended-on stories (Rule 2), write acceptance criteria as invariants (Rule 3). Every story is a vertical slice that crosses all system boundaries its capability requires. A story that touches only one boundary (only schema, only service, only UI) and delivers nothing a person can demonstrate is not a story — fold it into the first story that needs it as a line item.

Each story records in `traces`: Use Case ID(s) it implements (e.g. `UC-01`, `UC-A2`), the arc42 component(s) it touches, and any constraining ADR(s).

Judge each story's `tier` (`economy | standard | strong`) — the model strength its work needs, same vocabulary as agent frontmatter's `tier`.

When charter files exist, extract concrete implementation names (test framework, deployment target, API framework) and use them in acceptance criteria instead of placeholders. Example: rather than "the feature must be tested", use "the feature must be tested with pytest and deployed to AWS Lambda".

For each story, check whether existing tests in the codebase already cover its acceptance criteria. If pre-existing tests match the acceptance criteria, record their file paths in the story's `tests:` field (optional frontmatter, a list of test file paths or test identifiers).

Format each story file via `factory/scripts/mdformat --number <path>` per [markdown-formatting.md](../../factory/rulebooks/conventions/markdown-formatting.md).

**Completion**: every User Goal covered by at least one story, all stories meet INVEST, `traces` and `tier` present. Pre-existing tests are recorded in `tests:` where applicable.

## Step 3 — Prioritise with MoSCoW

Record each story's **MoSCoW** priority in its body: `**Priority:** must-have | should-have | could-have | wont-have`.

**Completion**: every story states a MoSCoW priority.

## Step 4 — Mark dependencies

List blocking stories in `deps` (by `ST-NNNN` id). Run `factory/scripts/backlog-lint --backlog-dir backlog` — it checks acyclicity — and fix any errors.

Present the complete backlog to the user. Ask:

- _"Are the MoSCoW priorities correct?"_
- _"Any missing stories?"_
- _"Should any dependencies be reordered?"_

**Completion**: `backlog-lint` reports zero errors, dependencies explicit, no circular chains, user confirms the backlog.

## Step 5 — Apply quality gates

Review every story through two lenses before presenting to the user:

**Junior Clarity:** Read the story as a junior developer. Can you start working right now — do you know which file to open first, what the first test asserts, and what "done" looks like? If not, the story is underspecified.

**Senior Acceptance:** Read the story as a senior grooming the backlog. Would you hand this to your team without a follow-up conversation — is the scope bounded, the demo concrete, every criterion testable, and nothing left to interpret? If not, the story is not ready.

**Completion**: every story passes both gates.

## Done Check

- [ ] Every User Goal from the actor-goal list is covered by at least one story
- [ ] EPIC-level and story-level slice tables confirmed by user (Step 1.5)
- [ ] Every EPIC and story crosses at least two system boundaries
- [ ] No horizontal (single-boundary) stories exist outside Epic 0
- [ ] Stories meet INVEST criteria (especially: small and testable)
- [ ] Dependencies are explicit in `deps` — no hidden ordering assumptions
- [ ] Stories reference Use Case IDs in `traces` for traceability
- [ ] Every story has a Demo section describing a concrete, showable capability
- [ ] Every story passes Junior Clarity and Senior Acceptance gates
- [ ] `factory/scripts/backlog-lint` reports zero errors
