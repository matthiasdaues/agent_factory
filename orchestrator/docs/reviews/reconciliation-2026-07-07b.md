# Reconciliation Report — Post-Refactoring (2026-07-07b)

**Date**: 2026-07-07
**Trigger**: CLI refactoring committed (working-tree gate, call-to-action, release/abort, dispatcher agent split)
**Scope**: `system-use-cases.md`, `05_building_block_view.md`, `06_runtime_view.md`, `architecture.dsl`, `interface-contracts.md` vs. implemented code.

## Discrepancy Table

| #   | Artifact                         | Spec location                                | Code location                                                 | Classification | Action                                                                 |
| --- | -------------------------------- | -------------------------------------------- | ------------------------------------------------------------- | -------------- | ---------------------------------------------------------------------- |
| 1   | Implementation phase agent model | `system-use-cases.md` §Phase model           | `agents/implementation-agent.md`, `agents/developer-agent.md` | **Spec stale** | Updated — added dispatcher note to implementation phase mapping        |
| 2   | `release` CLI command            | `system-use-cases.md` §Command interface     | `cli.py` `_handle_release()`                                  | **Spec stale** | Updated — added `release` requirement                                  |
| 3   | `abort` CLI command              | `system-use-cases.md` §Command interface     | `cli.py` `_handle_abort()`                                    | **Spec stale** | Updated — added `abort` requirement                                    |
| 4   | GateRunner port (`verify()`)     | `interface-contracts.md` §Gate Verification  | `ports.py` `GateRunner`                                       | Match ✓        | —                                                                      |
| 5   | InvocationContext                | `interface-contracts.md` §Invocation Context | `entities.py`, `ports.py`                                     | Match ✓        | —                                                                      |
| 6   | `halted_from` field              | ADR-0015                                     | `entities.py` `PhaseRecord.halted_from`                       | Match ✓        | —                                                                      |
| 7   | WorkingTreeGate adapter          | `05_building_block_view.md` §5.3             | `adapters/gate_runner.py` `WorkingTreeGate`                   | Match ✓        | —                                                                      |
| 8   | Call-to-action templates         | ADR-0014                                     | `adapters/prompt_composer.py` `_call_to_action()`             | Match ✓        | —                                                                      |
| 9   | Dispatcher internals in DSL      | `architecture.dsl`                           | Below adapter boundary (FR-M)                                 | N/A            | Not in scope — agent-internal parallelism is invisible to orchestrator |

## Spec Files Updated

1. **`system-use-cases.md` §Phase model** — Implementation phase mapping now documents the dispatcher pattern: `implementation-agent` is a dispatcher that spawns `developer-agent` subagents per story with classification-based model selection.
2. **`system-use-cases.md` §Command interface** — Added `release` (ADR-0015, VR-029) and `abort` command requirements.

## Code Defects Filed

None.

## Summary

3 spec-stale items found and fixed. 6 contract surfaces match between spec and code. No code defects. The dispatcher/developer-agent split is correctly invisible to the orchestrator's architecture (parallelism is below the adapter boundary per FR-M) — the DSL and building block view do not need updating.
