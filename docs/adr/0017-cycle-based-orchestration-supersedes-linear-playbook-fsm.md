---
id: 0017
status: accepted
evaluation: pugh-matrix
---

# Cycle-based orchestration supersedes linear playbook FSM

## Context

Factory Flow Control routes delivery work through ordered phases using a finite state machine (FSM). Each playbook defines a linear sequence of states with entry conditions, halt conditions, and `phase advance`/`phase retry` commands. `transition-lint` blocks staged files outside the current phase's output globs. The FSM enforces the declared order mechanically.

This model has three structural limitations that the accepted [cycle-based orchestration proposal](../proposals/cycle-based-orchestration.md) addresses:

1. **No non-linear routing.** A feature that needs only implementation and not architecture must still traverse every intermediate phase. Skipping, repeating, or branching requires a different playbook definition, not a runtime decision.
2. **Single workstream per checkout.** The playbook state marker (`.current-work/playbook-state.yml`) is a singleton. Two features cannot be in different phases simultaneously.
3. **Machine-enforced transitions.** The FSM decides whether a transition is allowed. The human's only choice is "advance or not." There is no separation between recommendation and decision.

No existing ADR conflicts with this decision. [ADR-0002](0002-factory-owns-flow-control-orchestrator-is-a-trigger.md) established that Factory scripts own flow control and the orchestrator is a trigger; this principle is preserved -- the Cycle Engine returns recommendations, and `cycle select`/`cycle retry` commands replace `phase advance`/`phase retry`.

## Decision

Replace the linear playbook FSM with a cycle-based directed graph. Five delivery cycles (IDEA, CONCEPT, ROADMAP, REFINE, REALIZE) plus a terminal DONE node form the graph. A declarative YAML delivery model (`packages/factory/engine/models/delivery.yaml`) declares cycles, routes, artifact declarations, trusted validators, and per-cycle delegated attempt limits.

A pure Cycle Engine container loads the model, evaluates artifact readiness, produces route recommendations, checks delegation grants, and enforces retry limits. It returns immutable decisions without writing state. A State Adapter container acquires locks, calls the engine, writes cycle state, and presents recommendations. The dependency direction is inward: adapters call the engine, never the reverse.

Per-workstream YAML state files under `.current-work/cycles/` replace the singleton playbook marker. OS-level exclusive locks prevent concurrent mutation. Session bindings under `.current-work/session-bindings/` track which workstream each CLI session observes.

The confirmed Pugh Matrix:

| Criterion                          | Weight | Linear playbook FSM (baseline) | Cycle-based directed graph | Enhanced FSM with conditional branching |
| ---------------------------------- | -----: | -----------------------------: | -------------------------: | --------------------------------------: |
| Non-linear routing                 |      3 |                              0 |                         +1 |                                      +1 |
| Human routing authority            |      3 |                              0 |                         +1 |                                       0 |
| Clean Architecture dependency dir. |      3 |                              0 |                         +1 |                                       0 |
| Concurrent workstreams             |      3 |                              0 |                         +1 |                                       0 |
| Delegation with bounded autonomy   |      2 |                              0 |                         +1 |                                      -1 |
| Observable-state resume            |      3 |                              0 |                          0 |                                       0 |
| Declarative model                  |      2 |                              0 |                         +1 |                                      -1 |
| Backward compatibility             |      2 |                              0 |                         -1 |                                      +1 |
| **Weighted total**                 |        |                          **0** |                    **+15** |                                  **+1** |

The cycle-based directed graph dominates on six of eight criteria. The enhanced FSM scores near the baseline because it preserves the command surface but inherits the single-workstream, machine-enforced-transition constraints. A weight shift on backward compatibility (from 2 to 3) would not change the outcome.

## Consequences

**Positive**

- Features may skip, repeat, or branch between delivery stages based on artifact evidence rather than following a fixed sequence.
- Multiple workstreams may be active simultaneously, each with independent cycle state and revision tracking.
- The engine recommends; the human decides. Route authority is separated from route evaluation.
- The Cycle Engine is a pure domain-logic container testable in isolation, with no filesystem, lock, or script dependencies.
- The delivery model is validated against a JSON Schema that rejects executable logic, preserving the declarative constraint.
- Delegation grants allow bounded agent autonomy with per-cycle retry limits, preventing runaway loops.

**Negative**

- Migration requires a compatibility period with diagnostic stubs for `phase advance` and `phase retry`. The `phase` command exits 2 and names the replacement for one release after cutover.
- `transition-lint` changes behavior: it validates the cycle model and workstream state files instead of checking staged files against phase output globs. The pre-migration finding codes (`TL-NOMARKER`, `TL-MARKER`, `TL-NOFSM`, `TL-STATE`, `TL-ORDER`) are retired.
- Existing playbook-based automation must be updated to use `cycle select`/`cycle retry` commands.
- The usage-record v1 schema gains three optional fields (`workstream_id`, `workstream_origin`, `cycle`), compatible with the additive-change policy but requiring consumer awareness.
