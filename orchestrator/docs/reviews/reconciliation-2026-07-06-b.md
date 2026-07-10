# Reconciliation Report — 2026-07-06 (Pass 2)

**Reviewer**: Reconciliation Agent (second pass — post-FAGAN implementation)
**Scope**: Full codebase-vs-spec reconciliation, all six contract surfaces

## 1. Scope

### Code paths compared

- `src/orchestrator/__init__.py`, `ports.py`, `entities.py`, `cli.py`, `phase_runner.py`, `chain_runner.py`, `loop_policy.py`, `model_resolver.py`, `approval_service.py`, `status_service.py`
- `src/orchestrator/adapters/`: `agent_registry.py`, `backlog_store.py`, `copilot.py`, `finding_ingest.py`, `findings_store.py`, `gate_runner.py`, `invocation_log.py`, `model_matrix.py`, `prompt_composer.py`, `run_state_store.py`
- `tests/`: all test files (277 passing, 1 skipped)

### Spec files compared

- `docs/spec/prd.md`, `docs/spec/actor-goal-list.md`, `docs/spec/todos.md`
- `docs/spec/use_cases/system-use-cases.md`, `UC-01` through `UC-07`
- `docs/spec/supplementary_specs/interface-contracts.md`, `entity-model.md`, `state-machines.md`, `validation-rules.md`
- `docs/01_introduction_and_goals.md` through `docs/12_glossary.md`
- `docs/adr/0001` through `docs/adr/0012`
- `docs/architecture.dsl`
- `CONTEXT.md`

## 2. Prior Findings Verification (Step 3)

| Finding                               | Status       | Verification                                                                                                                                                                                      |
| ------------------------------------- | ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| RECON-0001 (artifact staleness check) | **Resolved** | `ApprovalService.approve()` now re-gates when `GateRunner.artifacts_changed()` returns true; if re-gate fails, the approval is refused with a descriptive error. Implemented in commit `88c9486`. |
| RECON-0002 (reject note)              | **Resolved** | CLI `reject` subcommand accepts `--note NOTE`; `ApprovalService.reject(note=...)` stores `rejection_note` on the phase record. Implemented in commit `88c9486`.                                   |

## 3. New Discrepancy Table

| #   | Classification | Artifact                                                              | Spec location                            | Code location                  | Action taken                                                                                                                                     |
| --- | -------------- | --------------------------------------------------------------------- | ---------------------------------------- | ------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| 1   | Spec stale     | `CLIAdapter.invoke()` signature missing `model` param                 | `interface-contracts.md`                 | `ports.py:CLIAdapter`          | **Updated** — added `model: str \| None = None` as 4th parameter                                                                                 |
| 2   | Spec stale     | Adapter table signature missing `model`                               | `05_building_block_view.md` §5.3         | same                           | **Updated** — `invoke(prompt, cwd, timeout_s, model=None)`                                                                                       |
| 3   | Spec stale     | Invocation log fields: `model` and `gate_timed_out` undocumented      | `interface-contracts.md` §Invocation Log | `invocation_log.py`            | **Updated** — added `model` to entity field list; added `gate_timed_out` to gate outcome fields                                                  |
| 4   | Spec stale     | Reviewer auth/config error → Halt not in pseudocode                   | `state-machines.md` pseudocode + diagram | `phase_runner.py:217-222`      | **Updated** — added reviewer auth/config → Halted edges to pseudocode and Mermaid diagram                                                        |
| 5   | Spec stale     | `PHASE.order` field in ER diagram; code uses `run.chain` for ordering | `entity-model.md` ER diagram             | `PhaseRecord` dataclass        | **Updated** — removed `order` from PHASE entity                                                                                                  |
| 6   | Spec stale     | `ApprovalService` dependencies incomplete in DSL                      | `architecture.dsl`                       | `approval_service.py:__init__` | **Updated** — added `→ findingsStore`, `→ gateRunner`, `→ agentRegistry` relationships                                                           |
| 7   | Spec stale     | `ChainRunner → ApprovalService` incorrect                             | `architecture.dsl`                       | `chain_runner.py:__init__`     | **Updated** — removed; ChainRunner depends only on PhaseRunner + RunStateStore                                                                   |
| 8   | Undocumented   | `FindingIngestor` missing as container in DSL                         | `architecture.dsl`                       | `adapters/finding_ingest.py`   | **Updated** — added `findingIngestor` container; split `phaseRunner → findingsStore` into separate FindingsStore + FindingIngestor relationships |
| 9   | Undocumented   | `GateRunner.artifacts_changed()` method                               | `interface-contracts.md`                 | `ports.py:GateRunner`          | **Updated** — added method signature and usage note                                                                                              |
| 10  | Undocumented   | `FindingsStore.next_id()` method                                      | `interface-contracts.md`                 | `ports.py:FindingsStore`       | **Updated** — documented monotonic ID allocator method                                                                                           |

## 4. Spec Files Updated

| File                                                   | Change                                                                                                                                                                                                                                |
| ------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `docs/spec/supplementary_specs/interface-contracts.md` | Added `model` param to `CLIAdapter.invoke()`; added `model` and `gate_timed_out` to invocation log description; added `GateRunner.artifacts_changed()` method; documented `FindingsStore.next_id()`                                   |
| `docs/spec/supplementary_specs/state-machines.md`      | Added reviewer adapter auth/config error → Halted edges to pseudocode and Mermaid state diagram                                                                                                                                       |
| `docs/spec/supplementary_specs/entity-model.md`        | Removed `order` from PHASE entity in ER diagram                                                                                                                                                                                       |
| `docs/05_building_block_view.md`                       | Updated CLIAdapter signature to include `model`; updated ApprovalService description with full dependency list and re-gate behavior                                                                                                   |
| `docs/architecture.dsl`                                | Removed incorrect ChainRunner→ApprovalSvc relationship; added ApprovalSvc→FindingsStore/GateRunner/AgentRegistry; added FindingIngestor container; split PhaseRunner→FindingsStore into FindingsStore + FindingIngestor relationships |
| `docs/assets/images/*.{png,svg}`                       | Re-rendered all 3 views (SystemContext, Containers, CoreComponents) in both PNG and SVG from updated DSL                                                                                                                              |

## 5. Code Defects Filed

None. All code-vs-spec discrepancies were spec-stale or undocumented items. The code is correct.

## 6. Overall Assessment

After the 31 FAGAN finding fixes, the codebase is **well-aligned** with the specification. The 10 discrepancies found in this pass are all spec-stale items where the code correctly evolved during FAGAN implementation:

- **Model parameter plumbing** (items 1-3): `CLIAdapter.invoke()` gained a `model` parameter and the invocation log gained `model` and `gate_timed_out` fields — spec hadn't caught up.
- **Reviewer halt edges** (item 4): FAGAN-0009 correctly added reviewer auth/config error halting, matching the existing author halt behavior — the state machine pseudocode and diagram hadn't been updated.
- **Phase ordering** (item 5): `PHASE.order` was declared in the entity model but never implemented — `run.chain` provides canonical ordering, making a per-phase `order` field redundant.
- **DSL drift** (items 6-8): the re-gate logic in ApprovalService (FAGAN-0011/0012) added new port dependencies; the ChainRunner→ApprovalService relationship was always incorrect; FindingIngestor was missing as a container.
- **Port methods** (items 9-10): `GateRunner.artifacts_changed()` and `FindingsStore.next_id()` were in the code but not in the interface contracts spec.

**Handoff**: Spec reconciled — 6 files updated, diagrams re-rendered, no code defects. Run the **QA agent** for a second Fagan inspection to verify the FAGAN fixes and catch any regressions.
