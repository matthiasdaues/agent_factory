# Run 3 results (2026-11-18)

Raters Q1 to Q4 rated ATAM-0002, ATAM-0003, and ATAM-0007 with
`run-3/rules/rules-3.md`. The predictions are in
[run-3-predictions.md](run-3-predictions.md).

All twelve ratings are the same: architecture class, `risk`, exposure
`fails`, `major`, blocking. Q1 to Q3 recorded the importance as `open`, and Q4
left it empty.

| Prediction | Result |
| ------------------------------------- | ---------------------------------------------------------------------------------------------- |
| P5: `uncertain` gives a `question` | Not tested. No rater gave `uncertain`. |
| P6: `fails` gives a `major` risk | Held, 12 of 12. Weak: row 2 follows from the matrix, and two raters read the handoff's rating. |
| P7: all ratings in architecture class | Held, 12 of 12. |

## What the run shows

- Row 1 is still untested. Across all runs, only C1 (run 1) and K1 (run 2)
  gave ATAM-0003 and ATAM-0007 exposure `uncertain`. Both used rules without
  R2. T1 and T2 in run 2 used R2 without the rows and gave `fails`. So the
  rows did not cause the shift to `fails`. These three findings cannot test
  row 1, because raters on R2 do not give them `uncertain`.
- The exposure of a traced race is open. Q3 named the conflict: the
  definition of `fails` covers a traced race, but the calibration example
  ATAM-0014 rates a shown path of unchecked frequency as `uncertain`. This is
  the open gap on ATAM-0003 and ATAM-0007 in the report. Row 1 can only be
  tested once that gap is closed, or on a finding whose exposure is clearly
  `uncertain`.
- Row 2 has a wording defect. Q1 and Q2 noted that "the project ranks
  on two levels" cannot be checked when a project ranks nothing. § 10.2 gives
  priority 1 or 2, so the row should say that a project without a ranking
  uses those two levels.
- All four raters found that ATAM-0007 bundles two cases: a gap in the port
  description and a traced race. The rules do not say how to rate a finding
  that bundles a document gap with an architecture risk.

## Leaks

Q1 and Q3 read the gigacron handoff
`docs/handoff/2026-10-16-folder-architecture.md` at commit
f6618162d917d8b6f0774afd238ab21c17698fcf. Its "Semantic review" section calls
ATAM-0007 a "new major finding". Q2 to Q4 read the same file at
9bb3a27b890a5803a8caf5db3eadd19ca94ee26d, where it calls ATAM-0002 to
ATAM-0005 defects. The brief allows the file, because it holds the quality
scenarios. A later run needs a copy of the handoff without its review
section, and a brief that forbids the original.

The tool calls show no read of `docs/findings/`, `docs/reviews/`, `key/`,
the earlier runs, or another rater's output.
