---
id: ATAM-0007
source: atam-review
severity: high
category: defect
artifact: docs/adr/0029-per-story-drift-reports-block-the-wave-close.md#decision
status: resolved
resolution_summary: ADR-0029, section 6.12, the dispatch component, and QS-17 now state that close-wave records the closed wave and prepare-wave N refuses until wave N-1 is recorded closed, naming close-wave.
traces: [ADR-0029, QS-17, BR-062, DEC-28]
---

# A failing close-wave does not stop the next wave

**What is wrong:** QS-17 promises that "the next wave starts from a specification that matches the merged code". ADR-0029 and section 6.12 only make `dispatch close-wave` fail on an `open` row, or a `fixed` row on a core or seam artifact. Nothing ties the next wave to that result. Today `dispatch prepare-wave` blocks only on non-terminal stories of earlier waves (`packages/factory/scripts/dispatch`, `cmd_prepare_wave`, lines 907 to 921). It never reads the wave closeout. So take ST-0318 in wave 2 with an `open` row on `validation-rules.md`. `close-wave 2` fails, and `prepare-wave 3` still prepares and dispatches wave 3 against the old rule. A story built from the current architecture adds the row check to `close-wave` and leaves this path open. QS-17 stays unmet.

The response measure also overstates one case. A `rejected` row passes, because the code is wrong and a `BUG` finding replaces the row. Then the specification is right and the merged code is not.

**Fix:** State in ADR-0029, in section 6.12, in the `dispatch` row of section 5.4, and in the `dispatch close-wave` contract that `prepare-wave N+1` and `prepare-story` for a story of wave N+1 fail until wave N has a closeout record. Add a `prepare-wave` step to the `SpecFeedbackWaveClose` view or its key points. Reword the QS-17 response measure: the next wave starts only after every drift row on a core or seam artifact is `confirmed` or `rejected`, and each `rejected` row has a `BUG` finding. The requirements agent then adds a scenario for the refused `prepare-wave` to `core-artifact-ownership.feature`.
