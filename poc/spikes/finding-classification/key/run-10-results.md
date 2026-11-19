# Run 10 results (2026-11-19)

Design g, the side-text rule of run 9 with two added sentences, went to two
Sonnet and two Codex raters per batch, on the 28 document findings. The
predictions are in [run-10-predictions.md](run-10-predictions.md).

| Prediction                                         | Result                                                                    |
| -------------------------------------------------- | ------------------------------------------------------------------------- |
| P31: SPEC-0025 `minor` from all four               | Held, 4 of 4. In run 9, the models split: Sonnet `minor`, Codex `major`. |
| P32: SPEC-0011 `major`, `side_text: none`          | Held, 4 of 4.                                                             |
| P33: SPEC-0023 `minor`, SPEC-0024 `major`          | Held, 4 of 4 each.                                                        |
| P34: no other run-9 rating moves                   | Held.                                                                     |
| P35: severity and category agree on 28 of 28       | Held, 28 of 28. `in_use` agrees on 28 of 28 as well.                     |

## Agreement over the runs on the document findings

| Run | Rules                                | Severity and category agree | `in_use` agrees |
| --- | ------------------------------------ | --------------------------- | --------------- |
| 5   | rulebook with R1 and R2              | 21 of 27                    | 23 of 27        |
| 8   | plus the named in-use cases (R3)     | 26 of 28                    | 28 of 28        |
| 10  | plus the side-text rule with links   | 28 of 28                    | 28 of 28        |

Run 5 did not include the invented control SPEC-0027.

## Limits

- Both sentences of design g were written for SPEC-0011 and SPEC-0025, and
  the side-text rule for SPEC-0023 and SPEC-0024. Run 10 shows that the rules
  decide these findings and move no other one. It does not show that they
  decide document findings of another project.
- The raters named open points that did not split a rating: whether
  spec-lint reads Gherkin syntax (SPEC-0007), whether a Fix that defers to
  the stakeholder makes a finding a question (SPEC-0003, SPEC-0010), and how
  to weigh a finding that mixes a wrong link with a false side text
  (SPEC-0022).
- The filing commit d58d289 of SPEC-0016 to SPEC-0026 already holds some of
  the fixes. The raters judged the finding text as filed. `in_use` came out
  false in every case, so the fixes did not change a rating.

## Audit

The Sonnet transcripts and the Codex logs show no read of gigacron's
`docs/findings/`, `docs/reviews/`, or `docs/handoff/`, of `key/`, of earlier
runs, or of another rater's output.
