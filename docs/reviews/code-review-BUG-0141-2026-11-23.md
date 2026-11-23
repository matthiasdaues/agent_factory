---
type: code-review
title: Code review of BUG-0141, the template replaces the inherited pytest options
date: 2026-11-23
status: pass
reviewer: code-review-agent
findings_filed: 0
story: BUG-0141
run:
branch: story/BUG-0141
branch_base: 571fd12439391700b254927bb6769ad62398119f
branch_head: 028d25a52a5c7292a8347c44858b129f807a5743
---

# Code review of BUG-0141, the template replaces the inherited pytest options

## Verdict

BUG-0141 passes the code review, and the review files no new finding. The `sitecustomize.py` of the template now removes every inherited `--basetemp` and `-p no:cacheprovider` in each form that pytest accepts, and then adds its own. It keeps every other option. The new test of two nested pytest levels fails on the old template with the exit `4` of the finding and passes on the fix.

The fix does not touch [IMPL-0104](../findings/register/code/IMPL-0104.json), which stays `open`. Three notes remain: the header of the template and the interface contract still say "appends", and an unbalanced quote in `PYTEST_ADDOPTS` now stops coverage.

Next, the developer agent commits this report on `story/BUG-0141`. Then the implementation agent runs the gate-check step.

## Scope

The review covers the diff `571fd124..028d25a5`, the one commit `028d25a5`. It changes three files:

- `packages/factory/skills/setup-crap-score/crap-measure-python`: `SITECUSTOMIZE` splits the inherited `PYTEST_ADDOPTS` with `shlex.split`, drops `--basetemp X`, `--basetemp=X`, `-p no:cacheprovider` and `-pno:cacheprovider`, and writes the rest with `shlex.join`, followed by its own `--basetemp` and `-p no:cacheprovider`.
- `tests/factory/test_crap_gate_template.py`: one test starts pytest two levels deep under the template, and one test checks that the project option `--strict-markers` survives.
- `docs/findings/BUG-0141.md`: `status` changes to `resolved`.

The review read BUG-0141, DEC-85, and the row of the Python template in `docs/spec/interface-contracts.md`.

## Checks of the stripping

The probe `/tmp/claude-1000/-home-matthiasdaues-Documents-datenschoenheit-agent-factory/89fd1670-49e4-4a59-97db-e1035150aa04/scratchpad/st0451-review/bug0141/strip_forms.py` takes the `SITECUSTOMIZE` text from the worktree template. It runs that text with each inherited value below and prints the `PYTEST_ADDOPTS` that it writes. The work folder is `/w/pytest`, and `<pid>` is the ID of the probe process.

| Inherited `PYTEST_ADDOPTS`                            | Written `PYTEST_ADDOPTS`                                                         | pytest accepts the inherited form |
| ----------------------------------------------------- | -------------------------------------------------------------------------------- | --------------------------------- |
| `--basetemp=/x/1`                                     | `--basetemp=/w/pytest/<pid> -p no:cacheprovider`                                 | yes                               |
| `--basetemp /x/1`                                     | the same                                                                         | yes                               |
| `'--basetemp=/a b/1'`                                 | the same                                                                         | yes                               |
| `--basetemp '/a b/1'`                                 | the same                                                                         | yes                               |
| `-pno:cacheprovider`                                  | the same                                                                         | yes                               |
| `-p no:cacheprovider`                                 | the same                                                                         | yes                               |
| `-p=no:cacheprovider`                                 | kept, then the template's own two options                                        | no: plugin `=no:cacheprovider`    |
| `--basetem=/x/1`                                      | kept, then the template's own two options                                        | no: unrecognized argument         |
| `-p no:randomly -p no:cacheprovider --strict-markers` | `-p no:randomly --strict-markers --basetemp=/w/pytest/<pid> -p no:cacheprovider` | yes                               |
| `-o cache_dir=/c -k 'not slow'`                       | kept with its quotes, then the template's own two options                        | yes                               |
| `--basetemp` without a value                          | `--basetemp=/w/pytest/<pid> -p no:cacheprovider`                                 | no                                |
| `'unbalanced`                                         | `ValueError: No closing quotation`                                               | no                                |

The two forms that the code keeps, `-p=no:cacheprovider` and the abbreviation `--basetem=`, are forms that pytest 9.2.0 itself refuses, so no accepted form gets past the stripping. The review ran both through pytest to check this. The code drops a word only when it is `--basetemp`, starts with `--basetemp=`, is `-pno:cacheprovider`, or is `-p` followed by `no:cacheprovider`. So `-p no:randomly`, `-o` and `-k` with a quoted value keep their place and their quotes. The only option the code can drop wrongly is a value that is itself the word `--basetemp`, such as `-k --basetemp`, which no project writes.

An unbalanced quote is the one case that changes behavior. `shlex.split` raises, Python reports "Error in sitecustomize" and goes on, and `coverage.process_startup()` never runs. The template then exits non-zero with "coverage recorded no data". Before the fix the template appended without parsing. pytest itself splits `PYTEST_ADDOPTS` with `shlex.split` and stops on the same value, so only a `TEST_COMMAND` that is not pytest can meet this case. The review records it as a note.

## IMPL-0104

The fix changes nothing for a test that calls `pytest.main()` in its own process. `sitecustomize.py` runs once when the process starts, so the inner pytest reads the same single `--basetemp` as the outer one and clears it. Case 3 of `/tmp/claude-1000/-home-matthiasdaues-Documents-datenschoenheit-agent-factory/89fd1670-49e4-4a59-97db-e1035150aa04/scratchpad/st0451-review/bug0141/repro_template.sh` still gives exit `1` under the template, and plain pytest on the same project passes. IMPL-0104 stays `open` and minor.

## The tests

`test_bug_0141_a_pytest_two_levels_deep_keeps_its_own_tmp_path` starts each inner pytest inside the `tmp_path` of the level above it. That is the layout of the ST-0449 proof. It asserts exit `0`, three distinct `tmp_path` folders, and that none of them is left afterwards. `/tmp/claude-1000/-home-matthiasdaues-Documents-datenschoenheit-agent-factory/89fd1670-49e4-4a59-97db-e1035150aa04/scratchpad/st0451-review/bug0141/old_template.sh` puts the template of `571fd124` into the worktree. On that template the test fails with the message of the finding: "argument --basetemp: basetemp must not be empty, the current working directory or any parent directory of it (config source: via PYTEST_ADDOPTS)". `old_template.sh restore` puts the committed template back.

`test_bug_0141_a_project_option_of_pytest_addopts_survives_the_template` passes on the old template too. It guards against stripping too much, not against the bug, and it does that: a fix that dropped `--strict-markers` would fail it. No test hands the template an inherited `--basetemp X` with a space or `-pno:cacheprovider`. The nested test produces only the template's own form `--basetemp=X`. The probe above covers the other forms, so the review records no finding.

## Findings

| Finding                                                                                                                                                                                                                                                      | Artifact                                                              | Category   | Type          | Severity | Basis                                                                                    | Filed as    |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------- | ---------- | ------------- | -------- | ---------------------------------------------------------------------------------------- | ----------- |
| The header of the template still says that each Python process "appends --basetemp", but the process now replaces the inherited `--basetemp` and `-p no:cacheprovider`. Change "appends" to "replaces the inherited ones with".                              | `packages/factory/skills/setup-crap-score/crap-measure-python:97-102` | suggestion | documentation | note     | `in_use: false`, `harms_downstream: false`, `fails_purpose: false`, `raises_cost: false` | report only |
| The row of the Python template in `docs/spec/interface-contracts.md` says the same "appends". The story has no drift report, so the developer agent can add a row for the `domain-modeling-agent` to the drift report of the feature.                        | `docs/spec/interface-contracts.md:404`                                | suggestion | documentation | note     | `in_use: false`, `harms_downstream: false`, `fails_purpose: false`, `raises_cost: false` | report only |
| An unbalanced quote in an inherited `PYTEST_ADDOPTS` makes `shlex.split` raise in `sitecustomize.py`, so coverage never starts and the message hides the cause. A `try` that keeps the inherited value unparsed on `ValueError` would keep coverage running. | `packages/factory/skills/setup-crap-score/crap-measure-python:157`    | suggestion | checking      | note     | `in_use: false`, `harms_downstream: false`, `fails_purpose: false`, `raises_cost: false` | report only |

## Focus areas

| Focus area         | Result                                                                                                                                                                               |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Correctness        | Each pytest process gets exactly one `--basetemp` and one `-p no:cacheprovider`, as BUG-0141 and DEC-85 ask. No form that pytest accepts survives, and no project option is lost.    |
| Clean Architecture | The change stays inside the template. `crap-score` is untouched.                                                                                                                     |
| SOLID              | `sitecustomize.py` keeps its one job: it sets the pytest options of its process and starts coverage.                                                                                 |
| Maintainability    | The loop is fourteen lines inside a string constant, so no linter or type checker reads it. The two new tests and the comment above the constant state why the options are replaced. |
| Consistency        | The new tests follow the helpers `_write_project` and `_run` and the `spec` mark CG-03-IT-10 of the neighbouring tests.                                                              |

## Verification

```bash
uv run --directory /home/matthiasdaues/Documents/datenschoenheit/agent_factory/.current-work/feature/crap-gate-self-host/story/BUG-0141 pytest -q -n 4 tests/factory/test_crap_gate_template.py tests/factory/test_crap_gate_proof.py tests/factory/test_crap_gate_text.py
```

The run passed 101 tests on `028d25a5`. On the template of `571fd124`, the nested test failed and the option test passed. The probes lie in `/tmp/claude-1000/-home-matthiasdaues-Documents-datenschoenheit-agent-factory/89fd1670-49e4-4a59-97db-e1035150aa04/scratchpad/st0451-review/bug0141/`:

- `strip_forms.py` runs the stripping code on the forms of [Checks of the stripping](#checks-of-the-stripping).
- `old_template.sh` puts the old template in place, and `old_template.sh restore` puts the committed one back.
- `repro_template.sh` runs the case of IMPL-0104 on the worktree template.
