[back to index](README.md)

# 10. Quality Requirements

## 10.1 Quality Tree

Priorities: **1 = critical, 2 = important, 3 = nice to have.** Derived from the PRD non-functional requirements (§5).

```
Quality
├── Determinism (Q1, prio 1) ......... same artifacts → same gate result
├── Isolation (Q2, prio 1) ........... reviewer independent of author
├── Safety (Q3, prio 1) .............. bounded loops, single run, atomic state
├── Operability (Q4, prio 2) ......... observe, interrupt, resume without corruption
├── Portability (Q5, prio 2) ......... CLI-agnostic core
├── Bounded cost (Q6, prio 2) ........ every invocation times out
└── Minimal dependencies (Q7, prio 3)  stdlib-first
```

These are the criteria the ADR Pugh matrices ([chapter 9](09_architecture_decisions.md)) draw on.

## 10.2 Quality Scenarios

Each scenario is `source → stimulus → artifact → response → measure`, phrased so it can become a test. IDs (QS-##) are referenced by the ATAM review ([reviews/atam-review.md](reviews/atam-review.md)).

> **Scope note (amended 2026-07-12, PhaseRunner collapse):** QS-13 and QS-14 describe execution-time properties (invocation logging, `CLIAdapter` portability) that now hold in `factory/`, not the orchestrator — its own `status > log` view always renders empty (no invocation-log writer remains), and there is no `CLIAdapter` port left to extend. QS-18 partially moved: exit code and gate behaviour parity between TUI and direct mode still holds; findings ingestion and logging no longer happen in either mode. See the repo-root `docs/spec/prd.md` and `docs/adr/0002-factory-owns-flow-control-orchestrator-is-a-trigger.md`.

| ID        | Quality      | Scenario                                                                                    | Measure (response)                                                                                                                               |
| --------- | ------------ | ------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| **QS-01** | Determinism  | The same committed artifact set is gated twice.                                             | Identical `GateResult` and identical finding set both times (NFR-1, VR-015).                                                                     |
| **QS-02** | Determinism  | The gate hook reports one error-severity finding.                                           | The hook exits non-zero **iff** ≥1 error finding exists; warning/info never block (BR-002, VR-001).                                              |
| **QS-03** | Determinism  | Control-flow decision at any branch.                                                        | The decision is made from exit codes + structured findings only — never from parsing agent prose (§8.2).                                         |
| **QS-04** | Isolation    | A reviewer runs after its author in the same phase.                                         | The reviewer is a separate OS process with no inherited context; verifiable structurally (BR-004, VR-004).                                       |
| **QS-05** | Safety       | A reviewer keeps producing open findings every pass.                                        | Loop-back stops at the cap (default 3); the run halts and summons the human; findings left open (BR-001/003, VR-002).                            |
| **QS-06** | Safety       | The gate hook itself crashes (tool missing / exception).                                    | The run halts immediately without counting an author iteration; the tooling error is surfaced (BR-015, VR-014).                                  |
| **QS-07** | Safety       | The adapter reports an auth/availability failure.                                           | The run halts without counting an author iteration (BR-018, VR-018).                                                                             |
| **QS-08** | Safety       | A second run is attempted while one is active.                                              | The orchestrator refuses to start while a lock is held or `run.json` is `running` (BR-017, VR-017).                                              |
| **QS-09** | Safety       | The process is killed mid-write of `run.json` or a finding.                                 | No half-written record survives (write-then-rename); the next read is consistent (NFR-3, VR-010).                                                |
| **QS-10** | Safety       | A phase commits its artifacts.                                                              | The commit targets a dedicated run branch from a clean tree, never force-pushed, never the operator's branch (BR-016, NFR-3).                    |
| **QS-11** | Operability  | A run is interrupted and later resumed.                                                     | Resume continues from the checkpoint, never re-running a `complete` phase; re-gates if tracked artifacts changed (UC-06, VR-005/012).            |
| **QS-12** | Operability  | The operator runs `status` mid-run.                                                         | Current phase, iteration, open-finding count, last gate result, and mode are reported; no state is mutated (UC-05, VR-008).                      |
| **QS-13** | Operability  | Any agent subprocess completes.                                                             | The invocation is logged with agent, role, adapter, duration, exit, gate outcome (FR-J).                                                         |
| **QS-14** | Portability  | A new target CLI (Claude/Gemini) is added.                                                  | Only a new `CLIAdapter` implementation is written; no core module changes (FR-C, NFR-5).                                                         |
| **QS-15** | Portability  | A later phase needs an extra deterministic check.                                           | A new `pre-commit` hook is registered; no orchestrator change (FR-D4).                                                                           |
| **QS-16** | Bounded cost | An agent subprocess hangs.                                                                  | It is killed at the configured timeout and treated as a failed iteration (NFR-6).                                                                |
| **QS-17** | Minimal deps | The tool is installed on a clean machine.                                                   | It runs on the Python stdlib plus a single justified dependency (`jsonschema`); nothing else required (NFR-7, T-06).                             |
| **QS-18** | Operability  | The operator runs a function via the TUI leaf and via the direct-mode command.              | Both dispatch to the same service with identical exit code, gate behaviour, run-state mutation, findings ingestion, and logging (NFR-10, FR-V3). |
| **QS-19** | Safety       | The operator navigates menus, views displays, and exits the TUI without dispatching a leaf. | No `run.json`, findings, or log data is mutated by navigation or exit (NFR-11, VR-030).                                                          |
| **QS-20** | Operability  | The operator persists a default, then invokes with a CLI flag and a menu selection.         | The effective setting follows `menu > CLI flag > config.toml > built-in`, resolved identically in both modes (FR-Q3, VR-034).                    |

## 10.3 Priorities for evaluation

The ATAM review evaluates all scenarios but treats the priority-1 qualities (Determinism, Isolation, Safety) as the ones whose failure is unacceptable. Portability and operability are important but degrade gracefully; minimal dependencies is a preference that yields to a well-justified need (as `jsonschema` does).
