# Run 5 predictions, written before the run (2026-11-18)

Run 5 tests the rulebook's claim across models: two reviewers who record the
same facts give a finding the same severity. All 38 findings are rebuilt from
the filed text with `build-blind.py`, so ATAM-0006, ATAM-0009, and FAGAN-0003
are valid this time. The rules are the rulebook with R1 and R2
(`run-5/rules/rules-5.md`).

Three batches, as in run 1: A is SPEC-0001 to SPEC-0013, B is SPEC-0014 to
SPEC-0026, and C is ATAM-0002 to ATAM-0009, FAGAN-0001 to FAGAN-0003, and
RECON-0001. Each batch goes to four raters:

- two on `claude-sonnet-5-5` (SA1, SA2, SB1, SB2, SC1, SC2), as Claude Code
  subagents;
- two on `gpt-5.6-sol` (XA1, XA2, XB1, XB2, XC1, XC2), through `codex exec`
  with the project instructions switched off.

Run 1 on `claude-opus-5-5` gave 35 of 35 within-pair severity agreement,
under the rules before R1 and R2.

Predictions:

- P11: within each model, the two raters of a batch agree on severity in at
  least 34 of the 38 findings (90 %). A model below that refutes P11 for
  that model.
- P12: across models, a Sonnet rater and a Codex rater of the same batch
  agree on severity in at least 34 of 38 findings, for each of the four
  cross-model pairings. A pairing below that refutes P12.
- P13: the blocking value agrees at the same rate as severity, in P11 and in
  P12.

A refuted P12 with P11 holding means that the rules give each model a stable
answer, but not the same answer. That would refute the rulebook's claim for
reviewers on different models.

Known weaknesses:

- The thresholds are my choice. They are not derived from any standard.
- Codex runs without the Claude Code harness, so a difference can come from
  the harness as well as from the model.
