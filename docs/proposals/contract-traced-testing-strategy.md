---
schema_version: 2
title: Contract-Traced Testing Strategy
status: superseded
owner: md@matthiasdaues.de
created: 2026-08-28
updated: 2026-08-28
supersedes:

impact:
  scope: cross_component
  architecture_change: false
  external_contract_change: false
  boundaries:
    - .claude/skills/qa-strategy-from-spec/SKILL.md
    - .claude/skills/mutation-analysis/SKILL.md
    - .claude/agents/kit-manager.md
    - .claude/agents/developer-agent.md

governance:
  assurance: elevated
  risk_domains:
    - reliability

estimate:
  as_of: 2026-08-28
  basis: judgment
  confidence: medium
  human_review_hours:
    min: 1.0
    max: 2.0
  normalized_tokens:
    min: 8000
    max: 15000
  estimated_consumption:
    min: 120000
    max: 375000
    overhead_multiplier: 15
    playbook: feature-addition
---

# Feature Request: Contract-Traced Testing Strategy

## Summary

The QA strategy derivation chain (`kit-manager` → `qa-strategy-from-spec` → `developer-agent` → `mutation-analysis`) has no traceable link between the project's declared testing decisions, the repository's actual test infrastructure, and the per-feature QA strategy it produces. This proposal wires those four components into a closed loop where the charter is the authority, the repository is the ground truth, the Factory testing convention is shared vocabulary, and mutation analysis audits contract-ownership assignments mechanically.

## Motivation

Today `qa-strategy-from-spec` reads only the `.feature` file, entity model, and interface contracts. It applies the Factory `testing-strategy.md` convention as its structural backbone. The project charter (`docs/charter/development.md`) declares specific testing decisions — real PostgreSQL via Toxiproxy, no SQLite fallback, pytest markers, Vitest for Vue, `make test` as entry point — but none of these flow into the QA strategy. The repository's actual test infrastructure (`conftest.py` patterns, test directory layout, CI config) is also not consulted.

The result is a QA strategy that is coincidentally consistent with the charter, not traceably derived from it. An implementer must bridge the gap between what the QA strategy prescribes (layers, contracts, boundaries) and how the repository actually runs tests (fixtures, markers, entry points). That bridging happens silently in each developer-agent session and the knowledge evaporates.

Mutation analysis runs as a standalone gate that blocks on surviving mutants, but does not connect back to the QA strategy's contract-owner table. It cannot distinguish "the declared owner missed this fault" from "nobody caught it" — two different signals that require different responses.

## Core Principles

- The project charter is the authority for testing decisions; the Factory convention provides vocabulary, not bindings.
- The repository's test infrastructure is the ground truth; the QA strategy must be grounded in what exists, not what the convention assumes.
- Every contract-ownership assignment in a QA strategy must be mechanically verifiable — mutation analysis is the verification method.
- Feedback flows backward: implementation reality feeds back to the QA strategy and charter, not just forward from spec to tests.

## Design

### 1. kit-manager: structured testing bindings in the charter

The kit-manager's charter completeness sweep adds a structured testing-bindings table to `docs/charter/development.md`. The table declares, for each test layer the project uses:

| Layer                 | Tool                             | Infrastructure                        | Entry point  | Anti-patterns                        |
| --------------------- | -------------------------------- | ------------------------------------- | ------------ | ------------------------------------ |
| Deterministic linter  | Ruff, ESLint, pre-commit scripts | none                                  | `make check` | —                                    |
| Acceptance test       | pytest (behave or plain)         | PostgreSQL via Toxiproxy              | `make test`  | no SQLite, no mocked DB transactions |
| Contract test         | pytest, Vitest                   | none (golden fixtures)                | `make test`  | —                                    |
| Integration test      | pytest                           | PostgreSQL, NATS JetStream, Toxiproxy | `make test`  | no mocked broker custody             |
| End-to-end smoke test | pytest + docker compose          | full stack                            | `make test`  | no browser e2e beyond single smoke   |

The table is the project's binding of the Factory's five-layer vocabulary to concrete tooling and infrastructure. The kit-manager populates it from the existing Testing section prose and a repo scan (conftest.py, test directories, CI config, Makefile targets). Existing prose remains; the table makes it machine-traceable.

### 2. qa-strategy-from-spec: two new inputs, grounded derivation

The skill adds two required inputs before Step 1:

- `docs/charter/development.md` — read the testing-bindings table. Map feature contracts to the charter's declared layers, not the Factory's generic five. If a contract needs a layer the charter has not declared, emit a gap finding rather than silently assuming the layer exists.
- Repo scan — read root `conftest.py`, `packages/*/tests/` layout, and `Makefile`/`run-dev.sh` test targets. Verify that the charter's declared infrastructure and entry points match what exists. Record mismatches as gap findings.

The "Generated from" header in the output adds:

```markdown
- Charter testing bindings: `docs/charter/development.md` § Testing
- Repo test infrastructure: conftest.py, packages/*/tests/
```

Step 3 (Assign Test Owners) changes from "Apply `testing-strategy.md` as the governing policy" to "Apply the charter's testing-bindings table as the governing policy; use `testing-strategy.md` for vocabulary and the overlap-deletion protocol."

### 3. developer-agent: feedback channel for test-harness mismatches

When the developer-agent implements a story's tests and encounters a mismatch between the QA strategy's prescribed layer/tooling and the repository's actual test harness (missing fixture pattern, no marker support, wrong entry point, missing infrastructure), it invokes `spec-feedback` against the QA strategy document. The finding names the contract, the prescribed layer, and the concrete obstacle.

This is not a new mechanism — `spec-feedback` already exists. The change is that the developer-agent's workflow explicitly checks for harness mismatches after writing tests and before reporting the story as complete.

### 4. mutation-analysis: contract-ownership auditor mode

The `mutation-analysis` skill gains an optional input: the per-feature QA strategy's contract-owner table. When present, each surviving mutant is classified not just by location and resolution action, but also by:

- **Which contract it touches** — derived from the contract-owner table's source file and line mappings.
- **Whether the declared owner caught it** — cross-referenced against which test layer killed the mutant.

The survivor classification output adds a `contract_owner_status` field:

- `owner_held` — the declared owner killed the mutant. If overlap tests also killed it, that overlap is safe to trim.
- `owner_failed` — the declared owner did not kill the mutant, but another layer did. The ownership assignment in the QA strategy is wrong. File a `spec-feedback` finding.
- `uncaught` — no layer caught the mutant. Existing resolution actions apply (`add-missing-test`, `remove-dead-code`, `file-qa-finding`), directed at the declared owner.

This replaces the manual "representative fault" protocol in the testing strategy's safe-deletion procedure with a mechanical equivalent. When the developer-agent or a QA consolidation pass wants to delete overlapping tests, the mutation-analysis report provides the evidence that the surviving owner still detects the fault class.

## Scope

**In the first release:**

- kit-manager adds the testing-bindings table to `docs/charter/development.md` during charter completeness sweep and during `--init --scan` for brownfield onboarding.
- `qa-strategy-from-spec` reads the charter and scans the repo before assigning contract owners. Gap findings are emitted for undeclared layers and charter/repo mismatches.
- developer-agent invokes `spec-feedback` when test-harness mismatches are found during story implementation.
- `mutation-analysis` accepts the QA strategy's contract-owner table as optional input and classifies survivors by ownership status.

**Explicitly deferred (do NOT plan stories for these):**

- Automated reconciliation of the charter's testing-bindings table against CI pipeline definitions.
- A structured machine-readable format for the testing-bindings table (YAML, JSON); the first release uses a Markdown table.
- Integration with external test-analytics or coverage-tracking systems.
- Changes to the Factory `testing-strategy.md` convention itself — this proposal works within the existing vocabulary.

## Design Details

**Charter table format.** The testing-bindings table uses the same five layer names as the Factory convention. The "Tool" column names the concrete test runner or linter. The "Infrastructure" column names required services (PostgreSQL, NATS, Toxiproxy) or "none." The "Entry point" column names the shell command. The "Anti-patterns" column lists what must not be used at that layer in this project (e.g., "no SQLite fallback"). If a project does not use all five layers, the unused rows are omitted, not marked "n/a."

**Repo scan scope.** The qa-strategy-from-spec repo scan reads: root `conftest.py`, each `packages/*/tests/conftest.py`, `Makefile` test targets, `run-dev.sh` test-related commands, `pyproject.toml` pytest configuration, and `vitest.config.*`. It does not execute tests or parse CI pipeline YAML.

**Mutation-analysis contract mapping.** The contract-owner table maps contracts to source scenarios. The mutation-analysis script maps mutants to source files and lines. The join is by file path: a mutant in a file that a contract's source scenario exercises is attributed to that contract. This is approximate — a file may contain code for multiple contracts — but it is sufficient for the first release. Finer-grained mapping (function-level, AST-level) is deferred.

**Feedback loop closure.** When `spec-feedback` files a finding against the QA strategy, the finding names the specific contract-owner row that is wrong and proposes a correction. The QA strategy is updated in the same story or in a follow-up QA loop, not deferred indefinitely.

## Open Questions

- Should the testing-bindings table live in its own charter file (`docs/charter/testing.md`) rather than as a section in `development.md`? Separating it would make the kit-manager's scan target cleaner but adds a file to maintain.

## Completion Criteria

- The kit-manager produces a testing-bindings table in `docs/charter/development.md` that a human reviewer confirms matches the repository's actual test infrastructure.
- `qa-strategy-from-spec` fails with a diagnostic when `docs/charter/development.md` is missing or lacks a testing-bindings table.
- A per-feature QA strategy produced after this change traces every contract-owner assignment to a charter-declared layer, not to the Factory convention directly.
- `mutation-analysis --qa-strategy <path>` classifies each surviving mutant by contract-ownership status (`owner_held`, `owner_failed`, `uncaught`) when the QA strategy is provided.
- The developer-agent invokes `spec-feedback` at least once during a story where the test harness does not match the QA strategy's prescribed layer, and the resulting finding is actionable.
- The full loop is demonstrable on the existing `production-grade-remote-command-foundation` feature: re-derive its QA strategy with the charter as input and confirm the contract-owner assignments change or gain traceability.

## Guiding Rule

The Factory convention names the layers; the charter binds them to this project; the QA strategy maps contracts to those bindings; mutation analysis verifies the map holds; and mismatches flow backward, not into silence.
