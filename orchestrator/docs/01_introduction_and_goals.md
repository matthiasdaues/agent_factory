[back to index](README.md)

# 1. Introduction and Goals

## 1.1 Requirements Overview

The Agent HQ workflow is an eight-agent chain (requirements → spec-review → architecture → architecture-review → planning → implementation → reconciliation → qa) with deliberate author/reviewer loops and human approval points. Today it is driven by hand: the operator edits the CLI instruction file to swap the active agent, starts a fresh session per step to preserve context isolation, and copy-pastes handoff prompts between sessions. Correctness depends on the operator remembering to run gates, honour the separate-session rule, and loop until each review is clean.

The **Agent Session Orchestrator** is a thin Python CLI that runs the chain — a single step, one phase, or the whole sequence — with the deterministic quality gates enforced automatically and human judgement reserved for the decisions that genuinely need it.

The authoritative requirements live in [`spec/prd.md`](spec/prd.md). The essential functional scope:

| Group                | Requirement                                                                                          |
| -------------------- | ---------------------------------------------------------------------------------------------------- |
| Execution surface    | `run-step`, `run-phase`, `status`, `resume`, `approve` (FR-A)                                        |
| Session isolation    | every agent runs in a fresh CLI subprocess with no inherited context (FR-B)                          |
| CLI-agnostic         | one adapter contract abstracts the target CLI; Copilot is first (FR-C)                               |
| Deterministic gates  | `pre-commit` is the gate bus; a commit's hooks decide pass/fail (FR-D)                               |
| Findings store       | one validated JSON file per finding, the source of truth for loop state (FR-E)                       |
| Loop control         | supersede-and-retry, capped, halt on exhaustion (FR-F)                                               |
| Human approval       | pause at phase gates for interactive confirmation (FR-G); unattended auto-approval is deferred (NG6) |
| Completion detection | inferred from the filesystem against each agent's declared `outputs` (FR-H)                          |
| Run state & resume   | `.orchestrator/run.json` + findings store make a run resumable (FR-I)                                |
| Observability        | each subprocess invocation is logged (FR-J)                                                          |

## 1.2 Quality Goals

The top architectural quality goals, in priority order, derived from the non-functional requirements (§5 of the PRD) and elaborated as scenarios in [chapter 10](10_quality_requirements.md).

| #   | Quality goal            | Motivation                                                                                                                                       |
| --- | ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| Q1  | **Determinism** (NFR-1) | Same artifacts must yield the same gate result — the LLM sits *between* deterministic checks (Eichhorst's principle at the orchestration layer). |
| Q2  | **Isolation** (NFR-2)   | A reviewer's judgement must be independent of the author's reasoning, exactly as a developer must not review their own PR.                       |
| Q3  | **Safety** (NFR-3)      | No unbounded loops, a single active run, atomic state writes, commits only on a dedicated run branch from a clean tree.                          |
| Q4  | **Operability** (NFR-4) | A run can be observed, interrupted, and resumed without corrupting state.                                                                        |
| Q5  | **Portability** (NFR-5) | The core is CLI-agnostic; the MVP targets a local machine, CI/container later.                                                                   |

Two further goals shape decisions but rank below the top five: **bounded cost** (NFR-6 — every invocation has a timeout) and **minimal dependencies** (NFR-7 — prefer the standard library).

## 1.3 Stakeholders

| Role                     | Contact                | Expectations                                                                                                                                            |
| ------------------------ | ---------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Operator** (primary)   | author of Agent HQ     | Launch a step or drive the chain one phase at a time, watching each run and trusting the gates; a clear halt with a reason when a phase cannot proceed. |
| **Future practitioners** | adopters on other CLIs | The orchestration must be CLI-agnostic so Claude and Gemini plug in behind the same contract.                                                           |

_Deferred: a **Scheduler** (cron / CI) running the chain unattended returns with a messaging channel or Web-UI (NG6)._
| **Downstream phase** | the next agent in the chain | Build only on a phase whose gate passed and whose latest review has zero open findings. |
