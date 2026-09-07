---
id: 0012
status: accepted
evaluation: pugh-matrix
---

# Dispatcher-owned semantic gate loop

## Context

The Factory introduces three semantic quality gates — CRAP scoring, mutation analysis, and dependency-rule checking — that run deterministic scripts on committed code. The question is where in the workflow these gates fire and who owns their execution.

Three models were evaluated:

1. **Developer-owned** (baseline): The developer agent runs the gate scripts itself after writing code, reads the results, and fixes issues in the same context window.
2. **Dispatcher-owned**: The implementation-agent dispatcher runs the gate scripts after the developer commits. If any gate fails, the dispatcher spawns a fresh developer agent with only the gate reports and affected files as input. The developer never sees or runs the gates.
3. **CI-owned**: The gates run in a CI pipeline (GitHub Actions, etc.) triggered by push or PR. Results feed back to the local workflow asynchronously.

The core tension: the Factory's foundational principle "Agentic Creation, Deterministic Validation" requires that agents do not validate their own work. A developer agent running its own quality gates is self-validation — the same trust boundary violation that ADR-0003 eliminated for test execution.

## Decision

The implementation-agent dispatcher owns the semantic gate loop. The developer agent creates code and tests; the dispatcher runs the gates on committed artifacts; a fresh developer agent fixes failures. This separation holds for all three gates.

### Pugh Matrix

| Criterion                                           | Weight | A: Developer-owned (baseline) | B: Dispatcher-owned | C: CI-owned |
| --------------------------------------------------- | ------ | ----------------------------- | ------------------- | ----------- |
| No self-validation (foundational principle)         | 3      | 0                             | +1                  | +1          |
| Context contamination prevention                    | 2      | 0                             | +1                  | +1          |
| Gate skip prevention                                | 3      | 0                             | +1                  | +1          |
| Iteration speed (fix feedback latency)              | 2      | 0                             | 0                   | -1          |
| Clean Architecture (creation/validation separation) | 2      | 0                             | +1                  | +1          |
| Existing infrastructure fit                         | 1      | 0                             | +1                  | -1          |
| **Weighted total**                                  |        | **0**                         | **+11**             | **+7**      |

Option B wins. Both B and C satisfy the no-self-validation principle, but CI-owned gates (C) add network latency and require infrastructure the Factory does not currently have. The dispatcher already owns wave scheduling, branch/merge ordering, and completion tracking (it is the implementation-agent). Extending its per-story loop with a gate-check step is a natural fit.

### Gate execution sequence

After each developer-agent commit:

1. Dispatcher runs `crap-score` on committed artifacts.
2. Dispatcher runs `mutation-analysis` (diff-scoped to the story's changed production files).
3. Dispatcher runs `dependency-check` against `architecture.dsl` dependency rules.
4. Each gate produces a JSON report under `.current-work/<gate-name>/<story-id>.json`.
5. If all gates pass, the dispatcher proceeds to `premerge-check` and merge.
6. If any gate fails, the dispatcher spawns a fresh developer agent with only the failing gate reports and affected files as input context. Maximum three fix iterations before the story is marked blocked.

Each fix iteration starts a fresh developer context. Gate output from a prior iteration does not accumulate in the developer's window.

## Amended

**Date**: 2026-08-28
**Reason**: Test Gate Presence over Test Execution ([proposal](../proposals/test-gate-presence-over-test-execution.md))

The dispatcher's three-gate quality sequence loses its second gate. `factory/scripts/mutation-analysis` is deleted from the repository because it hardcodes mutmut with pytest internals and assumes the test runner is reachable on the host — the same boundary violation that motivated deleting `factory/scripts/run-tests`.

**Gate execution sequence (amended):**

After each developer-agent commit:

1. Dispatcher runs `crap-score` on committed artifacts.
2. Dispatcher runs `dependency-check` against `architecture.dsl` dependency rules.
3. Each gate produces a JSON report under `.current-work/<gate-name>/<story-id>.json`.
4. If all gates pass, the dispatcher proceeds to `premerge-check` and merge.
5. If any gate fails, the dispatcher spawns a fresh developer agent with only the failing gate reports and affected files as input context. Maximum three fix iterations before the story is marked blocked.

Mutation testing is entirely the project's responsibility. If the project sets it up, it runs through the project's own hooks or CI, not the dispatcher's gate loop. The `mutation-analysis` skill is retained as setup guidance for project-owned mutation testing, not a prescribed tool chain.

## Amended

**Date**: 2026-09-01
**Reason**: Configuration-driven gates and `test_design_verify` conditional gate ([proposal](../proposals/test-design-skill.md), ST-0189)

The dispatcher's gate list is no longer hardcoded. The dispatcher reads per-gate configuration from `docs/charter/testing.yaml`'s `gates` section. Each gate entry carries an `enabled` flag; gates where `enabled` is `false` are skipped. Gate-specific parameters (such as `crap_score.threshold`) are passed to the corresponding script at invocation time. ADR-0012 retains authority over gate execution ordering; `testing.yaml` provides per-gate configuration only.

A fourth gate, `test_design_verify`, is added as a **conditional** entry. It is active when the story file contains a Test Design section or a Prior Tests section (output of the `test-design` skill). It is skipped when no test-design output exists in the story. The gate validates that every owned contract in the story's traces has a corresponding test assertion in the Test Design section.

**Gate execution sequence (amended):**

After each developer-agent commit:

1. Dispatcher reads `docs/charter/testing.yaml`'s `gates` section for per-gate enabled/threshold configuration.
2. Dispatcher runs `crap-score` on committed artifacts, passing the `threshold` from `gates.crap_score.threshold`.
3. Dispatcher runs `dependency-check` against `architecture.dsl` dependency rules.
4. **Conditional:** Dispatcher runs `test-design-verify` on the story file — active when test-design output exists, skipped otherwise.
5. Each gate produces a JSON report under `.current-work/<gate-name>/<story-id>.json`.
6. If all gates pass, the dispatcher proceeds to `premerge-check` and merge.
7. If any gate fails, the dispatcher spawns a fresh developer agent with only the failing gate reports and affected files as input context. Maximum three fix iterations before the story is marked blocked.

## Consequences

**Positive:**

- The developer agent never runs validation scripts. Creation and validation are separated at the process boundary, consistent with ADR-0003 (test execution via hooks) and the foundational "Agentic Creation, Deterministic Validation" principle.
- Fresh developer context per fix iteration prevents gate analysis, failed fix attempts, and error messages from consuming the developer's context window. Each iteration gets the maximum available context for the fix.
- The dispatcher owns the gate results and the merge decision. The developer cannot skip or suppress a gate.
- The gate loop is local. No CI infrastructure, no network round-trip, no pipeline YAML. Gates run at machine speed in the same environment as the developer agent.

**Negative:**

- The dispatcher's per-story loop becomes more complex: it now includes a gate-check step with branching (pass → merge, fail → spawn fix iteration, cap → block story). The dispatcher's implementation-agent markdown grows to accommodate this logic.
- A story with persistent gate failures consumes up to six developer spawns (three at current tier, three at tier+1 via escalation) before terminal failure. This is bounded and intentional, but it is more token spend than the current model where no semantic gates exist.
- CI-based gates remain unavailable as a safety net. A human who bypasses the dispatcher (manual merge) also bypasses the semantic gates. This mirrors the existing design: client-side hooks are an operational gate for managed workflows, not a security boundary.

## Referenced from

- [ADR-0003 — Test execution via mechanically triggered gates](0003-test-execution-via-hooks.md)
- [Proposal: Agentic Quality Gates and Requirements Consolidation](../proposals/implemented/agentic-quality-gates-and-specification-consolidation.md)
- [foundational-principles.md](../../factory/rulebooks/conventions/foundational-principles.md)
