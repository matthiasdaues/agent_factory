# Run 8 results (2026-11-18)

Design e, the case list of run 7 with corrected wording, went to two Sonnet
and two Codex raters per batch, on all 28 document findings. The predictions
are in [run-8-predictions.md](run-8-predictions.md).

| Measure                                          | Run 5, without the cases | Run 8, with the cases |
| ------------------------------------------------ | ------------------------ | --------------------- |
| `in_use`, four raters agree                      | 23 of 27                 | 28 of 28              |
| Severity and category, four raters agree         | 21 of 27                 | 26 of 28              |
| Positive control SPEC-0027 in use and `critical` | not in the run           | 4 of 4                |

Run 5 had 27 of these findings, all but SPEC-0027, with RECON-0001 in
another batch. Its counts cover those 27.

| Prediction                                 | Result                                                                                                      |
| ------------------------------------------ | ----------------------------------------------------------------------------------------------------------- |
| P22: `in_use` agrees on 28 of 28           | Held.                                                                                                       |
| P23: severity agrees except 0017 and 0023  | Refuted by SPEC-0024. SPEC-0017 now agrees, and SPEC-0023 still splits as expected.                        |
| P24: the control passes 4 of 4             | Held.                                                                                                       |
| P25: every other finding is not in use     | Held.                                                                                                       |
| P26: no agreed run-5 rating moves          | Refuted for SPEC-0024 by one rater: XB2 gives `major`, where all four raters of run 5 gave `minor`.      |

## What the run shows

P25 in the predictions says that all twelve raters of run 5 gave the 22 new
findings `in_use: false`. Each finding had four raters in run 5, not twelve.
The claim holds for those four.

- The case list decides `in_use` for every document finding of gigacron, on
  both models. The three findings that split on `in_use` in run 5
  (SPEC-0013, SPEC-0014, SPEC-0015) now agree at `major`, and RECON-0001
  agrees at `suggestion`/`note`.
- The cases did no harm on the 22 findings they were not written for. Every
  one of them keeps `in_use: false`.
- The two remaining splits are `fails_purpose` calls, not `in_use` calls.
  SPEC-0023 splits by model, as in run 5: Sonnet `minor`, Codex `major`.
  SPEC-0024 splits within Codex. The question in both is whether a reader
  who follows a faulty side text reaches a wrong result or only pays for a
  second look.

## Audit

The Codex logs and the Sonnet transcripts show no read of gigacron's
`docs/findings/`, `docs/reviews/`, or `docs/handoff/`, of `key/`, of earlier
runs, or of another rater's output.
