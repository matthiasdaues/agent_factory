# Reader scores: versions R and S

Each answer is scored against the key in `06-reader-test.md`. A label other than `right` carries a reason of at most 15 words.

## Scores per question

| Q   | R                                                                                                         | S                                                                                               |
| --- | --------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| Q01 | right                                                                                                     | right                                                                                           |
| Q02 | right                                                                                                     | right                                                                                           |
| Q03 | right                                                                                                     | right                                                                                           |
| Q04 | right                                                                                                     | right                                                                                           |
| Q05 | right                                                                                                     | right                                                                                           |
| Q06 | partial: adds an open dev-merge refusal, which blurs "only these two"                                     | right                                                                                           |
| Q07 | missing: says "not in the text"; the key decides no "ask"                                                 | right                                                                                           |
| Q08 | right                                                                                                     | right                                                                                           |
| Q09 | right                                                                                                     | right                                                                                           |
| Q10 | right                                                                                                     | right                                                                                           |
| Q11 | right                                                                                                     | right                                                                                           |
| Q12 | right                                                                                                     | right                                                                                           |
| Q13 | partial: names a ledger record, not the `close-wave 1` command a builder needs                            | right                                                                                           |
| Q14 | right                                                                                                     | right                                                                                           |
| Q15 | right                                                                                                     | right                                                                                           |
| Q16 | partial, conflict: no for coverage, but the mutation-testing stored result contradicts "each gate reruns" | partial: no for coverage, but the mutation-testing stored result contradicts "each gate reruns" |
| Q17 | right                                                                                                     | right                                                                                           |
| Q18 | right                                                                                                     | right                                                                                           |
| Q19 | right                                                                                                     | right                                                                                           |
| Q20 | right                                                                                                     | right                                                                                           |
| Q21 | right                                                                                                     | right                                                                                           |
| Q22 | right                                                                                                     | right                                                                                           |
| Q23 | right                                                                                                     | partial: leaves open whether `done` and `pending` pass `dispatch close`                         |
| Q24 | right                                                                                                     | right                                                                                           |
| Q25 | right                                                                                                     | right                                                                                           |
| Q26 | right                                                                                                     | partial: omits findings counted through their `story` field                                     |
| Q27 | right                                                                                                     | right                                                                                           |
| Q28 | right                                                                                                     | right, conflict: two homes for stored gate results                                              |
| Q29 | partial: omits nested ledgers and that `--orphans` ignores `mode`                                         | partial: omits nested ledgers and that `--orphans` ignores `mode`                               |
| Q30 | right                                                                                                     | right                                                                                           |
| Q31 | open-right                                                                                                | open-right                                                                                      |
| Q32 | right                                                                                                     | right                                                                                           |
| Q33 | right                                                                                                     | right                                                                                           |
| Q34 | right                                                                                                     | right                                                                                           |
| Q35 | right                                                                                                     | right                                                                                           |
| Q36 | missing: says "not in the text"; the key states a second test run per story                               | missing: says "not in the text"; the key states a second test run per story                     |
| Q37 | right                                                                                                     | right                                                                                           |
| Q38 | open-right                                                                                                | open-right                                                                                      |
| Q39 | open-right                                                                                                | open-right                                                                                      |
| Q40 | open-right                                                                                                | open-right                                                                                      |

## Totals

| Label             | R   | S   |
| ----------------- | --- | --- |
| right             | 30  | 31  |
| partial           | 4   | 4   |
| wrong             | 0   | 0   |
| missing           | 2   | 1   |
| open-right        | 4   | 4   |
| invented          | 0   | 0   |
| conflict (marker) | 1   | 1   |

## Patterns

Neither reader stated anything false, and neither invented an answer to an open question. Both readers found all four open questions open. Both missed the cost of the gate rerun (Q36), so neither version states that cost. Both readers repeated a mutation-testing exception that blurs the fresh-rerun rule (Q16). R lost points where the text left a mechanism unstated (Q07, Q13). S lost points where the text left out a pass rule or a second route (Q23, Q26). The two versions perform about the same.
