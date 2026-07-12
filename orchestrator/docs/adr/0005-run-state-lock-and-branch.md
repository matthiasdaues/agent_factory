# 0005. Run state as a single atomic JSON file, with a run lock and a dedicated run branch

**Status**: Accepted

> **Amended 2026-07-12 (PhaseRunner collapse):** `run.json` and the single-run lock remain in the orchestrator; run-branch creation and resume-driven execution moved to `factory/`. See the repo-root `docs/spec/prd.md` and `docs/adr/0002-factory-owns-flow-control-orchestrator-is-a-trigger.md`.

## Context

A run must be observable, interruptible, and resumable without corruption (Q4, NFR-4, FR-I). Safety demands a single active run, atomic state writes, and commits that never endanger the operator's working tree (Q3, NFR-3): commits go to a dedicated run branch from a clean tree, never force-pushed (BR-016, BR-017). Resume must skip completed phases (VR-005) and re-gate stale artifacts (VR-012).

The question is how the orchestrator persists run state, enforces single-run, and isolates its commits.

### Alternatives (Pugh Matrix)

Baseline **A**: derive all state from git history/commits (no separate state file). **B**: a single `run.json` written atomically, a `run.lock` lockfile, and a dedicated run branch. **C**: a SQLite run database.

| Criterion                                        | Weight | A: git-only | B: run.json + lock + branch | C: SQLite |
| ------------------------------------------------ | ------ | ----------- | --------------------------- | --------- |
| Safety — atomic checkpoint writes (Q3)           | 3      | 0           | +1                          | 0         |
| Safety — single-run enforcement (Q3)             | 3      | 0           | +1                          | 0         |
| Operability — explicit resumable checkpoint (Q4) | 2      | 0           | +1                          | +1        |
| Operability — human-inspectable / diffable (Q4)  | 2      | 0           | +1                          | -1        |
| Minimal dependencies (Q7)                        | 1      | 0           | +1                          | 0         |
| **Weighted total**                               |        | **0**       | **+11**                     | **0**     |

B wins. Git history alone (A) is coarse and gives no lock. SQLite (C) offers a checkpoint but is opaque to git and inspection and enforces nothing about single-run on its own.

## Decision

Persist run state as a **single `.orchestrator/run.json`**, matching the run-state schema ([interface-contracts.md](../spec/supplementary_specs/interface-contracts.md)):

- Written **atomically** (write-then-rename); validated on write (VR-010). It records `run_id`, `branch`, `chain`, `current_phase`, `iteration`, `mode`, and per-phase status. `idle` is never persisted — an absent `run.json` *is* idle.
- A **`run.lock`** enforces the single-active-run invariant (BR-017, VR-017): the orchestrator refuses to start while a lock is held or `run.json` shows `mode: running`; `resume` reclaims the lock for the recorded run.
- All commits go to a **dedicated run branch** created or selected at run start, from a clean tree, never force-pushed (BR-016) — the operator's working branch is never touched.
- `run.json` + the findings store together are the complete resumable checkpoint; resume skips `complete` phases (VR-005) and re-gates if tracked artifacts changed since the checkpoint (VR-012).

## Consequences

**Positive**

- A crash never leaves a half-written checkpoint (QS-09); the next `resume` reads a consistent state.
- Single-run is enforced explicitly, preventing two runs from racing on the same tree (QS-08).
- Run state is plain JSON — inspectable and diffable, matching the store's ethos ([ADR-0004](0004-file-per-finding-store.md)).

**Negative / risks**

- Two persistence mechanisms (git branch for artifacts, JSON for run metadata) must be kept coherent on resume; the re-gate-on-staleness rule (VR-012) is the reconciliation step.
- The run branch may diverge from the operator's working branch over a long run; merging it back is the operator's responsibility, out of the orchestrator's scope (risk R-6).

**Hardening (from the ATAM review)**

- **Resume idempotency (ATAM-R07)**: phase `status` + iteration alone under-specify the checkpoint. The run branch HEAD and the current iteration's ingested findings are the sub-phase checkpoint; on resume an already-present commit for the current iteration is not re-committed and an already-ingested reviewer pass is not re-run, so a crash mid-iteration cannot burn an empty-commit iteration or duplicate findings.
- **Status needs the last gate (ATAM-R05)**: the phase record carries a `last_gate` object so `status` reports the last gate result without re-running it.
- **ID allocator crash-safety (ATAM-R08)**: the next id is `max(existing FND-NNNN in findings/) + 1`, derived from the directory rather than a separately stored counter, so it is inherently crash-safe and never reuses an id.
- **Lock liveness (ATAM-R09)**: the lock records the holder's PID and start time; a lock whose PID is dead is treated as stale and reclaimable with a warning, so a crashed run does not wedge the tool.
- **Clean-tree enforcement (ATAM-R10)**: at `run-phase` start the orchestrator refuses to proceed on a dirty tree with a clear message (rather than committing unrelated changes), making the "clean tree from a run branch" precondition (UC-02) an enforced check, not an assumption.
