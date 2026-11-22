---
type: code-review
title: Code review of BUG-0133, name property accessors and skip overload stubs
date: 2026-11-22
status: pass
reviewer: code-review-agent
findings_filed: 0
story: BUG-0133
run:
branch: story/BUG-0133
branch_base: 4d99dc4cb142eb5d3fb1a21af8f8f28188952838
branch_head: f46f328ef663f13d0fd66135dcfeeac715e8335f
---

# Code review of BUG-0133, name property accessors and skip overload stubs

## Verdict

The fix of BUG-0133 passes the code review. A property with a setter and a deleter, and a function with `@overload` stubs, now give one row per name. The four cases in the brief are each handled or refused with exit `2` and a message that names the function. The review files no finding and records two notes. BUG-0133 has `status: resolved`, which the fix commit set, and the review confirms it.

Next, the developer agent commits this report on `story/BUG-0133`. Then the implementation agent runs the gate-check step.

## Scope

The review covers the diff `feature/crap-gate-setup...story/BUG-0133`, from `4d99dc4c` to `f46f328e`, one commit. It changes the template `crap-measure-python`, `tests/factory/test_crap_gate_template.py`, the finding file and the new spec-feedback report. The template now reads the decorators of each function with `ast` and matches them to the radon blocks by the line of `def`.

## The cases

The review ran `function_blocks` of the template on one small file per case.

| Case                                                                               | Names of the rows                                                | Result                                                                     |
| ---------------------------------------------------------------------------------- | ---------------------------------------------------------------- | -------------------------------------------------------------------------- |
| `from typing import overload as ov`, two `@ov` stubs                               | `A.f`, `A.f`, `A.f`                                              | Refused: `crap-score` exits `2` and names `A.f` twice. See the first note. |
| `import typing as t`, one `@t.overload` stub                                       | `g`, `g`                                                         | Refused the same way.                                                      |
| `@functools.cached_property`                                                       | `B.size`                                                         | Handled: one row, no accessor.                                             |
| A property with setter and deleter in a nested class                               | `Outer.Inner.w`, `Outer.Inner.w.setter`, `Outer.Inner.w.deleter` | Handled.                                                                   |
| Getter after its setter: `v = property(_get)`, `@v.setter`, then `@property def v` | `C._get`, `C.v.setter`, `C.v`                                    | Handled: the names differ.                                                 |
| `@p.getter` after `@property def p`                                                | `D.p`, `D.p`                                                     | Refused. See the second note.                                              |
| `def` with arguments over several lines, under `@overload` and `@q.setter`         | `E.q`, `E.q.setter`, `E.h`                                       | Handled: the match by the line of `def` holds for a multi-line signature.  |

## Findings

| Finding                                                                                                                                                                                                                                                                                                                                                                                   | Category   | Type     | Severity | Basis                                                                                    | ID  |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------- | -------- | -------- | ---------------------------------------------------------------------------------------- | --- |
| `OVERLOAD_DECORATORS` holds only the names `overload`, `typing.overload` and `typing_extensions.overload`. An alias such as `from typing import overload as ov` or `import typing as t` leaves the stubs in, so `crap-score` exits `2`. The message names the function, so the User sees the cause. A small step would read the `import` lines of the file and add each alias to the set. | suggestion | checking | note     | `in_use: false`, `harms_downstream: false`, `fails_purpose: false`, `raises_cost: false` | —   |
| `PROPERTY_ACCESSORS` leaves out `getter`. A `@p.getter` that replaces the getter of a property repeats the name `D.p`, so `crap-score` exits `2` and names it. The form is rare. Adding `getter` would give `D.p.getter`.                                                                                                                                                                 | suggestion | checking | note     | `in_use: false`, `harms_downstream: false`, `fails_purpose: false`, `raises_cost: false` | —   |

The three rows of `docs/spec/work/spec-feedback-BUG-0133.md` name the drift of BR-130 and DEC-12, of the feature file, and of the QA strategy. They stay `open` for their owners at the close of the wave.

## Focus areas

| Focus area         | Result                                                                                                                                                                               |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Correctness        | The setter and deleter names follow the qualified name of BR-130 and keep the getter's name. A double name of any other kind still makes `crap-score` exit `2` (DEC-12).             |
| Clean Architecture | The change stays in the template. `crap-score` holds no code of a language, and its duplicate check is unchanged.                                                                    |
| SOLID              | `decorator_names` reads the decorators, and `row_name` decides the name. `function_blocks` only joins them.                                                                          |
| Maintainability    | The template now parses each file twice, once with radon and once with `ast`. The cost is small next to the test run. A future change to the naming has one place to go: `row_name`. |
| Consistency        | The new test carries CG-03-IT-02, as the spec-feedback row says. The header of the template describes the accessor names and the skipped stubs.                                      |

## Verification

```bash
uv run --directory .current-work/feature/crap-gate-setup/story/BUG-0133 pytest tests/factory/test_crap_gate_template.py tests/factory/test_crap_gate_text.py -q -n auto
```

The run printed `45 passed in 20.90s`. A first run failed one text check, because the review's own driver had left a bytecode cache next to the template. The review removed that cache and ran the tests again.
