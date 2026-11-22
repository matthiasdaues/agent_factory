---
type: code-review
title: Code review of IMPL-0090, hand files and exclude to the measuring command
date: 2026-11-22
status: pass
reviewer: code-review-agent
findings_filed: 0
story: IMPL-0090
run:
branch: story/IMPL-0090
branch_base: fe8fd5182af5abb5a0b21ce71f830dcf4a8b4eed
branch_head: 87eb47fe99605bef86a25784cffd767a66d0eaa9
---

# Code review of IMPL-0090, hand files and exclude to the measuring command

## Verdict

The fix of IMPL-0090 passes the code review. It holds: an untested script without a file ending no longer stops a measure that leaves the script out. The review files no finding and records one note. IMPL-0090 has `status: resolved`, which the fix commit set, and the review confirms it.

Next, the developer agent commits this report on `story/IMPL-0090`. Then the implementation agent runs the gate-check step.

## Scope

The review covers the diff `feature/crap-gate-setup...story/IMPL-0090`, from `fe8fd518` to `87eb47fe`, one commit. It changes `crap-score`, the template `crap-measure-python`, the skills `crap-score` and `setup-crap-score`, `INDEX.yaml`, two test files, the finding file, and the new spec-feedback report. The fix follows DEC-65 in `docs/proposals/crap-gate-setup.md`.

## The fix against the finding

| Case                                                        | Before the fix         | After the fix                                                    |
| ----------------------------------------------------------- | ---------------------- | ---------------------------------------------------------------- |
| `exclude: ["tools/**"]`, untested script `tools/helper`     | `crap-score` exits `2` | `crap-score` exits `0` and judges `a.py` and `tests/test_a.py`   |
| `files: "a.py"`, untested script `tools/helper`             | `crap-score` exits `2` | `crap-score` exits `0` and judges only `a.py`                    |
| `files: "**"`, no `exclude`, untested script `tools/helper` | `crap-score` exits `2` | `crap-score` exits `2` and names `tools/helper`, as BR-130 wants |
| An `exclude` pattern with a line break                      | No check               | `crap-score` exits `2` and names the measure and the field       |

The review ran each case through `crap-score --all` of the branch on the scratch project of IMPL-0090. The template ran with `TEST_COMMAND` set to an absolute interpreter path, because IMPL-0091 is still open.

The copy of `glob_match` in the template matches `dispatch_lib.glob_match`. The review compared both on 60,005 pairs of pattern and path: random pairs over the characters `a`, `b`, `/`, `.`, `*`, `**` and `?`, the examples of BR-131, and the empty pattern. No pair gave a different answer.

## Findings

| Finding                                                                                                                                                                                       | Category   | Type          | Severity | Basis                                                                                    | ID  |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------- | ------------- | -------- | ---------------------------------------------------------------------------------------- | --- |
| The new message of `crap-score` reads "has a exclude pattern with a line break". The article does not fit `exclude`. The wording "has a pattern in {key} with a line break" fits both fields. | suggestion | documentation | note     | `in_use: false`, `harms_downstream: false`, `fails_purpose: false`, `raises_cost: false` | —   |

The three rows of `docs/spec/work/spec-feedback-IMPL-0090.md` name the drift of BR-130 and of the two contracts in `docs/spec/interface-contracts.md`. They stay `open` for the domain-modeling agent at the close of the wave.

## Focus areas

| Focus area         | Result                                                                                                                                                                                                           |
| ------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Correctness        | The table above shows the four cases. `crap-score` still applies `files` and `exclude` to the rows (DEC-10), so a command that ignores the variables changes no verdict.                                         |
| Clean Architecture | The template keeps its own copy of `glob_match`, so it names no path under `.agent-factory/` (BR-130). The variables are the only new contract between `crap-score` and the command.                             |
| SOLID              | `kept` and `patterns` each have one job, and `code_files` calls them before the language check.                                                                                                                  |
| Maintainability    | The glob dialect now lives in two places, the template and `dispatch_lib.py`. The template must stand alone, so the copy is the price of BR-130. No test compares the two copies; the review compared them once. |
| Consistency        | Both skills describe the variables in the words of DEC-65, and the template header names the dialect of BR-131.                                                                                                  |

## Verification

```bash
uv run --directory .current-work/feature/crap-gate-setup/story/IMPL-0090 pytest tests/factory/test_crap_gate_template.py tests/factory/test_crap_score.py tests/factory/test_crap_gate_score.py tests/factory/test_crap_gate_proof.py tests/factory/test_crap_gate_text.py -q -n auto
```

The run printed `131 passed in 15.41s`.
