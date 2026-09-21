---
name: create-backlog
description: Break specification and architecture into a local backlog of markdown stories — EPICs and User Stories with INVEST criteria and MoSCoW priority.
category: planning
---

# Create Backlog

Break the specification and architecture into a prioritised backlog of EPICs and User Stories, written as local markdown files under `backlog/`. The artifact chain is: **existing codebase** (ground truth, located via technical concerns in `docs/agent-context.md`) + scope map + `.feature` files (target) → **`backlog/epics.md`** → individual `backlog/ST-NNNN.md` stories. The planning agent surveys the code first, reads the spec second, and derives stories as deltas from what exists to what the spec requires.

Every story is a **tracer bullet** — a **vertical slice** that is independently implementable, traceable to its spec rule, and respects architectural boundaries.

### Information discovery

Factory-canonical artifacts (`scope-map.md`, `.feature` files, `testing.yaml`) are read by path. Everything else — source directories, supplementary specs, ADRs, handbooks, architecture views, conventions — is discovered through the concern sections in `docs/agent-context.md`. Each concern section carries `Read:` paths — follow them instead of hardcoding project-specific file paths. As a pre-backlog activity, the planning agent reads the full concern registry by judgment, not narrowed by story concerns.

Stories are project artifacts, not entries in an external tracker: one file per story, `backlog/ST-NNNN.md`, with strict frontmatter validated by `.agent-factory/factory/scripts/backlog-lint`.

## Operational sequence

The operational procedure is split into four phase-gated skills. Each skill ends when its output is delivered; the user confirms or adjusts before invoking the next. This structural separation enforces the pause points that prose instructions cannot.

| Phase | Skill                                                                    | What happens                                   | Output                               |
| ----- | ------------------------------------------------------------------------ | ---------------------------------------------- | ------------------------------------ |
| 1     | [`create-backlog-epics`](../create-backlog-epics/SKILL.md)               | Survey codebase, propose EPIC slicing approach | EPIC slice table for approval        |
| 2     | [`create-backlog-write-epics`](../create-backlog-write-epics/SKILL.md)   | Write the EPIC artifact from approved approach | `backlog/epics.md`                   |
| 2.5   | [`testability-probe`](../testability-probe/SKILL.md)                     | Assess testability, resolve contract ownership | Probe sections in `backlog/epics.md` |
| 3     | [`create-backlog-story-slices`](../create-backlog-story-slices/SKILL.md) | Sketch story-level slices per EPIC             | Story slice tables for approval      |
| 4     | [`create-backlog-stories`](../create-backlog-stories/SKILL.md)           | Write stories, prioritise, validate            | `backlog/ST-NNNN.md` files           |
| 5     | [`grilling`](../grilling/SKILL.md) (story target)                        | Grill each story against its open questions    | Resolved blockquotes in story        |
| 6     | [`make-concrete`](../create-backlog-make-concrete/SKILL.md)              | Work resolved answers into home sections       | Operationalised story                |
| 7     | [`slice story`](../create-backlog-slice-story)                           | Cut implementation stories, close original     | `backlog/ST-NNNNA.md` files          |

Quality gates (Agent-Answerability and International Readability) run at the end of every phase, not just the final one.

Each phase skill references this document for shared definitions below.

## Story file format

See [story.md template](../../rulebooks/templates/story.md) for the complete frontmatter schema and body structure.

**Key frontmatter fields:**

- `id`: `ST-NNNN` for new stories; `ST-NNNNA`, `ST-NNNNB`, … when an existing story is resized and split into multiple replacements. When allocating: scan existing `backlog/ST-*.md` filenames — for a new story, increment the highest numeric ID; for a split, increment the highest letter suffix on that numeric ID. Unique; matches the filename
- `epic`: The EPIC this story belongs to (references a section in `backlog/epics.md`)
- `title`: What the story delivers — active verb phrase ("Activate a Domain...", "Reject raw secrets..."), never a noun phrase
- `tier`: economy | standard | strong (model tier needed)
- `status`: pending | in_progress | review | blocked | done
- `deps`: Story IDs that block this one (optional)
- `traces`: Use Case / ADR / component IDs implemented (optional)
- `touches`: Directory prefixes the story works within — including test directories — for overlap detection and scope enforcement
- `quality-gates`: Semantic gates for this story; filled by the planner from `testing.yaml`'s enabled gates (empty for prose-only stories)

EPICs are documented in `backlog/epics.md` — each EPIC section carries actor goals, demo, scope, dependencies, boundaries, size, and a building-block inventory with capacity estimates. The `epic:` frontmatter value in each story references its parent EPIC by name. MoSCoW priority lives in the prose body (the frontmatter schema is closed; `backlog-lint` rejects unknown fields).

## Story composition rules

Three rules govern how stories are decomposed and written.

### Rule 1: Goal First, then Demo

Write the Goal statement first — one sentence describing what behavior must exist after the story ships. Then write the Demo Scenario section: two to four sentences showing what a person can demonstrate. Concrete values, walkthrough format.

**If you cannot write the Goal, the story is not deliverable.**

Every story delivers a capability a person can demonstrate. Infrastructure — markers, migrations, types, scaffolding — enters as a line item inside the story that needs it.

### Rule 2: Forward from Status Quo

Start every story by stating what exists now **in the codebase** — files, modules, tests, schemas that are already there — plus the deliverables of all stories it depends on. This becomes the Inputs section. Identify which files and directories the story changes; this becomes the Affected Paths section. The gap between today's codebase and what the story delivers is the story's scope.

Chain stories so each one's deliverables become status quo for every story that depends on it. The dependency graph is a chain of accumulating status quos, rooted in today's code.

Spec rules are traces — evidence of coverage, not the decomposition axis. A story exists because it delivers a capability, not because a rule needs coverage. The code shape determines how the work decomposes; the spec determines what work is needed.

**MUST NOT** decompose by layer. One story for types, one for schema, one for service, one for API, one for UI is horizontal decomposition — it produces stories that individually deliver nothing showable and violates the vertical-slice gate.

Do not derive stories from components, layers, or implementation stages. Derive each story from an actor-visible outcome, then include every internal change required to deliver that outcome. An internal component may be a standalone story only when that component is itself a supported interface used by a named actor or external consumer. Build only the internal slice each actor-facing story requires — never a standalone "build the engine" or "create the schema" story.

Each story **MUST** cross all system boundaries its capability requires. Infrastructure (identity types, schema scaffolding, test markers, pre-commit fixes) enters as a line item inside the story that first uses it, never as a standalone story — unless the story was already created by the `capture-charter` completeness sweep as part of Epic 0. The planning agent never creates Epic 0 stories; it only acknowledges ones the charter sweep produced.

### Rule 3: Criteria Are Invariants

Each acceptance criterion is a falsifiable statement a test can prove or disprove:

- "X produces Y" (positive invariant)
- "X never Y" (negative invariant)
- "When X, then Y" (boundary condition)

Trace the scope-map rule parenthetically. Do not specify test paths, framework choices, or implementation approach.

### Rule 4: Constraints Are Boundaries

Every must-not from ADRs, conventions, testing regime, and scope exclusions goes in the Constraints section. A must-not buried in prose is a must-not the agent will miss. Constraints are not "nice to haves" — they are hard boundaries the implementation cannot cross.

## Quality gates

Read [writing-quality-gates.md](../../rulebooks/conventions/writing-quality-gates.md) now and hold every rule as a writing constraint throughout every phase. No prose reaches terminal output or a file until it passes all four gates. Do not write first and check later.

## Done Check

- [ ] Every User Goal from the actor-goal list is covered by at least one story

- [ ] EPIC slicing approach confirmed by user (Phase 1)

- [ ] `backlog/epics.md` confirmed by user (Phase 2)

- [ ] Story-level slice tables confirmed by user (Phase 3)

- [ ] Every story names an actor or external consumer, a supported entry point, and an externally observable outcome

- [ ] Every story's demo uses the shipped interface — not test output, source inspection, or direct invocation of internals

- [ ] No horizontal stories exist outside Epic 0 (a story derived from a component rather than an actor-visible outcome is horizontal)

- [ ] Stories meet INVEST criteria (especially: small and testable)

- [ ] Dependencies are explicit in `deps` — no hidden ordering assumptions

- [ ] Stories reference Use Case IDs in `traces` for traceability

- [ ] Every story has a Goal statement describing required behavior

- [ ] Every story has a Demo section describing a concrete, showable capability

- [ ] Every story passes Agent-Answerability and International Readability gates

- [ ] `.agent-factory/factory/scripts/backlog-lint` reports zero errors

- [ ] Every story has a "Resolve Before Implementation" section (even if "None")
