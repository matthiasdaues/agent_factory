---
type: code-review
title: Code review of BUG-0135, count an overload as a stub only through a typing import
date: 2026-11-22
status: pass
reviewer: code-review-agent
findings_filed: 0
story: BUG-0135
run:
branch: story/BUG-0135
branch_base: c2fab60c4fd5a7f6a6c3db973a56049d89cd3d92
branch_head: 3c07cf0f730073899be5282bc0a7ef848dc766a1
---

# Code review of BUG-0135, count an overload as a stub only through a typing import

## Verdict

The fix of BUG-0135 passes the code review. A function under the `overload` of another library now gets its row, and a stub under the `overload` of `typing` or `typing_extensions` gets none. The review files no finding and records one note on a file that rebinds `overload` after it imports the one of `typing`. BUG-0135 has `status: resolved`, which the fix commit set, and the review confirms it.

Next, the developer agent commits this report on `story/BUG-0135`. Then the implementation agent runs the gate-check step.

## Scope

The review covers the diff `feature/crap-gate-setup...story/BUG-0135`, from `c2fab60c` to `3c07cf0f`, one commit. It changes `overload_names` and the header of the template `crap-measure-python`, `tests/factory/test_crap_gate_template.py`, the finding file, and the new spec-feedback report.

## The cases

The review ran `function_blocks` of the template on one small file per case.

| Case                                                                                                                              | Rows            | Result                                                              |
| --------------------------------------------------------------------------------------------------------------------------------- | --------------- | ------------------------------------------------------------------- |
| `from mylib import overload`, then `@overload def e`                                                                              | `e`             | Correct: the function runs and gets its row.                        |
| `import typing as t`, a stub `@t.overload def f` and the implementation `f`                                                       | `f`             | Correct: one row for the implementation.                            |
| A local `def overload(f)` and no import of `typing`, then `@overload def a`                                                       | `overload`, `a` | Correct: both functions run and get their rows.                     |
| `from typing import overload` inside `if TYPE_CHECKING:`, a local `def overload` under `else:`, a stub and the implementation `d` | `overload`, `d` | Correct: the stub gets no row, and both functions that run get one. |
| `from typing import overload`, then a local `def overload(f)`, then `@overload def b`                                             | `overload`      | `b` runs and gets no row. See the note.                             |
| `from typing import overload`, then `from mylib import overload`, then `@overload def c`                                          | none            | `c` runs and gets no row. See the note.                             |

## Findings

| Finding                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | Category   | Type     | Severity | Basis                                                                                    | ID  |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------- | -------- | -------- | ---------------------------------------------------------------------------------------- | --- |
| `overload_names` collects the import names with `ast.walk` and ignores the order of the bindings. When a file imports the `overload` of `typing` and later rebinds the name, by a `def overload` or by `from mylib import overload`, the functions under the later binding run but get no row. The gate then never judges them. A file that binds `overload` twice at module level is rare. A later change could walk the module body in order and let the last binding of the name win, keeping a binding under `if TYPE_CHECKING:` as a stub binding. | suggestion | checking | note     | `in_use: false`, `harms_downstream: false`, `fails_purpose: false`, `raises_cost: false` | —   |

The rows of `docs/spec/work/spec-feedback-BUG-0135.md` stay `open` for their owners at the close of the wave.

## Focus areas

| Focus area         | Result                                                                                                                                                           |
| ------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Correctness        | The table of cases shows the import forms of the brief and the `TYPE_CHECKING` guard. Only a rebound name of the note gives a missing row.                       |
| Clean Architecture | The change stays in the template. `crap-score` and its duplicate check are unchanged.                                                                            |
| SOLID              | `overload_names` decides which decorator names mark a stub, and `row_name` uses that set.                                                                        |
| Maintainability    | The constant `OVERLOAD_DECORATORS` is gone, so the names come from one place: the imports of the file. The header lists each import form with the name it gives. |
| Consistency        | The new tests cover the import forms of the header, and they follow the style of the BUG-0133 tests.                                                             |

## Verification

```bash
uv run --directory .current-work/feature/crap-gate-setup/story/BUG-0135 pytest tests/factory/test_crap_gate_template.py tests/factory/test_crap_gate_text.py -q -n auto
```

The run printed `49 passed in 4.71s`.
