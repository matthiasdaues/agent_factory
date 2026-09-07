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

## Operational sequence

The operational procedure is split into four phase-gated skills. Each skill ends when its output is delivered; the user confirms or adjusts before invoking the next. This structural separation enforces the pause points that prose instructions cannot.

| Phase | Skill                                                                    | What happens                                   | Output                                     |
| ----- | ------------------------------------------------------------------------ | ---------------------------------------------- | ------------------------------------------ |
| 1     | [`create-backlog-epics`](../create-backlog-epics/SKILL.md)               | Survey codebase, propose EPIC slicing approach | EPIC slice table for approval              |
| 2     | [`create-backlog-write-epics`](../create-backlog-write-epics/SKILL.md)   | Write the EPIC artifact from approved approach | `backlog/epics.md`                         |
| 2.5   | [`test-design`](../test-design/SKILL.md) (optional)                      | Design test scenarios from contracts           | Test-design sections in `backlog/epics.md` |
| 3     | [`create-backlog-story-slices`](../create-backlog-story-slices/SKILL.md) | Sketch story-level slices per EPIC             | Story slice tables for approval            |
| 4     | [`create-backlog-stories`](../create-backlog-stories/SKILL.md)           | Write stories, prioritise, validate            | `backlog/ST-NNNN.md` files                 |

Junior Clarity and Senior Acceptance gates run at the end of every phase, not just the final one.

Each phase skill references this document for shared definitions below.

## Story file format

See [story.md template](../../rulebooks/templates/story.md) for the complete frontmatter schema and body structure.

**Key frontmatter fields:**

- `id`: ST-NNNN, zero-padded, unique; matches the filename
- `epic`: The EPIC this story belongs to (references a section in `backlog/epics.md`)
- `title`: What the story delivers — active verb phrase ("Activate a Domain...", "Reject raw secrets..."), never a noun phrase
- `tier`: economy | standard | strong (model tier needed)
- `status`: pending | in_progress | review | blocked | done
- `deps`: Story IDs that block this one (optional)
- `traces`: Use Case / ADR / component IDs implemented (optional)
- `outputs`: Files the story produces — **including its test file(s)**, so `premerge-check --scope` covers them without manual widening

EPICs are documented in `backlog/epics.md` — each EPIC section carries actor goals, demo, scope, dependencies, boundaries, size, and a building-block inventory with capacity estimates. The `epic:` frontmatter value in each story references its parent EPIC by name. MoSCoW priority lives in the prose body (the frontmatter schema is closed; `backlog-lint` rejects unknown fields).

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

**MUST NOT** decompose by layer. One story for types, one for schema, one for service, one for API, one for UI is horizontal decomposition — it produces stories that individually deliver nothing showable and violates the vertical-slice gate. Each story **MUST** cross all system boundaries its capability requires. Infrastructure (identity types, schema scaffolding, test markers, pre-commit fixes) enters as a line item inside the story that first uses it, never as a standalone story — unless the story was already created by the `capture-charter` completeness sweep as part of Epic 0. The planning agent never creates Epic 0 stories; it only acknowledges ones the charter sweep produced.

### Rule 3: Criteria Are Invariants

Each acceptance criterion is a falsifiable statement a test can prove or disprove:

- "X produces Y" (positive invariant)
- "X never Y" (negative invariant)
- "When X, then Y" (boundary condition)

Trace the scope-map rule parenthetically. Do not specify test paths, framework choices, or implementation approach.

## Done Check

- [ ] Every User Goal from the actor-goal list is covered by at least one story
- [ ] EPIC slicing approach confirmed by user (Phase 1)
- [ ] `backlog/epics.md` confirmed by user (Phase 2)
- [ ] Story-level slice tables confirmed by user (Phase 3)
- [ ] Every EPIC and story crosses at least two system boundaries
- [ ] No horizontal (single-boundary) stories exist outside Epic 0
- [ ] Stories meet INVEST criteria (especially: small and testable)
- [ ] Dependencies are explicit in `deps` — no hidden ordering assumptions
- [ ] Stories reference Use Case IDs in `traces` for traceability
- [ ] Every story has a Demo section describing a concrete, showable capability
- [ ] Every story passes Junior Clarity and Senior Acceptance gates
- [ ] `factory/scripts/backlog-lint` reports zero errors
