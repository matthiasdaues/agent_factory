---
type: code-review
title: Code review of BUG-0137, a broken docs/testing.yaml stops the merge without a traceback
date: 2026-11-23
status: defects
reviewer: code-review-agent
findings_filed: 0
story: BUG-0137
run:
branch: story/BUG-0137
branch_base: 99064e9a87bbf9223fe548831d7f383bc07dc462
branch_head: 6af49ba1b15159e25a5ecaf5f6d07cfc9848d1b5
---

# Code review of BUG-0137, a broken docs/testing.yaml stops the merge without a traceback

## Verdict

BUG-0137 does not pass the code review, and the finding stays `open`. The fix handles every case that DEC-83 lists for `dev`, and the YAML cases at the story head. Two malformed story heads still break DEC-83:

- A `docs/testing.yaml` that is not valid UTF-8 ends in a traceback.
- A `gates.crap-score` that is no mapping is not refused. Without `dev`, it even gives exit `0`.

A scratch run of the real `premerge-check` reproduces both. Both gaps are the defect of BUG-0137, on the same lines, so the review files no new finding. It added the reproductions and the corrected fix to [BUG-0137](../findings/BUG-0137.md).

Next, the developer agent extends `story_testing_yaml_refusal` and `_read_testing_yaml` as BUG-0137 now describes, and adds both cases to `HEAD_BROKEN`. Then the code review of BUG-0137 runs again.

## Scope

The review covers the diff `99064e9a..6af49ba1`, the two commits `fd379adf` and `6af49ba1`. They change three files:

- `packages/factory/scripts/premerge-check`:
  - The new exception `BrokenTestingYaml` is raised by `_parse_testing_yaml` and by `trusted_crap_entry`.
  - The new function `story_testing_yaml_refusal` checks the file of the story head.
  - `crap_cannot_measure` turns a broken file of `dev` into exit `3`.
  - `resolve_gates` drops the gate when the file of `dev` is broken, so that `crap_cannot_measure` names it.
  - `main` runs the refusal before the semantic gates.
- `tests/factory/test_crap_gate_premerge.py`: 15 new tests, which are the five broken shapes of `DEV_BROKEN` and of `HEAD_BROKEN` and the cases around them.
- `docs/spec/work/spec-feedback-BUG-0137.md`: the drift rows of DEC-83.

## The probe

QA's probe `repeat-premerge.py` calls three functions of `premerge-check` directly. The review wrote an end-to-end probe instead: `/tmp/claude-1000/-home-matthiasdaues-Documents-datenschoenheit-agent-factory/89fd1670-49e4-4a59-97db-e1035150aa04/scratchpad/bug0137/probe.py`. It builds the repository of `_build_repo` from `test_crap_gate_premerge.py`, whose built-in gates are recording stubs, and runs the real `premerge-check` of the worktree. "Stub calls" names the gates that `premerge-check` started.

| Case                                                   | Exit | Stub calls   | Traceback | What the output says                                                                          |
| ------------------------------------------------------ | ---- | ------------ | --------- | --------------------------------------------------------------------------------------------- |
| Head and `dev` both invalid YAML                       | `1`  | none         | no        | `BLOCK testing-yaml: docs/testing.yaml of ST-0350 is not valid YAML`                          |
| Head file is a date, `2026-11-23`                      | `1`  | none         | no        | the refusal "is empty or no mapping (expected mapping, got date)"                             |
| Head file is a number, `5`                             | `1`  | none         | no        | the refusal "… got int"                                                                       |
| Head `gates:` with no value, `dev` enabled             | `1`  | none         | no        | "no entry gates.crap-score", because `gates:` counts as no gates and `dev` enables the gate   |
| Head with a gate key `1`, `dev` enabled                | `1`  | `crap-score` | no        | "gates.1 … has no command", the refusal of an unknown gate                                    |
| Head `measures: 5` or `measures: ["x"]`, `dev` enabled | `0`  | `crap-score` | no        | The stub passes. The real `crap-score` exits `2` on the shape (BR-128), which gives exit `3`. |
| Head `mutation-testing: "on"`, `dev` enabled           | `0`  | `crap-score` | no        | mutation-testing counts as not set up; see the notes                                          |
| `dev` file is a date                                   | `3`  | none         | no        | `GATE CANNOT MEASURE: crap-score`, naming the file of `dev`                                   |
| `dev` `gates.crap-score: 5`                            | `3`  | none         | no        | the same                                                                                      |
| **Head `gates.crap-score: 5`, no `dev`**               | `0`  | none         | no        | `PASS semantic-gates: no gate applies`, and the merge passes                                  |
| **Head `gates.crap_score: "on"` (old key), no `dev`**  | `0`  | none         | no        | the same                                                                                      |
| Head `gates.crap-score: 5`, `dev` enabled              | `1`  | none         | no        | "no entry gates.crap-score", which blocks but does not name the broken entry                  |
| **Head not valid UTF-8**                               | `1`  | none         | **yes**   | `UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff`                                    |

### Gap 1: a story head that is not valid UTF-8 ends in a traceback

`story_testing_yaml_refusal` reads the file with `path.read_text()` and catches only `OSError`. A `UnicodeDecodeError` is a `ValueError`, so it escapes, and `premerge-check` ends with a traceback. The exit code is `1`, so the merge stops, but DEC-83 asks for a refusal without a traceback. `_read_testing_yaml` has the same narrow clause. Called directly on the same folder, both `gate_entries` and `story_testing_yaml_refusal` raise `UnicodeDecodeError`. The commit before this fix, `99064e9a`, raises the same error in `gate_entries`. The clause became narrow with SEC-0011, so this gap is older than the fix.

### Gap 2: a gates.crap-score that is no mapping is not refused at the story head

DEC-83 asks for a refusal with exit `1` when `gates.crap-score` is no mapping at the story head. `story_testing_yaml_refusal` calls only `_parse_testing_yaml`, which checks the file and the `gates` section. It does not call `_crap_score_is_broken`, so `crap-score: 5` passes the check. `_entries_of` then skips the value, and the head counts as without an entry. Without `dev`, `crap_cannot_measure` sees no entry, so the merge passes with exit `0`. The same story with a real entry gets exit `3` (DEC-82). So the shape of the entry decides whether the story merges. With an enabled `dev`, the merge stops with exit `1`, but the refusal says that the entry is missing.

```text
the story writes gates.crap-score: 5 in a repository without dev
        ↓
story_testing_yaml_refusal parses the file and checks only the gates section
        ↓
_entries_of skips the value, so the head has no entry
        ↓
crap_cannot_measure finds no dev and no head entry, so it returns None
        ↓
premerge-check passes with exit 0, where a real entry gives exit 3
```

The corrected fix is in [BUG-0137](../findings/BUG-0137.md).

## The order of the checks in main

`main` runs `story_testing_yaml_refusal` first. A broken file at the head therefore gives exit `1`, and the semantic gates do not run. `crap_cannot_measure` does not run either, so a broken file of `dev` is not named in the same run. The probe row "head and `dev` both invalid YAML" shows this: exit `1`, and the output names only the file of the story.

This order matches BR-136: exit `3` applies only when every other check passed, and a failed check gives exit `1`, because the code must change anyway. The story repairs its file, the next run of `premerge-check` reaches the read of `dev`, and that run gives exit `3`. So the broken file of `dev` is not lost, only reported one run later. The review records this as a note.

## The feature merge

The new code runs only in the block for a story branch, where `story_id` is set. A merge of the feature branch into `dev` does not enter that block, so no semantic gate and no read of `docs/testing.yaml` runs there. `test_cg_08_the_feature_merge_runs_no_crap_score` passes.

## Findings

| ID or finding                                                                                                                                                                                                                                                                                                     | Artifact                                            | Category   | Severity | Status or filed as | Blocks |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------- | ---------- | -------- | ------------------ | ------ |
| [BUG-0137](../findings/BUG-0137.md): a story head that is not valid UTF-8 ends in a traceback, and a head `gates.crap-score` that is no mapping is not refused. Without `dev`, the second gives exit `0`. Fix: extend `story_testing_yaml_refusal` and `_read_testing_yaml`, and add both cases to `HEAD_BROKEN`. | `packages/factory/scripts/premerge-check:956-978`   | defect     | major    | `open`, annotated  | yes    |
| A broken head file hides a broken file of `dev` for one run, because the refusal of the head stops the run before `crap_cannot_measure`. This follows BR-136 and costs one more run, so nothing needs to change.                                                                                                  | `packages/factory/scripts/premerge-check:1650-1662` | suggestion | note     | report only        | no     |
| A head `gates.mutation-testing` that is no mapping counts as "not set up", and the gate does not run. DEC-80 and DEC-83 cover only `crap-score`, so this stays the behavior of every gate except `crap-score`. A story can turn mutation testing off the same way with `enabled: false`.                          | `packages/factory/scripts/premerge-check:862-884`   | suggestion | note     | report only        | no     |
| A non-boolean `enabled` on `dev`, such as text, counts as not enabled, and the gate does not run. A story cannot change `dev`, so this is a setup fault of a person and not a bypass.                                                                                                                             | `packages/factory/scripts/premerge-check:895-906`   | suggestion | note     | report only        | no     |

BUG-0137 keeps the severity and the class that QA gave it. This review changes only the record of the fix.

## Focus areas

| Focus area         | Result                                                                                                                                                                                                                |
| ------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Correctness        | Every case of DEC-83 on `dev` works. At the head, the YAML cases and the `gates` section work. The UTF-8 case and a `gates.crap-score` that is no mapping do not work.                                                |
| Clean Architecture | One parser serves the head and `dev`. The decision between exit `1` and exit `3` stays in `main` and `crap_cannot_measure`.                                                                                           |
| SOLID              | `_parse_testing_yaml` checks the shape, `story_testing_yaml_refusal` decides for the head, and `crap_cannot_measure` decides for `dev`. The check of `gates.crap-score` lives only on the `dev` path, which is gap 2. |
| Maintainability    | The messages name the file, the branch and the cause. `_YAML_PARSE_ERRORS` keeps the fallback without PyYAML working.                                                                                                 |
| Consistency        | The refusal line follows the `BLOCK <check>:` pattern of the other checks. The new tests use `_build_repo` with `dev_testing`, as the tests of SEC-0011 do.                                                           |

## Verification

```bash
uv run --directory /home/matthiasdaues/Documents/datenschoenheit/agent_factory/.current-work/feature/crap-gate-trusted-source/story/BUG-0137 pytest -q -n auto tests/factory/test_crap_gate_premerge.py tests/factory/test_premerge_check.py tests/factory/test_run_lifecycle_premerge.py tests/factory/test_crap_gate_journey.py tests/factory/test_crap_gate_dispatch.py tests/factory/test_run_lifecycle_dispatch.py tests/factory/test_dispatch_merge_safety.py
uv run --directory /home/matthiasdaues/Documents/datenschoenheit/agent_factory/.current-work/feature/crap-gate-trusted-source/story/BUG-0137 python /tmp/claude-1000/-home-matthiasdaues-Documents-datenschoenheit-agent-factory/89fd1670-49e4-4a59-97db-e1035150aa04/scratchpad/bug0137/probe.py /home/matthiasdaues/Documents/datenschoenheit/agent_factory/.current-work/feature/crap-gate-trusted-source/story/BUG-0137
```

The first command passed 303 tests on `6af49ba1`. The second prints the rows of [The probe](#the-probe). `utf_check.py` next to the probe calls `gate_entries` and `story_testing_yaml_refusal` on a folder whose file is not valid UTF-8. It also takes `premerge-check-old`, the copy at `99064e9a`.
