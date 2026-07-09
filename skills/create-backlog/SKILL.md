---
name: create-backlog
description: Break specification and architecture into a local backlog of markdown stories — EPICs and User Stories with INVEST criteria and MoSCoW priority.
category: planning
disable-model-invocation: true
---

# Create Backlog

Break the specification and architecture into a prioritised backlog of EPICs and User Stories, written as local markdown files under `backlog/`. Every story is a **tracer bullet** — a **vertical slice** that is independently implementable, traceable to its Use Case, and respects architectural boundaries.

Stories are project artifacts, not entries in an external tracker: one file per story, `backlog/ST-NNNN.md`, with strict frontmatter validated by `scripts/backlog-lint`.

Read `CONTEXT.md` if it exists — use the project's domain vocabulary in story titles and descriptions.

## Story file format

```markdown
---
id: ST-0001                       # ST-NNNN, zero-padded, unique; matches the filename
epic: Domain Entities             # the EPIC this story belongs to (a grouping label, not a separate file)
title: Define domain entity dataclasses
classification: trivial           # trivial | standard | hard — difficulty band, drives the model tier
status: pending                   # pending | in-progress | done | blocked
deps: [ST-0002]                   # story ids that block this one (optional)
traces: [UC-02, ADR-0003]         # Use Case / ADR / component ids this story implements (optional)
outputs: [src/orchestrator/entities.py]   # files the story is expected to produce
---

# <title>

<what the story delivers, in the domain's language>

**Priority:** must-have          # MoSCoW — must-have | should-have | could-have | wont-have

## Acceptance Criteria

- <criterion derived from the Gherkin scenarios / postconditions>
```

EPICs are **not** separate files — an EPIC is the `epic:` frontmatter value shared by its stories. MoSCoW priority lives in the prose body (the frontmatter schema is closed; `backlog-lint` rejects unknown fields).

## Step 1 — Define EPICs

Read `docs/spec/actor-goal-list.md` and `docs/spec/use_cases/`. Group related User Goals into EPICs — each a coherent slice developable and demonstrable independently.

**Completion**: every User Goal belongs to exactly one EPIC (an `epic:` value).

## Step 2 — Break EPICs into User Stories

For each EPIC, create `backlog/ST-NNNN.md` stories meeting **INVEST** — particularly: Independent (dependencies explicit in `deps`), Small (one implementation session), Testable (acceptance criteria from the Gherkin scenarios).

Respect **Clean Architecture** layer boundaries — each story touches one layer, or crosses layers only through defined interfaces.

Each story records in `traces`: Use Case ID(s) it implements (e.g. `UC-01`, `UC-A2`), the arc42 component(s) it touches, and any constraining ADR(s).

Judge each story's `classification` (`trivial | standard | hard`) — the difficulty band the model matrix maps to a tier.

Format each story file via `scripts/mdformat --number <path>` per [markdown-formatting.md](../../rulebooks/markdown-formatting.md).

**Completion**: every User Goal covered by at least one story, all stories meet INVEST, `traces` and `classification` present.

## Step 3 — Prioritise with MoSCoW

Record each story's **MoSCoW** priority in its body: `**Priority:** must-have | should-have | could-have | wont-have`.

**Completion**: every story states a MoSCoW priority.

## Step 4 — Mark dependencies

List blocking stories in `deps` (by `ST-NNNN` id). Run `scripts/backlog-lint --backlog-dir backlog` — it checks acyclicity — and fix any errors.

Present the complete backlog to the user. Ask:

- _"Are the MoSCoW priorities correct?"_
- _"Any missing stories?"_
- _"Should any dependencies be reordered?"_

**Completion**: `backlog-lint` reports zero errors, dependencies explicit, no circular chains, user confirms the backlog.

## Done Check

- [ ] Every User Goal from the actor-goal list is covered by at least one story
- [ ] Stories meet INVEST criteria (especially: small and testable)
- [ ] Dependencies are explicit in `deps` — no hidden ordering assumptions
- [ ] Stories reference Use Case IDs in `traces` for traceability
- [ ] Stories respect architectural layer boundaries
- [ ] `scripts/backlog-lint` reports zero errors
