# Run 9 results, Sonnet half (2026-11-18)

Design f, the side-text rule, went to two Sonnet and two Codex raters per
batch, on the 28 document findings of run 8. The predictions are in
[run-9-predictions.md](run-9-predictions.md).

The four Codex raters stopped before they rated a finding. The Codex account
hit its usage limit, and each log ends with "You've hit your usage limit".
The Codex half has to run again after the limit resets. Until then, this run
tests the rule on one model only.

| Prediction                                     | Sonnet half                                                       |
| ---------------------------------------------- | ----------------------------------------------------------------- |
| P27: SPEC-0023 `minor`, `omission`             | Held, 2 of 2.                                                     |
| P28: SPEC-0024 `major`, `false`                | Held, 2 of 2. In run 8, both Sonnet raters gave it `minor`.       |
| P29: no other run-8 rating moves               | Held. The other 26 findings keep their run-8 rating and `in_use`. |
| P30: severity and category agree on 28 of 28   | Held within Sonnet, 28 of 28. Not tested across models.           |

Open points the raters named, none of which moved a rating:

- SPEC-0025, a wrong cross-link to an entity that exists, fits neither side
  case. Both Sonnet raters of batch B recorded `omission` and kept `minor`.
- Two raters asked whether state-machine pseudocode and todo items count as
  side texts. Both recorded `false`, which did not change a severity.

## Audit

The Sonnet transcripts show no read of gigacron's `docs/findings/`,
`docs/reviews/`, or `docs/handoff/`, of `key/`, of earlier runs, or of
another rater's output.
