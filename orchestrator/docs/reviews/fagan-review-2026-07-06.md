# Fagan Review Report — 2026-07-06

**Reviewer**: QA Agent (first pass)
**Scope**: Full codebase — all production source under `src/orchestrator/`
**Method**: Fagan Inspection against five focus areas (Correctness, Clean Architecture, SOLID, Maintainability, Consistency)

## Scope

### Files inspected

- `src/orchestrator/__init__.py`
- `src/orchestrator/entities.py`
- `src/orchestrator/ports.py`
- `src/orchestrator/phase_runner.py`
- `src/orchestrator/chain_runner.py`
- `src/orchestrator/loop_policy.py`
- `src/orchestrator/model_resolver.py`
- `src/orchestrator/approval_service.py`
- `src/orchestrator/status_service.py`
- `src/orchestrator/adapters/gate_runner.py`
- `src/orchestrator/adapters/findings_store.py`
- `src/orchestrator/adapters/finding_ingest.py`
- `src/orchestrator/adapters/run_state_store.py`
- `src/orchestrator/adapters/copilot.py`
- `src/orchestrator/adapters/agent_registry.py`
- `src/orchestrator/adapters/backlog_store.py`
- `src/orchestrator/adapters/model_matrix.py`
- `src/orchestrator/adapters/prompt_composer.py`
- `src/orchestrator/adapters/invocation_log.py`
- `src/orchestrator/cli.py`

### Spec files used for correctness

- `CONTEXT.md`, `docs/spec/prd.md`
- `docs/spec/use_cases/system-use-cases.md`, UC-01 through UC-07
- `docs/spec/supplementary_specs/interface-contracts.md`, `entity-model.md`, `state-machines.md`, `validation-rules.md`
- `docs/05_building_block_view.md`, `docs/adr/0001` through `0012`

### Test files reviewed for coverage

- All 22 test files under `tests/`

______________________________________________________________________

## Finding Table

| Finding                                                                                                                                                          | Artifact                                    | Category   | Severity |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------- | ---------- | -------- |
| FAGAN-0001: Resolved model never passed to adapter invocation — CLIAdapter.invoke() has no model parameter; matrix selection is ineffective (FR-K2/K3/VR-023)    | `ports.py`, `phase_runner.py`, `copilot.py` | Defect     | Critical |
| FAGAN-0002: run_phase() ignores persisted sub-state on resume — always resets to AUTHORING, replaying work instead of resuming from checkpoint (UC-06, ATAM-R07) | `phase_runner.py`                           | Defect     | Critical |
| FAGAN-0003: Malformed open findings silently skipped — missing/invalid fields cause a real finding to be dropped, enabling false-clean approval (VR-006)         | `finding_ingest.py`                         | Defect     | Critical |
| FAGAN-0004: RunLock acquire is not atomic — read-then-replace TOCTOU race allows concurrent starts (VR-017, BR-017)                                              | `run_state_store.py`                        | Defect     | Critical |
| FAGAN-0005: Interactive mode ignores composed prompt — agent receives no context, definition, or findings (UC-01, FR-B2)                                         | `copilot.py`                                | Defect     | Critical |
| FAGAN-0006: Missing reviewer silently downgraded to gate-only — `ValueError` caught and swallowed (VR-011, BR-006)                                               | `cli.py`                                    | Defect     | Critical |
| FAGAN-0007: Story classification never threaded into phase execution — `by-class` always falls back to default (BR-021, FR-K1/K2)                                | `phase_runner.py`, `model_resolver.py`      | Defect     | Major    |
| FAGAN-0008: Deterministic gate findings never ingested — gate fails, author is looped but never told what's wrong (UC-02, VR-001/014)                            | `phase_runner.py`, `ports.py`               | Defect     | Major    |
| FAGAN-0009: Reviewer auth/config errors not halted immediately — treated as ordinary failure, sent through RetryOrHalt (BR-018/020)                              | `phase_runner.py`                           | Defect     | Major    |
| FAGAN-0010: Phase sequencing uses run.phases not run.chain — ordering could drift from canonical order (BR-006)                                                  | `chain_runner.py`                           | Defect     | Major    |
| FAGAN-0011: Stale artifacts only refused, not re-gated — UC-04 ext 3a says re-run gate, not just refuse (VR-012, BR-013)                                         | `approval_service.py`                       | Defect     | Major    |
| FAGAN-0012: approve() sets RUNNING but does not advance chain — persisted state says "running" with no phase executing (UC-04)                                   | `approval_service.py`                       | Defect     | Major    |
| FAGAN-0013: Gate runner ignores branch and allows unclean tree — commits could land on wrong branch, unrelated changes staged (BR-016, VR-016)                   | `gate_runner.py`                            | Defect     | Major    |
| FAGAN-0014: Missing pre-commit config treated as pass not error — absent gate infra is a silent pass (ADR-0003, BR-015)                                          | `gate_runner.py`                            | Defect     | Major    |
| FAGAN-0015: Error count regex instead of structured findings parse — brittle English regex can't parse spec-lint JSON (ADR-0003, ATAM-R02)                       | `gate_runner.py`                            | Defect     | Major    |
| FAGAN-0016: Local schema stricter than published contract — requires `created_by`/`resolved_by`, spec doesn't (VR-006)                                           | `findings_store.py`                         | Defect     | Major    |
| FAGAN-0017: Ingestor depends on concrete FilesystemFindingsStore — violates Dependency Inversion (ADR-0001)                                                      | `finding_ingest.py`                         | Defect     | Major    |
| FAGAN-0018: Interactive mode never sets auth/config error flags — misclassifies adapter failures (BR-018/020)                                                    | `copilot.py`                                | Defect     | Major    |
| FAGAN-0019: Path traversal via crafted story_id — no validation, path can escape backlog/ (VR-022)                                                               | `backlog_store.py`                          | Defect     | Major    |
| FAGAN-0020: update_status() is not atomic — crash can corrupt story file (ADR-0008)                                                                              | `backlog_store.py`                          | Defect     | Major    |
| FAGAN-0021: Frontmatter not schema-validated — hand-rolled parser, no schema check (VR-022)                                                                      | `backlog_store.py`                          | Defect     | Major    |
| FAGAN-0022: Matrix adapter does not validate semantic content — invalid on_missing silently accepted (FR-K4, VR-024)                                             | `model_matrix.py`                           | Defect     | Major    |
| FAGAN-0023: Malformed agent frontmatter yields empty outputs silently — degrades instead of fail-fast (VR-011)                                                   | `agent_registry.py`                         | Defect     | Major    |
| FAGAN-0024: All commands build full runtime unnecessarily — status/approve fail if model-matrix.conf missing (UC-05, VR-008)                                     | `cli.py`                                    | Defect     | Major    |
| FAGAN-0025: run-all reuses existing run instead of requiring resume — undermines approval boundary (UC-03, VR-017)                                               | `cli.py`                                    | Defect     | Major    |
| FAGAN-0026: VR-017 check incomplete — only lock, not run.json mode (VR-017, BR-017)                                                                              | `cli.py`                                    | Defect     | Major    |
| FAGAN-0027: --cap accepts zero/negative values violating VR-002                                                                                                  | `cli.py`, `loop_policy.py`                  | Defect     | Major    |
| FAGAN-0028: run-step does not write invocation log entry — breaks observability contract (FR-J, QS-13)                                                           | `cli.py`                                    | Defect     | Major    |
| FAGAN-0029: No handler-level tests for CLI commands — composition-root wiring untested                                                                           | `tests/`                                    | Defect     | Major    |
| FAGAN-0030: backlog-lint missing traces/traceability tests — VR-022 enforcement gap                                                                              | `tests/`                                    | Defect     | Major    |
| FAGAN-0031: No end-to-end test that model reaches adapter command — FAGAN-0001 untested (FR-K)                                                                   | `tests/`                                    | Defect     | Major    |
| Interactive empty-commit spec contradiction — state-machines.md and system-use-cases.md disagree                                                                 | `phase_runner.py`                           | Question   | Major    |
| PhaseRecord missing `order` field from ER diagram — ordering via run.chain instead                                                                               | `entities.py`                               | Question   | Minor    |
| LoopPolicy.should_exit() never called — dead policy code (SRP)                                                                                                   | `loop_policy.py`                            | Suggestion | Minor    |
| Gate log omits timed_out field — incomplete versus documented GateResult                                                                                         | `invocation_log.py`                         | Defect     | Minor    |
| cli.py has too many responsibilities — SRP, split into modules                                                                                                   | `cli.py`                                    | Suggestion | Minor    |

______________________________________________________________________

## Summary by Focus Area

| Focus Area         | Defect | Suggestion | Question | Total |
| ------------------ | ------ | ---------- | -------- | ----- |
| Correctness        | 27     | 0          | 1        | 28    |
| Clean Architecture | 2      | 0          | 0        | 2     |
| SOLID              | 0      | 2          | 0        | 2     |
| Maintainability    | 0      | 0          | 0        | 0     |
| Consistency        | 2      | 0          | 1        | 3     |
| Coverage           | 3      | 0          | 0        | 3     |

## Summary by Severity

| Severity  | Count  |
| --------- | ------ |
| Critical  | 6      |
| Major     | 25     |
| Minor     | 5      |
| **Total** | **36** |

______________________________________________________________________

## Assessment

### Strengths

The codebase demonstrates strong architectural discipline:

- **Clean separation** between domain entities, ports, and adapters (ADR-0001) is faithfully implemented. The dependency rule is respected — the core never imports an adapter.
- **Domain model** (`entities.py`) closely mirrors the ER diagram and interface contracts. Enums are well-defined with consistent lowercase string values.
- **Test coverage** is thorough for the core state machine: `test_phase_runner.py` and the integration tests exercise the author→gate→review→loop flow comprehensively.
- **Atomic I/O** in `run_state_store.py` and `findings_store.py` follows a careful temp-file + fsync + replace pattern.
- **Consistent patterns** across adapters: each adapter maps cleanly to one port, serialization/deserialization is symmetric, and error handling is structured.

### Critical Issues

Six critical defects require immediate attention:

1. **Model selection is dead code** (FAGAN-0001) — the entire matrix/classification model pipeline produces a value that is logged but never used. This is the highest-impact finding.
2. **Resume replays work** (FAGAN-0002) — resuming a run always restarts the current phase from AUTHORING.
3. **Silent finding drop** (FAGAN-0003) — a typo in a finding's severity field can cause a false-clean approval.
4. **Lock race** (FAGAN-0004) — the single-run lock is not atomic.
5. **Interactive prompt loss** (FAGAN-0005) — interactive agents start with no context.
6. **Silent reviewer loss** (FAGAN-0006) — a missing reviewer agent definition degrades silently.

### Themes

- **Validation gaps**: Several adapters parse input with ad-hoc code and skip validation (agent registry, backlog store, model matrix, finding ingest). The pattern should be: parse → validate against published schema → return typed object, as `findings_store.py` does correctly.
- **Interactive mode**: A recurring incomplete path — prompt delivery (FAGAN-0005), error classification (FAGAN-0018), and empty-commit behavior (Question) all need attention.
- **Gate contract**: The gate runner and core don't have a full findings exchange contract; deterministic findings are lost (FAGAN-0008), and the error discriminator is brittle (FAGAN-0015).

______________________________________________________________________

## Findings Filed

31 findings filed as `docs/findings/FAGAN-0001.md` through `FAGAN-0031.md`, all with `status: open`.

## Handoff

> _"Fagan inspection found 6 critical and 25 major defects across 31 findings. Fix them and re-submit for QA."_

Recommended fix order:

1. FAGAN-0001 (model selection) — highest impact, most code paths affected
2. FAGAN-0002 (resume) — correctness of core state machine
3. FAGAN-0004 (lock race) — concurrency safety
4. FAGAN-0006 (silent reviewer loss) — fail-fast
5. FAGAN-0003 (finding drop) — safety-critical
6. FAGAN-0005 (interactive prompt) — usability
7. Remaining major findings by dependency order
