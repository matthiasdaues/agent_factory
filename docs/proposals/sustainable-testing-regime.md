---
schema_version: 2
title: "Sustainable Testing Regime"
status: open
owner: agent-factory
created: 2026-07-22
updated: 2026-07-29
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
  as_of: 2026-07-29
  basis: judgment
  confidence: low
  human_review_hours: unknown
  normalized_tokens: unknown
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

The suite currently collects 448 pytest cases. The largest concentrations are
usage capture (`test_usage_capture.py`: 65 functions / 1,747 lines;
`test_usage_capture_pi_e2e.py`: 32 functions / 1,353 lines) and research
artifacts, where many tests assert individual frontmatter fields, file presence,
or prose fragments already governed by schemas and `index-lint`.

The full suite completes in about 83 seconds, so runtime is tolerable. The
problem is maintainability: every finding tended to add a named regression case,
shared lifecycle behavior was repeated through adapters, and declarative files
were inspected by many narrow pytest functions. This makes ownership unclear and
safe deletion difficult.

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

### Four-layer portfolio

| Layer                  | Owns                                                                     | Initial planning range |
| ---------------------- | ------------------------------------------------------------------------ | ---------------------: |
| Deterministic linters  | Frontmatter, indexes, schemas, traceability, formatting                  |         Outside pytest |
| Contract tests         | Parsers, normalization, policies, state transitions, security invariants |          120–160 cases |
| Integration tests      | Installation, removal, persistence, subprocess and filesystem boundaries |            40–60 cases |
| End-to-end smoke tests | One representative journey per CLI or major workflow                     |            10–20 cases |

The ranges guide consolidation; they are not acceptance gates. A contract may
justify a case outside the range.

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
6. Do not hide complexity by putting unrelated assertions or large scenario
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
- Consolidation of research structural tests.
- Consolidation of usage-capture core tests.
- Thin Claude, Copilot, and Codex adapter smoke suites.
- Transition-focused Pi capture tests.
- Consolidation of shared capture lifecycle, installation, and removal tests.
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

The repository should plausibly settle near 180–250 collected cases after the
scoped consolidation, but no story passes or fails on that number. It passes on
explicit ownership, reduced test code, preserved contract detection, and a green
full suite.

## Open Questions

None. Domain-specific ambiguity is resolved conservatively: retain a test when
its distinct contract cannot be proven redundant within the story.

## Completion Criteria

- Every scoped test domain publishes its owned contracts and layers.
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
