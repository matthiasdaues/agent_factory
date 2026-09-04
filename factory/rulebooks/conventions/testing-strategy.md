---
title: Contract-Owned Testing Strategy
category: quality
enforcement: test authors and reviewers
version: 2.0.0
---

# Contract-Owned Testing Strategy

Keep the smallest suite that makes every important contract fail loudly at
its lowest sufficient layer. Test count and coverage percentage are
diagnostics, not quality targets.

## Why we test

A test suite in a factory-managed project serves two purposes:

1. **Catch what agents get wrong.** AI agents produce well-formed output
   most of the time, but they drift silently — renaming a path, dropping a
   conditional, changing the meaning of an instruction while keeping its
   shape. Tests are the mechanical check that catches these mistakes. This
   is the "deterministic validation" half of the factory's foundational
   principle.

2. **Give the team confidence.** The human team needs to know that the
   codebase does what they believe it does — correctness, security,
   regressions. This need exists regardless of who wrote the code. The
   factory must not dilute, replace, or restructure the team's existing
   tests to serve its own needs.

These two purposes meet in the middle of the test suite and pull apart at
the edges. The strategy must serve both.

## Three-layer model

The test suite divides into three bands. Each band has a primary purpose,
and that purpose decides who owns the testing philosophy there.

### Base — structural gates

| Layer                | Owns                                                             |
| -------------------- | ---------------------------------------------------------------- |
| Deterministic linter | Declarative structure: frontmatter, indexes, schemas, formatting |

The base catches malformed output before it reaches review. Two kinds of
linter coexist here:

- **Team linters** (ruff, eslint, mypy, formatters, pre-commit hooks the
  team already runs) own code quality. When a project already has linting
  and formatting in place, the factory does not duplicate or override it.
- **Factory linters** (context-lint, backlog-lint, spec-lint,
  transition-lint, index-lint) validate factory-specific artifact shapes
  that the team's tools do not know about. They are always additive.

For greenfield projects with no existing toolchain, the factory provides a
starting set. The team may replace it as they establish their own
conventions.

**When is the base complete?** Every factory artifact type has a structural
gate, and every team artifact type is covered by the team's own toolchain.

### Middle — contract tests

| Layer         | Owns                                                                           |
| ------------- | ------------------------------------------------------------------------------ |
| Contract test | Internal behavior: parsing, normalization, policy, state transitions, security |

This is where the two purposes meet. A contract test can verify a
requirement and act as a tripwire for agent drift at the same time.

The most dangerous agent mistakes are not structural — a linter would catch
those. They are semantic: an agent rewrites a function in valid code that
passes every linter but quietly changes what the function does. Only a test
that exercises the actual behavior will catch that.

Contract tests are the thinnest layer and the highest-value investment per
test.

**When is the middle complete?** Every internal interface and every policy
rule has one owning test that fails on a representative fault.

### Top — behavioral verification

| Layer                 | Owns                                                                                                                               |
| --------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| Acceptance test       | Observable behavior: `.feature` file execution via Gherkin runner (behave, cucumber, godog) owns the feature's behavioral contract |
| Integration test      | Boundaries: installation, removal, persistence, subprocesses, filesystems                                                          |
| End-to-end smoke test | One representative journey through a CLI or major workflow                                                                         |

The top layers verify that the assembled system delivers what was promised.
The team owns the testing philosophy here: their runner, their fixture
conventions, their assertion style, their domain boundaries. The factory's
feature-addition playbook adds top-layer tests for every new feature, but it
writes them in the style the project already uses. `detect-test-regime`
discovers the toolchain; the QA strategy maps contracts to layers; the
developer agent reads the team's existing tests as a style guide.

**When is the top complete?** The team decides. The factory ensures every
new feature gets top-layer tests, but what counts as "enough" is a team
judgment.

## How the balance shifts by project type

| Project type           | Base                                           | Middle                                              | Top                                                 |
| ---------------------- | ---------------------------------------------- | --------------------------------------------------- | --------------------------------------------------- |
| Pure factory           | Factory linters only                           | Primary investment — this is where faults hide      | Minimal — no team to set the philosophy             |
| Brownfield onboarding  | Team's existing linters; factory adds its own  | Factory adds contract tests for agent-touched code  | Team's existing suite; factory adds per-feature     |
| Opinionated greenfield | Team establishes linters; factory adds its own | Shared investment — team and factory build together | Team owns philosophy; factory writes in their voice |

## One contract, one owner

Every contract has one owning layer and one test or linter that is kept.
An adapter proves only its own translation or wiring, not the shared core.
A higher layer may exercise the same path as part of a journey, but it must
not duplicate the lower layer's assertions.

Record each contract's risk, owning layer, owner, known overlap, and
retained case near the relevant tests. A regression strengthens the
existing owner before it creates another case.

## Admit a new test

Add a test only when at least one of these is true:

- It protects a contract that has no test yet.
- It would catch a semantic change that existing structural checks miss.
- It covers a distinct security or process boundary.
- It reaches an integration seam the owning contract test cannot.
- It replaces weaker coverage while reducing total maintenance.

If none applies, strengthen the existing owner. Do not add a pytest case
for a rule already checked by a linter. Do not use a coverage percentage,
a minimum case count, or a cosmetic reduction target as a gate.

A composite risk score like CRAP (which weights complexity against coverage)
is not a coverage target. The gate threshold is on the composite score.
Such scores are admissible as gates when the pressure they create is toward
smaller code, not toward higher coverage numbers.

## Choose cases by behavior

Partition inputs into equivalence classes. Keep one representative from each
class, plus boundary values and genuinely distinct failure modes. Use a
compact data table when cases differ only in fixture values. Keep security
boundaries separate even when they share a code path. Do not hide unrelated
contracts in one scenario or a large assertion loop just to reduce the case
count.

## Risk classes

Risk classes group contracts by how complex their failure modes are. They
decide how thorough the test design must be. They are separate from layers:
a layer says *where* the test lives; the risk class says *how much design
effort* the test gets.

The factory defines three defaults. Projects can override or extend them in
`docs/charter/testing.yaml` under `risk_classes:`. The precedence chain:

1. **Project overrides in `testing.yaml`** — if `risk_classes:` is present,
   its definitions win for the classes it names.
2. **Linked testing strategy document** — if `testing_strategy:` in
   `testing.yaml` points to a document, consult it before falling back.
3. **Factory defaults below** — these apply when no project override exists.

| Risk class   | Characteristics                                          | Format                               | Budget                                     |
| ------------ | -------------------------------------------------------- | ------------------------------------ | ------------------------------------------ |
| `critical`   | Atomicity, concurrency, security invariants, idempotency | Given/When/Then/Forbidden            | Unbounded: every distinct failure mode     |
| `standard`   | CRUD operations, input validation, read APIs             | Concrete scenario text               | Equivalence: one per class plus boundaries |
| `structural` | Declarative structure, formatting, schema conformance    | Linter-owned (no test-design output) | Deterministic layer only; no pytest needed |

### Failure-scenario format

`critical` contracts use Given/When/Then/Forbidden to name the specific
failure the test prevents:

```
Given <precondition describing the system state>
When <action that triggers the contract>
Then <expected outcome under normal conditions>
Forbidden <the specific failure mode this test catches>
```

The `Forbidden` line is the test's reason for existence. If the designer
cannot state what failure mode the test catches, the test should not exist.

`standard` contracts use concrete scenario text with expected inputs and
assertions, budgeted at one representative per equivalence class plus
boundary values and distinct failure modes.

`structural` contracts are owned by linters. The test-design process writes
no pytest scenarios for them.

## Delete overlapping tests safely

For each consolidation batch:

1. Record collected cases and test-code lines before the change.
2. Name the surviving owner before deleting overlap.
3. Introduce a controlled fault (or use a bad fixture) and observe the owner
   fail.
4. Restore the implementation and run the affected domain.
5. Record cases and lines after the change, then run the full suite with
   warnings treated as errors.

Fault evidence identifies the command, fault, expected owner, and observed
failure. It is working evidence, not committed sabotage.

When a gate marker, dispatch record, or handoff identifies the revision used
for this evidence, it MUST use the full 40-character commit SHA. Abbreviated
SHAs are display-only.

## References

- [foundational-principles.md § Agentic Creation, Deterministic Validation](foundational-principles.md#agentic-creation-deterministic-validation)
- [sustainable-testing-regime.md](../../../docs/proposals/sustainable-testing-regime.md)
- [rules.md § Testing](../rules.md#testing)
