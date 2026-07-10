# 0003. pre-commit as the deterministic gate bus

**Status**: Accepted — gating mechanism partially superseded by [ADR-0013](0013-working-tree-gate-model.md) (commit responsibility shifts to agents; hook configuration remains valid)

## Context

The gate between steps must be deterministic (Q1, NFR-1): the same committed artifacts must always yield the same pass/fail, so the LLM's non-determinism is bracketed by reproducible checks. The host is already a git repository with `pre-commit` installed and configured (C2). The requirements phase's check, `spec-lint`, already exists as a script (C5). Later phases need additional checks (`ruff`, `pytest`) without reworking the orchestrator (FR-D4).

The question is how the orchestrator runs the deterministic check and decides pass/fail.

### Alternatives (Pugh Matrix)

Baseline **A**: the orchestrator runs each linter directly as a subprocess and interprets its output. **B**: commit the staged artifacts and let `pre-commit` hooks run as the gate; the hook exit code decides. **C**: build a custom check-runner/plugin system inside the orchestrator.

| Criterion                                       | Weight | A: run linters directly | B: pre-commit bus | C: custom runner |
| ----------------------------------------------- | ------ | ----------------------- | ----------------- | ---------------- |
| Determinism — pinned, reproducible checks (Q1)  | 3      | 0                       | +1                | 0                |
| Safety — gate bound to the artifact commit (Q3) | 3      | 0                       | +1                | 0                |
| Extensibility — add hooks w/o core change (Q5)  | 2      | 0                       | +1                | +1               |
| Minimal code — reuse host tooling (Q7)          | 1      | 0                       | +1                | -1               |
| Operability (Q4)                                | 2      | 0                       | 0                 | 0                |
| **Weighted total**                              |        | **0**                   | **+9**            | **+1**           |

B wins decisively. `pre-commit` gives pinned hook versions (determinism), binds the gate to the exact commit under review (safety), and lets later phases register hooks in config alone — with none of the code a custom runner (C) would require.

## Decision

Use **`pre-commit` as the gate bus**. After an author produces its declared `outputs`, the `GateRunner` stages those paths and commits on the run branch; `pre-commit` runs the configured hooks. The hook's exit code is the gate result:

- The phase gate hook exits non-zero **iff** at least one error-severity finding exists (BR-002, VR-015); warning/info are recorded but non-blocking (VR-001).
- `spec-lint --format json` is the requirements-phase hook; later phases add hooks (`ruff`, `pytest`) with no orchestrator change (FR-D4, QS-15).
- The `GateRunner` distinguishes `passed=false` (findings — loop the author) from `errored` (hook crash / missing tool — halt, not author-fixable, BR-015). An auto-fixing hook that rewrites files is re-staged and re-committed **once** (ext. 5c), not looped.

## Consequences

**Positive**

- Determinism by construction: pass/fail is an exit code over a fixed commit, never an interpretation of prose (QS-01, QS-02, QS-03).
- The gate is literally the commit's hooks, so what is reviewed is exactly what is gated; no drift between "checked" and "committed" (QS-10).
- New checks are configuration, not code (QS-15).

**Negative / risks**

- Couples the orchestrator to `pre-commit` being installed and correctly configured — made a precondition (C2) and surfaced as a gate *error* (halt) if missing, rather than a silent pass.
- The error-vs-findings distinction depends on hooks behaving well (exit non-zero for findings, crash only on infra failure); a misbehaving hook could blur it (risk R-2/R-3, mitigated by the once-only re-stage rule and schema validation).

**Hardening (from the ATAM review)**

- `pre-commit` returns a non-zero exit for *both* a findings failure and a crash, so the exit code alone cannot drive the halt-vs-loop decision (ATAM-R02). The `GateRunner` resolves this by **output**, not exit code: a hook that emits its declared machine-readable findings (`spec-lint --format json` → a parseable array) is a **findings** result (loop); no parseable findings — a traceback, missing tool, or a non-zero from `pre-commit` itself — is an **error** (halt, BR-015). The `GateResult` DTO in [interface-contracts](../spec/supplementary_specs/interface-contracts.md) records this.
- The gate subprocess carries the same timeout as an agent invocation (ATAM-R04); a gate timeout is an error (halt, BR-020), so a hanging hook can no longer stall the run.
