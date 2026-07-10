# Reconciliation Report — 2026-07-06

**Reviewer**: Reconciliation Agent (first pass)
**Scope**: Full codebase-vs-spec reconciliation, all six contract surfaces

## 1. Scope

### Code paths compared

- `src/orchestrator/__init__.py`, `ports.py`, `entities.py`, `cli.py`, `phase_runner.py`, `chain_runner.py`, `loop_policy.py`, `model_resolver.py`, `approval_service.py`, `status_service.py`
- `src/orchestrator/adapters/`: `agent_registry.py`, `backlog_store.py`, `copilot.py`, `finding_ingest.py`, `findings_store.py`, `gate_runner.py`, `invocation_log.py`, `model_matrix.py`, `prompt_composer.py`, `run_state_store.py`
- `tests/`: all 22 test files

### Spec files compared

- `docs/spec/prd.md`, `docs/spec/actor-goal-list.md`, `docs/spec/todos.md`
- `docs/spec/use_cases/system-use-cases.md`, `UC-01` through `UC-07`
- `docs/spec/supplementary_specs/interface-contracts.md`, `entity-model.md`, `state-machines.md`, `validation-rules.md`
- `docs/01_introduction_and_goals.md` through `docs/12_glossary.md`
- `docs/adr/0001` through `docs/adr/0012`
- `CONTEXT.md`

## 2. Discrepancy Table

| #   | Classification    | Artifact                                                        | Spec location                      | Code location                   | Action taken                                                                   |
| --- | ----------------- | --------------------------------------------------------------- | ---------------------------------- | ------------------------------- | ------------------------------------------------------------------------------ |
| 1   | Spec stale        | Run state schema: `last_gate` missing `timed_out`               | `interface-contracts.md`           | `run_state_store.py:16-58`      | **Updated** — added `timed_out: boolean` to last_gate schema                   |
| 2   | Spec stale        | Run state schema: missing `tooling_version`                     | `interface-contracts.md`           | `run_state_store.py:32`         | **Updated** — added `tooling_version: string\|null`                            |
| 3   | Spec stale        | Run state schema: phase objects missing `iteration`             | `interface-contracts.md`           | `run_state_store.py:44`         | **Updated** — added `iteration: integer` to phase items                        |
| 4   | Spec stale        | Glossary: `InvocationResult` missing `config_error`             | `12_glossary.md`                   | `ports.py:24-45`                | **Updated** — added `config_error` to definition                               |
| 5   | Spec stale        | Glossary: `Halt` missing adapter-config failure                 | `12_glossary.md`                   | `CONTEXT.md` (correct)          | **Updated** — aligned with CONTEXT.md                                          |
| 6   | Spec stale        | Glossary: Port list missing 4 ports                             | `12_glossary.md`                   | `ports.py`                      | **Updated** — added `FindingIngestor`, `Logger`, `BacklogStore`, `ModelMatrix` |
| 7   | Spec stale        | System use cases: missing `reject` CLI command                  | `system-use-cases.md`              | `cli.py:133`                    | **Updated** — added `reject` command requirement                               |
| 8   | Undocumented      | `init` command not in spec                                      | `system-use-cases.md`              | `cli.py:136-142, 288-374`       | **Updated** — added `init` requirement                                         |
| 9   | Undocumented      | CLI flags not specified                                         | `system-use-cases.md`              | `cli.py:110-117`                | **Updated** — added CLI flags section                                          |
| 10  | **Code defect**   | `approve()` missing artifact staleness check                    | `UC-04 ext 3a`, `VR-012`, `BR-013` | `approval_service.py:14-27`     | **Filed** as `RECON-0001` (major)                                              |
| 11  | **Code defect**   | `reject` missing optional note                                  | `UC-04 ext 2a`                     | `approval_service.py:29-36`     | **Filed** as `RECON-0002` (minor)                                              |
| 12  | Undocumented      | `Artifact`, `Iteration`, `Approval` entities defined but unused | `entity-model.md`                  | `entities.py:116-134`           | **Updated** — noted in entity-model.md                                         |
| 13  | Undocumented      | Interactive mode not in system requirements                     | `system-use-cases.md`              | `phase_runner.py`, `copilot.py` | **Updated** — added interactive requirement                                    |
| 14  | Undocumented      | `init` scaffolding not in spec                                  | —                                  | `cli.py:288-374`                | **Updated** — covered by item 8                                                |
| 15  | Terminology drift | Phase definition: glossary vs CONTEXT.md                        | `12_glossary.md`                   | `CONTEXT.md`                    | **Updated** — removed extra clause, aligned                                    |
| 16  | Terminology drift | State diagram "Idle" vs schema "pending"                        | `state-machines.md`                | `interface-contracts.md`        | **Updated** — added naming note                                                |
| 17  | Speculative       | Approval entity relationship                                    | `entity-model.md`                  | `approval_service.py`           | **Updated** — noted implicit representation                                    |
| 18  | Speculative       | Resume staleness check                                          | `VR-012`, `UC-06`                  | `cli.py`, `chain_runner.py`     | Covered by `RECON-0001`                                                        |

## 3. Spec Files Updated

| File                                                   | Change                                                                                                                                                     |
| ------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `docs/spec/supplementary_specs/interface-contracts.md` | Added `tooling_version`, `iteration` to run state schema; added `timed_out` to persisted `last_gate`                                                       |
| `docs/spec/supplementary_specs/entity-model.md`        | Noted that `Approval`, `Artifact`, `Iteration` are defined but not yet used by application services                                                        |
| `docs/spec/supplementary_specs/state-machines.md`      | Added naming note: diagram "Idle" = JSON schema "pending"                                                                                                  |
| `docs/spec/use_cases/system-use-cases.md`              | Added `reject` command, `init` command, CLI flags section, interactive-mode requirement                                                                    |
| `docs/12_glossary.md`                                  | Fixed `InvocationResult` (added `config_error`), fixed `Halt` (added adapter-config failure), expanded Port list, aligned Phase definition with CONTEXT.md |

## 4. Code Defects Filed

| Finding      | Severity | Summary                                                                                     |
| ------------ | -------- | ------------------------------------------------------------------------------------------- |
| `RECON-0001` | Major    | `ApprovalService.approve()` missing artifact staleness check (VR-012, UC-04 ext 3a, BR-013) |
| `RECON-0002` | Minor    | `reject` command does not support optional note (UC-04 ext 2a)                              |

## 5. Linter Results

Linting deferred — `spec-lint` and `arch-lint` are pre-commit hooks that run in the gate, not standalone commands available for manual invocation.

## 6. Overall Assessment

The codebase is **well-aligned** with the specification. The state machine, entity model, port interfaces, and validation rules are faithfully implemented. The 18 discrepancies found are predominantly spec-stale items where the code correctly evolved (run state schema fields, glossary gaps) or documentation gaps for features that were added during implementation (`init`, CLI flags, interactive mode).

The two code defects are both in `ApprovalService`:

- **RECON-0001 (Major)**: the artifact staleness check on approval (VR-012/UC-04/BR-013) is unimplemented — a stale approval could advance a phase whose artifacts changed after the gate.
- **RECON-0002 (Minor)**: the `reject` command doesn't accept the optional note the spec calls for.

**Handoff**: 2 code defects filed → hand back to the **Implementation Agent** to fix, then re-submit for reconciliation pass 2.
