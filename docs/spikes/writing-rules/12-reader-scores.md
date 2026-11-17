# Reader scores: run lifecycle

The answer key is `06-reader-test.md`. Each reader answered the 40 questions from one version: K, M, or T. Every label other than `right` gives a reason.

## Scores per question

| Q   | K                                                                                        | M                                                                         | T                                                                          |
| --- | ---------------------------------------------------------------------------------------- | ------------------------------------------------------------------------- | -------------------------------------------------------------------------- |
| Q01 | right                                                                                    | right, conflict (reported L306 against L276 on the branch base)           | right                                                                      |
| Q02 | right                                                                                    | right                                                                     | right                                                                      |
| Q03 | right                                                                                    | right                                                                     | right                                                                      |
| Q04 | right                                                                                    | right                                                                     | right                                                                      |
| Q05 | right                                                                                    | right                                                                     | right                                                                      |
| Q06 | right                                                                                    | right                                                                     | right                                                                      |
| Q07 | right                                                                                    | missing: says "not in the text"; the key says refuse, not ask             | missing: says "not in the text"; the key says refuse, not ask              |
| Q08 | right                                                                                    | right                                                                     | right                                                                      |
| Q09 | right                                                                                    | right                                                                     | right                                                                      |
| Q10 | right                                                                                    | right                                                                     | right                                                                      |
| Q11 | right                                                                                    | right                                                                     | right                                                                      |
| Q12 | right                                                                                    | right                                                                     | right                                                                      |
| Q13 | right                                                                                    | right                                                                     | right                                                                      |
| Q14 | right                                                                                    | right                                                                     | right                                                                      |
| Q15 | right                                                                                    | right                                                                     | right                                                                      |
| Q16 | right                                                                                    | right                                                                     | right                                                                      |
| Q17 | right                                                                                    | right                                                                     | right                                                                      |
| Q18 | right                                                                                    | right                                                                     | right                                                                      |
| Q19 | right                                                                                    | right                                                                     | right                                                                      |
| Q20 | right                                                                                    | right                                                                     | right                                                                      |
| Q21 | right                                                                                    | right                                                                     | right                                                                      |
| Q22 | right                                                                                    | partial: omits "once", and that only ledger states count during the run   | right                                                                      |
| Q23 | right                                                                                    | right                                                                     | right                                                                      |
| Q24 | right                                                                                    | right, conflict (reported L102 against L83 on orchestrated `re-dispatch`) | right                                                                      |
| Q25 | right                                                                                    | right                                                                     | right                                                                      |
| Q26 | partial: omits findings whose `story` names a story of the run                           | partial: omits findings whose `story` names a story of the run            | partial: omits findings whose `story` names a story of the run             |
| Q27 | right                                                                                    | right                                                                     | right                                                                      |
| Q28 | right                                                                                    | partial: omits merged branches from what `close` removes                  | right                                                                      |
| Q29 | partial: omits nested ledgers and that `mode` is ignored                                 | partial: omits nested ledgers and that `mode` is ignored                  | partial: omits nested ledgers and that `mode` is ignored                   |
| Q30 | partial: says other code identifiers and error messages are not covered                  | right                                                                     | right                                                                      |
| Q31 | invented: answers "adds a gate"; the key says undecided                                  | open-right                                                                | open-right                                                                 |
| Q32 | right                                                                                    | right                                                                     | right                                                                      |
| Q33 | right                                                                                    | right                                                                     | right                                                                      |
| Q34 | right                                                                                    | right                                                                     | right                                                                      |
| Q35 | right                                                                                    | partial: names the stop before the merge; omits watching and undoing      | right                                                                      |
| Q36 | right                                                                                    | missing: says "not in the text"; the key says a second test run           | right                                                                      |
| Q37 | right                                                                                    | right                                                                     | right                                                                      |
| Q38 | open-right                                                                               | open-right                                                                | open-right                                                                 |
| Q39 | invented: "No such rule" reads as settled; stricter label, since the text leaves it open | open-right                                                                | open-right                                                                 |
| Q40 | open-right                                                                               | open-right                                                                | open-right, conflict (reported L194 against L336 on returns reaching Jira) |

## Totals

All 40 questions:

| Label          | K   | M   | T   |
| -------------- | --- | --- | --- |
| right          | 33  | 29  | 33  |
| partial        | 3   | 5   | 2   |
| wrong          | 0   | 0   | 0   |
| missing        | 0   | 2   | 1   |
| open-right     | 2   | 4   | 4   |
| invented       | 2   | 0   | 0   |
| conflict marks | 0   | 2   | 1   |

Builder questions (Q01–Q31):

| Label      | K   | M   | T   |
| ---------- | --- | --- | --- |
| right      | 27  | 25  | 27  |
| partial    | 3   | 4   | 2   |
| wrong      | 0   | 0   | 0   |
| missing    | 0   | 1   | 1   |
| open-right | 0   | 1   | 1   |
| invented   | 1   | 0   | 0   |

Approver questions (Q32–Q40):

| Label      | K   | M   | T   |
| ---------- | --- | --- | --- |
| right      | 6   | 4   | 6   |
| partial    | 0   | 1   | 0   |
| wrong      | 0   | 0   | 0   |
| missing    | 0   | 1   | 0   |
| open-right | 2   | 3   | 3   |
| invented   | 1   | 0   | 0   |

Override questions (Q04, Q05, Q06, Q07, Q10, Q17, Q18, Q22, Q33, Q37):

| Label   | K   | M   | T   |
| ------- | --- | --- | --- |
| right   | 10  | 8   | 9   |
| partial | 0   | 1   | 0   |
| missing | 0   | 1   | 1   |
| wrong   | 0   | 0   | 0   |

## Patterns

No version states an overridden decision, so no answer scores `wrong`. K fails on open questions. It gives a decided answer to Q31 and Q39, so its readers cannot tell what is still open. K also blurs the scope of the rename (Q30). M and T fail where a decision is a negative, not a step: neither says that the design avoids "ask" (Q07). M also drops cost and scope details (Q36, Q28, Q22), and it reports two conflicts in its own text. All three versions leave out the same builder details (Q26, Q29). T comes out cleanest.
