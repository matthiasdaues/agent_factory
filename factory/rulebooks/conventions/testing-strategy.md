---
title: Contract-Owned Testing Strategy
category: quality
enforcement: test authors and reviewers
version: 1.0.0
---

# Contract-Owned Testing Strategy

Keep the smallest suite that makes every important observable contract fail
loudly at its lowest sufficient layer. Test count and coverage percentage are
diagnostics, not quality targets.

## Five layers

| Layer                 | Owns                                                                                                                               |
| --------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| Deterministic linter  | Declarative structure: frontmatter, indexes, schemas, traceability, and formatting                                                 |
| Acceptance test       | Observable behavior: `.feature` file execution via Gherkin runner (behave, cucumber, godog) owns the feature's behavioral contract |
| Contract test         | Internal behavior: parsing, normalization, policy, state transitions, and security invariants                                      |
| Integration test      | Boundaries: installation, removal, persistence, subprocesses, and filesystems                                                      |
| End-to-end smoke test | One representative journey through a CLI or major workflow                                                                         |

## One contract, one owner

Every observable contract has one owning layer and one retained test or linter.
Shared behavior belongs to the shared core; an adapter proves only its distinct
translation, accounting, wiring, or boundary behavior. A higher layer may
exercise the same path as part of a journey, but it must not duplicate the
lower-layer assertions.

The acceptance test layer (`.feature` files executed through a Gherkin test runner)
owns the feature's behavioral contract — what end users or the system observe. The
contract test layer owns internal behavior: parsing, normalization, policy, and
state transitions. These two layers do not overlap: a `.feature` Scenario tests
observable behavior; a contract test tests the internal mechanism. Contract tests
strengthen the design of individual components; acceptance tests verify that the
assembled system delivers the promised behavior.

Record the contract, its risk, owning layer, owner, known overlap, and retained
case close to the relevant tests or subsystem documentation. A regression
strengthens that owner before it creates another case.

## Admit a new test

Admit a proposed test only when at least one answer is yes:

- Does it protect a new observable contract?
- Does it cover a distinct security or process boundary?
- Does it exercise an integration seam the owning contract test cannot reach?
- Does it replace weaker coverage while reducing total maintenance?

If none applies, strengthen the existing owner. Do not add pytest coverage for
a rule already owned by a deterministic linter. Do not use a fixed coverage
percentage, a minimum case count, or a cosmetic reduction target as an
acceptance gate.

A composite structural risk score — such as CRAP, which weights cyclomatic
complexity against coverage — is not a coverage target. Coverage enters as a
counterweight to complexity; the gate threshold is on the composite score, not
on coverage itself. Such scores are admissible as acceptance gates when the
pressure they apply is toward smaller code, not toward higher coverage numbers.

## Choose cases by behavior

Partition inputs into equivalence classes and retain one representative from
each class, plus boundary values and genuinely distinct failure modes. Prefer a
compact data table when cases differ only in fixture values. Keep security
boundaries separate even when they traverse the same code path. Do not conceal
unrelated contracts in one scenario or a large assertion loop merely to reduce
the collected-case count.

## Risk classes

Risk classes group contracts by failure-mode complexity to determine test-design
treatment. They are orthogonal to layers: a layer says _where_ the test lives;
the risk class says _how thorough_ the test design must be.

The factory defines three default risk classes below. Projects can override or
extend them in `docs/charter/testing.yaml`'s `risk_classes:` section. The
precedence chain is:

1. **Project-level overrides in `testing.yaml`** — if `risk_classes:` is
   present, use its definitions for matching classes.
2. **Project-linked testing strategy document** — if a testing strategy is
   configured (via `testing_strategy:` in `testing.yaml`), consult it for
   risk-class definitions before falling back.
3. **Factory convention defaults below** — these definitions apply when no
   project override exists.

| Risk class   | Characteristics                                          | Format                               | Budget                                     |
| ------------ | -------------------------------------------------------- | ------------------------------------ | ------------------------------------------ |
| `critical`   | Atomicity, concurrency, security invariants, idempotency | Given/When/Then/Forbidden            | Unbounded: every distinct failure mode     |
| `standard`   | CRUD operations, input validation, read APIs             | Concrete scenario text               | Equivalence: one per class plus boundaries |
| `structural` | Declarative structure, formatting, schema conformance    | Linter-owned (no test-design output) | Deterministic layer only; no pytest needed |

### Failure-scenario format

`critical` contracts use the Given/When/Then/Forbidden format to capture the
specific failure mode the test is designed to catch:

```
Given <precondition describing the system state>
When <action that triggers the contract>
Then <expected outcome under normal conditions>
Forbidden <the specific failure mode this test catches>
```

The `Forbidden` line is the test's reason for existence — it names the exact
failure the test is designed to prevent. If the test designer cannot state what
failure mode the test catches, the test should not exist.

`standard` contracts use concrete scenario text with expected inputs and
assertions. The admit-a-test budget applies: one representative per equivalence
class plus boundary values and distinct failure modes.

`structural` contracts are owned by the deterministic linter layer. The
test-design process emits no pytest scenarios for structural contracts; they are
validated by linters, schema validators, and formatters at CI time.

## Delete overlapping tests safely

For each consolidation batch:

1. Record collected cases and test-code lines before the change.
2. Name the surviving contract owner before deleting overlap.
3. Introduce a controlled representative fault, or use a controlled bad
   fixture, and observe the owner fail.
4. Restore the implementation or fixture and run the affected domain.
5. Record cases and lines after the change, then run the full suite with
   warnings treated as errors.

Representative-fault evidence identifies the command, fault, expected owner,
and observed failure. It is working evidence, not committed sabotage and not a
requirement for mutation-testing infrastructure.

When a gate marker, dispatch record, handoff, or other machine-consumed record
identifies the revision used for this evidence, it MUST use the full
40-character commit SHA. Abbreviated SHAs are display-only.

## References

- [sustainable-testing-regime.md](../../../docs/proposals/sustainable-testing-regime.md)
- [rules.md § Testing](../rules.md#testing)
