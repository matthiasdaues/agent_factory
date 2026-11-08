# Agreement check of the finding classification, 2026-11-07

## Result

The check failed. New rules: 18 of 20 findings agree. Old rules: 20 of 20 agree. The new count reaches 16 but does not exceed the old count, so the check does not pass.

The old runs agreed on every finding because they rate nearly all of them `major`. That is agreement without discrimination: the old rules separate the findings less, and they agree more. The two runs that disagree under the new rules differ on SPEC-0012 and BUG-0006, where one run rated `major` and the other `minor`.

## Method

- Model: `opus`, the strong tier that the review agents use (`tier: strong` in `packages/factory/agents/qa-agent.md` and the other review agents).
- Four runs, each a fresh subagent session. Two used `packages/factory/rulebooks/conventions/finding-classification.md`. Two used `report-format.md` as `git show 74e036f1:packages/factory/rulebooks/conventions/report-format.md` gives it.
- Each run read one file: the rules under test and the 20 texts. The orchestrator did not hand the conversation, the proposal, or any other file to a run.
- Each text keeps the title, what is wrong, and how it was fixed. The IDs were replaced by labels F01 to F20, in a shuffled order. Each label carries its review class, because the new rulebook has one rule per class.
- A `question` counts as disagreement. No run gave one.
- Differences from the proposal: the runs read their prompt from one file instead of receiving it inline, and the class label was given to the old runs as well. `report-format.md` at `74e036f1` differs by one line from its state just before ST-0386 (`2e4cd6fb`).

## Quotas and picks

The quotas are 6 document, 5 code, 4 runtime, 2 architecture, and 3 security. Each class took the lowest-numbered closed findings of `docs/findings/` that are not migrated to the register, have a "What is wrong" and a fix or resolution text, and are named in neither the rulebook, the proposal, nor the feature file. The security picks are the three fixed by the proposal.

| Class        | Picks                                                            |
| ------------ | ---------------------------------------------------------------- |
| document     | SPEC-0012, SPEC-0013, SPEC-0014, SPEC-0015, SPEC-0016, SPEC-0017 |
| code         | FAGAN-0006, FAGAN-0007, FAGAN-0008, FAGAN-0009, FAGAN-0010       |
| runtime      | BUG-0003, BUG-0004, BUG-0005, BUG-0006                           |
| architecture | ATAM-0003, ATAM-0005                                             |
| security     | FAGAN-0021, SEC-0005, SEC-0006                                   |

BUG-0035, BUG-0054, BUG-0058, BUG-0063, BUG-0073, and BUG-0081 are runtime calibration examples of the rulebook and were left out.

## Severity per finding

| Finding    | Class        | New run 1 | New run 2 | New agree | Old run 1 | Old run 2 | Old agree |
| ---------- | ------------ | --------- | --------- | --------- | --------- | --------- | --------- |
| ATAM-0003  | architecture | major     | major     | yes       | critical  | critical  | yes       |
| ATAM-0005  | architecture | major     | major     | yes       | major     | major     | yes       |
| BUG-0003   | runtime      | major     | major     | yes       | major     | major     | yes       |
| BUG-0004   | runtime      | major     | major     | yes       | major     | major     | yes       |
| BUG-0005   | runtime      | major     | major     | yes       | critical  | critical  | yes       |
| BUG-0006   | runtime      | major     | minor     | no        | major     | major     | yes       |
| FAGAN-0006 | code         | major     | major     | yes       | major     | major     | yes       |
| FAGAN-0007 | code         | major     | major     | yes       | major     | major     | yes       |
| FAGAN-0008 | code         | major     | major     | yes       | major     | major     | yes       |
| FAGAN-0009 | code         | major     | major     | yes       | major     | major     | yes       |
| FAGAN-0010 | code         | major     | major     | yes       | major     | major     | yes       |
| FAGAN-0021 | security     | major     | major     | yes       | critical  | critical  | yes       |
| SEC-0005   | security     | note      | note      | yes       | minor     | minor     | yes       |
| SEC-0006   | security     | minor     | minor     | yes       | minor     | minor     | yes       |
| SPEC-0012  | document     | major     | minor     | no        | major     | major     | yes       |
| SPEC-0013  | document     | major     | major     | yes       | major     | major     | yes       |
| SPEC-0014  | document     | major     | major     | yes       | major     | major     | yes       |
| SPEC-0015  | document     | major     | major     | yes       | major     | major     | yes       |
| SPEC-0016  | document     | major     | major     | yes       | major     | major     | yes       |
| SPEC-0017  | document     | major     | major     | yes       | major     | major     | yes       |

## Counts

- New rules: 18 of 20 agree.
- Old rules: 20 of 20 agree.
- Passed: no. The pass condition is at least 16 and above the old count.

The story changes no rulebook to pass the check. The stakeholder decides the next step.
