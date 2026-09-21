---
name: slice-story
description: "Cut a concrete backlog story into independently implementable slices along contract boundaries. Phase 7 of the create-backlog sequence."
category: planning
---

# Slice Story

Cut a concrete, grilled story into implementation stories that the dispatcher
can send to developer agents. Each implementation story is a vertical slice
narrow enough for one implementation session.

The original story stays as the design record with `status: closed`. The
implementation stories are the dispatch units.

This is Phase 7 of the
[create-backlog sequence](../create-backlog/SKILL.md#operational-sequence),
after [`make-concrete`](../create-backlog-make-concrete/SKILL.md) (Phase 6). Story format,
composition rules, and quality gates live in the
[parent skill](../create-backlog/SKILL.md).

## Prerequisite

The original story has been through `make-concrete`. Its `## Resolve Before Implementation` section carries resolved blockquotes. Its home sections
(Domain Rule, Required API Behavior, Outputs, Acceptance Criteria, Constraints)
contain the concrete contract detail from the grilling.

## Procedure

### 1. Read and validate the original story

Read the story and its referenced ADRs, scope rules, and feature/spec sections.
Read local project conventions that govern the touched areas. Read nearby
dependent stories if this story is a prerequisite.

Validate that the story is ready to slice — check for these failure modes:

- Acceptance criteria depend on code or tables that do not exist yet and are
  not covered by `deps`.
- Stop conditions are already true at story start.
- Response shapes conflict with project conventions.
- ADR IDs, dependency IDs, or document links are ambiguous.
- HTTP status, persistence, validation, or side-effect rules are still implied.
- The story prescribes internal method names while leaving public contracts
  unclear.

If any failure mode fires, report it and send the story back for another
grilling or make-concrete pass. Do not slice a story with unresolved contract
ambiguity.

### 2. Decide the split

Split when the story crosses more than one hard boundary:

- Backend API and frontend UI.
- Database schema and user-facing behavior.
- Generated OpenAPI/types and consumers of those types.
- Core behavior and cache/interaction polish.
- Domain behavior and demo/seed-data preparation.
- Cross-capability boundary changes and the capability they serve.

Do not split by file path alone. Split by what can be verified independently.

Each slice must have a demo — a concrete capability a person can show. A slice
that delivers nothing observable is not a slice; fold it into the first slice
that needs it.

**Prefer the backend/frontend boundary as the primary cut.** Split the backend
slices among themselves first, then the frontend slices. Do not pair each
capability with its own UI slice — that couples every backend contract to a
frontend session and hides the moment the API became demonstrable.

**Name the demo surface before writing the slice.**

| Slice kind | Demo surface                        | End-to-end means                                                               |
| ---------- | ----------------------------------- | ------------------------------------------------------------------------------ |
| Backend    | the project's API client collection | every route **and every rejection path** is callable against a seeded database |
| Frontend   | the running UI                      | every user action reaches routes a predecessor slice already delivered         |

A backend slice is complete when a person can demonstrate it with no UI. A
frontend slice ships no backend change. If a slice needs both to be
demonstrable, the cut is in the wrong place.

If the story is narrow enough to implement in one session without crossing
hard boundaries, do not split. Set the original story's `status` to `in-progress`
and dispatch it directly.

### 3. Write implementation stories

Create `backlog/ST-NNNNA.md`, `backlog/ST-NNNNB.md`, etc. Allocate letter
suffixes by scanning existing `backlog/ST-NNNN*.md` filenames and incrementing
the highest suffix.

Each implementation story uses the
[story template](../../rulebooks/templates/story.md). Frontmatter includes all
required and relevant optional fields: `id`, `epic`, `title`, `tier`, `status`,
`deps`, `traces`, `touches`, `concerns`, `risk_level`, `quality-gates`.

For each implementation story:

**Inherit from the original.** The concrete detail (Domain Rule, Required API
Behavior, Outputs, Acceptance Criteria, Constraints) was resolved during
grilling and make-concrete. Each slice inherits the subset relevant to its
scope. Do not water down the contract detail — the grilling made it precise
for a reason.

**Narrow the scope.** Each slice carries only the acceptance criteria, affected
paths, outputs, and constraints that belong to its boundary. Move criteria that
belong to a different slice into that slice, not into Out of Scope.

**Give every fact one home.** Each section answers one question. A fact stated
in its home section is referenced elsewhere, never restated. Before writing a
sentence, ask which section owns it; if another section owns it, write a
reference instead.

| Section              | Owns                                        | Never contains                              |
| -------------------- | ------------------------------------------- | ------------------------------------------- |
| Goal                 | the observable outcome                      | how it is verified or built                 |
| Domain Rule          | invariants and must-nevers, domain language | status codes, request shapes, API mechanics |
| Demo Scenario        | the ordered walkthrough with literal values | deliverables                                |
| Demo Data            | the seeded rows                             | behavior                                    |
| Affected Paths       | where the work lands                        | what the work does                          |
| Outputs              | the deliverables                            | field lists owned by Required Behavior      |
| Suggested Agent Plan | the order of work                           | detail already in Outputs                   |
| Acceptance Criteria  | falsifiable checks                          | restatements of each other                  |

The common failures are a deliverable named in Affected Paths, Outputs, the
Agent Plan, and Acceptance Criteria; and a verification method stated in the
Goal. Both are redundancy, not emphasis.

**Specify demo data as data, not as a task.** Every slice carries a
`## Demo Data` section.

When the slice seeds rows, the section holds a table — one row per seeded
record, one column per field, literal values. It also states:

- Which seeding script is extended, named by path.
- Whether the slice extends an existing row or adds a new one.
- Which rows must be written directly through the model because no API
  delivers them yet.
- What the script's idempotency guard and existing output must preserve.

When the slice seeds nothing, the section says so and names the predecessor
slice whose seed set it depends on, plus the specific rows and states the flow
needs.

Every identifier in the Demo Scenario must resolve to a row in a Demo Data
table — in this slice or a predecessor. Never invent demo names inline.

**Write Affected Paths at the coarsest honest granularity.** Name a file only
when that exact file already exists and the slice changes it. For work that
creates new files, name the directory that will hold them and say what is
added.

- `src/module/service.py` — existing file, extend ✅ (the file exists)
- `src/module/` — new `dtos.py`, `errors.py` ✅ (directory plus intent)
- `src/module/dtos.py` — new file to create ❌ (a path guessed at planning time)

A path invented at planning time ages badly and constrains the developer agent
for no benefit. This also makes the `touches` derivation trivial — the
directory prefixes are already written.

**Chain dependencies.** The first slice has no `deps` on sibling slices (it may
depend on other stories). Later slices depend on earlier siblings via `deps`.
The dependency chain follows the build order: backend contract before generated
types, generated types before frontend consumption, core behavior before polish.

**Write Inputs as a reading manifest.** The first slice lists the original
story in Inputs. Later slices list their predecessor sibling. Each slice also
lists the spec rules, ADRs, and codebase files relevant to its boundary.

**Frontend slices.** State prerequisites clearly:

- Backend contract exists (delivered by a predecessor slice or `deps` story).
- OpenAPI/generated types exist.
- Seeded demo data exists — the slice's `## Demo Data` section names the
  predecessor seed set and the specific rows and states the UI flow needs.

State expected structure without prescribing internal names:

- Use generated OpenAPI types.
- Use explicit DTO-to-form and form-to-request mappers when shapes differ.
- Map backend validation errors into the project form-error shape.
- Keep route views as composition surfaces where practical.
- Keep cache polish separate unless required for the core user flow.

**Verification.** Read `docs/testing.yaml` for project-approved verification
commands. Do not invent local test commands when the project requires
container-based or make-target tests.

**Suggested Agent Plan.** Write a short numbered plan in implementation order.
Reference Affected Paths and Outputs. Do not write file-by-file scripts.

### 4. Close the original story

Set the original story's `status` to `closed` in its frontmatter. The original
story stays in the backlog as the design record — it is not deleted or archived.
Its Resolve Before Implementation blockquotes remain the decision record for the
implementation stories.

### 5. Quality gate

Read [writing-quality-gates.md](../../rulebooks/conventions/writing-quality-gates.md) now and hold every rule as a writing constraint. Compose every implementation story with all four gates active — no sentence reaches terminal output or a file until it passes.

Implementation stories do not carry a `## Resolve Before Implementation`
section. They inherit the resolved answers in their home sections.

### 6. Format and validate

Format each story via `.agent-factory/factory/scripts/mdformat --number <path>`.

Run `.agent-factory/factory/scripts/backlog-lint --backlog-dir backlog` to validate frontmatter,
check dependency acyclicity, and confirm touches hygiene.

## Output

- Implementation story files: `backlog/ST-NNNNA.md`, `backlog/ST-NNNNB.md`, etc.
- Original story: `status: closed`.
- Updated `deps` in any nearby stories that previously depended on the original
  (they now depend on the relevant implementation slice).

Present the sliced stories to the user. Show:

- The dependency chain between slices.
- The recommended first slice for implementation.
- Any acceptance criteria from the original that did not land in a slice
  (this is a slicing defect — every original criterion must have a home).

## This skill ends here

The implementation stories are ready for dispatch. The original story is closed.
Commit all story files to `dev` per the
[branching policy](../../rulebooks/conventions/branching-policy.md).
