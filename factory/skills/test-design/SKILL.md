---
name: test-design
description: "Design test scenarios from .feature contracts and the scope map before stories are cut. Assigns one test owner per contract across the backlog, classifies contracts by risk class, and writes concrete failure scenarios into backlog/epics.md. Optional step 2.5 in the create-backlog sequence, between create-backlog-write-epics and create-backlog-story-slices."
category: planning
inputs:
  - backlog/epics.md
  - docs/spec/*.feature
  - docs/spec/scope-map.md
  - docs/charter/testing.yaml
outputs:
  - backlog/epics.md
disable-model-invocation: false
---

# Test Design

Read the behavioral contracts a confirmed epic slicing must satisfy, assign each
contract to exactly one test-owning story across the whole backlog, classify it
by risk class, and write concrete test-design output into `backlog/epics.md`.
This output becomes the developer-agent's prescribed TDD RED phase — it writes
exactly the scenarios recorded here, not tests it invents itself.

This is optional step 2.5 in the
[create-backlog sequence](../create-backlog/SKILL.md#operational-sequence): it
runs after [`create-backlog-write-epics`](../create-backlog-write-epics/SKILL.md)
(phase 2, `backlog/epics.md` confirmed) and before
[`create-backlog-story-slices`](../create-backlog-story-slices/SKILL.md)
(phase 3). It is also invocable standalone against an existing, already-storied
backlog to retrofit test-design output.

Proposal trace: [test-design-skill.md](../../../docs/proposals/test-design-skill.md).
Behavioral spec: [test-design.feature](../../../docs/spec/test-design.feature).

## Prerequisite guard

Before doing anything else, check `docs/charter/testing.yaml`:

1. **File does not exist.** Fail immediately:

   > `test-design` requires `docs/charter/testing.yaml`. Run `detect-test-regime`
   > first to record the project's test suites and testing strategy link.

   Write no output to `backlog/epics.md`.

2. **File exists but has no `testing_strategy:` key.** Fail immediately:

   > `docs/charter/testing.yaml` has no `testing_strategy:` link. Run
   > `detect-test-regime` to populate it before running `test-design`.

   Write no output to `backlog/epics.md`.

3. **File exists but has no `suites:` section.** Fail immediately:

   > `docs/charter/testing.yaml` has no `suites:` section. Run
   > `detect-test-regime` to record the project's test suites before running
   > `test-design`.

   Write no output to `backlog/epics.md`.

Only when `testing_strategy:` and `suites:` are both present does the
procedure below run. This mirrors the QA strategy's boundary case: a
`testing_strategy:` link with no `suites:` section is a partial charter
configuration and must fail the guard, not proceed with an assumed default.

## Inputs

- `backlog/epics.md` — confirmed epic slicing with EPIC-level Actor Goals and
  a Building-Block Inventory table per EPIC.
- `docs/spec/*.feature` — consolidated Gherkin behavioral contracts. Each
  `Rule:` groups the Scenarios for one actor-goal pair.
- `docs/spec/scope-map.md` — joins behavioral-rule sentences to their `.feature`
  source and, once implemented, to the code that realizes them.
- `docs/charter/testing.yaml` — `testing_strategy:` link, `suites:`, and
  optional `risk_classes:` overrides.
- The document at `testing_strategy:` (defaults to
  [testing-strategy.md](../../rulebooks/conventions/testing-strategy.md)) —
  risk-class definitions, failure-scenario formats, budget rules, and the
  admit-a-test gate.

## Procedure

### 1. Read the testing strategy

Read the document linked from `testing_strategy:` in `testing.yaml`. Adopt its
risk-class definitions, failure-scenario formats, budget rules, and
admit-a-test gate as design constraints for every step below. Then check
`testing.yaml` for a `risk_classes:` section:

- **Present** — its entries override the strategy document's definitions for
  the risk classes it names (partial overrides are allowed: a project may
  redefine only `standard` and leave `critical`/`structural` at their
  strategy-document or Factory defaults).
- **Absent** — use the strategy document's definitions as-is.

### 2. Collect trace IDs from the building-block inventory

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
re-run standalone against a backlog whose `backlog/ST-NNNNNN.md` files were
already written), read those `traces:` values directly instead of re-deriving
them from Actor Goals — they are more precise than the EPIC-level match.

### 3. Read each contract's rule, scenarios, and architecture owner

For each contract cluster collected in step 2:

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
tracer (step 9).

**Ordering signal, in precedence order:**

1. **Explicit `deps:`** — if the candidate stories already exist as
   `backlog/ST-NNNNNN.md` files with `deps:` frontmatter (re-run case), build a
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
   `ST-NNNNNN` numeric ID.
4. **Circular dependency detected** among candidates: do not fail the run.
   Fall back to the lowest `ST-NNNNNN` ID among the cyclic group, and record a
   `> Warning: circular dependency among <IDs> tracing <contract> — resolved to <ID> by lowest ID` blockquote immediately under that story's Failure scenarios
   section, so a human reviewer can confirm or correct it.

Every contract ends this step with exactly one owner. No contract is ever
resolved twice, and no two contracts at the same layer share an owner in a
way that produces duplicate coverage — one contract, one test, one layer.

### 5. Classify each contract by risk class

For each contract, resolve its risk class using this precedence chain:

1. `testing.yaml`'s `risk_classes:` section, if it defines a matching class.
2. The document at `testing_strategy:` (read in step 1).
3. Factory convention defaults (`critical`, `standard`, `structural`) from
   [testing-strategy.md](../../rulebooks/conventions/testing-strategy.md).

Match the contract's Scenario language against each class's characteristics:

- **`critical`** — atomicity, concurrency, protocol compliance, security
  invariants, idempotency.
- **`standard`** — CRUD operations, input validation, read APIs.
- **`structural`** — declarative structure, formatting, schema conformance.
- **Custom classes** (e.g. a project-defined `financial` class) — apply when
  the contract is explicitly tagged with that class's name in the `.feature`
  file or the story's own scope, and use its `format`, `budget`, and
  `requires` fields exactly as defined in `testing.yaml`.

If a custom risk class in `testing.yaml` is missing its `format` field,
reject it with a diagnostic (`> Warning: risk class <name> has no format — skipping test-design output for contracts tagged <name>`) rather than
guessing a format; it falls through to no output for those contracts until
the project fixes the definition.

### 6. Write failure scenarios for `critical` contracts

For each `critical` contract, write one Given/When/Then/Forbidden scenario
per distinct failure mode (unbounded budget — every distinct failure mode
identified in the `.feature` Scenarios gets its own entry):

```
Given <precondition describing the system state>
When <action that triggers the contract>
Then <expected outcome under normal conditions>
Forbidden <the specific failure mode this test catches>
```

The `Forbidden` line is mandatory and must name a concrete failure, not a
restatement of the `Then` line. If no distinct failure mode can be named, do
not write the scenario — go back to step 5 and re-check the risk class; a
contract with no nameable failure mode is rarely `critical`.

Write these into the owning story's `#### Failure scenarios` section (format in
[Output format](#output-format) below).

### 7. Write concrete scenarios for `standard` contracts

For each `standard` contract, write concrete scenario text with expected
inputs and assertions, respecting the admit-a-test budget: one representative
per equivalence class, plus boundary values and distinct failure modes.
Before adding a scenario, check the admit-a-test gate from the testing
strategy — admit it only if it protects a new observable contract, covers a
distinct security or process boundary, exercises an integration seam the
owning contract test cannot reach, or replaces weaker coverage while reducing
total maintenance. Do not pad the budget with restatements of the same
equivalence class.

Write these into the owning story's `#### Failure scenarios` section.

### 8. Emit nothing for `structural` contracts

`structural` contracts are owned by the deterministic linter layer. Do not
write a `#### Failure scenarios` entry for them at all — no placeholder, no empty
scenario. They remain fully covered by schema validators, linters, and
formatters outside this skill's scope.

### 9. Propagate Prior Tests to non-owning stories

For every story that traces a contract but does not own it (step 4 assigned
ownership elsewhere), write a `#### Prior Tests` section on that story's
entry in `epics.md`, listing the owner's test module and the specific test
function(s) that cover the contract:

```
- DOM-01 — owned by ST-0180 at `tests/test_domain.py::test_entity_uniqueness`
```

Name both the module path and the function — a module path alone is not
enough for the developer-agent to run the right check first. If the owning
story's exact test function is not yet known (the owner hasn't been
implemented yet), name the owner story and its planned test module from
step 6/7's Failure scenarios output instead of leaving the entry blank; never emit
a `#### Prior Tests` section with an empty list — a story with prior-test
obligations but no resolvable entry is a defect in the resolution pass
(re-check step 4), not something to paper over with an empty section.

The developer-agent runs these listed tests first, before writing any new
code, and its implementation must keep them green. This is not new test
work — it is inherited regression coverage from the owning story.

### 10. Populate the `tests:` key

For each owning story only (never for a non-owning story — its `tests:` key,
if any, comes from its own separately-owned contracts, not from what it
merely traces), list the test module(s) it owns in a `tests:` line on its
`epics.md` entry. List only modules this story is responsible for
authoring or extending — not modules it merely runs as Prior Tests.

## Output format

For every story that owns at least one contract, or that traces a contract it
does not own, add a subsection immediately after that EPIC's Building-Block
Inventory table:

```markdown
#### ST-0185 — Create the test-design skill

tests: [tests/factory/test_test_design.py]

##### Failure scenarios

- **Contract:** `Ownership resolution: introducing story owns` (test-design.feature
  Rule 3, Scenario 1) — risk class: `critical` — layer: `contract_test`

```

Given a contract traced by stories ST-0185 (introducing) and ST-0186 (non-owning)
When the test-design skill resolves ownership in a single backlog-wide pass
Then ST-0185 is recorded as the sole owner of the contract's test
Forbidden both ST-0185 and ST-0186 emitting a Failure scenarios entry for the same contract

```

##### Prior Tests

- `Ownership resolution: introducing story owns` — owned by ST-0185 at
`tests/factory/test_test_design.py::test_ownership_goes_to_introducing_story`
```

Rules for this block:

- The story-level header (`####`) uses the story's own EPIC heading depth
  plus one — it sits under the EPIC's `### Building-Block Inventory` table,
  not inside it. Do not add a `tests`/Failure scenarios/Prior Tests column to the
  table itself; the table stays a scan-at-a-glance index, the subsections
  carry the detail.
- `##### Failure scenarios` appears only on the owning story, and only when it owns
  at least one `critical` or `standard` contract (never for `structural`
  contracts — step 8).
- `##### Prior Tests` appears only on a non-owning story that traces a
  contract owned elsewhere.
- A story with neither owned nor traced-but-not-owned contracts gets no
  subsection at all — do not emit empty scaffolding.
- `tests:` lists only modules this story is proven to own (step 10); omit the
  line entirely on a story with no owned test modules.

Format `backlog/epics.md` via `factory/scripts/mdformat --number backlog/epics.md`
per [markdown-formatting.md](../../rulebooks/conventions/markdown-formatting.md)
after writing.

## This skill ends here

`backlog/epics.md` carries test-design output: `tests:` on every owning
story, `#### Failure scenarios` with risk-classified failure scenarios, and
`#### Prior Tests` on every non-owning tracer. The user reviews the
enrichment, then proceeds to
[`create-backlog-story-slices`](../create-backlog-story-slices/SKILL.md)
(phase 3) as usual — this skill does not itself write `backlog/ST-NNNNNN.md`
files; [`create-backlog-stories`](../create-backlog-stories/SKILL.md) (phase
4\) carries the `tests:`, `#### Failure scenarios`, and `#### Prior Tests` sections
from `epics.md` into the individual story files verbatim.
