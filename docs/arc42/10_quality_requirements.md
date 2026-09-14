[back to index](../README.md)

# 10. Quality Requirements

This chapter defines testable quality scenarios for the cycle-based orchestration architecture. Each scenario follows the standard form: stimulus, environment, response, and response measure. The scenarios derive from the Pugh Matrix criteria in [ADR-0017](../adr/0017-cycle-based-orchestration-supersedes-linear-playbook-fsm.md) and the crosscutting concepts in [chapter 8](08_crosscutting_concepts.md).

## 10.1 Quality Attribute Scenarios

### QS-1: Non-linear routing

| Field             | Description                                                                                                   |
| ----------------- | ------------------------------------------------------------------------------------------------------------- |
| Quality attribute | Flexibility                                                                                                   |
| Stimulus          | A feature needs only implementation and not architecture or planning work.                                    |
| Environment       | The delivery model declares routes from CONCEPT directly to REALIZE.                                          |
| Response          | The human selects REALIZE. The engine writes the transition without requiring traversal of ROADMAP or REFINE. |
| Response measure  | The workstream state file records cycle REALIZE with attempt 1. No intermediate cycle states were created.    |

References: [ADR-0017 § Decision](../adr/0017-cycle-based-orchestration-supersedes-linear-playbook-fsm.md#decision), [cycle-based-orchestration.feature Rule "Human operator selects the next cycle"](../spec/cycle-based-orchestration.feature)

### QS-2: Human routing authority

| Field             | Description                                                                                                                  |
| ----------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| Quality attribute | Controllability                                                                                                              |
| Stimulus          | The engine recommends route CONCEPT → ROADMAP. The human wants REALIZE instead.                                              |
| Environment       | Normal operation with a bound workstream.                                                                                    |
| Response          | The engine accepts the selection, records a warning that evidence for REALIZE did not pass, and writes the transition.       |
| Response measure  | The workstream state file records cycle REALIZE. The recommendation result shows the warning. No gate blocked the selection. |

References: [ADR-0017 § Decision](../adr/0017-cycle-based-orchestration-supersedes-linear-playbook-fsm.md#decision), [cycle-based-orchestration.feature Rule "Human operator selects the next cycle"](../spec/cycle-based-orchestration.feature)

### QS-3: Clean Architecture dependency direction

| Field             | Description                                                                                                                                                                     |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Quality attribute | Testability, Maintainability                                                                                                                                                    |
| Stimulus          | A developer adds a filesystem read or a lock acquisition call inside the Cycle Engine container.                                                                                |
| Environment       | The architecture.dsl dependency rules are enforced by `dependency-check`.                                                                                                       |
| Response          | `dependency-check` detects the inward-violating import and fails.                                                                                                               |
| Response measure  | Exit code 1 with the violating import path named. The engine has zero relationships to state files in the DSL. All data reaches the engine as function arguments from adapters. |

References: [architecture.dsl Cycle Engine container](architecture.dsl), [section 5.3](05_building_block_view.md#53-level-2-component-view----cycle-engine)

### QS-4: Concurrent workstreams

| Field             | Description                                                                                                                           |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| Quality attribute | Concurrency correctness                                                                                                               |
| Stimulus          | Two CLI sessions attempt to write to the same workstream state file within the same second.                                           |
| Environment       | Both sessions hold a session binding for the same workstream. One acquires the OS-level exclusive lock first.                         |
| Response          | The second session waits for the lock. When it acquires the lock, it detects a revision or digest mismatch and exits with a conflict. |
| Response measure  | Exit code 1 (conflict) for the second session. No data loss. The first session's write is intact. Lock timeout is 5 seconds.          |

References: [cycle-based-orchestration.feature Rule "Concurrent sessions detect conflicts"](../spec/cycle-based-orchestration.feature), [section 8.13](08_crosscutting_concepts.md#813-cycle-based-orchestration-model)

### QS-5: Delegation with bounded autonomy

| Field             | Description                                                                                                                                                       |
| ----------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Quality attribute | Safety                                                                                                                                                            |
| Stimulus          | An agent with an explicit-route delegation grant reaches the per-cycle `delegated_attempt_limit`.                                                                 |
| Environment       | The agent has retried the current cycle to the limit declared in the delivery model.                                                                              |
| Response          | The retry adapter returns `paused` with reason `delegated_attempt_limit_reached` and `next_action: request_human_direction`. The agent stops.                     |
| Response measure  | The workstream state file shows `attempt` equal to the limit. No further delegated retries modify state until a human intervenes. Human retries remain available. |

References: [cycle-based-orchestration.feature Rule "Delegated retry respects attempt limits"](../spec/cycle-based-orchestration.feature), [state-machines.md § Retry State](../spec/supplementary_specs/state-machines.md)

### QS-6: Observable-state resume

| Field             | Description                                                                                                                                                                       |
| ----------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Quality attribute | Resilience                                                                                                                                                                        |
| Stimulus          | A session terminates unexpectedly (crash, network loss, user interrupt).                                                                                                          |
| Environment       | A workstream state file and session binding exist on disk. No process holds a lock.                                                                                               |
| Response          | A new session reads the workstream state file, evaluates artifact readiness, and presents route recommendations. No prior session's process-local state is needed.                |
| Response measure  | The new session produces the same recommendation result as the interrupted session would have at the same commit. All state is derived from files on disk and the delivery model. |

References: [ADR-0017 § Consequences](../adr/0017-cycle-based-orchestration-supersedes-linear-playbook-fsm.md#consequences), [section 8.13](08_crosscutting_concepts.md#813-cycle-based-orchestration-model)

### QS-7: Declarative model constraint

| Field             | Description                                                                                                                       |
| ----------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| Quality attribute | Safety, Integrity                                                                                                                 |
| Stimulus          | Someone adds a shell command, pipe, redirect, subshell invocation, or backtick expansion to a validator field in `delivery.yaml`. |
| Environment       | The cycle-model-v1 JSON Schema validates the model on every engine load.                                                          |
| Response          | Schema validation rejects the model and names the field containing the executable command.                                        |
| Response measure  | The engine does not load. Exit code indicates validation failure. No executable logic reaches the engine from the model.          |

References: [validation-rules.md § Cycle model validation rule 08](../spec/supplementary_specs/validation-rules.md), [cycle-based-orchestration.feature Rule "Engine loads and validates the delivery model"](../spec/cycle-based-orchestration.feature)

### QS-8: Backward compatibility

| Field             | Description                                                                                                                        |
| ----------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| Quality attribute | Compatibility                                                                                                                      |
| Stimulus          | A user or script invokes `factory/scripts/phase advance` after the cycle-based migration.                                          |
| Environment       | The `phase` diagnostic stub is installed. The cycle-based commands (`cycle select`, `cycle retry`) are available.                  |
| Response          | The stub exits 2 and prints the name of the replacement command. It does not emulate the old single-forward-transition behavior.   |
| Response measure  | Exit code 2. Standard error names `cycle select` as the replacement. Characterization tests verify the exit code and message text. |

References: [ADR-0017 § Consequences](../adr/0017-cycle-based-orchestration-supersedes-linear-playbook-fsm.md#consequences), [cycle-based-orchestration.feature Rule "Legacy phase command provides a diagnostic stub"](../spec/cycle-based-orchestration.feature)

## 10.2 Quality Attribute Priority

The Pugh Matrix in [ADR-0017](../adr/0017-cycle-based-orchestration-supersedes-linear-playbook-fsm.md#decision) assigns weights that reflect the relative priority of these attributes:

| Priority | Quality attribute                 | Weight | Scenarios |
| -------- | --------------------------------- | -----: | --------- |
| 1        | Flexibility (non-linear)          |      3 | QS-1      |
| 1        | Controllability (human authority) |      3 | QS-2      |
| 1        | Testability (Clean Architecture)  |      3 | QS-3      |
| 1        | Concurrency correctness           |      3 | QS-4      |
| 1        | Resilience (observable resume)    |      3 | QS-6      |
| 2        | Safety (delegation bounds)        |      2 | QS-5      |
| 2        | Integrity (declarative model)     |      2 | QS-7      |
| 2        | Compatibility (migration)         |      2 | QS-8      |

## Referenced from

- [09_architecture_decisions.md](09_architecture_decisions.md) — ADR-0017 Pugh Matrix criteria are the source of these scenarios
- [08_crosscutting_concepts.md](08_crosscutting_concepts.md) — principles that underpin QS-3 and QS-7
