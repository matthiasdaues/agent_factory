# Actor-Goal List — Factory Flow Control

Derived from [`prd.md`](prd.md). Goal levels use Cockburn's "does the actor go home happy?" test: **User Goal** (sea level) if yes; **Subfunction** if it is only a means reused across use cases.

## Actors

- **Human Operator** (primary) — a person driving Agent Factory directly by hand.
- **Orchestrator-as-Trigger** (primary) — the nested `orchestrator/` Python CLI, invoking the same mechanisms programmatically in the Human Operator's place.
- **CLI-Invoked Agent** (secondary) — the Claude Code, Copilot CLI, or Pi session `trigger` dispatches; a supporting actor with no goal of its own beyond executing the agent definition it was handed. Under Pi it is also the *caller* of `run_agent`, since Pi has no native subagent concept: it spawns a fresh Pi session for the agent it wants to run (AG-10).
- *Supporting actor* — **git / pre-commit**, which invokes `transition-lint` and the guardrail hook at the moments a git operation fires; it has no goal of its own.

## Goals

| ID    | Actor                                   | Goal                                                                                                                            | Level       |
| ----- | --------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------- | ----------- |
| AG-01 | Human Operator, Orchestrator-as-Trigger | Advance a playbook run to its next phase only when that phase's entry conditions are met                                        | User Goal   |
| AG-02 | Human Operator                          | Be stopped from committing a file that belongs to a phase other than the run's current one                                      | User Goal   |
| AG-03 | Human Operator, Orchestrator-as-Trigger | Retry the current phase's author step without risking an endless loop                                                           | User Goal   |
| AG-04 | Human Operator, Orchestrator-as-Trigger | Dispatch a named agent or one playbook step to a CLI session, interactive or unattended, under a scoped allowlist               | User Goal   |
| AG-05 | Human Operator, Orchestrator-as-Trigger | Resume a playbook run after an interruption by re-deriving what is next from observable state                                   | User Goal   |
| AG-06 | Human Operator, Orchestrator-as-Trigger | Keep the machine-readable catalog of every agent, skill, and playbook consistent with their source frontmatter                  | User Goal   |
| AG-07 | Human Operator, CLI-Invoked Agent       | Be stopped from running a destructive or gate-bypassing git command before it executes                                          | User Goal   |
| AG-08 | Human Operator                          | Wire Agent Factory's tooling, guardrail hook, and gate config into a project without disturbing what is already there           | User Goal   |
| AG-09 | Human Operator                          | Run project tests deterministically via unavoidable hooks, never via agent-commanded shell execution                            | User Goal   |
| AG-10 | Human Operator, CLI-Invoked Agent       | Invoke a factory agent under Pi in a genuinely separate session, preserving the author/reviewer independence Pi otherwise lacks | User Goal   |
| SF-01 | (system)                                | Parse the `.fsm.yml` subset (block mappings, block sequences, inline comments) into nested data                                 | Subfunction |
| SF-02 | (system)                                | Evaluate one gate condition (`file_exists`, `files_exist`, `no_open_findings`, `script_exit_zero`)                              | Subfunction |
| SF-03 | (system)                                | Match a staged file path against an `outputs:` glob                                                                             | Subfunction |

Subfunctions SF-01…SF-03 are extracted because `transition-lint` and `phase advance`/`retry` each re-implement the same FSM parsing and glob-matching primitives; they are specified once in [supplementary_specs/validation-rules.md](supplementary_specs/validation-rules.md) and referenced, not repeated per use case.

## Referenced from

- [prd.md](prd.md)
