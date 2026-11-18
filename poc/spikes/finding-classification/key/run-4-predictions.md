# Run 4 predictions, written before the run (2026-11-18)

Raters E1, E2, E3, and E4 rate ATAM-0002, ATAM-0003, and ATAM-0007 with
`run-4/rules/rules-4.md`. That file is `rules-3.md` plus one exposure
paragraph: a path shows a failure only when the scenario's own stimulus
starts it in the scenario's environment. A path that also needs an event the
scenario does not name, or an implementation choice the design leaves open,
gives `uncertain`. Row 2 of the draft calibration now says that a project
without a ranking uses the two levels of § 10.2.

The raters get the handoff's scenario list at each filing commit and may not
read the handoff itself.

My reading of the three findings under the rule:

- ATAM-0002: scenario 2 at 9bb3a27b890a5803a8caf5db3eadd19ca94ee26d names two
  members that reach their final states at the same moment. The finding
  traces that interleaving, so the exposure is `fails`.
- ATAM-0003: no scenario at 9bb3a27b890a5803a8caf5db3eadd19ca94ee26d names a
  write that runs while the Odate boundary passes. Scenario 7 names a
  publication after an Odate has opened. The traced paths need the boundary
  inside the write, which no scenario names, so the exposure is `uncertain`.
- ATAM-0007: scenario 4 at f6618162d917d8b6f0774afd238ab21c17698fcf names a
  publication that commits while the worker projects the Plan at the
  boundary tick. Case 2 of the finding is that path, so the exposure is
  `fails`. Case 1 needs an implementation choice and is `uncertain`, but
  case 2 decides.

Predictions:

- P8: all four raters give ATAM-0002 exposure `fails` and rate it a `major`
  risk. Any other exposure or category refutes P8.
- P9: all four raters give ATAM-0003 exposure `uncertain`. Any `fails`
  refutes P9.
- P10: all four raters give ATAM-0007 exposure `fails`, decided by case 2.
  Any `uncertain` refutes P10.
- P5 (row 1, from run 3): every rating with `exposure: uncertain` has category
  `question`, `severity: null`, and `blocking: false`. Any such rating with
  category `risk` refutes P5. If P9 fails on every rater, P5 is untested
  again.
- P7 (R2): all twelve ratings are in the architecture class.

Known weaknesses:

- I wrote the rule after reading these findings, and I derived P9 and P10
  from my own reading of the scenarios. A rater who reads scenario 7 as
  covering the boundary case refutes P9, and that counts against the rule as
  worded.
- All raters run on `claude-opus-5-5`.
