# Run 9 predictions, written before the run (2026-11-18)

Run 9 tests design f: the stakeholder's decision on side texts. A side text
that leaves out a case of a correct main rule answers `raises_cost`; a side
text that states something false answers `fails_purpose`. Rules:
`run-9/rules/rules-f.md`. Same 28 findings and batches as run 8, two Sonnet
and two Codex raters per batch.

- P27: SPEC-0023 gives `minor` and `side_text: omission` from all four
  raters.
- P28: SPEC-0024 gives `major` and `side_text: false` from all four raters.
- P29: every other finding keeps its agreed run-8 severity and `in_use`.
- P30: severity and category agree on 28 of 28.

Weakness: the rule was written for these two findings. P29 is the test that
it does no harm elsewhere.

Written before dispatch. The run started later the same day, after a usage-limit pause; the predictions were not changed.
