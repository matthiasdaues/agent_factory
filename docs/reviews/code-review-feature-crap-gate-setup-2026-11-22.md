---
type: code-review
title: Code review of the whole feature feature/crap-gate-setup
date: 2026-11-22
status: pass
reviewer: code-review-agent
findings_filed: 4
story:
run: feature/crap-gate-setup
branch: feature/crap-gate-setup
branch_base: 9ea68284539b1f175dea21617c125a578e3db474
branch_head: 8beaa7eb90f8fd36c4ed4cf7b06db732a9be9004
---

# Code review of the whole feature feature/crap-gate-setup

## Verdict

The feature does not pass the code review. The review files two blocking findings of severity `major`, two register files of severity `minor`, and five notes.

Both blocking findings lie in the Python template `crap-measure-python`, where it meets `crap-score` and the setup skill. IMPL-0090: the template stops a measure for an untested script without a file ending, also when the measure leaves the script out, so an exclusion of setup step 3 cannot help. This repository holds such a script: the template source itself. IMPL-0091: the template and `crap-score` hand their own uv environment to the project's tests, so a test command `python -m pytest` runs in the wrong interpreter.

The contracts between `crap-score`, `premerge-check`, `dispatch` and `gate-setup-proof` fit. Each caller passes the arguments of BR-127, the exit codes `2` and `3` travel to `blocked` as BR-124 and BR-136 say, and `resume-gates` takes only the edge of BR-135. The nine test files of the feature pass: 301 tests.

Next, the implementation agent adds IMPL-0090 and IMPL-0091 as units of work with `dispatch add <finding-id>`. After the merge of the fixes, this review runs again on the feature branch.

## Scope

The review covers the diff `9ea68284..e4cb6d4b` of `feature/crap-gate-setup`: 124 files, the stories ST-0433 to ST-0448. Each story had its own review (`docs/reviews/code-review-ST-04*-2026-11-2*.md`), so this review read the code for what only the whole shows:

- The contracts between `crap-score`, `premerge-check`, `dispatch`, `dispatch_lib.py`, `gate-setup-proof`, the template `crap-measure-python`, and the skills `crap-score` and `setup-crap-score`.
- Code that two or more scripts repeat, beyond IMPL-0083.
- Behavior that the specification states and no story built.
- Text in the agent definitions and skills that contradicts the code.

The review read `docs/proposals/crap-gate-setup.md`, the Rules of `docs/spec/features/crap-gate-setup.feature`, BR-127 to BR-139 in `docs/spec/validation-rules.md`, the sections of `docs/spec/interface-contracts.md` on `crap-score`, `gate-setup-proof`, `premerge-check` and `dispatch`, and `docs/spec/work/crap-gate-setup-qa-strategy.md`. It read `crap-score`, `gate-setup-proof` and the template in full, and the diffs of `premerge-check`, `dispatch`, `dispatch_lib.py`, `finding-lint` and `guard-human-fields`. ST-0449 enables the gate in this repository after the merge (DEC-49), so its open rows CG-12-LN-06 and CG-13 are out of scope.

## The contracts between the parts

| Contract                                   | Producer                                                       | Consumer                                                | Result                                                                                                                                                 |
| ------------------------------------------ | -------------------------------------------------------------- | ------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Call of the gate (BR-127)                  | gate-check step, `premerge-check`, `gate-setup-proof`, setup   | `crap-score`                                            | Each caller passes exactly one of `--base` and `--all`, and no threshold and no list of files.                                                         |
| Report folder at the merge (BR-136)        | `premerge-check`                                               | `crap-score`, the refusal text                          | The report lands in `<primary>/.current-work/crap-score/`, and the refusal reads it only after exit `1` (IMPL-0071).                                   |
| Exit `2` to exit `3` to `blocked` (BR-124) | `crap-score`, the `ready` check of `premerge-check`            | `premerge-check`, `dispatch merge-story`                | Exit `3` only when every other check passed; `merge-story` sets the reason `gate cannot measure: crap-score` on both ways.                             |
| The edge back to `dispatched` (BR-135)     | `dispatch resume-gates`                                        | `Ledger.transition`                                     | `GUARDED_EDGES` keeps the edge from every other caller, and the guard refuses an entry without its branch (DEC-63).                                    |
| `ready` commands (BR-129, BR-136, BR-137)  | `gates.crap-score.measures`                                    | `crap-score`, `premerge-check`, `dispatch init`         | All three run each command in its own process group with SIGTERM and SIGKILL after 5 seconds. IMPL-0093 names the readers that differ.                 |
| The message of a failed test run (BR-138)  | `crap-score`: `the measuring command of measure <name> exited` | "Reports a gap" of `gate-setup-proof`                   | The regular expression of the check matches the message of `run_command`. A note below names the coupling.                                             |
| Rows of the measuring command (BR-130)     | template `crap-measure-python`                                 | `crap-score`                                            | The rows have the six fields or `parse_error`. IMPL-0090 and IMPL-0091 name two cases where the template exits `1` for a project that the setup plans. |
| Exceptions register (BR-132)               | the stakeholder on `dev`                                       | `crap-score`, `finding-lint`, the stop notice, the hook | `crap-score` reads `refs/heads/dev` only. `finding-lint` and `stop_notice` skip the file by name, and `guard-human-fields` refuses every write.        |

## Findings

| Finding                                                                                                                                                                                                                                                                                                                                                                                          | Category   | Type          | Severity | Basis                                                                                    | ID                                                    |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ---------- | ------------- | -------- | ---------------------------------------------------------------------------------------- | ----------------------------------------------------- |
| The template stops with "coverage cannot reach" for every untested script without a file ending in the folder. `crap-score` applies `files` and `exclude` only to rows, and the command writes none. So an exclusion of setup step 3 and a second measure of setup step 1 cannot help. In this repository, the template source itself is such a script, because the tests run only a copy of it. | defect     | function      | major    | `in_use: false`, `harms_downstream: false`, `fails_purpose: true`, `raises_cost: false`  | [IMPL-0090](../findings/IMPL-0090.md)                 |
| The template keeps `VIRTUAL_ENV` and `PATH` of its own uv environment for `TEST_COMMAND`, and `crap-score` does the same for each measuring command. A test command `python3 -m pytest` starts the template's interpreter and fails with "No module named pytest", so the gate cannot measure.                                                                                                   | defect     | interface     | major    | `in_use: false`, `harms_downstream: false`, `fails_purpose: true`, `raises_cost: false`  | [IMPL-0091](../findings/IMPL-0091.md)                 |
| Step 4d calls `dispatch merge-story` without a background job. `premerge-check` now runs the full `crap-score` and the test suite, and BR-134 gives the reason why a foreground call can end too early. A call that ends early merges nothing and costs a full rerun.                                                                                                                            | defect     | timing        | minor    | `in_use: false`, `harms_downstream: false`, `fails_purpose: false`, `raises_cost: true`  | [IMPL-0092](../findings/register/code/IMPL-0092.json) |
| Four scripts read the measures of `gates.crap-score` with different checks, and two scripts repeat the signal code. A `ready` value `""`, both keys `crap_score` and `crap-score`, and the old key alone each give a different answer in at least one reader.                                                                                                                                    | suggestion | structure     | minor    | `in_use: false`, `harms_downstream: false`, `fails_purpose: false`, `raises_cost: true`  | [IMPL-0093](../findings/register/code/IMPL-0093.json) |
| `crap-score/SKILL.md` § Report says that `premerge-check` reads no report. `premerge-check` reads the new report after exit `1` to name the failing functions, as the Scenario "The refusal names the failing functions from the report after exit 1" requires. ADR-0003 has the right sentence: no report decides a merge. Copy its wording into the skill.                                     | suggestion | documentation | note     | `in_use: false`, `harms_downstream: false`, `fails_purpose: false`, `raises_cost: false` | —                                                     |
| The table of exit codes in `crap-score/SKILL.md` lists `0`, `1` and `2`. The docstring of `crap-score` and BR-129 also name `128 + n` after a stop signal, and `implementation-agent.md` handles it. The skill is the description of the gate (DEC-01), so one row would close the gap.                                                                                                          | suggestion | documentation | note     | `in_use: false`, `harms_downstream: false`, `fails_purpose: false`, `raises_cost: false` | —                                                     |
| "Reports a gap" of `gate-setup-proof` decides by a regular expression on the text of a `crap-score` message. A rewording of `run_command` in `crap-score` makes the check fail for every measure. `test_crap_gate_proof.py` runs the real `crap-score`, so a test would catch the rewording.                                                                                                     | suggestion | interface     | note     | `in_use: false`, `harms_downstream: false`, `fails_purpose: false`, `raises_cost: false` | —                                                     |
| Workflow step 2 of `test-strategy-agent.md` gives `gates.crap-score.threshold` as an example of a setting that the agent proposes, and step 3 leaves the entry `gates.crap-score` out of the diff. A setting of `mutation-testing` would be the fitting example.                                                                                                                                 | suggestion | documentation | note     | `in_use: false`, `harms_downstream: false`, `fails_purpose: false`, `raises_cost: false` | —                                                     |
| The QA strategy says that the test of DEC-61 carries the marker CG-10-IT-02 until a story moves it to CG-10-IT-04. No story moved it, so CG-10-IT-02 marks two tests in `test_crap_gate_dispatch.py`, and no test carries CG-10-IT-04. The reconciliation run can move the marker or drop the sentence.                                                                                          | suggestion | test          | note     | `in_use: false`, `harms_downstream: false`, `fails_purpose: false`, `raises_cost: false` | —                                                     |

IMPL-0090 and IMPL-0091 block the feature. Each `minor` finding has a register file with `status: open`, and the commit that fixes it sets `status` to `resolved`. The implementation agent acts on all four. IMPL-0083 stays open and covers the stop of a process group in three scripts.

## Behavior of the specification without code

The review compared the Rules of the feature with the code. Every Rule outside the Rule of this repository has code, and its tests in the QA strategy name test IDs that exist. The rows without a test are CG-12-LN-06 (T-0402) and CG-13-IT-01 to CG-13-IT-03 and CG-13-LN-01, which belong to ST-0449. CG-10-IT-04 is the marker of the note above.

## Focus areas

| Focus area         | Result                                                                                                                                                                                                                                                        |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Correctness        | The calls, exit codes and ledger edges fit across the scripts, as [The contracts between the parts](#the-contracts-between-the-parts) shows. IMPL-0090 and IMPL-0091 are two cases in which the template cannot measure a project that the setup skill plans. |
| Clean Architecture | `crap-score` holds no code of a language, and the template names no path under `.agent-factory/` (BR-130). `crap-score` and `gate-setup-proof` take `glob_match` from `dispatch_lib.py`, so both use one glob dialect (DEC-35).                               |
| SOLID              | Each script has one job: measure and judge, check one measure, check a merge, move the ledger. IMPL-0093 names one rule, the reading of the measures, that four scripts hold.                                                                                 |
| Maintainability    | IMPL-0083 and IMPL-0093 together name the repeated code: the stop of a process group, the reading of the measures, and the signal code. The tests drive each script as a subprocess on temporary repositories.                                                |
| Consistency        | The agent definitions and skills match the code, apart from the four text notes. IMPL-0092 names the one call whose run time the gate changes and whose text says nothing about a background job.                                                             |

## Verification

```bash
uv run --directory .current-work/feature/crap-gate-setup/invocation pytest tests/factory/test_crap_gate_template.py tests/factory/test_crap_gate_text.py tests/factory/test_crap_gate_journey.py -q -n auto
uv run --directory .current-work/feature/crap-gate-setup/invocation pytest tests/factory/test_crap_gate_score.py tests/factory/test_crap_gate_judging.py tests/factory/test_crap_gate_lock.py tests/factory/test_crap_gate_dispatch.py tests/factory/test_crap_gate_premerge.py tests/factory/test_crap_gate_proof.py -q -n auto
```

The two runs printed `39 passed in 7.59s` and `262 passed in 14.51s`. The review checked IMPL-0090 and IMPL-0091 with the filled-in template on a small temporary project, as each finding file shows.

## Repeat pass at 8beaa7eb

The feature passes the code review at `8beaa7eb90f8fd36c4ed4cf7b06db732a9be9004`. No blocking finding of the run is open, and this pass files no new finding. It records one new note.

The pass covers `e4cb6d4b..8beaa7eb`: the fixes of IMPL-0090 and IMPL-0091 with their story reviews, the merges `c7f84d72` and `712547fb`, and the drift rows of waves 5 and 6 (DEC-65, DEC-66). The merged files of `crap-score`, the template, the two skills, `implementation-agent.md` and the two changed test files equal the head of `story/IMPL-0091`. So the merges changed no reviewed code.

| Finding   | Status on the feature branch | Evidence                                                                                                                                                                         |
| --------- | ---------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| IMPL-0090 | `resolved`                   | `docs/reviews/code-review-IMPL-0090-2026-11-22.md`: the scratch project gives exit `0` with `exclude` or a narrow `files` pattern, and exit `2` without either, as BR-130 wants. |
| IMPL-0091 | `resolved`                   | The second repeat pass in `docs/findings/IMPL-0091.md`: exit `0` when started directly and from two nested `uv run --script` wrappers.                                           |
| IMPL-0092 | `resolved`                   | Step 4d and step 6 of the run by hand start `dispatch merge-story` as a background job, and BR-134 names it (DEC-66).                                                            |
| IMPL-0093 | `open`, `minor`              | No fix yet. It does not block the merge.                                                                                                                                         |

The drift rows bring BR-129, BR-130, BR-134, the contract of the template, and the QA strategy in line with the code. Two notes of the first pass are fixed: the skill `crap-score` and the CG-10-IT-04 marker. The other three notes need no change.

| Finding                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | Category   | Type      | Severity | Basis                                                                                    | ID  |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------- | --------- | -------- | ---------------------------------------------------------------------------------------- | --- |
| `caller_environment()` covers the commands that `crap-score` starts. The same `ready` commands also run in `dispatch init`, through `run_in_own_group` with `env=None`, and in `premerge-check`, through `_worktree_environment`, which keeps `PATH`. There they still see the uv environment of `dispatch`. So a `ready` command that starts `python3` by name can pass in `crap-score` and fail at the start of a run. A typical `ready` command checks a Compose stack and starts no Python. A later story can share one `caller_environment()` from `dispatch_lib.py`, as IMPL-0093 proposes for the reading of the measures. | suggestion | interface | note     | `in_use: false`, `harms_downstream: false`, `fails_purpose: false`, `raises_cost: false` | —   |

`implementation-agent.md` has 20,101 tokens with its inputs, and `index-lint --check` warns and exits `0`. The warning does not block the merge, and a cut belongs in its own story.

Next, the QA agent runs step 2 of the feature checks on `feature/crap-gate-setup`.

```bash
uv run --directory .current-work/feature/crap-gate-setup/invocation pytest tests/factory/test_crap_gate_template.py tests/factory/test_crap_score.py tests/factory/test_crap_gate_score.py tests/factory/test_crap_gate_proof.py tests/factory/test_crap_gate_premerge.py tests/factory/test_crap_gate_dispatch.py tests/factory/test_crap_gate_text.py tests/factory/test_crap_gate_judging.py tests/factory/test_crap_gate_lock.py tests/factory/test_crap_gate_journey.py -q -n auto
```

The run printed `319 passed in 35.02s`. `finding-lint` exited `0`.
