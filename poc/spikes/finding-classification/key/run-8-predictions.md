# Run 8 predictions, written before the run (2026-11-18)

Run 8 tests design e: the case list of run 7, with "the changed text"
replaced by "the text that the Fix replaces, as that text stands now". The
rules are `run-8/rules/rules-e.md`.

The set is every document finding of gigacron: SPEC-0001 to SPEC-0026,
RECON-0001, and the invented control SPEC-0027, so 28 findings. 22 of them
were not part of runs 6 and 7, and the cases were not written for them.

Batch A is SPEC-0001 to SPEC-0013 and SPEC-0027. Batch B is SPEC-0014 to
SPEC-0026 and RECON-0001. Each batch goes to two raters on
`claude-sonnet-5-5` and two on `gpt-5.6-sol`.

The baseline is run 5, on the rulebook with R1 and R2 but without the cases.

Predictions:

- P22: within each batch, the four raters agree on `in_use` for every
  finding, 28 of 28. Any split refutes P22.
- P23: the four raters agree on severity for every finding except SPEC-0017
  and SPEC-0023, which split on `fails_purpose` in run 5. Any other split
  refutes P23.
- P24: SPEC-0027 gives `in_use: true` and `critical` from all four raters of
  batch A.
- P25: every other finding gives `in_use: false`. In run 5, all 22 new
  findings gave `false` from all twelve raters.
- P26: the cases do not move an agreed run-5 rating. For each of the 22 new
  findings, the agreed severity of run 5 stays. A changed value refutes P26
  for that finding.

Known weaknesses:

- P25 and P26 test that the cases do no harm. They cannot show that the cases
  decide a new hard case, because the new findings were easy for `in_use` in
  run 5.
- Two raters per model and batch.
