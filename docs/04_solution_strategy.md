[back to index](README.md)

# 4. Solution Strategy

## 4.1 The central decision: factory owns flow control, orchestrator is a trigger

`orchestrator/` used to run its own `PhaseRunner`, an independent state machine driving the agent chain. That ownership has inverted. `factory/scripts/{transition-lint,phase,trigger}` plus the `run-step` skill are now the actual flow-control mechanism: they gate, advance, cap, and dispatch a playbook run from state that lives on disk, not inside any one process. `orchestrator/` is one possible trigger of these mechanisms — a stand-in for a human manually running them. A human typing commands and the orchestrator CLI are peers; neither owns sequencing or gating anymore, both just invoke factory tooling.

This reverses this repo's own prior architecture and is easy to get wrong without context — anyone who last touched this code before the inversion would assume `orchestrator/` still owns the phase chain. Full rationale and alternatives considered: [09_architecture_decisions.md § ADR-0002](09_architecture_decisions.md).

## 4.2 Technology and design decisions

- **Python 3.8+ stdlib only, per gate script.** No virtualenv, no third-party dependency. `transition-lint`, `phase`, `trigger`, and `index-lint` each carry their own minimal YAML-subset parser rather than sharing one through a library — see [08_crosscutting_concepts.md § 8.1](08_crosscutting_concepts.md#81-independent-scripts-over-a-shared-core).
- **State lives in files, not in a process.** The marker (`.agent-factory/playbook-state.yml`), the FSM (`factory/playbooks/<name>.fsm.yml`), and the catalog (`factory/INDEX.yaml`) are the only state Factory Flow Control has. Any actor — human, orchestrator, or a freshly started agent session — reads the same files and reaches the same answer.
- **`run-step` re-derives, never trusts.** There is no persisted "what phase are we on" field beyond the marker itself, and even the marker is corroborated against what is actually on disk (outputs, gate result, open findings) before `run-step` decides fresh start, resume, advance, or escalate.

## 4.3 Decomposition strategy

Each mechanism is an independently invocable, standalone script or hook — not layers of a shared core. `transition-lint` only reads and reports; `phase` only reads and, on success, writes the marker; `trigger` only resolves and dispatches; `index-lint` only regenerates the catalog. No mechanism imports another's internals — `trigger` reuses `index-lint`'s `load_agents()`/`load_playbooks()` and `matrix-lint`'s `parse_matrix()` as library functions, not by depending on their control flow.

This mirrors Clean Architecture's dependency rule at script granularity: each mechanism owns one concern of the run's state (Single Responsibility) — the marker owns *where a run is*, the FSM owns *what the run's phases are*, the catalog owns *what agents/skills/playbooks exist*. See [docs/spec/supplementary_specs/entity-model.md § intro](spec/supplementary_specs/entity-model.md).

## 4.4 Approach to the key quality goals

| Quality goal    | How it's achieved                                                                                                                                                                   |
| --------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Determinism     | `transition-lint`'s glob ownership and `phase advance`'s `entry_conditions` are pure functions of files on disk — no judgement call, no LLM in the gate path.                       |
| Resumability    | `run-step` (see [06_runtime_view.md § 6.4](06_runtime_view.md#64-resume-and-dispatch-uc-05-uc-04)) re-checks outputs, gate result, and open findings from disk on every invocation. |
| Safety          | `block-dangerous-git.sh` and `trigger`'s own allow/deny lists mirror each other — two independent layers, not one point of failure (BR-020).                                        |
| CLI-agnosticism | `trigger` builds a separate command for `claude` vs. `copilot`, both reached through the same `--cli` flag; every other mechanism has no CLI awareness at all.                      |
| Simplicity      | Zero third-party dependencies; adding a mechanism means adding one more stdlib script, not a shared library upgrade.                                                                |

## 4.5 Incremental, opt-in adoption

A project need not adopt the whole harness at once. Without a marker file, `transition-lint` is a no-op (`TL-NOMARKER`, info-severity) — a project not using the harness sees no behaviour change. Without a playbook's own `.fsm.yml`, `phase advance`/`retry` and `run-step` fall back to prose-driven judgement calls (see [docs/spec/prd.md § 7 Assumptions](spec/prd.md#7-assumptions)). Only `greenfield-development.fsm.yml` exists today ([NG4](spec/prd.md#non-goals)); every other playbook is driven by prose alone until it earns one.

## Referenced from

- [docs/spec/prd.md § 1 Problem Statement](spec/prd.md#1-problem-statement)
- [docs/concepts.md § The phase chain](concepts.md#the-phase-chain)
