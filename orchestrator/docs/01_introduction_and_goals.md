[back to index](README.md)

# 1. Introduction and Goals

## 1.1 Requirements Overview

The Agent HQ workflow is an eight-agent chain (requirements → spec-review → architecture → architecture-review → planning → implementation → reconciliation → qa) with deliberate author/reviewer loops and human approval points. Today it is driven by hand: the operator edits the CLI instruction file to swap the active agent, starts a fresh session per step to preserve context isolation, and copy-pastes handoff prompts between sessions. Correctness depends on the operator remembering to run gates, honour the separate-session rule, and loop until each review is clean.

The **Agent Session Orchestrator** is a thin Python CLI that observes and manages the state of a run — reporting status, browsing the backlog, persisting operator defaults, and recording the human approvals at phase gates. Flow control — phase sequencing, gating, the iteration loop, model resolution, prompt composition, CLI dispatch, and findings ingestion — moved out of the orchestrator into `factory/`. See the repo-root [`docs/spec/prd.md`](../../docs/spec/prd.md) and [ADR-0002](../../docs/adr/0002-factory-owns-flow-control-orchestrator-is-a-trigger.md).

The authoritative requirements live in [`spec/prd.md`](spec/prd.md). The functional scope below is the workflow's; the orchestrator now implements only the observe-and-manage rows. The execution rows — session isolation, CLI dispatch, the gate, the loop, completion detection — moved to `factory/`.

| Group                | Requirement                                                                                                                                       |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| Execution surface    | `status`, `approve`, `reject`, `abort`, `release`, `init`, and the TUI menu; `run-step`/`run-phase`/`resume` execution moved to `factory/` (FR-A) |
| Session isolation    | every agent runs in a fresh CLI subprocess with no inherited context — spawned by `factory/` (FR-B)                                               |
| CLI-agnostic         | one adapter contract abstracts the target CLI; Copilot is first — the adapter lives in `factory/` (FR-C)                                          |
| Deterministic gates  | `pre-commit` is the gate bus; a commit's hooks decide pass/fail — driven by `factory/` (FR-D)                                                     |
| Findings store       | one validated JSON file per finding, the source of truth for loop state; the orchestrator reads it (FR-E)                                         |
| Loop control         | supersede-and-retry, capped, halt on exhaustion — moved to `factory/` (FR-F)                                                                      |
| Human approval       | pause at phase gates for interactive confirmation (FR-G); unattended auto-approval is deferred (NG6)                                              |
| Completion detection | inferred from the filesystem against each agent's declared `outputs` — inferred in `factory/` (FR-H)                                              |
| Run state & resume   | `.orchestrator/run.json` + findings store are the observed run record; the `resume` command moved to `factory/` (FR-I)                            |
| Observability        | each subprocess invocation is logged; `factory/` writes the log, the orchestrator reads it (FR-J)                                                 |

## 1.2 Quality Goals

The top architectural quality goals, in priority order, derived from the non-functional requirements (§5 of the PRD) and elaborated as scenarios in [chapter 10](10_quality_requirements.md).

| #   | Quality goal            | Motivation                                                                                                                                       |
| --- | ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| Q1  | **Determinism** (NFR-1) | Same artifacts must yield the same gate result — the LLM sits *between* deterministic checks (Eichhorst's principle at the orchestration layer). |
| Q2  | **Isolation** (NFR-2)   | A reviewer's judgement must be independent of the author's reasoning, exactly as a developer must not review their own PR.                       |
| Q3  | **Safety** (NFR-3)      | No unbounded loops, a single active run, atomic state writes, commits only on a dedicated run branch from a clean tree.                          |
| Q4  | **Operability** (NFR-4) | A run can be observed and its state managed (approve, reject, release, abort) without corruption.                                                |
| Q5  | **Portability** (NFR-5) | The core is CLI-agnostic; the MVP targets a local machine, CI/container later.                                                                   |

Two further goals shape decisions but rank below the top five: **bounded cost** (NFR-6 — every invocation has a timeout) and **minimal dependencies** (NFR-7 — prefer the standard library).

## 1.3 Stakeholders

| Role                     | Contact                | Expectations                                                                                                                                                                                       |
| ------------------------ | ---------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Operator** (primary)   | author of Agent HQ     | Watch a run, approve at phase gates, and manage run state (approve, reject, release, abort); a clear halt with a reason when a phase cannot proceed. Phase execution is driven through `factory/`. |
| **Future practitioners** | adopters on other CLIs | The orchestration must be CLI-agnostic so Claude and Gemini plug in behind the same contract.                                                                                                      |

_Deferred: a **Scheduler** (cron / CI) running the chain unattended returns with a messaging channel or Web-UI (NG6)._
| **Downstream phase** | the next agent in the chain | Build only on a phase whose gate passed and whose latest review has zero open findings. |
