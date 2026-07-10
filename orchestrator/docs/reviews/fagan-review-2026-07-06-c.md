# Fagan Code Inspection — Pass 3 (2026-07-06)

**Date**: 2026-07-06\
**Inspector**: general-purpose sub-agent (Claude Sonnet 4.5)\
**Duration**: ~26 minutes, 358 tool calls\
**Scope**: All production code (`orchestrator/src/orchestrator/**/*.py`)\
**Cross-ref**: spec, state-machines, entity-model, interface-contracts, use cases

## Summary

| Metric               | Value                                        |
| -------------------- | -------------------------------------------- |
| Files inspected      | 17 production, 12 test                       |
| Defects found        | 10 (8 major, 2 minor)                        |
| Prior fixes verified | FAGAN-0032/0036/0037/0038 fully resolved     |
| Prior fixes partial  | FAGAN-0033/0034/0035 only partially resolved |
| Tests passing        | 291 passed, 1 skipped                        |

## Findings

| ID         | Severity | Category       | File                | Description                                             |
| ---------- | -------- | -------------- | ------------------- | ------------------------------------------------------- |
| FAGAN-0039 | major    | contract       | approval_service.py | Failed re-gate wedges run in awaiting-approval          |
| FAGAN-0040 | major    | contract       | approval_service.py | Findings checked on wrong iteration (off-by-one)        |
| FAGAN-0041 | minor    | consistency    | approval_service.py | current_phase advance doesn't sync run.iteration        |
| FAGAN-0042 | major    | contract       | phase_runner.py     | Resume from GATING not idempotent (ATAM-R07)            |
| FAGAN-0043 | major    | contract       | phase_runner.py     | Resume from REVIEWING duplicates findings               |
| FAGAN-0044 | major    | contract       | gate_runner.py      | Dirty worktree not rejected (BR-016)                    |
| FAGAN-0045 | major    | contract       | finding_ingest.py   | Mixed pre-commit stdout drops gate findings             |
| FAGAN-0046 | major    | contract       | gate_runner.py      | Auto-fixing hook re-stage/re-run missing (UC-02 ext 5c) |
| FAGAN-0047 | major    | error-handling | cli.py              | Halted runs exit 0 (UC-07 ext 3a)                       |
| FAGAN-0048 | minor    | consistency    | cli.py              | resume --yes persists mode=paused while running         |

## Prior Finding Verification

- **Fully resolved**: FAGAN-0032 (run branch bootstrap), FAGAN-0036 (interactive stderr), FAGAN-0037 (--story), FAGAN-0038 (empty-commit approval)
- **Partially resolved**: FAGAN-0033 (index reset added but worktree not checked → FAGAN-0044), FAGAN-0034 (gate output wired but mixed stdout not parsed → FAGAN-0045), FAGAN-0035 (PAUSED semantics correct but iteration sync missing → FAGAN-0041)

## Coverage Gaps Identified

- No dirty-worktree rejection test for `PreCommitGateRunner`
- No test for `ingest_gate_output()` with mixed pre-commit stdout
- Resume tests codify non-idempotent behavior instead of ATAM-R07 contract
- No handler-level test asserting non-zero exit on halted runs
- No approval test asserting latest-cycle finding checks

## Assessment

Not a clean pass. The deepest issues are around resume idempotency (FAGAN-0042/0043) and the re-gate wedge state (FAGAN-0039). The exit-code issue (FAGAN-0047) is also significant for CI/unattended usage.
