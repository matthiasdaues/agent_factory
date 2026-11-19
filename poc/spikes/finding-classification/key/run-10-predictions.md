# Run 10 predictions, written before the run (2026-11-19)

Run 10 tests design g: the side-text rule of run 9 plus two sentences from
the stakeholder's decisions after run 9.

1. A link or cross-reference that points to the wrong target answers
   `raises_cost`.
2. A table or list that states the rule itself is a main rule, not a side
   text.

The rules are `run-10/rules/rules-g.md`. The 28 findings, batches, brief, and
blind copies are those of run 9. Each batch goes to two raters on
`claude-sonnet-5-5` and two on `gpt-5.6-sol`.

Predictions:

- P31: SPEC-0025 gives `minor` from all four raters of batch B.
- P32: SPEC-0011 gives `major` from all four raters of batch A, with
  `side_text: none`.
- P33: SPEC-0023 stays `minor` and SPEC-0024 stays `major` from all four
  raters, as in run 9.
- P34: every other finding keeps its agreed run-9 rating and `in_use`.
- P35: severity and category agree on 28 of 28.

Known weaknesses:

- SPEC-0025 has a second defect besides the link: a table row for the
  Dispatch Engine that replaced the Agent Gateway row. A rater who reads that
  row as a false statement can still give `major`, which refutes P31.
- Both sentences were written for SPEC-0011 and SPEC-0025.
