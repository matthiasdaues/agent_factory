---
name: create-backlog
description: Break specification and architecture into a local backlog of markdown stories — EPICs and User Stories with INVEST criteria and MoSCoW priority.
category: planning
disable-model-invocation: true
---

# Create Backlog

Break the specification and architecture into a prioritised backlog of EPICs and User Stories, written as local markdown files under `backlog/`. Every story is a **tracer bullet** — a **vertical slice** that is independently implementable, traceable to its Use Case, and respects architectural boundaries.

Stories are project artifacts, not entries in an external tracker: one file per story, `backlog/ST-NNNN.md`, with strict frontmatter validated by `factory/scripts/backlog-lint`.

Read `docs/CONTEXT.md` if it exists — use the project's domain vocabulary in story titles and descriptions.

## Story file format

See [story.md template](../../rulebooks/templates/story.md) for the complete frontmatter schema and body structure.

**Key frontmatter fields:**

- `id`: ST-NNNN, zero-padded, unique; matches the filename
- `epic`: The EPIC this story belongs to (grouping label, not a separate file)
- `title`: What the story delivers
- `tier`: economy | standard | strong (model tier needed)
- `status`: pending | in_progress | review | blocked | done
- `deps`: Story IDs that block this one (optional)
- `traces`: Use Case / ADR / component IDs implemented (optional)
- `outputs`: Files the story produces

EPICs are **not** separate files — an EPIC is the `epic:` frontmatter value shared by its stories. MoSCoW priority lives in the prose body (the frontmatter schema is closed; `backlog-lint` rejects unknown fields).

## Step 1 — Define EPICs

Read `docs/spec/actor-goal-list.md` and `docs/spec/use_cases/`. Group related User Goals into EPICs — each a coherent slice developable and demonstrable independently.

**Completion**: every User Goal belongs to exactly one EPIC (an `epic:` value).

## Step 2 — Break EPICs into User Stories

For each EPIC, create `backlog/ST-NNNN.md` stories meeting **INVEST** — particularly: Independent (dependencies explicit in `deps`), Small (one implementation session), Testable (acceptance criteria from the Gherkin scenarios).

Respect **Clean Architecture** layer boundaries — each story touches one layer, or crosses layers only through defined interfaces.

Each story records in `traces`: Use Case ID(s) it implements (e.g. `UC-01`, `UC-A2`), the arc42 component(s) it touches, and any constraining ADR(s).

Judge each story's `tier` (`economy | standard | strong`) — the model strength its work needs, same vocabulary as agent frontmatter's `tier`.

Format each story file via `factory/scripts/mdformat --number <path>` per [markdown-formatting.md](../../factory/rulebooks/conventions/markdown-formatting.md).

**Completion**: every User Goal covered by at least one story, all stories meet INVEST, `traces` and `tier` present.

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

## Done Check

- [ ] Every User Goal from the actor-goal list is covered by at least one story
- [ ] Stories meet INVEST criteria (especially: small and testable)
- [ ] Dependencies are explicit in `deps` — no hidden ordering assumptions
- [ ] Stories reference Use Case IDs in `traces` for traceability
- [ ] Stories respect architectural layer boundaries
- [ ] `factory/scripts/backlog-lint` reports zero errors
