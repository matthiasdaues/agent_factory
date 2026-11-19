# Run 7 predictions, written before the run (2026-11-18)

Run 7 tests design d: an ordered list of named cases for `in_use` of a
document, built from the stakeholder's four decisions after run 6:

1. A story that defers work to the text is not in use, also when it
   restates the content.
2. With a Fix that offers options, the statement is in use only when it is
   in use under every option.
3. Code that follows the other side of a contradiction is not in use, and
   gives no harm.
4. A correct Scenario whose implementing story is planned but not done is a
   `suggestion` with severity `note`.

The rules are `run-7/rules/rules-d.md`. The brief asks for a key
`in_use_case` with the name of the deciding case. The six findings and their
blind copies are those of run 6. Two raters on `claude-sonnet-5-5` (Sd1,
Sd2) and two on `gpt-5.6-sol` (Xd1, Xd2) rate them.

| Finding    | `in_use` | Case                     | Severity            |
| ---------- | -------- | ------------------------ | ------------------- |
| SPEC-0007  | false    | `syntax`                 | `major`             |
| SPEC-0027  | true     | `built`                  | `critical`          |
| SPEC-0013  | false    | `deferral`               | `major`             |
| SPEC-0014  | false    | `other-side` on option 1 | `major`             |
| SPEC-0015  | false    | `other-side` on option 1 | `major`             |
| RECON-0001 | false    | `none` or `open-story`   | `suggestion`/`note` |

Predictions:

- P18: the four raters agree on `in_use` for all six findings. Any split
  refutes P18.
- P19: the four raters agree on severity and category for all six findings.
  Any split refutes P19.
- P20: the agreed values match the table. A different agreed value counts
  against the wording of a case, not against alignment.
- P21: both controls pass, as in run 6.

Known weaknesses:

- I wrote the cases after reading these six findings and the raters' evidence
  from run 6. A pass shows that the cases decide these findings, not that
  they decide new ones. A later run needs findings that no case was written
  for.
- Two raters per model.
