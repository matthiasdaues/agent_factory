---
schema_version: 2
title: Test-Design Layer Redistribution
status: accepted
owner: Matthias Daues
created: 2026-09-08
updated: 2026-09-09
supersedes:

impact:
  scope: cross_component
  architecture_change: false
  external_contract_change: true
  boundaries:
    - factory/skills/test-design/SKILL.md
    - factory/agents/developer-agent.md
    - factory/agents/qa-agent.md
    - factory/agents/planning-agent.md
    - factory/agents/reconciliation-agent.md
    - factory/agents/implementation-agent.md
    - factory/rulebooks/conventions/testing-strategy.md
    - factory/rulebooks/conventions/cross-reference-format.md
    - factory/skills/create-backlog/SKILL.md
    - factory/skills/create-backlog-stories/SKILL.md
    - factory/skills/create-backlog-write-epics/SKILL.md
    - factory/scripts/test-design-verify
    - factory/rulebooks/templates/story.md

governance:
  assurance: routine
  risk_domains:
    - operations
    - quality

estimate:
  as_of: 2026-09-08
  basis: judgment
  confidence: medium
  human_review_hours:
    min: 1.0
    max: 2.0
  normalized_tokens:
    min: 4000
    max: 10000
  estimated_consumption:
    min: 60000
    max: 150000
    overhead_multiplier: 15
    playbook: feature-addition
---

# Feature Request: Test-Design Layer Redistribution

## Summary

Move detailed test-case design from planning time (epic level, before code exists)
to implementation time (story level, code in hand). The planning agent's test-design
step splits into a new `testability-probe` skill (testability assessment and contract
ownership resolution) and a narrowed `test-design` skill (detailed test authoring,
now invoked by the developer agent with code in hand). The QA agent reviews all
tests but does not author new ones. The reconciliation agent audits test-to-contract
traceability alongside its existing `@`-reference backfill.

## Scope

**In the first release:**

- The `testability-probe` skill at `factory/skills/testability-probe/SKILL.md`,
  replacing the current `test-design` skill's planning-time role with testability
  assessment and contract ownership resolution.
- The narrowed `test-design` skill at `factory/skills/test-design/SKILL.md`,
  refactored as an implementation skill invoked by the developer agent.
- The `create-backlog` parent skill's operational sequence table updated to
  reference `testability-probe` at phase 2.5 instead of `test-design`.
- The `create-backlog-write-epics` skill (step 2) updated to surface the
  `testability-probe` option instead of `test-design`.
- The `create-backlog-stories` skill updated to carry ownership assignments
  (not failure scenarios) from `epics.md` into story files.
- The developer agent updated to invoke `test-design` post-GREEN for
  non-`.feature` stories and to record the `tests:` field and
  `test-design-pass` field at commit time.
- The QA agent's Fagan review criteria updated to cross-reference tests
  against traced contracts and check the `test-design-pass` field.
- The reconciliation agent extended with a test traceability audit step.
- The `test-design-verify` gate script adapted to verify the `tests:` field
  instead of `#### Failure scenarios` / `#### Prior Tests` sections for new
  stories.
- The `testing-strategy.md` convention extended with a section on the two-pass
  test authoring model.
- The story template at `factory/rulebooks/templates/story.md` updated with
  `tests:` and `test-design-pass` field documentation.

**Explicitly deferred (do NOT plan stories for these):**

- Migration of existing stories with `#### Failure scenarios` or
  `#### Prior Tests` sections to the new model. The developer agent's backward
  compatibility path handles these as-is.
- Updates to `testing.yaml` templates for the `testability-probe` outputs.
  The probe writes into `epics.md`, not `testing.yaml`.
- Changes to `backlog-lint` validation rules. The existing rules continue to
  work; new rules for `test-design-pass` and `tests:` are a follow-up.
- Retroactive testability probes for backlogs planned before this change.

## Motivation

The current test-design skill (planning phase 2.5) writes detailed failure scenarios,
assigns risk classes, resolves contract ownership, and propagates prior-test references
— all before a single line of code exists. This front-loads design work that is
inherently speculative at epic level:

- **Failure scenarios are guesses.** Without code, the scenarios describe anticipated
  failure modes, not observed ones. They get rewritten or abandoned once
  implementation reveals actual seams and boundaries.
- **Contract ownership is premature.** The ownership resolution algorithm
  (topological sort over candidate stories) operates on building-block inventory rows
  that may shift during story slicing and implementation.
- **The developer agent is already constrained.** The RED phase instruction says
  "write exactly the failure scenarios specified — no additions, no substitutions."
  This locks implementation to speculative test designs rather than letting the
  developer respond to what the code actually does.

Meanwhile, the planning-level value of test-design — catching untestable epic scoping
— does not require detailed test cases. A lightweight testability probe achieves that
signal at a fraction of the cost. And the one planning-level concern that genuinely
needs the full backlog view — contract ownership resolution — can be preserved in the
probe without dragging along speculative test authoring.

## Proposed Design

### Test layers and lifecycle

| Layer                            | Lifecycle point              | Owner                | Purpose                                                                            |
| -------------------------------- | ---------------------------- | -------------------- | ---------------------------------------------------------------------------------- |
| Testability probes + ownership   | Planning (epic level)        | Planning agent       | Catch untestable scoping; resolve *who* owns each contract's tests                 |
| Detailed test design + authoring | Implementation (story level) | Developer agent      | Design and write tests with code in hand; record test traceability                 |
| Test review                      | QA (post-implementation)     | QA agent             | Judge coverage and correctness by cross-referencing tests against traced contracts |
| Test traceability audit          | Reconciliation (post-QA)     | Reconciliation agent | Verify and backfill test-to-contract references in story files                     |

### Change 1: Fork the test-design skill into two skills

The current `test-design` skill splits along its natural seam:

**`testability-probe`** — new planning skill. Per epic, it:

1. **Assesses testability.** Can this epic's actor goals be expressed as observable,
   assertable outcomes? If not, the scoping is wrong.
2. **Identifies instrumentation boundaries.** What system boundaries would tests
   instrument? Names the seams, not the test cases.
3. **Flags testability red flags.** Acceptance criteria that resist concrete tests
   are scoping defects, not test-design problems.
4. **Resolves contract ownership** across the full backlog. This is the one concern
   that requires the backlog-wide view: topological sort over candidate stories,
   one owner per contract. The probe writes ownership assignments
   ("contract X owned by ST-NNNN") into `backlog/epics.md` but does not write
   test paths or failure scenarios — those do not exist yet.

Output is a short section per epic in `backlog/epics.md` — a testability paragraph
plus an ownership table, not a scenario catalog. The planning agent presents it
for user review and discussion.

**`test-design`** — retains the name, becomes an implementation skill. Invoked by
the developer agent with code in hand. Its detailed machinery — failure scenarios,
risk classification, edge-case identification — operates on observed code, not
projected inventory rows. It no longer resolves ownership (the probe already did
that) and no longer runs at epic level.

The two skills share only the prerequisite guard (reading `testing.yaml` and
risk-class definitions). Almost no shared procedure — a mode parameter on a single
skill would produce a 300+ line file where the agent skips half based on a flag.

### Change 2: Developer agent gains `test-design` and records traceability

The developer agent gains `test-design` as a skill. Its workflow changes:

1. **Analyse** — unchanged.
2. **Agree seams** — unchanged.
3. **Red-Green-Refactor** — two test passes:
   - **Pass 1 (TDD):** Derive tests from acceptance criteria (`.feature` Scenarios
     or story spec). Standard Red-Green-Refactor cycle.
   - **Pass 2 (test-design, conditional):** After GREEN, if the story is **not**
     `.feature`-governed, invoke `test-design` against the implemented code to
     identify integration paths and edge cases the TDD cycle did not cover. Author
     those additional tests. For `.feature`-governed stories, skip — the `.feature`
     file is the test design, and the developer's existing contract-test gap-fill
     handles internal seams.
4. **Commit** — unchanged, plus: write the `tests:` field in the story file
   (`backlog/ST-NNNN.md`) listing test modules this story owns, and write the
   `test-design-pass` field recording the outcome. This is test-to-contract
   traceability recorded at the point of authorship.
5. **Spec feedback** — unchanged.

#### Story-level test-design procedure

When the developer agent invokes the narrowed `test-design` skill post-GREEN, the
skill follows this procedure:

**Inputs:**

- The story's implemented code (files under the story's `outputs:` paths).
- The story's `traces:` frontmatter — contract IDs traced to `.feature` rules.
- The story's ownership assignments from the testability probe in `epics.md`
  ("contract X owned by this story").
- `testing.yaml` — `testing_strategy:` link, `suites:`, and `risk_classes:`
  overrides.

**Procedure:**

1. Read `testing.yaml` and the linked testing strategy. Adopt risk-class
   definitions, failure-scenario formats, and budget rules.
2. Read the story's ownership assignments from `epics.md`. Only contracts
   owned by this story are candidates for new test design; non-owned contracts
   are covered by prior tests from the owning story.
3. For each owned contract, read the corresponding `.feature` rule and its
   scenarios to understand the behavioral specification.
4. Read the implemented code under the story's output paths. Identify the
   actual seams, integration points, and edge cases the code reveals.
5. Classify each owned contract by risk class using the existing precedence
   chain: `testing.yaml` `risk_classes:` > strategy document > convention
   defaults.
6. Compare the TDD pass 1 tests against the owned contracts. Identify
   integration paths and edge cases the TDD cycle did not cover.
7. For uncovered `critical` contracts: write Given/When/Then/Forbidden failure
   scenarios as test cases. For uncovered `standard` contracts: write concrete
   scenario tests with expected inputs and assertions, within the admit-a-test
   budget. `structural` contracts remain linter-owned — no test output.
8. Author the test cases as executable test files in the test suite, following
   the project's test conventions from `testing.yaml`'s `suites:` section.

**Output:** Test files in the test suite (not sections in `epics.md`). The
developer agent records the authored test modules in the story's `tests:` field
at commit time.

**What this procedure does NOT do:**

- Ownership resolution — the `testability-probe` already resolved that at
  planning time.
- Writing into `epics.md` — test output lives in the test suite and the story
  file's `tests:` field, not in the planning artifact.
- Running for `.feature`-governed stories — the `.feature` file is the test
  design for those.

#### Observable signals for QA

At commit time, the developer agent writes a `test-design-pass` field in the
story file's frontmatter:

- `test-design-pass: done` — the developer invoked `test-design` and authored
  any additional tests it identified (or confirmed no additional tests were
  needed).
- `test-design-pass: skipped-feature-governed` — the story is `.feature`-governed;
  the post-TDD test-design pass was correctly skipped.

This gives QA a mechanical signal to distinguish "developer assessed and found
nothing needed" from "developer skipped the step." A story with no
`test-design-pass` field that is not `.feature`-governed is a QA finding.

**Backward compatibility:** Stories with pre-existing `#### Failure scenarios`
sections (from the current test-design skill) continue to work. The developer
agent's existing conditional logic handles this: "If `#### Failure scenarios`
section exists, write exactly those scenarios." This proposal stops generating
new `#### Failure scenarios` at epic level; stories created after this change
ships will not have them, and the developer's RED phase derives from acceptance
criteria instead.

### Change 3: QA agent review criteria expand

The QA agent's structure is unchanged. Its Fagan inspection and bug-hunt steps
already review all tests. The expansion is in review criteria:

- Cross-reference the test suite against traced contracts: every traced contract
  must have a corresponding test, or a justified exclusion (e.g., structural
  contracts are linter-owned).
- Check the `test-design-pass` field: flag non-`.feature` stories where the field
  is absent (the developer skipped the step) or where `done` stories have no
  integration tests beyond TDD contract tests despite the test-design skill
  identifying gaps.
- Assess whether testability red flags from planning were addressed — any flags
  raised at epic level should have corresponding test coverage at story level.

No coverage percentages, no per-story minimums. The invariant is: **every traced
contract either has a test or a justified exclusion.** The tests themselves are
the evidence; QA reads them and judges.

### Change 4: Reconciliation agent audits test traceability

The reconciliation agent already backfills `@`-references (implementation code)
in `.feature` files and populates the scope map's `Feature Link` column. This
proposal extends its audit to test traceability:

- Verify that every story file's `tests:` field matches its actual test files.
- Backfill missing `tests:` entries where the developer omitted them but tests
  exist.
- File `RECON` findings for contracts with ownership assignments (from the
  testability probe) but no corresponding test coverage in the owning story.

Test references stay in story files (`backlog/ST-NNNN.md`), not in `.feature`
files. The `@`-reference mechanism in `.feature` files remains exclusively
for implementation code, consistent with the cross-reference-format convention.

## Impact on Existing Artifacts

### Stories with pre-existing `#### Failure scenarios` sections

Honored as-is. The developer agent's existing conditional path ("write exactly
those scenarios") remains. This proposal stops generating new ones at planning
time; it does not retroactively remove existing ones.

### The `#### Prior Tests` sections

Under the current skill, prior-test references include specific test module paths
and function names — which do not exist at planning time. Under this proposal,
the testability probe writes ownership only ("contract X owned by ST-NNNN"), not
test paths. The developer agent for a dependent story reads the ownership record,
discovers the owning story's actual test paths from its test files (the dependency
graph already prevents the dependent story from starting before its dependency is
implemented), and records the prior-test references with real paths.

### The `test-design-verify` gate

The `test-design-verify` gate script currently validates that owned contracts have
`#### Failure scenarios` entries and non-owning stories have `#### Prior Tests`
entries — artifacts that new stories under this proposal will not have.

The gate adapts rather than disappears. For stories created under the new model,
it verifies:

1. The story's `tests:` field is present and lists at least one test module for
   each owned contract.
2. The `test-design-pass` field is present and has a valid value (`done` or
   `skipped-feature-governed`).
3. For non-owning stories: the owning story's `tests:` field resolves to existing
   test files.

For stories with pre-existing `#### Failure scenarios` or `#### Prior Tests`
sections (backward compatibility), the gate continues to use its current
validation logic. The gate distinguishes old-model from new-model stories by
the presence or absence of the `test-design-pass` field.

### testing-strategy.md

Needs a section acknowledging the two-pass test authoring model: TDD contract
tests first, design-driven integration tests second. Risk-class definitions and
budget rules remain unchanged — they apply at authoring time regardless of when
authoring happens.

### Scope map

No change. The scope map traces rules to implementation code only. Test
traceability stays in story files.

### Story template

The story template at `factory/rulebooks/templates/story.md` adds documentation
for two fields:

- `tests:` — test modules this story owns. Populated by the developer agent at
  commit time, not inherited from epic-level planning.
- `test-design-pass:` — `done` or `skipped-feature-governed`. Populated by the
  developer agent at commit time.

## Alternatives Considered

| Alternative                                     | Verdict  | Rationale                                                                                                     |
| ----------------------------------------------- | -------- | ------------------------------------------------------------------------------------------------------------- |
| Kill test-design entirely                       | Rejected | Testability probes at epic level catch real scoping defects; ownership resolution needs the backlog-wide view |
| Single skill with mode parameter                | Rejected | Almost no shared procedure; a mode flag creates a long file where half is skipped                             |
| New test-agent (post-implementation)            | Rejected | Adds lifecycle complexity; the developer agent already has the code context                                   |
| Widen QA agent to author tests                  | Rejected | QA should judge, not author — mixing the roles weakens the review signal                                      |
| Split QA into review + test authoring           | Rejected | Unnecessary agent proliferation; developer agent is the natural test author                                   |
| Drop formal ownership resolution                | Rejected | Ownership needs the full backlog view; only planning has it                                                   |
| Handwritten test coverage assessment per story  | Rejected | Professional practice: tests are the evidence, not prose about tests. QA cross-references mechanically        |
| Status quo (detailed test-design at epic level) | Rejected | Speculative test cases create churn and constrain implementation without matching observed code               |

## Completion Criteria

01. The `testability-probe` skill exists at `factory/skills/testability-probe/SKILL.md`
    with the procedure described in Change 1: testability assessment (observable
    outcomes, instrumentation boundaries, red flags) and backlog-wide contract
    ownership resolution.
02. The `testability-probe` skill writes ownership assignments ("contract X owned
    by ST-NNNN") and a testability paragraph per epic into `backlog/epics.md`, but
    does not write failure scenarios, test paths, or risk classifications.
03. The `test-design` skill at `factory/skills/test-design/SKILL.md` is refactored
    as an implementation skill with the story-level procedure described in Change 2:
    it reads implemented code, classifies owned contracts by risk class, identifies
    untested integration paths and edge cases, and authors test files.
04. The `test-design` skill does not resolve contract ownership (the probe did that)
    and does not write into `epics.md`.
05. The developer agent's skill list includes `test-design`. After GREEN on
    non-`.feature`-governed stories, it invokes `test-design` to identify and author
    integration and edge-case tests.
06. The developer agent skips the post-TDD `test-design` invocation for
    `.feature`-governed stories.
07. The developer agent writes the `tests:` field in the story file at commit time,
    listing test modules the story owns.
08. The developer agent writes the `test-design-pass` field in the story file at
    commit time: `done` or `skipped-feature-governed`.
09. The QA agent's Fagan inspection checks the `test-design-pass` field and
    cross-references the test suite against traced contracts.
10. The reconciliation agent verifies that every story's `tests:` field matches its
    actual test files, backfills missing entries, and files `RECON` findings for
    contracts with ownership assignments but no corresponding test coverage.
11. The `test-design-verify` gate validates the `tests:` field and
    `test-design-pass` field for new-model stories, and continues to validate
    `#### Failure scenarios` / `#### Prior Tests` for old-model stories.
12. Stories with pre-existing `#### Failure scenarios` sections continue to work
    under the developer agent's existing conditional path.
13. The `create-backlog` parent skill's sequence table references `testability-probe`
    at phase 2.5 instead of `test-design`.
14. The `create-backlog-write-epics` skill surfaces the `testability-probe` option
    before the user proceeds to step 3.
15. The `create-backlog-stories` skill carries ownership assignments (not failure
    scenarios) from `epics.md` into story files.
16. The `testing-strategy.md` convention includes a section on the two-pass test
    authoring model.
17. The story template at `factory/rulebooks/templates/story.md` documents the
    `tests:` and `test-design-pass` fields.

## Open Questions — Resolved

- **Ownership stability across story slicing.** EPIC-level ownership is stable
  enough. The probe resolves ownership per contract, and story slicing splits
  implementation work, not contracts. If a slice splits a contract boundary,
  that is a scoping defect the probe's testability assessment already flags —
  the correct response is to fix the scoping, not re-run the probe. The probe
  does not re-run after slicing.
- **Probe placement in the backlog sequence.** The `testability-probe` replaces
  `test-design` at phase 2.5 in the `create-backlog` sequence — it is a
  mandatory step, not discretionary. Making it optional would let planning
  agents skip testability assessment, losing the gate that catches untestable
  epic scoping before stories are written. The planning agent invokes it at
  the same point in the sequence where `test-design` ran before.
