# Reconciliation Report — Pass 4 (2026-07-07)

**Date**: 2026-07-07
**Trigger**: FAGAN-0039–0048 implementation and adversarial-review remediation committed (8f73ae0)
**Scope**: Production code vs. spec/architecture docs

## Context

The pass-3 findings (FAGAN-0039–0048) were implemented, then a four-way adversarial
review found four of the first-pass fixes broken (0040, 0044, 0045, 0047); all four were
remediated and re-reviewed before the commit. This pass syncs the supplementary specs to
the code as built. Three residual items surfaced by the review were filed as new findings
(FAGAN-0049–0051) rather than fixed in this batch.

## Discrepancies Found and Resolved

| #   | Surface           | File                   | Issue                                                                                | Resolution                                                                                                                      |
| --- | ----------------- | ---------------------- | ------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------- |
| 1   | PhaseRecord       | entity-model.md        | Missing `last_reviewed_cycle` field (FAGAN-0040)                                     | Added to PHASE entity (nullable) + note                                                                                         |
| 2   | Run state         | interface-contracts.md | `run.json` phase schema missing `last_reviewed_cycle`                                | Added property (`integer`/`null`)                                                                                               |
| 3   | Cycle counting    | interface-contracts.md | Cycle-tagging note omitted persisted-cycle approval/status read                      | Added "Persisted review cycle" note                                                                                             |
| 4   | GateRunner        | interface-contracts.md | Missing `head_is_gate_commit` / `gate_head` (FAGAN-0042)                             | Added methods + idempotent-resume bullet                                                                                        |
| 5   | GateRunner        | interface-contracts.md | Missing clean-tree / dirty-worktree reject (FAGAN-0044)                              | Added clean-tree precondition bullet                                                                                            |
| 6   | GateRunner        | interface-contracts.md | Missing auto-fix re-stage/rerun pass (FAGAN-0046)                                    | Added auto-fix retry bullet                                                                                                     |
| 7   | GateResult.output | interface-contracts.md | Described as stdout only                                                             | Updated to stdout + stderr                                                                                                      |
| 8   | FindingIngestor   | interface-contracts.md | `ingest_gate_output` didn't note mixed-stdout tolerance + dedup (FAGAN-0045)         | Updated ingest-mapping note                                                                                                     |
| 9   | State machine     | state-machines.md      | Approval pseudocode omitted re-gate + failed-re-gate recovery (FAGAN-0039/0040/0041) | Rewrote approved branch: findings guard on persisted cycle, staleness re-gate, `Gating`+`Halted` recovery, `run.iteration` sync |
| 10  | State machine     | state-machines.md      | Diagram missing recovery edge                                                        | Added `AwaitingApproval --> Gating : re-gate failed`                                                                            |
| 11  | State machine     | state-machines.md      | No exit-code contract (FAGAN-0047)                                                   | Added exit-codes note (0 ok/paused · 1 internal · 2 halted · 3 usage)                                                           |
| 12  | State machine     | state-machines.md      | Approval recovery not in notes (FAGAN-0039)                                          | Added approval-recovery note                                                                                                    |

## Already Consistent (confirmed, no change)

- **Resume idempotency** was already documented ahead of the code — state-machines.md note
  (ATAM-R07) and interface-contracts.md Run State note. The FAGAN-0042/0043 implementation
  now realizes exactly that description; both notes were verified, not changed.

## Architecture Diagrams

No re-render. This batch added fields to an existing entity (`PhaseRecord.last_reviewed_cycle`)
and methods to an existing port (`GateRunner`); it introduced no new component, container, or
relationship. `architecture.dsl` and `05_building_block_view.md` are unchanged, so the three
rendered views (SystemContext, Containers, CoreComponents) remain accurate and `arch-lint`
does not fire.

## Deferred (filed as new findings)

| Finding    | Origin               | Summary                                                                                                                                              |
| ---------- | -------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| FAGAN-0049 | FAGAN-0043 residual  | Resume from REVIEWING can still duplicate findings in the pre-ingest crash window; needs content-keyed ingest dedup or post-ingest markdown cleanup. |
| FAGAN-0050 | FAGAN-0046 residual  | Auto-fix hook that edits a non-declared file leaves untracked worktree dirt the next gate wrongly rejects.                                           |
| FAGAN-0051 | FAGAN-0042 hardening | Gate commit subject lacks iteration/run-id, weakening resume checkpoint detection; deferred to keep the remediation batch parallel-safe.             |

## Verification

- Full suite: 342 passed, 1 skipped.
- Code + finding-status flips committed in 8f73ae0; findings FAGAN-0039–0048 marked `resolved`.
- This pass is spec-only (no code change).
