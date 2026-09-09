---
name: testability-probe
description: "Assess epic testability and resolve contract ownership backlog-wide before stories are cut. Mandatory step 2.5 in the create-backlog sequence, between create-backlog-write-epics and create-backlog-story-slices. Writes a testability paragraph and ownership table per EPIC into backlog/epics.md — no failure scenarios, test paths, or risk classifications."
category: planning
inputs:
  - backlog/epics.md
  - docs/spec/*.feature
  - docs/spec/scope-map.md
  - testing.yaml (at docs/testing.yaml)
outputs:
  - backlog/epics.md
disable-model-invocation: false
---

# Testability Probe

Assess whether each confirmed EPIC's actor goals can be expressed as observable,
assertable outcomes, identify the system seams tests would instrument, flag
testability red flags, and resolve contract ownership across the full backlog.
This is the planning-time complement to the implementation-time `test-design`
skill — the probe catches scoping defects and resolves *who* owns each
contract's tests, while `test-design` (invoked by the developer agent with code
in hand) designs and writes the tests themselves.

This is mandatory step 2.5 in the
[create-backlog sequence](../create-backlog/SKILL.md#operational-sequence): it
runs after [`create-backlog-write-epics`](../create-backlog-write-epics/SKILL.md)
(phase 2, `backlog/epics.md` confirmed) and before
[`create-backlog-story-slices`](../create-backlog-story-slices/SKILL.md)
(phase 3).

Proposal trace: [test-design-layer-redistribution.md](../../../docs/proposals/test-design-layer-redistribution.md).

## Prerequisite guard

Before doing anything else, check `testing.yaml (at docs/testing.yaml)`:

1. **File does not exist.** Fail immediately:

   > `testability-probe` requires `testing.yaml (at docs/testing.yaml)`. Run
   > `detect-test-regime` first to record the project's test suites and testing
   > strategy link.

   Write no output to `backlog/epics.md`.

2. **File exists but has no `testing_strategy:` key.** Fail immediately:

   > `testing.yaml (at docs/testing.yaml)` has no `testing_strategy:` link. Run
   > `detect-test-regime` to populate it before running `testability-probe`.

   Write no output to `backlog/epics.md`.

3. **File exists but has no `suites:` section.** Fail immediately:

   > `testing.yaml (at docs/testing.yaml)` has no `suites:` section. Run
   > `detect-test-regime` to record the project's test suites before running
   > `testability-probe`.

   Write no output to `backlog/epics.md`.

Only when `testing_strategy:` and `suites:` are both present does the
procedure below run.

## Inputs

- `backlog/epics.md` — confirmed epic slicing with EPIC-level Actor Goals and
  a Building-Block Inventory table per EPIC.
- `docs/spec/*.feature` — consolidated Gherkin behavioral contracts. Each
  `Rule:` groups the Scenarios for one actor-goal pair.
- `docs/spec/scope-map.md` — joins behavioral-rule sentences to their `.feature`
  source and, once implemented, to the code that realizes them.
- `testing.yaml (at docs/testing.yaml)` — `testing_strategy:` link and `suites:`
  section (used only for the prerequisite guard and for identifying test suite
  locations when naming instrumentation boundaries).

## Procedure

### 1. Collect trace IDs from the building-block inventory

Each EPIC in `epics.md` lists **Actor Goals** that are the same sentences as
`.feature` `Rule:` titles (`create-backlog-epics` requires every User Goal to
belong to exactly one EPIC, and EPIC Actor Goals are written verbatim from the
actor-goal list). For each EPIC:

1. Match each Actor Goal sentence to its `.feature` `Rule:` — either directly
   (the Rule title matches the goal) or through `docs/spec/scope-map.md`,
   whose `Rule` column carries the same sentence and whose row links to the
   owning `.feature` file.
2. Each matched Rule is one **contract cluster** — its Scenarios are the
   candidate contracts this EPIC's stories must eventually be tested against.
3. Record, per EPIC, the full list of contract clusters it is responsible
   for. This is the trace-ID set the rest of the procedure resolves against.

If a story's own `traces:` frontmatter already exists (the skill is being
re-run standalone against a backlog whose `backlog/ST-NNNN.md` files were
already written), read those `traces:` values directly instead of re-deriving
them from Actor Goals — they are more precise than the EPIC-level match.

### 2. Assess testability per EPIC

For each EPIC, evaluate its Actor Goals against three questions:

1. **Observable outcomes.** Can each goal be expressed as a concrete,
   observable system state or output? A goal that describes an internal
   quality ("the code is clean") or a subjective property ("the user feels
   confident") is not directly testable — it must be decomposed into
   observable signals before stories are cut.

2. **Instrumentation boundaries.** What system seams would tests instrument
   to verify the goals? Name the boundaries — API endpoints, database tables,
   file system paths, message queues, configuration files, CLI exit codes —
   without designing the test cases. The purpose is to confirm that the seams
   exist (or will exist after the EPIC ships) and that they are accessible
   to the project's test suites.

3. **Testability red flags.** Flag any acceptance criterion or actor goal
   that resists concrete testing. Common red flags:

   - Goals expressed as negative universals ("never fails") without a
     bounded failure space.
   - Goals that require human judgment to evaluate ("looks correct",
     "is well-structured").
   - Goals whose observable outcome depends on state outside the system
     under test.
   - Goals that can only be tested by replaying the full implementation
     rather than asserting on a boundary.

   A red flag is a scoping defect signal, not a test-design problem. The
   correct response is to refine the goal's wording or decompose it, not
   to proceed and hope the developer figures it out.

Write a **testability paragraph** per EPIC (2–4 sentences) summarizing:
which goals have clear observable outcomes, which boundaries tests would
instrument, and any red flags. If all goals are testable, say so
explicitly — "All actor goals produce observable, assertable outcomes at
the following boundaries: ..."

### 3. Read each contract's rule and scenarios

For each contract cluster collected in step 1:

- Read the full `.feature` `Rule:` block — its Scenarios are the concrete
  behaviors that must be covered.
- Read the matching row(s) in `docs/spec/scope-map.md` to find the contract's
  architecture owner (the `Feature Link` column, once populated, or the
  building-block/boundary files named in the owning EPIC's `Boundaries`
  section when the Feature Link is not yet filled in).

### 4. Assign one test owner per contract

Ownership is resolved **once, backlog-wide, in a single pass through the
entire `epics.md`** — not per EPIC. A contract traced by stories in different
EPICs still gets exactly one owner.

**Candidate set.** For a given contract, the candidates are every story
(across every EPIC's Building-Block Inventory) whose Capability description
names the capability that introduces or first exercises that contract. A
story is a candidate if implementing its Capability is what makes the
contract's Scenarios true for the first time; a story that merely exercises
already-introduced infrastructure is not a candidate — it is a non-owning
tracer.

**Ordering signal, in precedence order:**

1. **Explicit `deps:`** — if the candidate stories already exist as
   `backlog/ST-NNNN.md` files with `deps:` frontmatter (re-run case), build a
   dependency graph from those fields.
2. **EPIC-level `Dependencies`** — each EPIC section in `epics.md` names the
   EPICs it depends on. Every story in a depending EPIC is ordered after
   every story in the EPICs it depends on.
3. **Building-Block Inventory row order** — within one EPIC, stories are
   listed in intended implementation order (the convention the create-backlog
   sequence already follows). Use table order as the within-EPIC dependency
   proxy when no explicit `deps:` exists yet.

**Resolution:**

1. Topologically sort the candidate set using the ordering signals above,
   applied in precedence order (fall through to the next signal only where
   the current one is silent — silent is not the same as absent, do not
   invert what an earlier signal already determined).
2. The first story in topological order owns the contract.
3. **No dependency relationship among candidates** (neither directly nor
   transitively ordered by any signal above): break the tie by the lower
   `ST-NNNN` numeric ID.
4. **Circular dependency detected** among candidates: do not fail the run.
   Fall back to the lowest `ST-NNNN` ID among the cyclic group, and record a
   `> Warning: circular dependency among <IDs> tracing <contract> — resolved to <ID> by lowest ID` blockquote immediately under that EPIC's ownership
   table, so a human reviewer can confirm or correct it.

Every contract ends this step with exactly one owner. No contract is ever
resolved twice, and no two contracts at the same layer share an owner in a
way that produces duplicate coverage — one contract, one test, one layer.

### 5. Present the probe output

Write the testability assessment and ownership resolution into
`backlog/epics.md` following the [output format](#output-format) below.
Present the enriched `epics.md` to the user for review and discussion.

If any EPIC has testability red flags, call them out explicitly in the
presentation and recommend specific wording changes before proceeding to
story slicing.

## Output format

For every EPIC, add a section immediately after that EPIC's Building-Block
Inventory table:

```markdown
### Testability Assessment

<2–4 sentence paragraph: which goals have observable outcomes, which
boundaries tests would instrument, any red flags.>

### Ownership Resolution

| Contract | .feature Rule | Owner | Rationale |
| -------- | ------------- | ----- | --------- |
| <contract name> | <file>#<Rule title> | ST-NNNN | <why this story — introduces the capability> |
```

Rules for this block:

- The `### Testability Assessment` heading sits at the same level as the
  EPIC's other `###` sections (Actor Goals, Demo, Scope, etc.).
- The `### Ownership Resolution` heading and its table follow the
  testability paragraph.
- Each row in the ownership table names one contract, its `.feature` source,
  the owning story, and a short rationale (one clause: "introduces X",
  "first to exercise Y").
- Non-owning tracers are not listed in the table — they appear only
  implicitly through the EPIC's Building-Block Inventory. The developer
  agent for a dependent story discovers prior tests from the owning story
  at implementation time.
- **Do not write** `#### Failure scenarios`, `#### Prior Tests`, `tests:`
  keys, risk classifications, or test paths. Those belong to the
  implementation-time `test-design` skill.

Format `backlog/epics.md` via `factory/scripts/mdformat --number backlog/epics.md`
per [markdown-formatting.md](../../rulebooks/conventions/markdown-formatting.md)
after writing.

## What this skill does NOT do

- **Write failure scenarios.** The probe assesses testability; detailed
  failure-mode identification happens at implementation time with code in
  hand (the `test-design` skill).
- **Classify contracts by risk class.** Risk classification is an
  implementation-time concern — it depends on the actual code shape, not
  the projected building-block inventory.
- **Write test paths or test file references.** Test files do not exist at
  planning time. The developer agent records `tests:` in the story file at
  commit time.
- **Run for individual stories.** The probe operates at EPIC level across the
  full backlog. Story-level test design is the `test-design` skill's job.

## This skill ends here

`backlog/epics.md` carries testability assessments and ownership tables.
The user reviews the probe output, adjusts any red-flagged goals, then
proceeds to
[`create-backlog-story-slices`](../create-backlog-story-slices/SKILL.md)
(phase 3) as usual — this skill does not itself write `backlog/ST-NNNN.md`
files.
