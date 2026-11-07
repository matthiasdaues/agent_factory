---
id: 0034
status: accepted
evaluation: pugh-matrix
---

# One register file per minor finding

## Context

A `minor` finding never blocks, but it must stay on record until someone
fixes it. The accepted proposal
[finding-classification.md](../proposals/finding-classification.md) first kept
these findings as lines in one JSONL register per review class, such as
`docs/findings/register/document.jsonl`. A line had no status. The fix deleted
the line, and a `merge=union` line in `.gitattributes` was to merge the
registers of two branches.

Take two branches. On branch one, a fix deletes the line of RECON-0027. On
branch two, a review appends the line of a new finding. A test of
`git merge-file --union` on git 2.34.1 showed that the deleted line comes
back in the merge. So a fixed finding returns to the register, and nothing
reports it. The test also showed a second gap: neither `init-factory` nor
`update-factory` writes `.gitattributes`, and this repository's own
`.gitattributes` lacks the line. So no project had the union merge that the
design needed.

Three options were weighed:

- **A, keep the deletion.** A register line has no status, and the fix
  deletes it. This is the baseline.
- **B, append status lines.** The fix appends a second line with the same ID
  and `status: resolved`, and the last status of an ID wins.
- **C, one file per finding.** Each `minor` finding is one JSON file
  `docs/findings/register/<class>/<ID>.json` with a `status` field. The fix
  changes the status, and the file stays.

## Decision

Each `minor` finding is one register file
`docs/findings/register/<class>/<ID>.json`, option C (DEC-60). The folder of
a class is its register. The status is `open`, `resolved`, or `waived`. The
reviewer agent writes `open`, and the commit that fixes the finding sets
`resolved`. Only the stakeholder sets `waived`, with `override_by` and
`override_reason`, when nobody will fix the finding (DEC-63). The design has
no union merge and no `.gitattributes` line.

The stakeholder chose from the totals A 0, B −2, and C +2. The rows below
break the totals down by criterion.

| Criterion                                                              | Weight | A: deletion (baseline) | B: status lines | C: one file |
| ---------------------------------------------------------------------- | ------ | ---------------------- | --------------- | ----------- |
| Merge safety: a fixed finding does not come back after a merge         | 3      | 0                      | +1              | +1          |
| Simplicity: no merge driver and no `.gitattributes` writer             | 2      | 0                      | 0               | +1          |
| Deterministic validation (QS-6): `schema-validate` checks a whole file | 1      | 0                      | −1              | +1          |
| One read gives the current status of a finding                         | 2      | 0                      | −1              | 0           |
| A reader sees the register of a class as one file                      | 2      | 0                      | 0               | −1          |
| Specification churn: decisions, rules, and Scenarios that change       | 2      | 0                      | −1              | −1          |
| **Weighted total**                                                     |        | **0**                  | **−2**          | **+2**      |

The result is close. With specification churn at weight 4, C ties A at 0.
So C wins only while the churn, a one-time cost, weighs less than the lasting
fault of a fixed finding that comes back. The stakeholder chose C.

C keeps parallel work apart. Two reviews on two branches add two new paths,
and two fixes change two different files, so git merges them without a
conflict. `finding-lint` runs `schema-validate` on each register file with
the schema of its class, `finding-register-<class>.schema.json` in
`packages/factory/rulebooks/schemas/`. A lowering by the stakeholder and the
rule that an ID names one file only become checks between two file paths.

## Consequences

- The proposal replaces DEC-33 and the register parts of DEC-49. BR-090 and
  BR-110 hold the new rules. The gap of the missing `.gitattributes` writer
  closes, because no project needs the line.
- A register file that `HEAD` holds is removed only when a finding file with
  the same ID replaces it, which is the raise of a `minor` finding.
  `finding-lint` rejects any other removal and names the ID.
- `guard-human-fields` guards `docs/findings/register/**/*.json` as well as
  the finding files ([ADR-0035](0035-guard-human-fields-in-every-cli.md)).
- The migration moves each line of the three old `.jsonl` registers into one
  register file under the same ID, with `status: open`, and removes the three
  files. 25 lines exist on 2026-11-07.
- `docs/findings/` gains one file per `minor` finding. The loop grep for
  `status: open` reads only `docs/findings/*.md`, so register files never
  enter the review loop.
- `next-id --plan-seed` of counter-ids-fitting counts the `id` field of each
  `.jsonl` line (BR-099). It must count the file names of the register files
  instead, or it misses every `minor` ID. The counter-ids-fitting stories,
  such as ST-0376, are done. So the finding-classification backlog plans the
  change as a cross-feature story that lands before the migration commit.
- [5.12](../arc42/05_building_block_view.md#512-level-2-component-view----finding-classification)
  lists the components, and QS-26 in
  [chapter 10](../arc42/10_quality_requirements.md#qs-26-parallel-reviews-merge-their-registers-without-loss)
  sets the measure.
