# Reconciliation Report — Pass 3 (2026-07-06)

**Date**: 2026-07-06\
**Trigger**: FAGAN-0032–0038 implementation committed (4885c2b)\
**Scope**: All production code vs. spec/architecture docs

## Discrepancies Found and Resolved

| #   | Surface             | File                        | Issue                                                        | Resolution                                                                |
| --- | ------------------- | --------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------------------- |
| 1   | GateResult          | interface-contracts.md      | Missing `output` field (FAGAN-0034)                          | Added field with transient note                                           |
| 2   | FindingIngestor     | interface-contracts.md      | Missing `ingest_gate_output` method (FAGAN-0034)             | Updated ingest mapping paragraph                                          |
| 3   | GateResult          | entity-model.md             | Missing `output` field in ER diagram (FAGAN-0034)            | Added to GATE_RESULT entity with transient annotation                     |
| 4   | GateResult          | entity-model.md             | Notes missing output/transient semantics                     | Updated GATE_RESULT note                                                  |
| 5   | ApprovalService     | 05_building_block_view.md   | Described as "advances to the next chain phase"              | Updated: pauses with `current_phase` advanced; accepts empty-commit       |
| 6   | State machine       | state-machines.md           | Empty-commit path only showed RetryOrHalt                    | Split: interactive → AwaitingApproval, non-interactive → RetryOrHalt      |
| 7   | State machine       | state-machines.md           | Approval pseudocode didn't show PAUSED semantics             | Added mode = Paused / Complete branching                                  |
| 8   | State machine       | state-machines.md           | Mermaid diagram missing interactive empty-commit edge        | Added `Gating --> AwaitingApproval : empty commit (interactive)`          |
| 9   | State machine       | state-machines.md           | Gate-failure pseudocode didn't mention gate output ingestion | Updated: `ingest gate output findings` + `ingest filed markdown findings` |
| 10  | UC-04               | UC-04-approve-phase-gate.md | Step 5 said "continues the chain"                            | Updated: sets mode to paused, operator runs resume                        |
| 11  | UC-04               | UC-04-approve-phase-gate.md | Missing empty-commit approval scenario                       | Added FAGAN-0038 acceptance criterion                                     |
| 12  | UC-04               | UC-04-approve-phase-gate.md | Activity diagram missing paused/complete branching           | Updated flowchart with last-phase decision                                |
| 13  | system-use-cases.md | system-use-cases.md         | "approve … continue the chain" stale                         | Updated: approve → paused, operator runs resume                           |
| 14  | system-use-cases.md | system-use-cases.md         | Missing `--story` CLI flag                                   | Added `--story <ST-NNNN>` with FAGAN-0037 reference                       |
| 15  | architecture.dsl    | architecture.dsl            | FindingIngestor description didn't mention gate output       | Updated container description                                             |

## Architecture Diagrams

All 3 views re-rendered (PNG + SVG):

- SystemContext
- Containers
- CoreComponents

## Verification

- 291 tests pass, 1 skipped
- No code changes in this pass (spec-only + diagram re-render)
