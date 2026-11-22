---
type: code-review
title: Code review of BUG-0134, count a one-line function as covered only after a call
date: 2026-11-22
status: pass
reviewer: code-review-agent
findings_filed: 0
story: BUG-0134
run:
branch: story/BUG-0134
branch_base: 03e0a0f8827207479a2cde2758798359bc1497f3
branch_head: 8328a9d154a6a5fb95f713ea203ee5de88a81d8a
---

# Code review of BUG-0134, count a one-line function as covered only after a call

## Verdict

The fix of BUG-0134 passes the code review. An untested one-line function now reports 0 % coverage, and a tested one reports 100 %. The line ratio of a function with a body of several lines stays the same with `branch = True`. The review accepts both stated limits and files no finding. BUG-0134 has `status: resolved`, which the fix commit set, and the review confirms it.

Next, the developer agent commits this report on `story/BUG-0134`. Then the implementation agent runs the gate-check step.

## Scope

The review covers the diff `feature/crap-gate-setup...story/BUG-0134`, from `03e0a0f8` to `8328a9d1`, one commit. It changes the template `crap-measure-python`, `tests/factory/test_crap_gate_template.py`, the finding file, and the new spec-feedback report.

## The cases

The review ran the template of the branch and the template of `feature/crap-gate-setup` on one small project. The project's tests ran under Python 3.14.0. The tests called some functions and left others out.

| Function in the project                                  | Called by the tests        | Feature branch | Fix        |
| -------------------------------------------------------- | -------------------------- | -------------- | ---------- |
| `def one_called(a): return a or 0`                       | yes                        | 100 %          | 100 %      |
| `def one_uncalled(a): return a or 0`                     | no                         | 100 %          | 0 %        |
| `async def aone_called(a): return a or 0`                | yes, through `asyncio.run` | 100 %          | 100 %      |
| `async def aone_uncalled(a): return a or 0`              | no                         | 100 %          | 0 %        |
| `def meth_called(self, a): return a or 0` in class `K`   | yes                        | 100 %          | 100 %      |
| `def meth_uncalled(self, a): return a or 0` in class `K` | no                         | 100 %          | 0 %        |
| `def one_raises(a): raise ValueError(a)`                 | yes, under `pytest.raises` | 100 %          | 0 %, limit |
| `def lone(a): return a or 0`, the only line of its file  | yes                        | 100 %          | 0 %, limit |
| `multi`, nine lines, two `if` and a `for`, one path run  | yes                        | 28.57 %        | 28.57 %    |
| `square = lambda x: x * x`                               | yes                        | no row         | no row     |
| `class Bare: x = 1`                                      | —                          | no row         | no row     |

So `branch = True` does not change the line ratio of `multi`. The fix keeps `executed_lines` and `missing_lines` and only reads the arcs in addition. A lambda and a class body give no row, because radon lists neither as a function, on both branches. That matches BR-130, which asks for one row per function.

## The two limits

| Limit                                                                                 | Effect on the gate                                                                                                                                                                                                                                                                 | Judgment   |
| ------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------- |
| A call that ends in an exception leaves no exit arc under `sys.monitoring`, so 0 %.   | A one-line function that only raises has no branch and complexity `1`, so it scores `1 × 1 + 1 = 2` at 0 %. That passes every threshold of 2 or more. A one-line function with branches that is tested only through an exception is rare.                                          | Acceptable |
| A lone one-line function on line 1 of its file gets 0 %, also when the tests call it. | At complexity `c` it scores `c × c + c`, such as 6 for `return a or 0`. A threshold below that fails a tested function. Such a file is rare, and the stakeholder can accept the function in the exceptions register, or the project can add a line, such as a docstring, above it. | Acceptable |

The header of the template states both limits, so a User who meets one finds the cause there.

## Findings

The review files no finding. Both limits are described above as accepted behavior and need no change in this unit.

The rows of `docs/spec/work/spec-feedback-BUG-0134.md` stay `open` for their owners at the close of the wave.

## Focus areas

| Focus area         | Result                                                                                                                                                                                                               |
| ------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Correctness        | The table of cases shows the fixed coverage for plain, async and method one-liners and the unchanged ratio of a longer function. The template no longer reports an untested function as covered, as BR-130 requires. |
| Clean Architecture | The change stays in the template. `crap-score` reads `coverage_pct` as before.                                                                                                                                       |
| SOLID              | `code_start` finds the first line of a function, `was_called` reads the arcs, and `function_coverage` decides the share.                                                                                             |
| Maintainability    | The rule for a function without its own body line sits in one place, `function_coverage`, and the header names it with its two limits.                                                                               |
| Consistency        | `function_blocks` now returns three values. Its only caller, `measure`, unpacks all three.                                                                                                                           |

## Verification

```bash
uv run --directory .current-work/feature/crap-gate-setup/story/BUG-0134 pytest tests/factory/test_crap_gate_template.py tests/factory/test_crap_gate_text.py tests/factory/test_crap_gate_proof.py -q -n auto
```

The run printed `90 passed in 10.19s`.
