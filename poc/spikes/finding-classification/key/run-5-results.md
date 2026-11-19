# Run 5 results (2026-11-18)

Twelve raters rated all 38 findings with `run-5/rules/rules-5.md`, the
rulebook with R1 and R2. Six ran on `claude-sonnet-5-5` (SA1 to SC2) and six
on `gpt-5.6-sol` through `codex exec` (XA1 to XC2). The predictions are in
[run-5-predictions.md](run-5-predictions.md).

## Agreement

| Field        | Sonnet pairs | Codex pairs | Sonnet against Codex, four pairings |
| ------------ | -----------: | ----------: | ----------------------------------- |
| Severity     |        37/38 |       37/38 | 32, 31, 31, 30 of 38                |
| Blocking     |        37/38 |       38/38 | 36, 36, 35, 35 of 38                |
| Category     |        38/38 |       38/38 | 36 of 38 in each pairing            |
| Review class |        38/38 |       38/38 | 38 of 38 in each pairing            |

| Prediction                                   | Result                                                                                                                                        |
| -------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| P11: within a model, at least 34 of 38       | Held for both models, 37 of 38 each.                                                                                                          |
| P12: across models, at least 34 of 38        | Refuted. All four pairings fall below, at 30 to 32.                                                                                           |
| P13: blocking agrees at the severity rate    | Refuted as worded. Blocking agrees more often than severity, because most splits fall between `major` and `critical`, and both block. |

## The splits

| Finding    | Sonnet                   | Codex                                    | Cause                                                                                                                                                                       | Blocking flips |
| ---------- | ------------------------ | ---------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------- |
| SPEC-0013  | `major`, both            | `critical`, both                         | `in_use`. Codex counts stories that defer to the stale todo item as encoding the statement. Sonnet does not.                                                              | No             |
| SPEC-0014  | `major`, both            | `critical`, both                         | `in_use`. Codex counts code that follows the other side of the contradiction as encoding the statement. Sonnet does not.                                                  | No             |
| SPEC-0015  | `major`, both            | `critical`, both                         | `in_use`, as SPEC-0014.                                                                                                                                                     | No             |
| RECON-0001 | `suggestion`/`note`, both | `defect`/`major`, both                  | `in_use` and `fails_purpose`. Codex counts the pending story ST-0003 as encoding the gate. Sonnet reads a correct Rule ahead of planned code.                            | Yes            |
| SPEC-0023  | `minor`, both            | `major`, both                            | `fails_purpose`. The rules leave open whether a summary that omits a case contradicts the full text.                                                                       | Yes            |
| ATAM-0006  | `risk`/`minor`, both     | `suggestion`/`note`, both                | No category fits a decision case. The finding was filed as a question, and no rater chose `question`.                                                                      | No             |
| FAGAN-0003 | `major`, both            | XC1 `major`, XC2 `critical`              | A fact. XC2 states that e2af4f3 was the tip of `dev` at filing. It is not on the first-parent line of `dev`, so it reached `dev` through a later merge. XC1 is right. | No             |
| SPEC-0017  | SB1 `major`, SB2 `minor` | `major`, both                            | `fails_purpose`. A duplicate scope ID that the context resolves.                                                                                                            | Yes, within Sonnet |

Each model splits with itself once, and the two models split with each
other on seven findings. On six of the seven, both raters of a model give
the same answer. So the cross-model splits are not noise. Each model reads
the rules its own way.

## What the run shows

- The rules give each model a stable answer, but not the same answer. This
  refutes the rulebook's claim for reviewers on different models.
- `in_use` for a document is the main cause. Four of the seven cross-model
  splits turn on it. R1 decided SPEC-0007 in run 2, but R1 does not say
  whether code that follows the other side of a contradiction, or a story
  that defers to the faulty text, encodes the statement. Run 2 tested a
  sentence for the first case, and it conflicted with another candidate
  sentence, so it was removed. These cases now split across models.
- Two findings flip blocking across models: RECON-0001 and SPEC-0023. RECON-0001 is in the
  report's open-gap table as a case that had not split yet. SPEC-0023 split
  for the first time.
- No rater filed a `question` for an unranked scenario. Sonnet set the
  importance from the scenario's theme, and Codex set it to `high`. For a
  scenario with exposure `fails`, the ranking changes nothing, so this did
  not change a severity. SC1 and SC2 rated ATAM-0006 with exposure
  `uncertain` and importance `medium`. Under the rules, that is a
  `question`, and ATAM-0006 was filed as one.

## Audit

The Sonnet transcripts and the Codex event logs show no read of
`docs/findings/`, `docs/reviews/`, `docs/handoff/`, `key/`, the earlier runs,
or another rater's output. The Codex logs sit in the session scratchpad.
