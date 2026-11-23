---
type: code-review
title: Code review of IMPL-0098, the HEAD check of DEC-76 only with --base
date: 2026-11-23
status: pass
reviewer: code-review-agent
findings_filed: 0
story: IMPL-0098
run:
branch: story/IMPL-0098
branch_base: 93de054d9cddd669f4072c7b11d1ddb082412bdd
branch_head: 5cb8843c114de542e2999ab6cbc67419f1c30439
---

# Code review of IMPL-0098, the HEAD check of DEC-76 only with --base

## Verdict

IMPL-0098 passes the code review, and the review files no new finding. The fix closes [IMPL-0098](../findings/IMPL-0098.md), so its status is now `resolved`. The refusal of a named branch whose tip is `HEAD` still holds with `--base`, and that includes a call that also passes `--settings-from-folder`.

Next, the developer agent commits this report and the changed status of IMPL-0098 on `story/IMPL-0098`. Then the implementation agent runs the gate-check step.

## Scope

The review covers the diff `93de054d..5cb8843c`, the one commit `5cb8843c`. It changes three files:

- `packages/factory/scripts/crap-score`: `GitRefSource` gets the parameter `refuse_head_tip`, and `open_source` passes `base is not None`.
- `tests/factory/test_crap_gate_trusted_source.py`: the new test `test_cg_14_all_on_the_checked_out_integration_branch_judges_with_its_values` for the `--all` row of CG-14-IT-08.
- `docs/spec/work/spec-feedback-IMPL-0098.md`: one drift row for BR-128, § Trusted gate source and § `docs/factory-settings.yaml`. The owner is the domain-modeling agent.

The review read DEC-79 in the Appendix of `docs/proposals/crap-gate-setup.md`, the finding IMPL-0098, and the call of `crap-score` in `gate-setup-proof`.

## Checks

Each case ran in a scratch repository under the scratchpad folder, with the `crap-score` of the story worktree.

| Case                                                                                                                               | Result                                                                                                                                                                              |
| ---------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `setup-step6.sh key`: `--all` on `main` with `integration_branch: main`, which is the reproduction of IMPL-0098                    | Exit `1` and the report. `main` holds no `docs/testing.yaml` yet, so the values come from the folder, and the output names that cause. Before the fix, the same case gave exit `2`. |
| `setup-step6.sh nokey`: the same case without the key                                                                              | Exit `1`, unchanged.                                                                                                                                                                |
| `own-branch.sh`: `--base feature/x`, whose `docs/factory-settings.yaml` names `story/ST-1`, with `HEAD` at the tip of `story/ST-1` | Exit `2` with "names the branch story/ST-1, whose tip is HEAD". The refusal of DEC-76 holds with `--base`.                                                                          |
| `own-branch.sh --settings-from-folder`: the same case with the option                                                              | Exit `2` with the same message. With the option, the key comes from the folder, and `base` is set, so the check runs.                                                               |

The row "own branch" of CG-14-IT-07 runs the call of the gate-check step, `--base feature/login`, and asserts "names the branch story/ST-0350, whose tip is HEAD" and exit `2`. So the test suite would catch a fix that dropped the check for `--base`. The new CG-14-IT-08 test runs `--all` on the checked-out `main` with the threshold 8 on `main` and 30 uncommitted in the folder. Both functions fail, so the test also shows that the run reads `main` and not the folder.

## The developer's open question

The developer asked whether `--base` with `--settings-from-folder` should keep the check, and said that no caller passes both options. That premise does not hold: `gate-setup-proof` passes both, `--base <start>` and `--settings-from-folder`, in `run_gate`. The check still does no harm there. The proof judges its own planted commit, whose parent is `<start>`, so the tip of a named branch is never the proof's `HEAD`. CG-02-IT-12 to CG-02-IT-14 pass with the fix.

The review recommends keeping the check for that combination. A call with `--base` judges a commit against a base, and the check costs one `git rev-parse`. DEC-79 says "only with `--base`" and so covers the combination as built. No change and no finding follow.

## Findings

| Finding                                                                                                                                                                                                                                             | Artifact                                        | Category   | Type      | Severity | Basis                                                                                    | Filed as    |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------- | ---------- | --------- | -------- | ---------------------------------------------------------------------------------------- | ----------- |
| `refuse_head_tip` defaults to `True`. Only `open_source` builds `GitRefSource` outside the tests, and it always passes the value. So a later caller that leaves the parameter out gets the stricter check. This matches DEC-76 and needs no change. | `packages/factory/scripts/crap-score:1120-1123` | suggestion | interface | note     | `in_use: false`, `harms_downstream: false`, `fails_purpose: false`, `raises_cost: false` | report only |

## Focus areas

| Focus area         | Result                                                                                                                                                                                                    |
| ------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Correctness        | The code matches DEC-79. A named branch that git does not hold still exits `2` for every call. The drift row carries DEC-79 to the three places of the specification that state the check for every call. |
| Clean Architecture | The decision stays at the layer that knows the call: `open_source` reads `base`, and the backend takes a flag. The gate logic in `main` is unchanged.                                                     |
| SOLID              | `GitRefSource` gets one parameter and no new responsibility.                                                                                                                                              |
| Maintainability    | The docstrings of `GitRefSource` and `open_source` name DEC-79 and the reason. The new test names the Example row that it covers.                                                                         |
| Consistency        | The parameter follows the pattern of `settings_from_folder`, a keyword parameter with a default value. The test uses the `repo` fixture and the helpers of the file.                                      |

## Verification

```bash
uv run --directory /home/matthiasdaues/Documents/datenschoenheit/agent_factory/.current-work/feature/crap-gate-trusted-source/story/IMPL-0098 pytest -q -n auto tests/factory/test_crap_gate_trusted_source.py tests/factory/test_crap_gate_trusted_proof.py tests/factory/test_crap_gate_score.py tests/factory/test_crap_gate_proof.py tests/factory/test_crap_gate_premerge.py
```

The run passed 164 tests on `5cb8843c`. The scripts of the checks are `/tmp/claude-1000/-home-matthiasdaues-Documents-datenschoenheit-agent-factory/89fd1670-49e4-4a59-97db-e1035150aa04/scratchpad/feature-review/setup-step6.sh` and `/tmp/claude-1000/-home-matthiasdaues-Documents-datenschoenheit-agent-factory/89fd1670-49e4-4a59-97db-e1035150aa04/scratchpad/feature-review/own-branch.sh`. Each takes the path of `crap-score` as its first argument.
