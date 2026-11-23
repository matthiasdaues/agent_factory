---
type: code-review
title: Code review of SEC-0012, crap-score --base refuses a missing dev
date: 2026-11-23
status: pass
reviewer: code-review-agent
findings_filed: 0
story: SEC-0012
run:
branch: story/SEC-0012
branch_base: f84dbd0c64d309cef740ddf771239fc0016ba910
branch_head: 9a31927b7baa9a1fd65fddd00942a8a09ac4bc41
---

# Code review of SEC-0012, crap-score --base refuses a missing dev

## Verdict

SEC-0012 passes the code review, and the review files no new finding. The status of [SEC-0012](../findings/SEC-0012.md) is now `resolved`. Without a local `dev`, `crap-score --base` exits `2` before it reads the settings or the register. `--all` and `--settings-from-folder` keep the fallback to the folder, so `gate-setup-proof` and setup step 6 still work without `dev`. `premerge-check` gives exit `3` without `dev` in both cases that the coordinator named.

Four texts outside the drift report still describe the old fallback for `--base`, and one new guard does not run the call it guards. The review records these as notes.

Next, the developer agent commits this report and the changed status of SEC-0012 on `story/SEC-0012`. Then the implementation agent runs the gate-check step.

## Scope

The review covers the diff `f84dbd0c..9a31927b`, the one commit `9a31927b`. It changes five files:

- `packages/factory/scripts/crap-score`: `GitRefSource` gets the parameter `judges_story`. When it is set, the key names no branch, and `refs/heads/dev` is missing, the constructor raises. `open_source` sets it to `base is not None and not settings_from_folder`.
- `tests/factory/test_crap_gate_trusted_source.py`: the rows "no branch dev" and "only origin/dev" move from CG-14-IT-06 to CG-14-IT-07 as exit-`2` cases, and two new tests guard the fallback of `--all` and of `--settings-from-folder` without `dev`.
- `tests/factory/test_crap_gate_score.py`: the two CG-05 tests now expect exit `2`, a message that names `dev`, and no report.
- `tests/factory/test_crap_score.py`: one fixture gets a branch `dev`. The orchestrator accepted this.
- `docs/spec/work/spec-feedback-SEC-0012.md`: seven drift rows.

The review read SEC-0012 and DEC-81 in the Appendix of `docs/proposals/crap-gate-setup.md`. QA's probes `probe-move-refs.sh` and `probe-delete-dev.sh` were no longer in the scratchpad folder, so the review wrote its own.

## Checks of crap-score

The probe is `/tmp/claude-1000/-home-matthiasdaues-Documents-datenschoenheit-agent-factory/89fd1670-49e4-4a59-97db-e1035150aa04/scratchpad/sec0012/probe.sh`. It takes the path of `crap-score` and the name of a case. In its repository, `dev` holds the threshold 8, and the story changes `f`, which scores 12. "Before" is `crap-score` at `f84dbd0c`, and "after" is `crap-score` at `9a31927b`.

| Case                                                                                     | Before                                       | After                                               |
| ---------------------------------------------------------------------------------------- | -------------------------------------------- | --------------------------------------------------- |
| `no-dev`: `dev` deleted, `--base feature/x`                                              | folder values, no register, `FAIL`, exit `1` | exit `2`, "git holds no branch dev"                 |
| `origin-dev`: only `refs/remotes/origin/dev`, `--base feature/x`                         | folder values, no register, exit `1`         | exit `2`, the same message                          |
| `register-only`: `dev` deleted, the story commits a register row that accepts `f`        | folder values, no register, exit `1`         | exit `2`, the same message                          |
| `named-missing`: `feature/x` names `integration_branch: main`, and `main` does not exist | exit `2`, "git holds no branch main"         | exit `2`, unchanged (DEC-76)                        |
| `dev-no-yaml`: `dev` without `docs/testing.yaml`                                         | folder values, `FAIL`, exit `1`              | folder values, `FAIL`, exit `1`, unchanged (DEC-69) |
| `dev-no-entry`: `docs/testing.yaml` on `dev` without `gates.crap-score`                  | folder values, `FAIL`, exit `1`              | folder values, `FAIL`, exit `1`, unchanged (DEC-69) |
| `all-no-dev`: `dev` deleted, `--all`                                                     | folder values, no register, exit `1`         | the same, unchanged                                 |
| `sff-no-dev`: `dev` deleted, `--base feature/x --settings-from-folder`                   | folder values, no register, exit `1`         | the same, unchanged                                 |

The settings and the register refuse together, because the constructor of `GitRefSource` raises before `gate_values` or `exceptions` runs. The refusal also comes before any measuring command starts. In the `register-only` case the story's own register row never counts, before or after, because the register comes only from git.

The last row is the call of `gate-setup-proof`, `--base <start> --settings-from-folder`. So the proof still runs in a repository without `dev`. CG-02-IT-12 to CG-02-IT-14 and the tests of `test_crap_gate_proof.py` pass.

## Checks of premerge-check

The second probe is `/tmp/claude-1000/-home-matthiasdaues-Documents-datenschoenheit-agent-factory/89fd1670-49e4-4a59-97db-e1035150aa04/scratchpad/sec0012/premerge_no_dev.py`. It builds the measured repository of `test_crap_gate_premerge.py`, with the real `crap-score` of the worktree as the installed copy, and its story head holds an enabled `gates.crap-score`. It deletes `dev` and runs the real `premerge-check`.

| Story                         | Result                                                                                                                                                                                                                        |
| ----------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `quality-gates: [crap-score]` | Exit `3`. `crap-score` runs, because the field forces it (BR-066), and exits `2` with "git holds no branch dev". The refusal starts with `GATE CANNOT MEASURE: crap-score` and quotes that message. No measuring command ran. |
| no `quality-gates` field      | Exit `3`. `crap-score` does not run, and `crap_cannot_measure` gives the message of DEC-82: "the branch dev does not exist, so no branch decides whether the CRAP gate runs".                                                 |

Both ways now end in exit `3`, so the story becomes `blocked` and not `failed`. A story whose field names `crap-score` while the head holds no entry still gets the refusal of DEC-21 with exit `1`, because the gate is not set up. The commit does not change that path.

## The tests

The two rows that moved to CG-14-IT-07 assert exit `2`, the message, no started measuring command and no report, through the shared body of the test. The guard of `--all` asserts the folder values and the notice of the missing register. The guard of `--settings-from-folder` runs `--all --settings-from-folder` and asserts the folder values. It does not run the call of `gate-setup-proof`, `--base <start> --settings-from-folder`; the probe row `sff-no-dev` covers that call. The CG-05 tests in `test_crap_gate_score.py` assert exit `2`, the message, the absence of the old notice and no report. The new branch `dev` in the fixture of `test_crap_score.py` makes that test judge with `--base` as before. Without the branch, the fixture would now stop at exit `2`, which is not what the test checks.

The fourteen CRAP gate and merge test files passed 536 tests on `9a31927b`.

## Findings

| Finding                                                                                                                                                                                                                                                                                                                                                                                                                      | Artifact                                                              | Category   | Type          | Severity | Basis                                                                                    | Filed as    |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------- | ---------- | ------------- | -------- | ---------------------------------------------------------------------------------------- | ----------- |
| `crap-score/SKILL.md` still says that without the ref of the default `dev`, the values come from the folder, for every call. Under DEC-81 that holds only for `--all` and `--settings-from-folder`. The skill is text that agents execute, so the developer agent can add "with `--all` or `--settings-from-folder`".                                                                                                        | `packages/factory/skills/crap-score/SKILL.md:60`                      | suggestion | documentation | note     | `in_use: false`, `harms_downstream: false`, `fails_purpose: false`, `raises_cost: false` | report only |
| The header of `crap-score` has two problems. § Exceptions still says "Without a branch dev, the output says that no register was read", for every call. § Trusted gate source now reads "With --all, without that ref, or without docs/testing.yaml on the branch …", which can be read as if `--all` were the condition of all three cases.                                                                                 | `packages/factory/scripts/crap-score:63-79`                           | suggestion | documentation | note     | `in_use: false`, `harms_downstream: false`, `fails_purpose: false`, `raises_cost: false` | report only |
| Decision 4 of ADR-0041 still names a missing default `dev` as a fallback to the folder for every call. The drift report does not list ADR-0041.                                                                                                                                                                                                                                                                              | `docs/adr/0041-crap-score-reads-trusted-values-through-one-reader.md` | suggestion | inconsistent  | note     | `in_use: false`, `harms_downstream: false`, `fails_purpose: false`, `raises_cost: false` | report only |
| The guard `test_cg_14_settings_from_folder_without_dev_judges_with_the_folder_settings` calls `--all --settings-from-folder`. `judges_story` is false for `--all` alone, so the guard would pass even if `open_source` ignored the option. The call of `gate-setup-proof` is `--base <start> --settings-from-folder`, and only that call shows that the option keeps the fallback. Change the call of the guard to `--base`. | `tests/factory/test_crap_gate_trusted_source.py`                      | suggestion | test          | note     | `in_use: false`, `harms_downstream: false`, `fails_purpose: false`, `raises_cost: false` | report only |
| arc42 § 5.2.3 still names a missing default `dev` as a fallback to the folder for every call. The drift report does not list arc42.                                                                                                                                                                                                                                                                                          | `docs/arc42/05_building_block_view.md:155`                            | suggestion | inconsistent  | note     | `in_use: false`, `harms_downstream: false`, `fails_purpose: false`, `raises_cost: false` | report only |

## Focus areas

| Focus area         | Result                                                                                                                                                                                                                |
| ------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Correctness        | The code matches DEC-81. DEC-76 and DEC-69 keep their behavior. Both ways through `premerge-check` give exit `3` without `dev`.                                                                                       |
| Clean Architecture | The rule stays in the layer of the trusted gate source. `open_source` knows the call, and the backend takes a flag, as for `refuse_head_tip`.                                                                         |
| SOLID              | `GitRefSource` gets one more flag and no new responsibility. Its constructor now holds three refusals. A later fourth flag would argue for a small object that describes the call, but two flags do not need one yet. |
| Maintainability    | The message names the branch and the reason. The docstrings of `GitRefSource` and `open_source` name DEC-81.                                                                                                          |
| Consistency        | The new parameter follows `refuse_head_tip`. The moved test rows keep the ids of the feature file.                                                                                                                    |

## Verification

```bash
uv run --directory /home/matthiasdaues/Documents/datenschoenheit/agent_factory/.current-work/feature/crap-gate-trusted-source/story/SEC-0012 pytest -q -n auto tests/factory/test_crap_gate_trusted_source.py tests/factory/test_crap_gate_trusted_proof.py tests/factory/test_crap_gate_score.py tests/factory/test_crap_gate_lock.py tests/factory/test_crap_gate_judging.py tests/factory/test_crap_gate_proof.py tests/factory/test_crap_gate_journey.py tests/factory/test_crap_gate_premerge.py tests/factory/test_crap_gate_dispatch.py tests/factory/test_crap_score.py tests/factory/test_premerge_check.py tests/factory/test_run_lifecycle_premerge.py tests/factory/test_crap_gate_text.py tests/factory/test_crap_gate_template.py
```

The run passed 536 tests on `9a31927b`. The two probes are named in [Checks of crap-score](#checks-of-crap-score) and [Checks of premerge-check](#checks-of-premerge-check). The copy of `crap-score` at `f84dbd0c` lies next to them as `old/crap-score`.
