---
type: code-review
title: Code review of IMPL-0091, run the measuring and test commands in the caller's environment
date: 2026-11-22
status: defects
reviewer: code-review-agent
findings_filed: 0
story: IMPL-0091
run:
branch: story/IMPL-0091
branch_base: 2ba27fe1e64ff3307e05d345725b2200e8e0af29
branch_head: eb65c7d304f13cd0ed7b6147e4b63f6f8884b282
---

# Code review of IMPL-0091, run the measuring and test commands in the caller's environment

## Verdict

The fix of IMPL-0091 holds only when `crap-score` starts directly, so IMPL-0091 stays open. At the merge, `dispatch merge-story` starts `crap-score` from its own uv environment, and `caller_environment()` does not remove that environment. The review filed no new finding. Instead, it set IMPL-0091 back to `open` and added the repeat pass to the finding file. The parts for IMPL-0092, the `crap-score` skill and the CG-10-IT-04 marker are correct. IMPL-0092 stays `resolved`.

Next, the developer agent fixes the environment that `dispatch` passes on, as the Fix of the repeat pass in IMPL-0091 says. Then this review runs again.

## Scope

The review covers the diff `feature/crap-gate-setup...story/IMPL-0091`, from `2ba27fe1` to `eb65c7d3`, one commit. It changes `crap-score`, the template `crap-measure-python`, the skill `crap-score`, `implementation-agent.md`, `INDEX.yaml`, three test files, IMPL-0091, IMPL-0092 and the new spec-feedback report.

## The fix against the findings

| Case                                                                                      | Result                                                                           |
| ----------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------- |
| IMPL-0091: `crap-score --all` started directly, `TEST_COMMAND` starts `python3 -m pytest` | Exit `0`, both functions `PASS`. The fix holds.                                  |
| IMPL-0091: the same call from an outer `uv run --script` wrapper, as `dispatch` starts it | Exit `2`: `python3` names the wrapper's interpreter, "No module named pytest".   |
| IMPL-0092: step 4d and step 6 of the run by hand                                          | Both start `dispatch merge-story` as a background job and name BR-134. Resolved. |
| Note: `crap-score/SKILL.md` § Report and § Exit codes                                     | The report rule follows DEC-54, and the table lists `128 + n` (DEC-56).          |
| Note: marker of the time-limit test of `dispatch init`                                    | The test carries CG-10-IT-04.                                                    |

The review ran both IMPL-0091 cases on the scratch project of the finding, with the project's interpreter first on `PATH`.

## The three limits of caller_environment()

| Limit                                                                                                   | Judgment                                                                                                                                                                                              |
| ------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| A `VIRTUAL_ENV` that the caller had set is lost, because uv overwrote it and keeps no copy.             | Acceptable. The `bin` folder of an activated environment stays on `PATH`, so `python` still finds it. `uv run` in the project picks `.venv` without the variable.                                     |
| Only the environment of the calling script goes. The uv environment of an outer caller stays on `PATH`. | Not acceptable. `dispatch` is such an outer caller on the main path of every merge, so the gate-check step and the merge give different verdicts for one commit. IMPL-0091 stays open for this limit. |
| The match compares real paths of `sys.prefix/bin`. A Windows layout with `Scripts` is not covered.      | Acceptable. `crap-score` already needs POSIX for `fcntl`, process groups and `prctl`.                                                                                                                 |

## Findings

| Finding                                                                                                                                                                                                                                                                                                                                                               | Category   | Type          | Severity | Basis                                                                                    | ID                                    |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------- | ------------- | -------- | ---------------------------------------------------------------------------------------- | ------------------------------------- |
| Repeat pass: `caller_environment()` leaves the uv environment of `dispatch` on `PATH`. So at the merge, `python3` in `TEST_COMMAND` starts the interpreter of `dispatch`, the gate cannot measure, and `merge-story` sets the story `blocked`. IMPL-0091 stays open with this case.                                                                                   | defect     | interface     | major    | `in_use: false`, `harms_downstream: false`, `fails_purpose: true`, `raises_cost: false`  | [IMPL-0091](../findings/IMPL-0091.md) |
| `implementation-agent.md` now has 20,101 tokens with its inputs, and `index-lint` warns above 20,000 and exits `0`. The two new sentences add 104 tokens, from 19,997. No cut is needed for this unit. Step 6 of the run by hand could point to step 4d in one clause instead of naming BR-134 a second time. A cut of the whole definition belongs to its own story. | suggestion | documentation | note     | `in_use: false`, `harms_downstream: false`, `fails_purpose: false`, `raises_cost: false` | —                                     |

The second copy of `caller_environment()` in the template is the price of BR-130: the template names no Factory code. IMPL-0093 already names the repeated reading of the gate settings.

## Focus areas

| Focus area         | Result                                                                                                                                                                                             |
| ------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Correctness        | The direct call works. The call through `dispatch` does not, as the repeat pass of IMPL-0091 shows.                                                                                                |
| Clean Architecture | The fix lands in the layer that runs the command. The remaining gap lies one layer up, in `dispatch`, which starts `premerge-check` and the `ready` commands.                                      |
| SOLID              | `caller_environment()` has one job, and `run_measure` and `run_tests` call it before they add their own variables.                                                                                 |
| Maintainability    | The new tests check the direct call: a `TEST_COMMAND` that names `python3` (CG-03-IT-01) and an environment without `VIRTUAL_ENV` (CG-04-CT-03). No test starts `crap-score` from a uv-run caller. |
| Consistency        | The skill and the agent definition match the code. The five spec-feedback rows name the drift of BR-129, BR-134 and the QA strategy.                                                               |

## Verification

```bash
uv run --directory .current-work/feature/crap-gate-setup/story/IMPL-0091 pytest tests/factory/test_crap_gate_template.py tests/factory/test_crap_score.py tests/factory/test_crap_gate_dispatch.py tests/factory/test_crap_gate_text.py tests/factory/test_crap_gate_premerge.py -q -n auto
packages/factory/scripts/index-lint --check
```

The test run printed `111 passed in 26.26s`. `index-lint` printed the token warning and exited `0`.
