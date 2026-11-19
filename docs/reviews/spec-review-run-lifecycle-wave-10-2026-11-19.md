---
type: inspect-spec
title: Spec review of the run-lifecycle wave-10 close
date: 2026-11-19
status: pass
reviewer: spec-review-agent
findings_filed: 1
story: run-lifecycle
scope: The specification, QA strategy, and test changes of f70f3e47..0157683c on feature/run-lifecycle, read against packages/factory/scripts/dispatch and dispatch_lib.py at f70f3e47
---

# Spec review of the run-lifecycle wave-10 close

The wave-10 changes pass, because no finding blocks. The `dispatch` contract, BR-113, BR-116, BR-117, the new `close-wave <N>` rule, and the notes of the Ledger Entry Lifecycle agree with each other. They also agree with the four fixes of ST-0431 in `dispatch` and `dispatch_lib.py`. The code under `packages/` did not change after `f70f3e47`. Each of the five new QA rows names a test in its file that carries the row's marker, and the five tests pass.

The review filed one minor finding as a register file:

- SPEC-0122: the contract now names the field `branch_head` of the ledger, and `DISPATCH_LEDGER` in the entity model lists `branch_head` only for a wave record. The domain-modeling agent adds the field.

This review confirms all six `fixed` rows on core artifacts in `spec-feedback-ST-0431.md` and rejects none.

Spec review is the `document` class. The code of the wave lives on `feature/run-lifecycle`, the run's own workspace, and no story or code outside the run encodes the reviewed statements. So every finding answers `in_use: false`. The caller dispatched this review without the stakeholder, so the review filed the finding without the pause point. The stakeholder sees it first in this report.

## Reviewed specification

- The diff `git diff f70f3e47..0157683c`, from the commits `2495af06` (domain modeling), `42475adc` (test strategy), and `0157683c` (test renames).
- `docs/spec/interface-contracts.md` § dispatch: the Usage, Writes, and Exit code rows, and the `re-dispatch` and `mark-failed` bullets. § `dispatch close-wave`: the Refuses, Empty wave, and Rerun rows.
- `docs/spec/validation-rules.md` § Dispatch ledger: the bullets on idempotent no-ops, `mark-failed`, and `close-wave <N>`, and BR-113, BR-116, and BR-117.
- `docs/spec/state-machines.md` § Ledger Entry Lifecycle: the notes on **Prepare** and **ReDispatch**, read with the pseudocode and the Mermaid diagram.
- `docs/spec/work/run-lifecycle-qa-strategy.md`: the rows RL-05-CT-08, RL-06-IT-06, RL-11-IT-05, RL-11-IT-06, and RL-12-IT-09, the layer rows, and the new row of Gap Findings.
- `tests/factory/test_run_lifecycle_dispatch.py` and `tests/factory/test_run_lifecycle_ledger.py`: the five renamed tests.
- `docs/spec/work/spec-feedback-ST-0431.md`.
- `docs/spec/entity-model.md` (DISPATCH_LEDGER), `docs/spec/glossary.md`, and `docs/spec/features/run-lifecycle.feature`, for consistency only.
- The code: `cmd_re_dispatch`, the parser of `mark-failed`, the base of `cmd_prepare_wave`, `cmd_close_wave`, and `_missing_wave_record` in `packages/factory/scripts/dispatch`. `Ledger.close_wave` and `lets_its_wave_close` in `packages/factory/scripts/dispatch_lib.py`. The core list is `packages/factory/rulebooks/core-artifacts.yaml`.
- `docs/spec/scope-map.md`, read only.

`spec-lint --spec-dir docs/spec`: `spec-lint: 0 error(s), 0 warning(s), 57 info across 107 spec file(s).`

## Deterministic findings

| Rule     | Subject                                                              | Verdict                                                                           |
| -------- | -------------------------------------------------------------------- | --------------------------------------------------------------------------------- |
| GLOSS001 | Glossary terms that no spec file uses, such as Workstream Resolver   | Dismissed. None is a run lifecycle term, and the skill files no such case.        |
| TODO001  | Open items in `docs/spec/work/todo.md` and `docs/spec/work/todos.md` | Dismissed. No item concerns the reviewed range.                                   |
| TRACE003 | BR-011 to BR-054 defined but never referenced                        | Dismissed. BR-113, BR-116, and BR-117 are referenced, and the rest is older.      |
| TRACE004 | `EPIC_BUILDING_BLOCK` in a relationship without an attribute block   | Dismissed. The entity belongs to the test-design entities, outside of this range. |

## Semantic findings

| ID        | Severity | Category | Type       | Characteristic | Artifact                        | Finding                                                                                                                                                                         | Acted on by           |
| --------- | -------- | -------- | ---------- | -------------- | ------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------- |
| SPEC-0122 | minor    | defect   | incomplete | Complete       | `docs/spec/entity-model.md:127` | The Writes row names the ledger field `branch_head`, which `init`, `merge-story`, and `close-wave` write. DISPATCH_LEDGER lists `branch_head` only as a field of a wave record. | domain-modeling-agent |

One note stays a row of this report and needs no change now:

| Note                                                                                                                                                                                                                                                                                      | Artifact                                          | Severity |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------- | -------- |
| The feature file has no Scenario for the four checks of ST-0431. The QA strategy already records this gap for the requirements agent in its Gap Findings, so this review files no second finding. The requirements agent can handle it together with SPEC-0111, SPEC-0116, and SPEC-0119. | `docs/spec/work/run-lifecycle-qa-strategy.md:358` | note     |

## Structure checks

### `docs/spec/interface-contracts.md`

The Usage row shows `--class CLASS` without brackets. The parser of `mark-failed` declares `--class` with `required=True`, so argparse exits non-zero and the ledger keeps no attempt, as the `mark-failed` bullet says. The `re-dispatch` bullet agrees with `cmd_re_dispatch`. The command refuses every state but `failed` and `blocked` before it reads any limit, names the entry and its state, and saves nothing. The Writes row agrees with `cmd_prepare_wave`, which reads the base from `refs/heads/<feature_branch>`, else `HEAD`. Code comments in that function also say that `branch_head` sets no base.

The `close-wave` rows agree with `cmd_close_wave` and `Ledger.close_wave`. A wave without a record and above 1 refuses until wave N-1 has a record. The message names the missing record and `dispatch close-wave N-1`, and the command saves nothing. A rerun on a recorded wave returns before that check, so it is a no-op. A wave without entries closes with empty lists, and `close_wave` calls the drift check only when the wave has entries. The check found SPEC-0122 in the entity model, which the Writes row now relies on.

### `docs/spec/validation-rules.md`

The list of idempotent no-ops no longer names `re-dispatch`, and the next sentence says why. The new `close-wave <N>` rule and the added sentence of BR-113 state the same order of waves as the contract and `_missing_wave_record`. Its example holds: when `add` takes back the only entry of wave 2, the entry goes to the next free wave, and wave 2 closes with empty lists after wave 1. BR-116 accepts only `failed` and `blocked` for `re-dispatch`, as the state machine does. BR-117 adds that a wave left without entries closes with empty lists, which matches `close_wave`.

### `docs/spec/state-machines.md`

The pseudocode and the Mermaid diagram already had **ReDispatch** only from **FAILED** and **BLOCKED**. The new note now says that every other state refuses, also **PREPARED**. The note on **Prepare** adds that `close-wave` waits for the previous record, as BR-113 says. The check found nothing.

### `docs/spec/work/run-lifecycle-qa-strategy.md` and the tests

Each new row names one test with its marker in the file of the row:

| QA row      | Test                                                                                        | File                             |
| ----------- | ------------------------------------------------------------------------------------------- | -------------------------------- |
| RL-05-CT-08 | `test_RL_05_CT_08_mark_failed_without_a_class_writes_no_attempt`                            | `test_run_lifecycle_ledger.py`   |
| RL-06-IT-06 | `test_RL_06_IT_06_re_dispatch_refuses_a_unit_of_work_that_has_not_stopped`                  | `test_run_lifecycle_dispatch.py` |
| RL-11-IT-05 | `test_RL_11_IT_05_close_wave_records_a_wave_whose_only_entry_add_moved`                     | `test_run_lifecycle_dispatch.py` |
| RL-11-IT-06 | `test_RL_11_IT_06_close_wave_refuses_an_empty_wave_before_the_record_of_the_wave_before_it` | `test_run_lifecycle_dispatch.py` |
| RL-12-IT-09 | `test_RL_12_IT_09_prepare_wave_cuts_the_branch_from_the_tip_of_the_feature_branch`          | `test_run_lifecycle_dispatch.py` |

Each ID appears in exactly one QA row and on exactly one `@pytest.mark.spec` marker. The five tests pass: `uv run pytest -q -k "RL_05_CT_08 or RL_06_IT_06 or RL_11_IT_05 or RL_11_IT_06 or RL_12_IT_09"` reports `9 passed`, because some tests are parametrized. The old markers RL-06-IT-03, RL-12-IT-01, RL-11-CT-01, RL-11-IT-02, and RL-05-CT-02 left these tests, so each old ID keeps only its own row.

### `docs/spec/glossary.md`

The range adds no term. The check found no second term for a concept of the range and no avoided term in use.

### `docs/spec/work/term-candidates.md`

The file holds no row with status `proposed`. The check found nothing.

### Pending stories

No pending story owns SPEC-0122. ST-0430 changes words, never rules, and edits no specification.

## Spec-feedback rows on core artifacts

The core list is `packages/factory/rulebooks/core-artifacts.yaml`. The reviewer sets each `fixed` row on a core artifact to `confirmed` or `rejected`.

| Report                     | Artifact                           | Drift                                       | Verdict     | Reason                                                                                                                |
| -------------------------- | ---------------------------------- | ------------------------------------------- | ----------- | --------------------------------------------------------------------------------------------------------------------- |
| `spec-feedback-ST-0431.md` | `docs/spec/interface-contracts.md` | `--class` is required                       | `confirmed` | The Usage row and the `mark-failed` bullet require `--class`, as the parser does.                                     |
| `spec-feedback-ST-0431.md` | `docs/spec/interface-contracts.md` | `re-dispatch` refuses the other five states | `confirmed` | The bullet names the five states, the exit `1`, the message, and that nothing is written, as `cmd_re_dispatch` does.  |
| `spec-feedback-ST-0431.md` | `docs/spec/interface-contracts.md` | The base of `prepare-wave`                  | `confirmed` | The Writes row names the tip of `refs/heads/<feature_branch>`, else `HEAD`, and says that `branch_head` sets no base. |
| `spec-feedback-ST-0431.md` | `docs/spec/interface-contracts.md` | A wave without entries                      | `confirmed` | The Empty wave row gives exit `0`, the empty lists, and no drift check, as `Ledger.close_wave` does.                  |
| `spec-feedback-ST-0431.md` | `docs/spec/interface-contracts.md` | `close-wave N` waits for the record of N-1  | `confirmed` | The Refuses row gives the refusal, the message, and that nothing is written, and the Rerun row gives the no-op.       |
| `spec-feedback-ST-0431.md` | `docs/spec/validation-rules.md`    | `re-dispatch` is no idempotent no-op        | `confirmed` | The first bullet no longer lists `re-dispatch` and says that it refuses a `prepared` entry.                           |

The row on `docs/spec/work/run-lifecycle-qa-strategy.md` is not on the core list, so it stays `fixed` and passes BR-062. The report holds no row on `docs/testing.yaml`.

## Prior findings

SPEC-0111, SPEC-0116, SPEC-0117, SPEC-0118, SPEC-0119, and SPEC-0121 stay `open`, because the range changes none of their artifacts. SPEC-0120 stays `resolved`. The open register files SPEC-0056 to SPEC-0070 concern the counter-ids feature and lie outside this range. This pass inspected the reviewed artifacts fresh and did not only check the prior list.

## Traceability summary

The new rules trace to BR-113, BR-116, and BR-117, and the five QA rows trace to the checks of ST-0431 through their tests. No Scenario traces the four checks, and the QA strategy records that gap (note above). `docs/spec/scope-map.md` was read only, and the review files nothing on its content.
