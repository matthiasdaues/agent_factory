---
title: Contract-Owned Testing Strategy
category: quality
enforcement: test authors and reviewers
version: 2.0.0
---

# Contract-Owned Testing Strategy

Keep the smallest suite that makes every important observable contract fail
loudly at its lowest sufficient layer. Test count and coverage percentage are
diagnostics, not quality targets.

## Why tests exist in an agentic workflow

A test suite in a factory-managed project serves two distinct functions:

1. **Agent-adversary detection.** AI agents are probabilistic authors. They
   produce well-formed output most of the time, but they silently drift —
   renaming a path, dropping a conditional branch, changing the meaning of an
   instruction while preserving its shape. Tests are the deterministic half
   of the foundational principle "agentic creation, deterministic validation."
   They exist to catch what the noisy channel gets wrong.

2. **Team assurance.** The human team needs confidence that the codebase does
   what they believe it does — correctness, security, regressions. This
   concern predates AI and persists regardless of who authored the code. The
   factory must not dilute, replace, or restructure the team's existing test
   suite to serve its own needs.

These two functions converge at the contract-test layer and diverge at the
extremes. The testing strategy must serve both without conflating them.

## Three-layer model

The five execution layers below group into three functional bands by primary
purpose. The bands determine who owns the testing philosophy at each level
and how the factory interacts with team-established practices.

### Base — structural gates

| Layer                | Owns                                                                 |
| -------------------- | -------------------------------------------------------------------- |
| Deterministic linter | Declarative structure: frontmatter, indexes, schemas, and formatting |

**Primary function:** agent-adversary detection.

The base catches malformed output before it reaches review. Two kinds of
linter coexist here without overlap:

- **Team linters** (ruff, eslint, mypy, formatters, pre-commit hooks the
  team already runs) own code quality. When a project already has linting and
  formatting in place, the factory backs down — it does not duplicate,
  override, or second-guess the team's structural toolchain.
- **Factory-specific linters** (context-lint, backlog-lint, spec-lint,
  transition-lint, index-lint) own factory artifact shapes that the team's
  toolchain cannot know about. These are additive, never substitutive.

For greenfield projects with no existing toolchain, the factory provides a
starting set. That is a default, not a requirement — the team may replace it
as they establish their own conventions.

**Sufficiency:** every factory artifact type has a structural gate, and every
team artifact type is covered by the team's own toolchain.

### Waist — contract tests

| Layer         | Owns                                                                           |
| ------------- | ------------------------------------------------------------------------------ |
| Contract test | Internal behavior: parsing, normalization, policy, state transitions, security |

**Primary function:** dual — agent-adversary detection and team assurance
converge here.

The contract-test layer is the thinnest and most valuable. A single contract
test can serve both functions simultaneously: it verifies a requirement *and*
it is a tripwire for agent drift. The most dangerous agent failures are not
structural — they are semantic. An agent rewrites a skill in valid YAML with
all required keys but subtly changes the behavior the skill prescribes. No
linter catches that. A contract test that exercises the behavior does.

This is where detection surface is thinnest and risk concentrates. Investment
in contract tests has the highest return per test of any layer.

**Sufficiency:** every script-to-instruction interface and every internal
policy has one owning test that would fail on a representative fault.

### Top — behavioral verification

| Layer                 | Owns                                                                                                                               |
| --------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| Acceptance test       | Observable behavior: `.feature` file execution via Gherkin runner (behave, cucumber, godog) owns the feature's behavioral contract |
| Integration test      | Boundaries: installation, removal, persistence, subprocesses, and filesystems                                                      |
| End-to-end smoke test | One representative journey through a CLI or major workflow                                                                         |

**Primary function:** team assurance.

The top layers verify that the assembled system delivers what was promised.
The team owns the testing philosophy here — their runner, their fixture
conventions, their assertion style, their domain boundaries. The factory's
feature-addition playbook produces top-layer tests for every new feature, but
it does so *in the team's voice*: shaped by the project's existing test suite,
not by factory convention. `detect-test-regime` discovers the toolchain;
the QA strategy maps contracts to layers; the developer agent reads the
team's existing tests as a style guide, not just their toolchain as a
capability list.

**Sufficiency:** the team's call. The factory ensures every feature-addition
produces top-layer coverage, but the team decides what "enough" means for
their domain.

## Adaptation by project type

The three-layer model applies to all factory-managed projects, but the
balance shifts by project type:

| Project type           | Base                                             | Waist                                                    | Top                                                   |
| ---------------------- | ------------------------------------------------ | -------------------------------------------------------- | ----------------------------------------------------- |
| Pure factory           | Factory linters only (no team toolchain)         | Primary investment — detection surface is here           | Minimal — no team to own the philosophy               |
| Brownfield onboarding  | Team's existing linters; factory adds its gates  | Factory adds contract tests for agent-touched interfaces | Team's existing suite; factory adds per-feature       |
| Opinionated greenfield | Team establishes linters; factory adds its gates | Shared investment — team and factory co-own              | Team owns philosophy; factory produces in their voice |

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
- Does it extend the detection surface against semantic agent drift?
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

- [foundational-principles.md § Agentic Creation, Deterministic Validation](foundational-principles.md#agentic-creation-deterministic-validation)
- [sustainable-testing-regime.md](../../../docs/proposals/sustainable-testing-regime.md)
- [rules.md § Testing](../rules.md#testing)
