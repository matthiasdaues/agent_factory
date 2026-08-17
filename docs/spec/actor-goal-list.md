# Actor-Goal List — Factory Specification

Derived from [`prd.md`](prd.md) and [`prd-architecture-modeling.md`](prd-architecture-modeling.md). Goal levels use Cockburn's "does the actor go home happy?" test: **User Goal** (sea level) if yes; **Subfunction** if it is only a means reused across use cases.

## Actors — Flow Control

- **Human Operator** (primary) — a person driving Agent Factory directly by hand.
- **Orchestrator-as-Trigger** (primary) — the nested `orchestrator/` Python CLI, invoking the same mechanisms programmatically in the Human Operator's place.
- **CLI-Invoked Agent** (secondary) — the Claude Code, Copilot CLI, or Pi session `trigger` dispatches; a supporting actor with no goal of its own beyond executing the agent definition it was handed. Under Pi it is also the *caller* of `run_agent`, since Pi has no native subagent concept: it spawns a fresh Pi session for the agent it wants to run (AG-10).
- **Phase Participant** (primary) — a human or factory agent completing one workflow phase and restarting the next from durable artifacts.
- **Assurance Auditor** (primary) — a requirements, planning, or quality participant proving which accepted dispatch safeguards are complete and identifying only verified gaps.
- **Handoff Semantic Reviewer** (supporting) — a designated human or agent comparing a structurally valid handoff with the phase artifacts and decisions to detect informational omissions a deterministic linter cannot infer.
- *Supporting actor* — **git / pre-commit**, which invokes `transition-lint` and the guardrail hook at the moments a git operation fires; it has no goal of its own.

## Actors — Architecture Modeling

- **Architecture Author** (primary) — a factory agent (architecture-agent, architecture-review-agent) or human creating and maintaining the JSONC architecture model. Works in JSONC exclusively; never edits the draw.io file directly.
- **Architecture Reviewer** (primary) — a factory agent or human reviewing the architecture model for correctness and constraint satisfaction. May propose structural changes by patching the JSONC model directly, then syncing.
- **Human Reviewer** (secondary) — a person who opens the draw.io file to adjust layout, annotate, or fix labels. Does not edit JSONC directly; label and description edits flow back via reverse sync.
- **Human Operator** (secondary, shared with Flow Control) — drives migration from Structurizr DSL and runs wrapper script commands by hand.
- *Supporting actor* — **git / pre-commit**, which invokes the architecture validation hook at commit time; it has no goal of its own.

## Goals — Flow Control

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
| AG-09 | Human Operator                          | Run project tests deterministically via mechanically triggered gates, never via agent-commanded shell execution                 | User Goal   |
| AG-10 | Human Operator, CLI-Invoked Agent       | Invoke a factory agent under Pi in a genuinely separate session, preserving the author/reviewer independence Pi otherwise lacks | User Goal   |
| AG-11 | Phase Participant                       | Continue a multi-phase workflow in a fresh session with bounded context while preserving every material fact needed downstream  | User Goal   |
| AG-12 | Assurance Auditor                       | Establish auditable completion evidence for every accepted dispatch safeguard without reopening already delivered behavior      | User Goal   |
| SF-01 | (system)                                | Parse the `.fsm.yml` subset (block mappings, block sequences, inline comments) into nested data                                 | Subfunction |
| SF-02 | (system)                                | Evaluate one gate condition (`file_exists`, `files_exist`, `no_open_findings`, `script_exit_zero`)                              | Subfunction |
| SF-03 | (system)                                | Match a staged file path against an `outputs:` glob                                                                             | Subfunction |

Subfunctions SF-01...SF-03 are extracted because `transition-lint` and `phase advance`/`retry` each re-implement the same FSM parsing and glob-matching primitives; they are specified once in [supplementary_specs/validation-rules.md](supplementary_specs/validation-rules.md) and referenced, not repeated per use case.

## Goals — Architecture Modeling

| ID    | Actor                                      | Goal                                                                                                              | Level       |
| ----- | ------------------------------------------ | ----------------------------------------------------------------------------------------------------------------- | ----------- |
| AG-13 | Architecture Author                        | Synchronize the JSONC model with the draw.io diagram after structural edits, preserving bidirectional consistency | User Goal   |
| AG-14 | Architecture Author, Architecture Reviewer | Validate that the architecture model is internally consistent and satisfies declared constraints                  | User Goal   |
| AG-15 | Architecture Author                        | Export architecture views as images for embedding in arc42 chapters                                               | User Goal   |
| AG-16 | Human Operator                             | Migrate an existing Structurizr DSL workspace to the JSONC + draw.io workflow in one step                         | User Goal   |
| AG-17 | Architecture Author, Human Reviewer        | Be stopped from committing architecture artifacts that are inconsistent or improperly co-staged                   | User Goal   |
| SF-04 | (system)                                   | Produce a human-readable structural change summary from model differences                                         | Subfunction |

SF-04 is extracted because `bausteinsicht diff` is reused by multiple consumers (PR descriptions, review workflows) but is not an actor goal on its own.

## Referenced from

- [prd.md](prd.md)
- [prd-architecture-modeling.md](prd-architecture-modeling.md)
