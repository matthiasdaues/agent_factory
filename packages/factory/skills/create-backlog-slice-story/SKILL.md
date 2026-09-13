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
after [`make-concrete`](../make-concrete/SKILL.md) (Phase 6). Story format,
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
- Demo data or seed data exists if the UI flow needs it.

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

Review every implementation story through two lenses:

**Agent-Answerability.** Every check from the
[create-backlog](../create-backlog/SKILL.md#agent-answerability-checks) table
must be answerable from the story alone.

**International Readability.** Six sentence-level checks on Goal, Domain Rule,
Demo Scenario, Required API Behavior, Constraints, and Agent Stop Conditions.

Implementation stories do not carry a `## Resolve Before Implementation`
section. They inherit the resolved answers in their home sections.

### 6. Format and validate

Format each story via `factory/scripts/mdformat --number <path>`.

Run `factory/scripts/backlog-lint --backlog-dir backlog` to validate frontmatter,
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
