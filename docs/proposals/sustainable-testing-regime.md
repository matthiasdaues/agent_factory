---
schema_version: 2
title: "Sustainable Testing Regime"
status: open
owner: agent-factory
created: 2026-07-22
updated: 2026-08-27
supersedes:

impact:
  scope: cross_component
  architecture_change: false
  external_contract_change: false
  boundaries:
    - factory/rulebooks/conventions/testing-strategy.md
    - factory/scripts/run-tests

governance:
  assurance: elevated
  risk_domains:
    - reliability
    - operations

estimate:
  as_of: 2026-08-27
  basis: judgment
  confidence: low
  human_review_hours: unknown
  normalized_tokens: unknown
  estimated_consumption: unknown
---

# Feature Request: Sustainable Testing Regime

## Summary

Replace the repository's additive test culture with a contract-owned testing
regime. The first release consolidates duplicated structural and behavioral
coverage, assigns each contract to one test layer, and keeps a small set of
end-to-end journeys for integration risk.

The goal is lower maintenance cost and clearer failure diagnosis, not a cosmetic
test-count target. A smaller suite is successful only when each retained test or
deterministic linter has a distinct reason to fail.

## Motivation

The suite currently collects roughly 1,000 pytest cases (785 test functions
across 76 files and 21,650 lines, expanding through parametrize). The largest
domain concentrations are:

- **Research** (155 functions) — many tests assert individual frontmatter fields,
  file presence, or prose fragments already governed by schemas and `index-lint`.
- **Usage capture** (128 functions) — `test_usage_capture.py` alone has 63
  functions / 1,982 lines; `test_usage_capture_pi_e2e.py` adds 33 functions /
  1,768 lines. Shared lifecycle behavior is repeated across CLI adapters.
- **Dispatch** (124 functions) — `test_dispatch_lifecycle.py` (35 functions /
  881 lines) and a cluster of integration files covering planning, merging,
  escalation, interruption, and status. Many test overlapping state-machine
  transitions.
- **Init-factory** (52 functions) — spread across nine files covering
  guardrails, codex generation, handoff contracts, and usage-capture wiring.

The problem is maintainability at scale: every finding tends to add a named
regression case, shared lifecycle behavior is repeated through adapters,
declarative files are inspected by many narrow pytest functions, and the dispatch
domain grew an integration-test file per concern without consolidating shared
state-machine contracts. This makes ownership unclear and safe deletion
difficult.

## Core Principles

- One observable contract has one owning layer.
- Shared behavior is tested in the shared core; adapters prove translation and
  wiring only.
- Deterministic linters own declarative structure, not pytest.
- Equivalence classes and distinct failure modes replace input cross-products.
- A regression strengthens an existing contract test before creating a new one.
- Test deletion requires evidence that a surviving test or linter catches a
  representative fault.
- Counts are reported by layer and contract; no minimum test count is a quality
  metric.

## Design

### Five-layer portfolio

| Layer                  | Owns                                                                            | Initial planning range |
| ---------------------- | ------------------------------------------------------------------------------- | ---------------------: |
| Deterministic linters  | Frontmatter, indexes, schemas, traceability, formatting                         |         Outside pytest |
| Acceptance tests       | Observable behavior via `.feature` files executed through a Gherkin test runner |  No existing cases yet |
| Contract tests         | Parsers, normalization, policies, state transitions, security invariants        |          200–280 cases |
| Integration tests      | Installation, removal, persistence, subprocess and filesystem boundaries        |           60–100 cases |
| End-to-end smoke tests | One representative journey per CLI or major workflow                            |            15–30 cases |

The ranges guide consolidation; they are not acceptance gates. A contract may
justify a case outside the range. The acceptance test layer has no existing
`.feature` files; this release does not create them but assigns contracts
so that future acceptance tests slot into the correct layer.

### Ownership record

Each consolidated domain records:

- the contract and its risk;
- its owning layer and test/linter;
- existing overlapping cases;
- the retained case or deterministic check;
- representative fault evidence proving the owner detects a violation.

Ownership may live in the relevant test module's top-level documentation or a
compact table beside the subsystem documentation. It must stay close enough to
the tests that reviewers can apply it when adding a case.

### Consolidation rules

1. Delete pytest checks for declarative structure already enforced by a schema,
   `index-lint`, or another deterministic validator.
2. Merge variations that differ only in fixture data into one equivalence-table
   contract test.
3. Keep distinct security boundaries separate even when they share a code path.
4. Test shared capture lifecycle transitions once. CLI adapter suites retain only
   adapter-specific payload, accounting, and wiring behavior.
5. Model Pi's distinct asynchronous lifecycle as state/event/terminal-outcome
   transitions, with separate smoke journeys only for human shutdown,
   `run_agent`, and `dispatch_wave`.
6. Consolidate dispatch integration files around shared state-machine contracts.
   Separate files per concern (escalation, interruption, merge, status) retain
   only the concern-specific transitions; shared dispatch lifecycle assertions
   belong in `test_dispatch_lifecycle.py`.
7. Do not hide complexity by putting unrelated assertions or large scenario
   loops into one test. Fewer cases must also mean less test code and fewer
   independently maintained fixtures.

### Verification while deleting

For every consolidation batch:

1. Record the baseline collected cases and test-module line count.
2. Identify the contract owner before deleting overlap.
3. Demonstrate one representative fault: temporarily violate the contract or
   run the retained test against a controlled bad fixture and observe failure.
4. Restore production code/fixture and run the affected domain.
5. Run the full suite with warnings treated as errors.

The fault demonstration is working evidence, not committed sabotage or a new
permanent mutation framework.

## Scope

**In the first release:**

- A repository testing-strategy convention and new-test decision rule.
- Consolidation of research structural tests (155 functions across 14+ files).
- Consolidation of usage-capture core tests (128 functions across 6 files).
- Consolidation of dispatch integration tests (124 functions across 12 files).
- Thin Claude, Copilot, and Codex adapter smoke suites.
- Transition-focused Pi capture tests.
- Consolidation of shared capture lifecycle, installation, and removal tests.
- Consolidation of init-factory tests (52 functions across 9 files).
- Before/after counts and contract-ownership evidence per domain.

**Explicitly deferred (do NOT plan stories for these):**

- A mandatory global coverage percentage.
- Mutation-testing infrastructure or a new test framework.
- CI-provider configuration or nightly scheduling; the repository does not own
  a confirmed universal CI surface for every consumer.
- Production-code refactoring whose only purpose is making deletion targets.
- Rewriting unrelated functional tests that already have clear ownership.

## Design Details

### New-test decision

A proposed test is admitted only if the reviewer can answer yes to at least one:

- Does it protect a new observable contract?
- Does it cover a distinct security or process boundary?
- Does it exercise an integration seam not reached by the owning contract test?
- Does it replace weaker coverage while reducing total maintenance?

If none applies, strengthen the existing owner instead.

### Expected direction

The repository should plausibly settle near 300–420 collected cases after the
scoped consolidation, but no story passes or fails on that number. It passes on
explicit ownership, reduced test code, preserved contract detection, and a green
full suite.

## Open Questions

None. Domain-specific ambiguity is resolved conservatively: retain a test when
its distinct contract cannot be proven redundant within the story.

## Completion Criteria

- Every scoped test domain records its owned contracts and layers in a
  docstring table at the top of the owning test module (or, for linter-owned
  contracts, beside the linter configuration).
- Structural duplication covered by deterministic validators is removed.
- Shared lifecycle behavior is not repeated in each CLI adapter suite.
- Pi lifecycle coverage is organized by unique transition and entry-point smoke
  journeys.
- Every story reports before/after cases and lines, plus representative fault
  evidence.
- The full suite passes with warnings treated as errors.

## Guiding Rule

Keep the smallest suite that makes every important contract fail loudly at its
lowest sufficient layer.

## Review — 2026-08-27

Reviewer: proposal-review-agent
Reviewed commit: e4ea2c70e11ee827e24642d822ef56184ffe91c7
Disposition: findings

### Findings

| ID      | Severity | Check | Status | Finding                                                                                                                                                                                                                                                                                                                                                                     |
| ------- | -------- | ----- | ------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| PROP-01 | major    | 03    | open   | Four-layer portfolio in Design contradicts the five-layer model in boundary file `testing-strategy.md`, which adds an Acceptance test layer (Gherkin `.feature` files) between Deterministic linter and Contract test. Planning cannot decompose layer-assignment stories when the proposal and convention disagree on how many layers exist and what each owns.            |
| PROP-02 | minor    | 01    | open   | Completion criterion 1 uses "publishes its owned contracts and layers" without specifying the artifact form or location. The Design section offers two options with "may" (test module docs or compact table) but the criterion itself does not reference which form satisfies it; a verifier cannot mechanically confirm what "publishes" means without asking the author. |
| PROP-03 | minor    | 08    | open   | Estimate omits the `estimated_consumption` block (overhead multiplier and playbook) rather than setting it to `unknown`. Template conformance requires the field to be present.                                                                                                                                                                                             |

### Summary

Checks 02, 04, 05, 06, and 07 pass cleanly. One major finding on check 03: the proposal describes a four-layer portfolio but the boundary convention it declares already contains a five-layer model with an Acceptance test layer the proposal does not account for — this must be reconciled before planning can decompose stories around consistent layers. Two minor findings address a vague completion criterion verb and a missing estimate template field.

## Review — 2026-08-28

Reviewer: proposal-review-agent
Reviewed commit: e4ea2c70e11ee827e24642d822ef56184ffe91c7
Disposition: findings

### Prior findings

| ID      | Severity | Check | Status | Finding                                                                                                                                                                                                                                                                                                               |
| ------- | -------- | ----- | ------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| PROP-01 | major    | 03    | open   | No change since prior review. The Design section still describes a "Four-layer portfolio" while boundary file `testing-strategy.md` defines five layers including an Acceptance test layer. The proposal has not been modified at this commit; the contradiction persists as stated in the 2026-08-27 review.         |
| PROP-02 | minor    | 01    | open   | No change since prior review. Completion criterion 1 still reads "publishes its owned contracts and layers" without specifying the artifact form. The Design section still hedges between test-module documentation and a compact table using "may"; the criterion remains unverifiable without author clarification. |
| PROP-03 | minor    | 08    | open   | No change since prior review. The estimate frontmatter still omits the `estimated_consumption` block entirely rather than setting it to `unknown`. Template conformance requires the field to be present.                                                                                                             |

### Fresh eight-check pass

| Check | Name                             | Status | Notes                                                                                                                                                             |
| ----: | -------------------------------- | ------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
|    01 | Completion criteria testable     | FAIL   | Criteria 2-6 are mechanically verifiable. Criterion 1 remains untestable (PROP-02).                                                                               |
|    02 | Scope boundary sharp             | PASS   | In-scope items name domains with function counts; deferred items are concrete exclusions. Partition is clean.                                                     |
|    03 | Design decomposable              | FAIL   | Consolidation rules and verification steps are concrete. Four-layer portfolio contradicts five-layer boundary convention (PROP-01). Planner cannot assign layers. |
|    04 | Impact classification consistent | PASS   | cross_component, no architecture change, no external contract change — all match the design.                                                                      |
|    05 | Boundary references exist        | PASS   | Both `factory/rulebooks/conventions/testing-strategy.md` and `factory/scripts/run-tests` resolve at the reviewed commit.                                          |
|    06 | Open questions genuine           | PASS   | "None" with conservative resolution principle is defensible, though the layer discrepancy (PROP-01) is functionally an unresolved question.                       |
|    07 | Motivation justifies timing      | PASS   | Concrete data (785 functions, 76 files, 21,650 lines) with named growth patterns justifies proactive consolidation.                                               |
|    08 | Estimate plausible               | FAIL   | `unknown` values acceptable at low confidence. `estimated_consumption` block still absent (PROP-03).                                                              |

### Summary

No changes were made to the proposal between the 2026-08-27 review and this pass — the commit SHA is identical. All three prior findings remain open and unaddressed. Checks 02, 04, 05, 06, and 07 pass. Checks 01, 03, and 08 fail on the same findings as the prior review. The major blocker remains PROP-01: the four-layer portfolio in the proposal body must be reconciled with the five-layer model in its own boundary convention before this proposal is ready to plan from.

## Review — 2026-08-28 (pass 2)

Reviewer: proposal-review-agent
Reviewed commit: e4ea2c70e11ee827e24642d822ef56184ffe91c7 (working-tree modifications, not yet committed)
Disposition: clean

### Prior findings — resolution

| ID      | Severity | Check | Prior Status | Status   | Resolution                                                                                                                                                                                                                                                                                                                                                                                             |
| ------- | -------- | ----- | ------------ | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| PROP-01 | major    | 03    | open         | resolved | Design heading changed to "Five-layer portfolio" and the table now includes an Acceptance test row between Deterministic linters and Contract tests with range "No existing cases yet." Clarifying note states this release assigns contracts for future acceptance tests rather than creating `.feature` files. The proposal now matches the five-layer model in boundary file `testing-strategy.md`. |
| PROP-02 | minor    | 01    | open         | resolved | Completion criterion 1 now reads "records its owned contracts and layers in a docstring table at the top of the owning test module (or, for linter-owned contracts, beside the linter configuration)." This specifies both the artifact form (docstring table) and its location, making the criterion mechanically verifiable without asking the author.                                               |
| PROP-03 | minor    | 08    | open         | resolved | Estimate frontmatter now includes `estimated_consumption: unknown`. Field is present and template-conformant.                                                                                                                                                                                                                                                                                          |

### Fresh eight-check pass

| Check | Name                             | Status | Notes                                                                                                                                                                                                                                               |
| ----: | -------------------------------- | ------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
|    01 | Completion criteria testable     | PASS   | All six criteria are mechanically verifiable: docstring table presence (1), linter-duplicate removal (2), no shared lifecycle in adapters (3), Pi transition organization (4), before/after metrics per story (5), green suite with `-W error` (6). |
|    02 | Scope boundary sharp             | PASS   | In-scope names four domains with function counts and file counts. Deferred items are five concrete exclusions. Partition is clean.                                                                                                                  |
|    03 | Design decomposable              | PASS   | Five-layer portfolio matches boundary convention. Seven consolidation rules are concrete. Five verification steps are specific. Planning can decompose into INVEST stories without re-deriving the design.                                          |
|    04 | Impact classification consistent | PASS   | `cross_component` fits multi-domain test consolidation. `architecture_change: false` and `external_contract_change: false` both match the design — this is internal test reorganization with no structural or API changes.                          |
|    05 | Boundary references exist        | PASS   | Both `factory/rulebooks/conventions/testing-strategy.md` and `factory/scripts/run-tests` resolve at the reviewed commit.                                                                                                                            |
|    06 | Open questions genuine           | PASS   | "None" with conservative retention principle is defensible now that the layer discrepancy is resolved. No padding disguised as questions.                                                                                                           |
|    07 | Motivation justifies timing      | PASS   | Concrete data (785 functions, 76 files, 21,650 lines) with named additive growth patterns justifies proactive consolidation over backlog deferral.                                                                                                  |
|    08 | Estimate plausible               | PASS   | All values `unknown` at `confidence: low` with `judgment` basis. `estimated_consumption` field present. Template-conformant.                                                                                                                        |

### Summary

The author addressed all three prior findings. The five-layer portfolio now matches the boundary convention, the first completion criterion specifies its artifact form and location, and the estimate frontmatter includes the required `estimated_consumption` field. All eight checks pass. The proposal is ready to plan from.
