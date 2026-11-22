---
type: fagan-review
title: Fagan inspection of feature/crap-gate-setup
date: 2026-11-22
status: pass
reviewer: qa-agent
findings_filed: 0
story:
run: feature/crap-gate-setup
branch: feature/crap-gate-setup
branch_base: 9ea68284539b1f175dea21617c125a578e3db474
branch_head: 100ea97d4fdcbb2c057d77e9a9fd2efc57b8a39f
---

# Fagan inspection of feature/crap-gate-setup

## Result

The inspection files no finding of its own. Two defects of the Python template came out of the bug hunt, and the bug-hunt report holds them: [BUG-0133](../findings/BUG-0133.md) and [BUG-0134](../findings/BUG-0134.md). Both are `major` and block the merge into `dev`. The inspection records two notes below.

Next, the implementation agent adds BUG-0133 and BUG-0134 as units of work with `dispatch add <finding-id>`.

## Scope

The inspection covers `git diff 9ea68284..100ea97d` of `feature/crap-gate-setup`: 133 files, the stories ST-0433 to ST-0448, and the finding fixes IMPL-0090 and IMPL-0091. It read `crap-score`, `gate-setup-proof` and the template `crap-measure-python` in full, and the diffs of `premerge-check`, `dispatch`, `dispatch_lib.py`, `finding-lint` and `guard-human-fields`.

The inspection checked them against the Rules of `docs/spec/features/crap-gate-setup.feature`, BR-127 to BR-139, the decisions DEC-01 to DEC-66 of `docs/proposals/crap-gate-setup.md`, and the Contract Owners and Boundary Cases of `docs/spec/work/crap-gate-setup-qa-strategy.md`. The decisions count as settled. The inspection did not file again what the code review of the feature already holds: IMPL-0083, IMPL-0090 to IMPL-0093 and its notes. ST-0449 enables the gate in this repository after the merge (DEC-49), so its rows CG-12-LN-06 and CG-13 are out of scope.

## Acceptance test

The QA strategy sets the acceptance layer to `out`, because the project declares no Gherkin runner. Each Scenario traces to a pytest test through the `spec` marker. The review ran the fourteen test files of the feature and of the changed scripts:

```bash
uv run --directory .current-work/feature/crap-gate-setup/invocation pytest tests/factory/test_crap_gate_template.py tests/factory/test_crap_score.py tests/factory/test_crap_gate_score.py tests/factory/test_crap_gate_proof.py tests/factory/test_crap_gate_premerge.py tests/factory/test_crap_gate_dispatch.py tests/factory/test_crap_gate_text.py tests/factory/test_crap_gate_judging.py tests/factory/test_crap_gate_lock.py tests/factory/test_crap_gate_journey.py tests/factory/test_guard_human_fields.py tests/factory/test_premerge_check.py tests/factory/test_finding_lint.py tests/factory/test_finding_stop.py -q -n auto -p no:cacheprovider
```

The run printed `879 passed in 57.24s`.

## Story checks

Every story ST-0433 to ST-0448 traces a Rule of `crap-gate-setup.feature`, so each one is `.feature`-governed. Such a story needs no `test-design-pass` field, and none is missing. No story has a `tests:` field. The code review of the feature compared every Rule with its tests and found a test ID for every contract row outside ST-0449, and this inspection found no contract without a test. The testability probe in `backlog/epics-crap-gate-setup.md` flags two red flags, and both have tests at story level. The refusal in the gate-check step has the text check CG-11-LN-01 and the merge check CG-11-IT-03. The agent steps of the setup skill have the text checks CG-01-LN-01 to CG-01-LN-05, and the proof stands behind them.

## Findings

| Finding                                                                                                                                                                                                                                                                                                                                                                                                               | Artifact                                       | Category   | Type      | Severity | Filed as      |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------- | ---------- | --------- | -------- | ------------- |
| `check_story_gates` returns the line `BLOCK ready-commands: ...` with the value `True`, so `main` counts a refusal as a passed check and then exits `3` through `unmeasured`. The comment explains the trick, but a reader of the result list sees a `BLOCK` line that passes. A third value, such as `cannot_measure`, would let `main` print the line and leave the passed checks alone. `basis`: all four `false`. | `packages/factory/scripts/premerge-check:1325` | suggestion | structure | note     | `report only` |
| `crap-score` keeps the score exact for any complexity up to the float maximum (`SCORE_CONTEXT`, 4,000 digits), but `report_row` writes the score as `float`. Above a complexity of about 1e154 the report then holds `Infinity`. The verdict stays right. The bug-hunt report names the observed case. `basis`: all four `false`.                                                                                     | `packages/factory/scripts/crap-score:103-106`  | suggestion | algorithm | note     | `report only` |

## Inspection by focus area

**Correctness.** `crap-score` implements BR-127 to BR-133 as written: the call check of `--base` and `--all`, the settings without a default, the shape check of each row before the filter (DEC-42), the duplicate check across measures (DEC-29), the diff against the merge base, the deletion rules (DEC-37, DEC-51), the half-up rounding (DEC-36), and the register from `refs/heads/dev` only. `premerge-check` passes `--base <target>` and the report folder of the primary checkout, and exits `3` only when every other check passed (BR-136, DEC-29). `dispatch merge-story` turns exit `3` into `blocked` with the exact reason, and `resume-gates` takes the guarded edge only for that reason and an existing branch (BR-135, DEC-63). `gate-setup-proof` refuses a wrong plant before it measures, and its four checks match BR-138. The template matches the Rows and Duty of BR-130 apart from the two cases of BUG-0133 and BUG-0134.

**Clean Architecture.** `crap-score` holds no code of a language, and the template names no path under `.agent-factory/` (BR-130). The glob dialect lives once in `dispatch_lib.py`. The template keeps its own copy of `glob_match` and `caller_environment` on purpose, so it runs without Factory code.

**SOLID.** No new violation with a concrete cost. IMPL-0093 already names the four readers of `gates.crap-score`.

**Maintainability.** The new functions are short, and their names say what they do. The stop of a process group exists in four copies: `crap-score`, `premerge-check`, `dispatch_lib.py`, and the signal code of `gate-setup-proof`. IMPL-0083 and IMPL-0093 cover them, so the inspection files nothing new.

**Consistency.** The scripts use the existing `run_git` and `git` wrappers, the ledger transitions, and the report format. The guard adds the register as its own kind, next to finding files, register files, and proposals.

**YAGNI.** No unused abstraction and no speculative setting. Each new option, `--report-dir`, `STORY_ID`, `GATE_FILES` and `GATE_EXCLUDE`, has a caller and a decision (DEC-27, DEC-65). The second note above names the one place where extra precision buys nothing in the report.
