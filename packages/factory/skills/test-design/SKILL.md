---
name: test-design
description: "Design and author integration and edge-case tests from implemented code. Invoked by the developer agent post-GREEN on non-.feature-governed stories. Reads ownership assignments from the testability probe, classifies owned contracts by risk class, identifies untested integration paths, and authors test files."
category: implementation
inputs:
  - backlog/ST-NNNN.md (the story being implemented)
  - backlog/epics.md (ownership assignments from testability-probe)
  - docs/spec/*.feature
  - docs/spec/scope-map.md
  - testing.yaml (at docs/testing.yaml)
outputs:
  - tests/**/* (authored test files)
disable-model-invocation: false
---

# Test Design

Design and author tests for integration paths and edge cases that the TDD
cycle (pass 1) did not cover. This is an implementation-time skill invoked
by the developer agent after GREEN on non-`.feature`-governed stories — it
operates on implemented code, not projected inventory rows.

This skill is the implementation-time complement to the planning-time
[`testability-probe`](../testability-probe/SKILL.md). The probe resolves
*who* owns each contract's tests; this skill designs and writes those tests
with the actual code in hand.

Proposal trace: [test-design-layer-redistribution.md](../../../docs/proposals/test-design-layer-redistribution.md).
Prior skill trace: [test-design-skill.md](../../../docs/proposals/test-design-skill.md).

## Prerequisite guard

Before doing anything else, check `testing.yaml (at docs/testing.yaml)`:

1. **File does not exist.** Fail immediately:

   > `test-design` requires `testing.yaml (at docs/testing.yaml)`. Run
   > `detect-test-regime` first to record the project's test suites and
   > testing strategy link.

   Author no test files.

2. **File exists but has no `testing_strategy:` key.** Fail immediately:

   > `testing.yaml (at docs/testing.yaml)` has no `testing_strategy:` link.
   > Run `detect-test-regime` to populate it before running `test-design`.

   Author no test files.

3. **File exists but has no `suites:` section.** Fail immediately:

   > `testing.yaml (at docs/testing.yaml)` has no `suites:` section. Run
   > `detect-test-regime` to record the project's test suites before running
   > `test-design`.

   Author no test files.

Only when `testing_strategy:` and `suites:` are both present does the
procedure below run.

## Inputs

- `backlog/ST-NNNN.md` — the story being implemented, with `traces:`
  frontmatter linking to `.feature` Rules and `touches:` listing the
  directories the story works within.
- `backlog/epics.md` — the `### Ownership Resolution` table for the story's
  EPIC, produced by the `testability-probe` skill. Contains ownership
  assignments ("contract X owned by ST-NNNN").
- `docs/spec/*.feature` — consolidated Gherkin behavioral contracts.
- `docs/spec/scope-map.md` — joins behavioral-rule sentences to their
  `.feature` source and implementation code.
- `testing.yaml (at docs/testing.yaml)` — `testing_strategy:` link,
  `suites:`, and optional `risk_classes:` overrides.
- The document at `testing_strategy:` (defaults to
  [testing-strategy.md](../../rulebooks/conventions/testing-strategy.md)) —
  risk-class definitions, failure-scenario formats, budget rules, and the
  admit-a-test gate.
- The story's implemented code — files under the story's `touches:` paths.

## Procedure

### 1. Read the testing strategy

Read the document linked from `testing_strategy:` in `testing.yaml`. Adopt
its risk-class definitions, failure-scenario formats, budget rules, and
admit-a-test gate as design constraints for every step below. Then check
`testing.yaml` for a `risk_classes:` section:

- **Present** — its entries override the strategy document's definitions for
  the risk classes it names (partial overrides are allowed).
- **Absent** — use the strategy document's definitions as-is.

### 2. Read ownership assignments

Read the `### Ownership Resolution` table in `backlog/epics.md` for the
story's EPIC. Identify which contracts this story owns. Only owned contracts
are candidates for new test design — non-owned contracts are covered by
prior tests from the owning story.

If no ownership resolution table exists (the `testability-probe` was not
run, or the backlog predates this change), fall back to treating every
contract traced by this story as owned. This handles backward-compatible
operation against older backlogs.

### 3. Read the .feature rules for owned contracts

For each owned contract, read the corresponding `.feature` Rule and its
Scenarios to understand the behavioral specification. Use the story's
`traces:` frontmatter to locate the `.feature` file and Rule, or resolve
through `docs/spec/scope-map.md`.

### 4. Read the implemented code

Read the implemented code under the story's `touches:` paths. Identify the
actual seams, integration points, and edge cases the code reveals. This is
the step that makes implementation-time test design fundamentally different
from planning-time — the code shape is known, not guessed.

### 5. Classify owned contracts by risk class

For each owned contract, resolve its risk class using this precedence chain:

1. `testing.yaml`'s `risk_classes:` section, if it defines a matching class.
2. The document at `testing_strategy:` (read in step 1).
3. Factory convention defaults (`critical`, `standard`, `structural`) from
   [testing-strategy.md](../../rulebooks/conventions/testing-strategy.md).

Match the contract's Scenario language and the observed code against each
class's characteristics:

- **`critical`** — atomicity, concurrency, protocol compliance, security
  invariants, idempotency.
- **`standard`** — CRUD operations, input validation, read APIs.
- **`structural`** — declarative structure, formatting, schema conformance.
- **Custom classes** — apply when the contract is explicitly tagged with that
  class's name, using its `format`, `budget`, and `requires` fields from
  `testing.yaml`.

### 6. Compare TDD tests against owned contracts

Read the test files authored during the TDD cycle (pass 1). For each owned
contract, check whether the existing tests cover:

- The contract's primary Scenarios (happy path).
- Integration paths revealed by the code — seams between components,
  boundary crossings, external-system interactions.
- Edge cases visible in the implementation — boundary values, error paths,
  state transitions.

Identify the gaps: integration paths and edge cases the TDD cycle did not
cover.

### 7. Author tests for uncovered contracts

For each uncovered path, apply the risk-class rules:

- **`critical` contracts:** Write Given/When/Then/Forbidden failure scenarios
  as executable test cases. Unbounded budget — every distinct failure mode
  gets its own test.

  ```
  Given <precondition describing the system state>
  When <action that triggers the contract>
  Then <expected outcome under normal conditions>
  Forbidden <the specific failure mode this test catches>
  ```

- **`standard` contracts:** Write concrete scenario tests with expected
  inputs and assertions, respecting the admit-a-test budget: one
  representative per equivalence class, plus boundary values and distinct
  failure modes. Check the admit-a-test gate before each test.

- **`structural` contracts:** Emit nothing — these are linter-owned.

Author the tests as executable test files in the project's test suite,
following the conventions from `testing.yaml`'s `suites:` section (test
directory, naming pattern, framework).

### 8. Report the outcome

Report to the developer agent:

- Which owned contracts were already covered by TDD tests (no action needed).
- Which contracts had gaps and what tests were authored to fill them.
- The list of authored test file paths — the developer agent records these
  in the story's `tests:` field at commit time.

If no gaps were found (TDD covered everything), report that explicitly —
the developer agent still writes `test-design-pass: done`.

## What this skill does NOT do

- **Resolve contract ownership.** The `testability-probe` already did that
  at planning time. This skill reads the probe's assignments.
- **Write into `backlog/epics.md`.** Test output lives in the test suite
  and the story file's `tests:` field, not in the planning artifact.
- **Run for `.feature`-governed stories.** The `.feature` file is the test
  design for those. The developer agent controls this conditional.
- **Write `#### Failure scenarios` or `#### Prior Tests` sections into
  `epics.md`.** Those were artifacts of the planning-time test-design model.
  Under this model, test artifacts are executable test files.

## This skill ends here

Test files are authored in the project's test suite. The developer agent
records the authored test module paths in the story's `tests:` field and
writes `test-design-pass: done` at commit time. QA reviews the tests; the
reconciliation agent audits traceability.
