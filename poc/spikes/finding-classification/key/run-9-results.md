# Run 9 results (2026-11-18 and 2026-11-19)

Design f, the side-text rule, went to two Sonnet and two Codex raters per
batch, on the 28 document findings of run 8. The predictions are in
[run-9-predictions.md](run-9-predictions.md).

The Sonnet half ran on 2026-11-18. The first Codex attempt stopped before any
rating, because the Codex account hit its usage limit. The Codex half ran on
2026-11-19 with the same brief, rules, and blind copies.

| Prediction                                   | Result                                                                                         |
| -------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| P27: SPEC-0023 `minor`, `omission`           | Held, 4 of 4. In run 8, the models split: Sonnet `minor`, Codex `major`.                      |
| P28: SPEC-0024 `major`, `false`              | Held, 4 of 4. In run 8, three raters gave `minor`.                                            |
| P29: no other run-8 rating moves             | Refuted on two findings, SPEC-0011 and SPEC-0025. The rule reached findings it was not written for. |
| P30: severity and category agree on 28 of 28 | Refuted. 26 of 28.                                                                             |

## The two new splits

- **SPEC-0025**, a glossary link in `backlog/epics.md` that points the term
  Attempt to the Task Instance entity. Sonnet recorded `omission` and kept
  `minor`. Codex recorded `false` and gave `major`. The rule says that a side
  text that states something the main rule contradicts answers
  `fails_purpose`. The link states that an Attempt is a Task Instance, and the
  entity model contradicts that, so the rule as worded gives `major`. The
  Sonnet raters did not read a wrong link as a statement. The rule does not
  name links, so it needs a sentence on them.
- **SPEC-0011**, an unordered table of lifecycle checks in
  `validation-rules.md`. XA2 recorded `omission` and gave `minor`. The other
  three raters recorded `none` and gave `major`, as in run 8. The table is a
  main rule, not a side text that repeats one. One rater stretched the
  definition.

## What the run shows

- The rule decides the two findings it was written for, on both models.
- It also moves findings at its edge. A wrong link splits by model, and a main
  rule can be mistaken for a side text.
- Before it goes into the rulebook, the rule needs two more sentences: a link
  that points to the wrong target states something false, and a table or list
  that states the rule itself is not a side text. Both are untested.

## Audit

The Sonnet transcripts and the Codex logs show no read of gigacron's
`docs/findings/`, `docs/reviews/`, or `docs/handoff/`, of `key/`, of earlier
runs, or of another rater's output.
