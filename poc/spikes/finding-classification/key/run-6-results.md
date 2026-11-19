# Run 6 results (2026-11-18)

Three designs for "a story or code encodes the statement" went to two
Sonnet and two Codex raters each, on six findings. The predictions are in
[run-6-predictions.md](run-6-predictions.md).

`T`/`F` is `in_use`, `h` marks `harms_downstream: true`.

| Finding    | Design a (same text)                | Design b (rework)                   | Design c (quote pair)               |
| ---------- | ----------------------------------- | ----------------------------------- | ----------------------------------- |
| SPEC-0007  | all `F`, `major`                    | all `F`, `major`                    | all `F`, `major`                    |
| SPEC-0027  | all `Th`, `critical`                | all `Th`, `critical`                | all `Th`, `critical`                |
| SPEC-0013  | Sonnet `F`, Codex `Th`              | Sonnet `F`, Codex `Th`              | Sc1 `F`, the other three `Th`       |
| SPEC-0014  | Sa1 `T`, Sa2 `Th`, Xa1 `F`, Xa2 `Th` | Sb1 `F`, the other three `Th`       | all `F`, `major`                    |
| SPEC-0015  | all `T`; Sa1 without `h`            | Sb1 `F`, the other three `Th`       | Sonnet `F`, Xc1 `T`, Xc2 `Th`       |
| RECON-0001 | Sonnet `note`, Codex `major`        | Sonnet `note`, Codex `major`        | `note`, `minor`, `major`, `major`   |

| Prediction                           | Result                                                                                  |
| ------------------------------------ | --------------------------------------------------------------------------------------- |
| P14: four raters agree on `in_use`   | Refuted for all three designs. Each splits on at least three of the six findings.       |
| P15: values match my reading         | Refuted in part. Design b gave SPEC-0013 `in_use: true` from Codex, which I had not read into it. |
| P16: both controls pass              | Held for all three designs, 12 of 12 each.                                              |
| P17: severity aligns on 0013 to 0015 | Refuted for all three designs. Design c aligned SPEC-0014 only.                          |

## What the run shows

No wording of the principle aligns the models. Each design moved a split,
but none removed it. The raters' evidence shows four separate questions
under the one word "encodes":

1. **A story line that defers work and restates the faulty content.**
   `ST-0003B-details.md:82` says "Unique configuration per Domain among
   current versions (`config_hash`) | Deferred". Codex counts it as encoding
   T-0052, because it restates the obsolete model. Sonnet mostly does not,
   because it only defers. Every design leaves both readings open.
2. **A Fix with options.** SPEC-0014 and SPEC-0015 offer two targets. A rater
   who checks every option finds one that the code follows; a rater who
   checks the finding's own wrong side does not.
3. **Code that follows the other side of a contradiction.** Several raters
   set `in_use: true` and then split on `harms_downstream`. The rules do not
   say whether that code is harm.
4. **A correct Scenario whose story is still pending.** RECON-0001 splits on
   category as well: Sonnet files a `suggestion`, Codex a `defect`. This is
   not an `in_use` question.

Each question asks for a policy, not a reading. The stakeholder decides
what counts, and the rule then names each case.

## Audit

The Codex logs and the Sonnet transcripts show no read of a rating. Three
Sonnet raters reported that a grep printed a file name or a line from
gigacron's `docs/findings/` or `docs/reviews/`. The transcripts show no line
with a severity or category from those files.
