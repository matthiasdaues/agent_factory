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

## Four layers

| Layer                 | Owns                                                                                      |
| --------------------- | ----------------------------------------------------------------------------------------- |
| Deterministic linter  | Declarative structure: frontmatter, indexes, schemas, traceability, and formatting        |
| Contract test         | Pure behavior: parsing, normalization, policy, state transitions, and security invariants |
| Integration test      | Boundaries: installation, removal, persistence, subprocesses, and filesystems             |
| End-to-end smoke test | One representative journey through a CLI or major workflow                                |

## One contract, one owner

Every observable contract has one owning layer and one retained test or linter.
Shared behavior belongs to the shared core; an adapter proves only its distinct
translation, accounting, wiring, or boundary behavior. A higher layer may
exercise the same path as part of a journey, but it must not duplicate the
lower-layer assertions.

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

## Choose cases by behavior

Partition inputs into equivalence classes and retain one representative from
each class, plus boundary values and genuinely distinct failure modes. Prefer a
compact data table when cases differ only in fixture values. Keep security
boundaries separate even when they traverse the same code path. Do not conceal
unrelated contracts in one scenario or a large assertion loop merely to reduce
the collected-case count.

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
