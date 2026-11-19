# Run 7 results (2026-11-18)

Design d, an ordered list of named cases for `in_use` of a document, went to
two Sonnet raters (Sd1, Sd2) and two Codex raters (Xd1, Xd2). The predictions
are in [run-7-predictions.md](run-7-predictions.md).

| Finding    | Sd1                      | Sd2                     | Xd1                     | Xd2                     |
| ---------- | ------------------------ | ----------------------- | ----------------------- | ----------------------- |
| SPEC-0007  | `F`, `major`, syntax     | `F`, `major`, syntax    | `F`, `major`, syntax    | `F`, `major`, syntax    |
| SPEC-0027  | `F`, `major`, other-side | `T`, `critical`, built  | `T`, `critical`, built  | `T`, `critical`, built  |
| SPEC-0013  | `F`, `major`, deferral   | `F`, `major`, deferral  | `F`, `major`, other-side | `F`, `major`, deferral |
| SPEC-0014  | `F`, `major`, built and other-side, in each rating |  |  |  |
| SPEC-0015  | `F`, `major`, built and other-side, in each rating |  |  |  |
| RECON-0001 | `suggestion`/`note`, open-story | `suggestion`/`note`, open-story | `suggestion`/`note`, deferral | `suggestion`/`note`, deferral |

| Prediction                         | Result                                                                    |
| ---------------------------------- | ------------------------------------------------------------------------- |
| P18: agreement on `in_use`         | Refuted by one rating: Sd1 on SPEC-0027. The other five findings agree.   |
| P19: agreement on severity, category | Refuted by the same rating. The other five findings agree.             |
| P20: agreed values match the table | Held for the five findings that agree.                                    |
| P21: both controls pass            | SPEC-0007 4 of 4. SPEC-0027 3 of 4.                                       |

## What the run shows

- The case list aligns the four findings that split across models in run 5.
  On SPEC-0013, SPEC-0014, SPEC-0015, and RECON-0001, both models give the
  same `in_use`, severity, and category.
- The miss is a wording defect. Case `built` says "does what the changed text
  says". Sd1 read "the changed text" as the text after the Fix and found the
  code on the other side of it. The case means the text as it stands, which
  the Fix replaces. Run 6 design a avoided this with "says now".
- The case names differ where two cases lead to the same answer: SPEC-0013
  `deferral` or `other-side`, RECON-0001 `open-story` or `deferral`. The
  `in_use` value does not depend on the choice.
- Both Sonnet raters asked how to record a Fix whose options give different
  cases. All four raters wrote one name per option, as the brief says.

The cases were written after reading these six findings, so the run shows
that they decide these six. It does not show that they decide new findings.
