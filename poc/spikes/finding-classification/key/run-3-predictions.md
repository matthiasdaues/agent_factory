# Run 3 predictions, written before the run (2026-11-18)

Raters Q1, Q2, Q3, and Q4 rate ATAM-0002, ATAM-0003, and ATAM-0007 with
`run-3/rules/rules-3.md`. That file is the current rulebook plus R1, R2, and
the two draft calibration rows for a scenario without a priority. All four
raters use the same file. Run 2 already holds a control without the rows:
K1 and K2 never filed a `question` for these findings.

- P5 (row 1): every rating in the architecture class with
  `exposure: uncertain` has category `question`, `severity: null`, and
  `blocking: false`. Any such rating with category `risk` refutes P5.
- P6 (row 2): every rating in the architecture class with `exposure: fails`
  has category `risk` and severity `major`. Any such rating that is a
  `question`, or has another severity, refutes P6.
- P7 (R2 repeat): all twelve ratings are in the architecture class. Any
  document-class rating refutes P7.
- Vacuity: if no rater gives `exposure: uncertain`, P5 is not tested, and the
  run says nothing about row 1. The same holds for P6 and `exposure: fails`.

Known weakness: I drafted the rows with these findings in view. The rows name
a cache decision, not a lock, so a rater cannot match them by wording.
