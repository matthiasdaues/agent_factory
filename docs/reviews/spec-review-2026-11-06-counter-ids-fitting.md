---
type: inspect-spec
title: Spec review of counter-ids-fitting, pass 1
date: 2026-11-06
status: defects
reviewer: spec-review-agent
findings_filed: 12
story: counter-ids-fitting
scope: The counter-ids-fitting specification at commit 38eba9ce28d006a1bf87b53d427757699c574ee9 on dev, read against the accepted proposal docs/proposals/counter-ids-fitting.md (DEC-01 to DEC-13)
---

# Spec review of counter-ids-fitting, pass 1

The specification of counter-ids-fitting is complete in its Rules and follows the proposal closely. Two major findings block the next step. Ten minor findings go to the register, and seven notes stay in this report.

The review applies the accepted proposal [finding-classification.md](../proposals/finding-classification.md) already, as the stakeholder decided. So a `major` finding is a file in `docs/findings/`, a `minor` finding is a line in `docs/findings/register/document.jsonl`, and a note stays here. The stakeholder was not present. The review filed the findings without the pause point, and the stakeholder sees them before any fix.

## Reviewed specification

- `docs/spec/features/counter-ids-fitting.feature`: 17 Rules and 53 Scenarios.
- `docs/spec/features/counter-ids.feature`: the two Scenarios that commit 4fdc7d1f changed, read with CID-04, CID-07, and CID-10.
- `docs/spec/work/counter-ids-fitting-gaps.md`: CIF-G01 to CIF-G12 and CIF-C01 to CIF-C10.
- `docs/spec/scope-map.md`: the 17 counter-ids-fitting rows, read only.
- `docs/spec/entity-model.md` § Counter IDs Fitting Entities, and the changed notes of § Counter IDs Entities.
- `docs/spec/interface-contracts.md` § Counter IDs Contracts.
- `docs/spec/validation-rules.md`: BR-074, BR-075, and BR-096 to BR-108.
- `docs/spec/state-machines.md`: Claim Lifecycle and Move Lifecycle.
- `docs/spec/glossary.md` § Counter IDs Vocabulary: the six confirmed terms.
- `docs/spec/work/counter-ids-fitting-qa-strategy.md`.
- `docs/proposals/counter-ids-fitting.md`, DEC-01 to DEC-13.
- The code that the contracts must fit: `packages/factory/scripts/next-id`, `packages/factory/scripts/init-factory` (`_derive_fitting_keys`, `_fitting_status`, `_reconcile_project_context`, `check_counter`), `packages/factory/agents/virgil.md` § Fitting, and the tests `tests/factory/test_counter_ids_text.py` and `tests/factory/test_next_id.py`.

`spec-lint`: `0 error(s), 0 warning(s), 58 info across 60 spec file(s).`

## Deterministic findings

| Rule     | Finding                                                | Disposition                                                                      |
| -------- | ------------------------------------------------------ | -------------------------------------------------------------------------------- |
| GLOSS001 | Glossary terms such as `Claim Register` are never used | Dismissed. No line names a term of § Counter IDs Vocabulary.                     |
| TODO001  | `todo.md` and `todos.md` hold unresolved items         | Dismissed. The count does not depend on this feature.                            |
| TRACE003 | BR-011 to BR-055 are never referenced                  | Dismissed. These rules predate the feature. BR-096 to BR-108 are all referenced. |
| TRACE004 | `EPIC_BUILDING_BLOCK` has no attribute block           | Dismissed. The entity predates the feature.                                      |

No info line names BR-074, BR-075, BR-096 to BR-108, or a counter-ids-fitting file.

## Semantic findings

| ID        | Severity | Category | Characteristic | Location                                              | Finding                                                                                                                                                                                     |
| --------- | -------- | -------- | -------------- | ----------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| SPEC-0059 | major    | defect   | Consistent     | `counter-ids.feature:265`, CID-07                     | CID-07 still makes `finding-format.md` the ID producer of nine prefixes and accepts `next-id <TAG>`. CIF-14, CIF-16, BR-107, and BR-108 move each prefix into its review file (CIF-G11).    |
| SPEC-0060 | major    | defect   | Consistent     | `counter-ids-fitting-qa-strategy.md:166`, `:193`      | The QA strategy says CIF-08 drops `next-id --seed` from the message of a clone without `origin`, and deletes the only test of that hint. CID-04 and the claim error table still require it. |
| SPEC-0061 | minor    | defect   | Complete       | `interface-contracts.md` § `next-id --move-to-origin` | The move names no result without the setting, without `origin`, without a local counter, or with a marker already in place. A declined seed leads to the third case.                        |
| SPEC-0062 | minor    | defect   | Complete       | `counter-ids-fitting-gaps.md` § Other Gaps, BR-102    | The move restarts after each stale lease without a limit. Only the QA strategy (CIF-QG01) asks for one; the gaps report does not.                                                           |
| SPEC-0063 | minor    | defect   | Consistent     | `validation-rules.md:576`, BR-102                     | BR-102, the move contract, and the Move Lifecycle take a non-zero exit for a failed move. BR-102, the gaps report, and the QA strategy also call the code open (CIF-G08).                   |
| SPEC-0064 | minor    | defect   | Consistent     | `interface-contracts.md:1086`                         | The Writes row says a claim leaves the clone unchanged. BR-075 now says a claim on the local counter writes into the project's own `.git`.                                                  |
| SPEC-0065 | minor    | defect   | Unambiguous    | `interface-contracts.md` § `next-id --plan-seed`      | The contract names no stream for the warnings of BR-100 or for the in-use message, while VIRGIL reads one command line from standard output.                                                |
| SPEC-0066 | minor    | defect   | Unambiguous    | `validation-rules.md:570`, BR-099 and BR-100          | BR-099 and BR-100 each read as the whole match rule. By BR-100, ADR files do not count, and BR-099 names `## T-NNNN` while real headings carry a title.                                     |
| SPEC-0067 | minor    | defect   | Complete       | `counter-ids-fitting-gaps.md` § Ambiguous Wording     | The fix of a minor finding deletes its register line. When it held the highest ID of a prefix, no branch tip holds it, and the seed hands the number out again.                             |
| SPEC-0068 | minor    | defect   | Complete       | `counter-ids-fitting-gaps.md` § Other Gaps            | Three Factory files number T entries in `todos.md` outside `next-id`. The specification neither covers nor excludes them; T-0008 tracks the merge of the two lists.                         |
| SPEC-0069 | minor    | defect   | Terminology    | `counter-ids-fitting.feature:472`, BR-108             | CIF-16 and BR-108 say "tag" and "finding tag", which the glossary lists under Avoid for ID Prefix.                                                                                          |
| SPEC-0070 | minor    | defect   | Terminology    | `glossary.md` § Counter IDs Vocabulary                | Fitting, Fitting Key, Orientation File, Text Test, Seed Plan, and Seed Pair have no glossary entry. Seed Plan and seed command name one concept.                                            |

SPEC-0059 and SPEC-0060 are finding files. SPEC-0061 to SPEC-0070 are lines in `docs/findings/register/document.jsonl`. SPEC-0069 and SPEC-0070 name `owner: domain-modeling-agent` in their text, as `inspect-spec` § Check the glossary requires.

### Notes

These observations need no change now, or another record already tracks them.

1. **CID-10 keeps the old `init-factory` hints.** "run `next-id --seed <number>` with a number above your highest ID" contradicts the seed per prefix of BR-101. Gap CIF-G01 records it, and DEC-13 leaves PROP-06 open for planning. So this review files no finding.
2. **New text uses "claim" alone.** BR-103 says "A claim that lands on the local counter". Open finding SPEC-0057 already covers the bare word in the structure files, so its fix should include BR-103.
3. **The Move Lifecycle belongs to no entity.** It describes one call of `next-id --move-to-origin`, as the Claim Lifecycle describes one claim. The entity model has no MOVE entity, which follows the precedent of the claim.
4. **A local clone after the move.** `init-factory` in a clone whose `origin` holds the marker finds `refs/ids/counters` with `git ls-remote` and sets `counter_seeded` to `true` by BR-105. That keeps the seed step from offering a second seed, which the proposal wants. BR-104 names no VIRGIL case for a `--plan-seed` that fails on a marker. The key skips the step, so the case does not arise in the normal flow.
5. **The first Gap Findings row of the QA strategy is stale.** It says that `interface-contracts.md` held no section for the feature. The section now exists, and its cases agree with the contract rows of the strategy, apart from SPEC-0060 and SPEC-0063.
6. **An unreachable remote on the first run.** BR-105 leaves the key "as it is" when the remote does not answer. On a first install there is no cached key yet. The fresh scan writes `false` for every other unset key, so `false` is the natural reading.
7. **The greenfield session start.** The CIF-01 decline Scenario expects the next session start to list the seed step as open. A greenfield session start lists no open step today. CIF-G07 records this, and PROP-09 stays open by DEC-13.

## Structure checks

### `docs/spec/entity-model.md`

Every entity that the feature file names has an attribute block, and the relationships agree with the Scenarios. FITTING lists five keys and FITTING_KEY_COUNTER_SEEDED the sixth, which matches CIF-04. PROJECT_REPOSITORY.path matches the CIF-02 Scenario. SEED_PLAN and SEED_PAIR have no glossary entry (SPEC-0070).

### `docs/spec/state-machines.md`

The Claim Lifecycle gains the event `MarkerRead`, and the pseudocode and the Mermaid diagram agree. The Move Lifecycle agrees with BR-102, BR-103, and the CIF-10 to CIF-12 Scenarios. Its pseudocode and its Mermaid edges correspond one to one. It has no event for a move that starts without a local claim commit (SPEC-0061) and no limit on the restart (SPEC-0062). Its own notes name the interrupted move (CIF-G05) and a failed restore.

### `docs/spec/validation-rules.md`

BR-096 to BR-108 each trace to a Rule of the feature file and to a decision of the proposal. BR-074 and BR-075 now name the local counter. BR-099 and BR-100 overlap (SPEC-0066). BR-102 contradicts itself on the exit code (SPEC-0063). BR-108 uses "finding tag" (SPEC-0069).

### `docs/spec/interface-contracts.md`

The usage rows, the remote order, the marker message, the `--plan-seed` cases, the `--move-to-origin` cases, and the `init-factory` key table agree with the Scenarios. A Scenario reaches each operation. The contracts fit `next-id` as it stands: `resolve_remote` is the one place for the new remote order, and `RemoteCounter.read` is the one place for the marker check. The Writes row still says a claim leaves the clone unchanged (SPEC-0064). The streams of `--plan-seed` are open (SPEC-0065), and the move lacks its precondition failures (SPEC-0061).

### `docs/spec/glossary.md`

The six confirmed terms agree with the feature file. The feature file says "ID producer" throughout and never "requestor", which the glossary lists under Avoid. Two defects remain: the avoided word "tag" (SPEC-0069) and six undefined terms (SPEC-0070).

### `docs/spec/work/term-candidates.md`

No row has the status `proposed`. The six terms of this feature are in the glossary, so the check found no finding.

### `docs/spec/work/counter-ids-fitting-qa-strategy.md`

Every Rule CIF-01 to CIF-17 has at least one contract row. The test setup keeps every test on local repositories in `tmp_path`, so no test reads or pushes to this project's remote. The retention policy deletes a test that still owns a live contract (SPEC-0060). The strategy also misses the CID-07-LN-01 tests that SPEC-0059 changes. It treats the exit code of a failed move as open (SPEC-0063).

The specification has no `docs/spec/schemas/` file and no area spec for this feature, so those checks did not run.

## Traceability summary

- All 17 Rules appear in the scope map, the Actor-Goal Matrix, and the QA strategy. The review found no orphan.
- Each of the 16 completion criteria of the proposal traces to a Rule or a gap in the gaps report.
- The entity model, the contracts, and the state machines cite BR-096 to BR-108, and `spec-lint` reports none of them as unreferenced.
- Gaps: the conflict between CID-07 and CIF-14 (SPEC-0059), the precondition failures of the move (SPEC-0061), the restart limit (SPEC-0062), the deleted register line (SPEC-0067), and the `todos.md` writers (SPEC-0068).

## Verdict

The specification is not ready for architecture. SPEC-0059 and SPEC-0060 block it. Both fixes are small. The requirements agent changes one Scenario Outline row of CID-07 and closes CIF-G11. The test-strategy agent corrects one Gap Findings row and one retention item. The minor findings in the register do not block.

## Handoff

Requirements agent: the spec review found 2 open blocking findings, SPEC-0059 and SPEC-0060. Address SPEC-0059, and hand SPEC-0060 to the test-strategy agent.

## Pass 2

Pass 2 reviewed commit 079034d92e7c338277c0dae154aae6b18e57f19e. It checked only SPEC-0059, SPEC-0060, and the text their fixes changed: row 265 of `counter-ids.feature` and three places in `counter-ids-fitting-qa-strategy.md`. The ten register lines SPEC-0061 to SPEC-0070 stay as they are.

| ID        | Severity | Status   | Result                                                                                                                                                                                                                                                                         |
| --------- | -------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| SPEC-0059 | major    | open     | Row 265 now names `id-prefixes.md`. That file is no ID producer and holds no claim rule by BR-108, so the Outline step "the rule tells the reader to run next-id with the ID prefix" cannot hold for it. CID-07 and BR-108 still contradict each other. CIF-G11 stays open.    |
| SPEC-0060 | major    | resolved | The QA strategy keeps `test_st_0370_clone_without_origin_names_origin_remote_and_seed` as CIF-08-IT-03, without `agent-factory.counterRemote`, with all three names in its assertion. The Gap Findings row and the retention line agree with CID-04 and the claim error table. |

The author asked whether the `id-prefixes.md` row holds. It does not. The pass-1 fix offered two options, and the author chose neither: the row moved to a third file. The fix for pass 3 is to remove the row. CIF-14 already requires each review file to name its own prefix. The changed text holds no other defect, so pass 2 files no new finding.

### Verdict after pass 2

The specification is not ready for architecture. SPEC-0059 blocks it. Its fix deletes one Outline row, closes CIF-G11, and adds one line to the QA strategy.
