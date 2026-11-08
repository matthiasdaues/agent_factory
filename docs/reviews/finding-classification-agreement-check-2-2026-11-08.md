# Agreement check 2 of the finding classification, 2026-11-08

## Result

The check passed. New rules: 20 of 20 findings agree. Old rules: 19 of 20 agree. The new count reaches 16 and exceeds the old count.

The margin is one finding. The first check on 2026-11-07 gave 18 of 20 under the new rules and 20 of 20 under the old rules, and it failed.

## Why the first runs split

The first runs returned table rows and no reasons, so this section names the reading each run most plausibly took. It is an inference from the two findings and the rows of the rulebook.

- **SPEC-0012, document, `major` against `minor`.** Six `@` references of a feature file named paths from before a rename. The `major` run most plausibly answered yes to `fails_purpose`, because reconciliation would report false broken references. The `minor` run most plausibly answered no, because the `fails_purpose` row spoke of a planner or implementer who cannot act, and a reader can still act on an old path.
- **BUG-0006, runtime, `major` against `minor`.** Two capture paths recorded one model under two identifiers, so grouping by `model` split the spend. The `major` run most plausibly read that as a wrong result. The `minor` run most plausibly read it as an observability gap, because each record names the right model on its own.

## The sharpened text

The rulebook commit `86d239bd` precedes the first run, and it changes only the rows of `Class: document` and `Class: runtime`. It adds no calibration example.

| Class    | Row             | Added text                                                                                                                                                                                                  |
| -------- | --------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| document | `fails_purpose` | Deciding question: does a person or tool that follows the statement as written reach a wrong result or report a false one? A "yes" answers `fails_purpose`, also when a later check would catch it.         |
| document | `raises_cost`   | The reader can act "and reaches the right result", but only after a second reading.                                                                                                                         |
| runtime  | `fails_purpose` | Deciding question: does a consumer that uses the output as its contract states get a false value or draw a false conclusion, also when each single record looks plausible? A "yes" answers `fails_purpose`. |
| runtime  | `raises_cost`   | The output that the path exists to produce stays correct.                                                                                                                                                   |

## Method

- Model: `opus`, the tier of the first check.
- Four runs, each a fresh subagent session. Two used the rulebook at `86d239bd`. Two used `report-format.md` at `74e036f1`.
- Each run read one file that held the rules under test and the 20 texts. The wording of the prompt is that of the first check.
- Each text keeps the title, what is wrong, and how it was fixed. The IDs were replaced by labels F01 to F20, in a shuffled order. Each label carries its review class.
- A `question` counts as disagreement. No run gave one.

## Quotas and picks

The quotas are 8 document, 5 code, 5 runtime, 2 architecture, and 0 security. This deviates from DEC-39, which names 6, 5, 4, 2, and 3: no fresh security finding is eligible, so the stakeholder gave its three slots to the document and runtime classes, which the sharpening targets.

Each class took the lowest-numbered closed findings of `docs/findings/` that have a "What is wrong" and a fix text. Left out were the first report's 20 picks, every ID that the rulebook, the proposal, or the feature file names, and every file of the migration.

| Class        | Picks                                                                                  |
| ------------ | -------------------------------------------------------------------------------------- |
| document     | SPEC-0018, SPEC-0019, SPEC-0020, SPEC-0021, SPEC-0022, SPEC-0023, SPEC-0024, SPEC-0025 |
| code         | FAGAN-0011, FAGAN-0012, FAGAN-0013, FAGAN-0014, FAGAN-0015                             |
| runtime      | BUG-0007, BUG-0009, BUG-0010, BUG-0011, BUG-0012                                       |
| architecture | ATAM-0006, ATAM-0007                                                                   |

## Severity per finding

| Finding    | Class        | New run 1 | New run 2 | New agree | Old run 1 | Old run 2 | Old agree |
| ---------- | ------------ | --------- | --------- | --------- | --------- | --------- | --------- |
| ATAM-0006  | architecture | major     | major     | yes       | major     | major     | yes       |
| ATAM-0007  | architecture | major     | major     | yes       | major     | major     | yes       |
| BUG-0007   | runtime      | critical  | critical  | yes       | critical  | critical  | yes       |
| BUG-0009   | runtime      | major     | major     | yes       | major     | major     | yes       |
| BUG-0010   | runtime      | major     | major     | yes       | major     | major     | yes       |
| BUG-0011   | runtime      | major     | major     | yes       | critical  | critical  | yes       |
| BUG-0012   | runtime      | major     | major     | yes       | major     | major     | yes       |
| FAGAN-0011 | code         | major     | major     | yes       | major     | major     | yes       |
| FAGAN-0012 | code         | major     | major     | yes       | major     | major     | yes       |
| FAGAN-0013 | code         | major     | major     | yes       | minor     | minor     | yes       |
| FAGAN-0014 | code         | minor     | minor     | yes       | major     | major     | yes       |
| FAGAN-0015 | code         | minor     | minor     | yes       | minor     | minor     | yes       |
| SPEC-0018  | document     | major     | major     | yes       | major     | major     | yes       |
| SPEC-0019  | document     | major     | major     | yes       | major     | major     | yes       |
| SPEC-0020  | document     | major     | major     | yes       | critical  | major     | no        |
| SPEC-0021  | document     | major     | major     | yes       | minor     | minor     | yes       |
| SPEC-0022  | document     | major     | major     | yes       | major     | major     | yes       |
| SPEC-0023  | document     | minor     | minor     | yes       | minor     | minor     | yes       |
| SPEC-0024  | document     | major     | major     | yes       | major     | major     | yes       |
| SPEC-0025  | document     | major     | major     | yes       | major     | major     | yes       |

## Counts

|                   | New rules | Old rules | Passed |
| ----------------- | --------- | --------- | ------ |
| First, 2026-11-07 | 18 of 20  | 20 of 20  | no     |
| Second, this one  | 20 of 20  | 19 of 20  | yes    |

The pass condition is at least 16 and above the old count.

Distribution of the second check: the new runs gave 1 `critical`, 16 `major`, and 3 `minor`. The old runs gave 3 and 2 `critical`, 13 and 14 `major`, and 4 and 4 `minor`.

## Limits of this result

- Both runs of each rule set use one model, so the check measures how stable the rules are under that model and not between reviewers.
- A difference of one finding is small. The result supports the sharpened rules and does not prove that they agree better in general.
- The first report's split findings are not measured again, as the story requires.
