# Actor-Goal List — Agent Session Orchestrator

Derived from [`prd.md`](prd.md). Goal levels use Cockburn's "does the actor go home happy?" test: **User Goal** (sea level) if yes; **Subfunction** if it is only a means reused across use cases.

> **Scope note (amended 2026-07-12, PhaseRunner collapse):** AG-01, AG-02, AG-03, AG-06, and SF-01 through SF-04 describe the execution surface deleted from the orchestrator (`PhaseRunner` and its supporting components) and moved to `factory/`. AG-04 (approve/reject) and AG-05 (status) are unaffected. See the repo-root `docs/spec/prd.md` and `docs/adr/0002-factory-owns-flow-control-orchestrator-is-a-trigger.md`.

## Actors

- **Operator** — the human driving a project through the Agent HQ chain (primary).
- *Supporting actors* (invoked, no goals of their own): the **authoring agent** and **reviewing agent** CLI subprocesses.
- *Deferred actor* — the **Scheduler** (an unattended cron/CI trigger) is out of current scope; it returns with unattended execution when the orchestrator gains a messaging channel or Web-UI (see Deferred scope below).

## Goals

| ID    | Actor    | Goal                                                                                                                                             | Level       |
| ----- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------ | ----------- |
| AG-01 | Operator | _(Superseded — moved to factory.)_ Run a single agent step in isolation and get its artifact                                                     | User Goal   |
| AG-02 | Operator | _(Superseded — moved to factory.)_ Drive one phase's author↔reviewer loop to a clean review                                                      | User Goal   |
| AG-03 | Operator | _(Superseded — moved to factory.)_ Drive the project through all phases in dependency order, running one phase at a time and approving each gate | User Goal   |
| AG-04 | Operator | Approve or reject the work at a phase gate                                                                                                       | User Goal   |
| AG-05 | Operator | Check the status of a run (phase, iteration, open findings)                                                                                      | User Goal   |
| AG-06 | Operator | _(Superseded — moved to factory.)_ Resume an interrupted run without losing or corrupting state                                                  | User Goal   |
| SF-01 | (system) | _(Superseded — moved to factory.)_ Isolate an agent session in a fresh CLI subprocess                                                            | Subfunction |
| SF-02 | (system) | _(Superseded — moved to factory.)_ Run the deterministic gate (commit → pre-commit hooks)                                                        | Subfunction |
| SF-03 | (system) | _(Superseded — moved to factory.)_ Record a finding to the local store                                                                           | Subfunction |
| SF-04 | (system) | _(Superseded — moved to factory.)_ Evaluate the loop condition (open findings + gate result)                                                     | Subfunction |

Subfunctions SF-01…SF-04 are extracted because every run-oriented goal (AG-01/02/03/06) reuses them; they are specified once and referenced, not repeated per use case.

## Deferred scope

- **AG-07 (Scheduler — run the chain unattended)** and the single-command automated full-chain run (`run-all`) are **deferred**. Every run is human-attended for now; the Operator drives the phases one at a time (AG-03). Automated and unattended chain execution return when the orchestrator gains a **messaging channel or Web-UI** through which a human can observe and approve a running chain remotely (todos.md T-36).

## TUI Addendum Goals

Derived from [`prd-tui-addendum.md`](prd-tui-addendum.md) (FR-P through FR-V). These extend the original actor-goal list with goals specific to the TUI menu mode.

| ID    | Actor    | Goal                                                                                                                                 | Level       |
| ----- | -------- | ------------------------------------------------------------------------------------------------------------------------------------ | ----------- |
| AG-08 | Operator | Discover and reach any orchestrator function through menu navigation without memorising commands                                     | User Goal   |
| AG-09 | Operator | Persist and manage default settings (adapter, timeout, cap, auto-approve)                                                            | User Goal   |
| AG-10 | Operator | Register, discover, and remove CLI adapters and their model dictionaries                                                             | User Goal   |
| AG-11 | Operator | _(Superseded — moved to factory.)_ Run a single skill from an agent in isolation                                                     | User Goal   |
| AG-12 | Operator | Browse the story backlog (list, by epic, ready, single story)                                                                        | User Goal   |
| AG-13 | Operator | Inspect run status through dedicated views (overview, phase details, findings, log)                                                  | User Goal   |
| SF-05 | (system) | Render a navigable menu with arrow-key selection and `-> ` cursor                                                                    | Subfunction |
| SF-06 | (system) | Render a read-only display screen and return to parent on keypress                                                                   | Subfunction |
| SF-07 | (system) | Resolve settings via the four-layer precedence (menu > CLI flag > config.toml > built-in default)                                    | Subfunction |
| SF-08 | (system) | _(Superseded — moved to factory.)_ Resolve the default model from an agent's declared tier and the active adapter's model dictionary | Subfunction |

Subfunctions SF-05…SF-08 support multiple TUI goals and are specified once. SF-08 extends the existing model resolution chain (FR-K) with the agent-tier axis.
