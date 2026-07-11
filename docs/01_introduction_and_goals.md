[back to index](README.md)

# 1. Introduction and Goals

## 1.1 Requirements Overview

`factory/` began as a library of agents, skills, and playbooks — prose read by a human or an AI CLI, with no enforcement. Nothing stopped a file from a later phase being staged before its predecessor's gate cleared. Nothing capped a review loop, so a stuck gate could churn forever. Factory Flow Control closes both gaps: a deterministic state-machine harness, a CLI-agnostic dispatch mechanism, and a generated catalog, all driven from observable, git-ignored local state — without requiring the `orchestrator/` Python CLI that used to own this job.

Full problem statement: [docs/spec/prd.md § 1 Problem Statement](spec/prd.md#1-problem-statement).

| ID  | Goal                                                                                                           | Mechanism                |
| --- | -------------------------------------------------------------------------------------------------------------- | ------------------------ |
| G1  | Gate which files may be staged in which playbook phase, deterministically, from a local marker                 | `transition-lint`        |
| G2  | Advance a run to its next phase only when that phase's entry conditions hold, recorded in the marker           | `phase advance`          |
| G3  | Cap how many times a phase's author step re-runs after a failing gate, configurable, with a default backstop   | `phase retry`            |
| G4  | Dispatch a named agent or one playbook step to a CLI session under a scoped permission allowlist               | `trigger`                |
| G5  | Resolve "what's next" and "is this a resume" from observable state every time, never a persisted status        | `run-step` skill         |
| G6  | Keep the machine-readable catalog of every agent, skill, and playbook generated from source, never hand-edited | `index-lint`             |
| G7  | Block a fixed list of destructive or gate-bypassing git commands before they run, for both supported CLIs      | `block-dangerous-git.sh` |
| G8  | Wire all of the above into a new or existing project, idempotently                                             | `init-factory`           |

Full goal list: [docs/spec/prd.md § 2 Goals and Non-Goals](spec/prd.md#2-goals-and-non-goals).

## 1.2 Quality Goals

Ranked by priority — see [10_quality_requirements.md § 10.1 Quality Tree](10_quality_requirements.md#101-quality-tree) for the full tree and scenarios.

1. **Determinism** — a gate's answer never depends on judgement or on who runs it; the same marker and the same files on disk always produce the same verdict.
2. **Resumability** — a crashed session, a closed terminal, or a fresh session never leaves work stranded behind stale state; every fact `run-step` needs is re-derived from disk.
3. **Safety** — a destructive or gate-bypassing git command is denied before it runs, on two independent layers.
4. **CLI-agnosticism** — every mechanism works identically whether a human types the command, `orchestrator/` invokes it programmatically, or a dispatched agent session runs it.
5. **Simplicity** — every gate script is Python 3.8+ stdlib only; no virtualenv, no third-party dependency to keep in sync.

## 1.3 Stakeholders

| Role                           | Actor                                     | Expectation                                                                                        |
| ------------------------------ | ----------------------------------------- | -------------------------------------------------------------------------------------------------- |
| Primary actor                  | Human Operator                            | Drives Agent Factory directly: runs scripts by hand, commits code, approves phase gates.           |
| Primary actor                  | Orchestrator-as-Trigger (`orchestrator/`) | Invokes the same mechanisms programmatically, as a peer of the Human Operator, not as their owner. |
| Secondary actor                | CLI-Invoked Agent                         | The Claude Code or Copilot CLI session `trigger` dispatches, under a scoped allowlist.             |
| Supporting actor (no own goal) | git / pre-commit                          | Invokes `transition-lint` and the guardrail hook at the moments a git operation fires.             |

Full actor list with Cockburn goal levels: [docs/spec/actor-goal-list.md](spec/actor-goal-list.md).

## Referenced from

- [docs/spec/prd.md § 3 Target Actors](spec/prd.md#3-target-actors)
- [docs/spec/actor-goal-list.md](spec/actor-goal-list.md)
