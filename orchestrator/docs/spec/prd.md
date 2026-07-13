# Orchestrator — Product Requirements Document

## Vision

The orchestrator replaces the human operator pressing "enter" between agent sessions. It is a mechanical dispatcher that rides the playbook's FSM rails, advancing the state marker one step at a time by delegating all decisions to the existing gate mechanism.

## Problem statement

Agent Factory's playbooks define a complete state machine: states, transitions, entry conditions, exit conditions, halt conditions. The gate scripts (`phase advance`, `phase retry`) enforce these conditions deterministically. The dispatch script (`trigger`) resolves agents and launches CLI sessions. All the pieces exist. But today, a human sits between them — reading the marker, picking the agent, calling trigger, waiting, calling phase advance, repeating. The human adds no judgement here; they press "enter" in a fixed sequence. That mechanical role is what the orchestrator automates.

## Scope

### In scope

- Execute one FSM step per invocation: resolve agent, dispatch, wait, check out-gate, advance or retry.
- Self-chain on successful advance (next step follows immediately).
- Stop at human gates (`agent: null`) and return control.
- Stop at final states and report completion.
- Stop when a halt condition fires (iteration cap) and report escalation.
- Stop on configuration errors (resolution failure) and report.
- Write structured audit entries to `.agent-factory/audit.log`.
- Support both Claude Code and GitHub Copilot CLI as dispatch targets.

### Out of scope

- Driving Phase 1 (Requirements) — always human-initiated.
- Parallel dispatch of multiple agents simultaneously.
- Failure recovery beyond iteration-cap retry (no model switching, no prompt rewriting).
- Prompt enrichment with open findings on retry (named gap, future enhancement).
- Backward transitions (rejection at human gates) — forward-only; rejection is `phase`'s concern.
- Session management, adapter layers, or CLI output parsing.

## Actors

| ID   | Actor          | Description                                                                    |
| ---- | -------------- | ------------------------------------------------------------------------------ |
| A-01 | Human operator | Initiates playbook runs, handles human gates, investigates halts               |
| A-02 | Orchestrator   | The dispatcher module itself — reads state, dispatches agents, advances marker |
| A-03 | AI agent       | The invoked agent (architecture-agent, qa-agent, etc.) — does the actual work  |
| A-04 | Gate mechanism | `phase advance` + `phase retry` — evaluates conditions, writes marker          |
| A-05 | Trigger        | Resolves agent → model, composes prompt, launches CLI                          |

## Functional requirements

| ID    | Requirement                                                                                                        | Traces |
| ----- | ------------------------------------------------------------------------------------------------------------------ | ------ |
| FR-01 | The orchestrator shall read the playbook state marker to determine the current FSM state.                          | UC-01  |
| FR-02 | The orchestrator shall resolve the current state's agent from the FSM definition.                                  | UC-01  |
| FR-03 | The orchestrator shall stop and return control when the current state has `agent: null`.                           | UC-02  |
| FR-04 | The orchestrator shall stop and report completion when the current state is `final: true`.                         | UC-03  |
| FR-05 | The orchestrator shall attempt `phase advance --dry-run` before dispatching to detect already-satisfied out-gates. | UC-01  |
| FR-06 | The orchestrator shall dispatch the resolved agent via `trigger agent <name> --background --cli <cli>`.            | UC-01  |
| FR-07 | The orchestrator shall block until the dispatched agent session completes.                                         | UC-01  |
| FR-08 | The orchestrator shall attempt `phase advance` after agent completion to check the out-gate.                       | UC-01  |
| FR-09 | The orchestrator shall call `phase retry` when the out-gate fails after dispatch.                                  | UC-04  |
| FR-10 | The orchestrator shall halt when `phase retry` refuses (iteration cap hit).                                        | UC-04  |
| FR-11 | The orchestrator shall self-chain (execute the next step) when `phase advance` succeeds.                           | UC-01  |
| FR-12 | The orchestrator shall halt immediately on trigger exit code 2 (resolution/config error).                          | UC-05  |
| FR-13 | The orchestrator shall write a JSON-lines audit entry per step to `.agent-factory/audit.log`.                      | UC-01  |
| FR-14 | The orchestrator shall accept `--playbook`, `--cli`, and `--from-state` parameters.                                | UC-01  |
| FR-15 | The orchestrator shall bootstrap the marker at `--from-state` if no marker exists.                                 | UC-01  |

## Non-functional requirements

| ID     | Requirement                                                                                                 |
| ------ | ----------------------------------------------------------------------------------------------------------- |
| NFR-01 | Zero third-party dependencies. Python 3.10+ stdlib only. Same constraint as all factory scripts.            |
| NFR-02 | The orchestrator shall not exceed 200 lines of code (excluding imports and docstring).                      |
| NFR-03 | Crash recovery: re-invocation after kill at any point shall resume correctly from the marker.               |
| NFR-04 | An agent shall never be able to distinguish orchestrator dispatch from human dispatch. Prompt is identical. |
| NFR-05 | The orchestrator shall complete its own logic (excluding agent runtime) in under 1 second per step.         |

## Constraints

| ID   | Constraint                                                                                                                                                                  |
| ---- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| C-01 | The orchestrator owns no sequencing logic of its own. All sequencing decisions are delegated to `phase advance` and `phase retry`.                                          |
| C-02 | The orchestrator owns no condition evaluation. All gate checks are delegated to `phase advance`.                                                                            |
| C-03 | The orchestrator owns no agent resolution or prompt composition. All dispatch is delegated to `trigger`.                                                                    |
| C-04 | The playbook state marker (`.agent-factory/playbook-state.yml`) is the single source of truth for execution position. The orchestrator reads it but only `phase` writes it. |
| C-05 | Phase 1 (Requirements) is never orchestrator-driven. The orchestrator's entry point is always a state where specs already exist.                                            |

## Success criteria

1. A human can type `run-playbook --playbook bug-fix --from-state IMPLEMENT_FIX --cli claude` and walk away. The orchestrator dispatches developer-agent, waits, checks tests_pass, dispatches qa-agent, waits, checks findings, stops at MARK_RESOLVED (human gate).
2. A greenfield project with completed specs can run from PHASE_2_ARCHITECTURE through to DONE (pausing at PHASE_3_APPROVAL for human confirmation) without manual intervention between agent sessions.
3. A halt condition (3 failed QA loops) stops the run with a clear escalation message rather than looping forever.
4. Killing the process at any point and re-running produces correct behavior — no corrupted state, no repeated work, no skipped gates.
