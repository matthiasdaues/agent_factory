---
type: code-review
title: Code review of BUG-0138, a broken docs/testing.yaml stops the feature merge without a traceback
date: 2026-11-23
status: pass
reviewer: code-review-agent
findings_filed: 1
story: BUG-0138
run:
branch: story/BUG-0138
branch_base: 25474b6b8ccb8c9091e2d9254aa7c61ff2394288
branch_head: 04484745ecf28cc57c4f50fd76db61e944c6f74d
---

# Code review of BUG-0138, a broken docs/testing.yaml stops the feature merge without a traceback

## Verdict

BUG-0138 passes the code review, and its status is now `resolved`. A feature merge whose `docs/testing.yaml` is broken now ends in `BLOCK testing-yaml` with exit `1` and no traceback. Every read of a broken file that is committed at the head is caught, on both kinds of merge.

The review files one register file of severity `minor`, [IMPL-0100](../findings/register/code/IMPL-0100.json). On a story merge, the story's own commands run in the premerge worktree. If one of them rewrites `docs/testing.yaml`, a later read of the file still escapes as a traceback. A scratch run reproduces this. The merge still stops with exit `1`, so the finding does not block.

The review of BUG-0137 said that the feature merge reads no `docs/testing.yaml`. That was wrong. `check_feature_merge` calls `check_test_suite`, which reads `test_command` from the file. QA found the crash on that path. This review lists every path, so the gap cannot hide again.

Next, the developer agent commits this report, the changed status of BUG-0138 and the register file on `story/BUG-0138`. Then the implementation agent runs the gate-check step.

## Scope

The review covers the diff `25474b6b..04484745`, the one commit `04484745`. It changes two files:

- `packages/factory/scripts/premerge-check`: `check_test_suite` catches `BrokenTestingYaml` from `read_test_command` and returns `BLOCK testing-yaml: … the test suite did not run`.
- `tests/factory/test_crap_gate_premerge.py`: the new test `test_bug_0138_broken_feature_settings_refuse_without_traceback`.

## Every reader of docs/testing.yaml

`premerge-check` has three functions that read the file and can raise:

- `_read_testing_text` raises `BrokenTestingYaml` for bytes that are not UTF-8, so no `UnicodeDecodeError` leaves it.
- `_parse_testing_yaml` raises `BrokenTestingYaml` for invalid YAML, a file that is no mapping, and a `gates` section that is no mapping.
- `_read_testing_yaml` combines the two and returns `{}` on an `OSError`.

Two functions call them: `gate_entries` and `read_test_command`. `trusted_crap_entry` reads the file of `dev` through `git show`, which decodes with `errors="replace"`, so no `UnicodeDecodeError` can arise there. From `dispatch_lib`, `premerge-check` imports `Ledger`, `StoryState`, `_load_yaml`, `glob_match`, `held_back` and `stop_notice`. None of them reads `docs/testing.yaml`. `_load_yaml` only parses the text it gets, and `stop_notice` reads the finding files with `errors="replace"`. The mutation-testing gate gets the path of the file as `--testing-yaml` and reads it in its own process. A crash there is an exit code that `rerun_gate` handles, not an exception inside `premerge-check`.

### The feature merge, `premerge-check dev feature/login`

The block for a story branch does not run, because the branch has no story ID.

| Path                                                                      | Reads                | Result for a broken file at the head                                           |
| ------------------------------------------------------------------------- | -------------------- | ------------------------------------------------------------------------------ |
| `main` → `check_feature_merge` → `check_test_suite` → `read_test_command` | `_read_testing_yaml` | Caught in `check_test_suite` since this commit: `BLOCK testing-yaml`, exit `1` |

`check_run_state`, `check_feature_reports` and `check_feature_findings` read the ledger, the reports and the findings, not `docs/testing.yaml`. QA's probe `repeat-feature-merge-bug0138.sh` shows the fix. A feature branch whose file holds `gates: []` gave `PASS test-suite` at `c0ae79bd`, where the file was never parsed for its `gates`. At `04484745`, it gives `BLOCK testing-yaml: docs/testing.yaml of feature/login has a gates section that is no mapping`, with exit `1` and no traceback.

### The story merge, `premerge-check feature/login story/ST-0350`

`main` calls `story_testing_yaml_refusal` first, which parses the file with the same two functions and catches `BrokenTestingYaml` itself. When the file is broken at the commit, the run ends there with exit `1`, and none of the later readers runs. When the file is valid, every later reader parses the same file and gets the same result. The exception is the case of IMPL-0100: the file changes on disk between two reads.

| Path                                                                                    | When it runs                      | Reads                                                |
| --------------------------------------------------------------------------------------- | --------------------------------- | ---------------------------------------------------- |
| `main` → `story_testing_yaml_refusal`                                                   | first                             | `_read_testing_text`, `_parse_testing_yaml`; catches |
| `main` → `resolve_gates` → `gate_entries`; `trusted_crap_entry` for `dev`, caught there | before any command                | `_read_testing_yaml`                                 |
| `main` → `not_set_up_notice` → `gate_entries`                                           | before any command                | `_read_testing_yaml`                                 |
| `check_story_gates` → `run_ready_commands` → `gate_entries`                             | before the ready commands         | `_read_testing_yaml`                                 |
| `check_story_gates` → `check_semantic_gates` → `gate_entries`                           | **after** the ready commands      | `_read_testing_yaml`, not caught                     |
| `check_story_gates` → `check_test_suite` → `read_test_command`                          | after the gates, before the suite | caught since this commit                             |
| `main` → `crap_cannot_measure` → `trusted_crap_entry`, then `gate_entries`              | **after** the test suite          | `dev` caught; the head read not caught               |

### IMPL-0100: a story command that rewrites the file

The two reads in bold run after code of the story head. The `ready` commands, the measuring commands and `test_command` all come from the story head (DEC-75). The review's probe `/tmp/claude-1000/-home-matthiasdaues-Documents-datenschoenheit-agent-factory/89fd1670-49e4-4a59-97db-e1035150aa04/scratchpad/bug0138/probe.py` commits a valid file, with a `dev` that enables the gate. One command of the story then runs `printf 'gates: [x' > docs/testing.yaml`:

```text
== test suite rewrites the file: exit 1; calls ['crap-score']; traceback True
     BrokenTestingYaml: is not valid YAML
== ready command rewrites the file: exit 1; calls []; traceback True
     BrokenTestingYaml: is not valid YAML
```

The merge stops in both cases, so no story merges this way. The output is a traceback and not a refusal that names the file, so the register file has severity `minor`. The fix that the register file names reads the file once in `main` and passes the values on. A smaller fix catches the exception around the semantic block.

## Tests

The new test runs the feature merge with two shapes, `gates: []` and invalid YAML. For each, it asserts exit `1`, the `BLOCK testing-yaml` line and no traceback. The review called `check_test_suite` directly on more shapes with `/tmp/claude-1000/-home-matthiasdaues-Documents-datenschoenheit-agent-factory/89fd1670-49e4-4a59-97db-e1035150aa04/scratchpad/bug0138/suite.py`, with `required=True` as the feature merge passes it:

| File of the feature branch | Result                                                      |
| -------------------------- | ----------------------------------------------------------- |
| Bytes that are not UTF-8   | `BLOCK testing-yaml: … is not valid UTF-8`                  |
| An empty file              | `BLOCK testing-yaml: … is empty or no mapping (… NoneType)` |
| A list                     | `BLOCK testing-yaml: … is empty or no mapping (… list)`     |
| A date                     | `BLOCK testing-yaml: … is empty or no mapping (… date)`     |
| `gates.crap-score: 5`      | `PASS test-suite`; see the note below                       |

The six related test files passed 348 tests on `04484745`.

## Findings

| Finding                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | Artifact                                            | Category   | Type     | Severity | Basis                                                                                    | Filed as                                              |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------- | ---------- | -------- | -------- | ---------------------------------------------------------------------------------------- | ----------------------------------------------------- |
| On a story merge, `gate_entries` in `check_semantic_gates` and in `crap_cannot_measure` parse `docs/testing.yaml` again after commands of the story ran, and neither catches `BrokenTestingYaml`. A command that rewrites the file ends the run in a traceback with exit `1`. Fix: parse the file once in `main` and pass the values on.                                                                                                                                                                                                                                     | `packages/factory/scripts/premerge-check:997-1022`  | defect     | checking | minor    | `in_use: false`, `harms_downstream: false`, `fails_purpose: false`, `raises_cost: true`  | [IMPL-0100](../findings/register/code/IMPL-0100.json) |
| On the feature merge, a `gates.crap-score` that is no mapping passes, because the feature merge parses only the file and the `gates` section. DEC-83 names this fault for the story head and for `dev`. The drift rows of BUG-0138 name only invalid YAML and a `gates` section that is no mapping for the feature merge. If the feature merge lands such an entry on `dev`, the next story merge stops with exit `3` and names the file of `dev`. The orchestrator decides whether the feature merge refuses it too, through `_crap_score_is_broken` in `check_test_suite`. | `packages/factory/scripts/premerge-check:1514-1530` | suggestion | function | note     | `in_use: false`, `harms_downstream: false`, `fails_purpose: false`, `raises_cost: false` | report only                                           |

| ID                                  | Severity | Status     | Blocks |
| ----------------------------------- | -------- | ---------- | ------ |
| [BUG-0138](../findings/BUG-0138.md) | major    | `resolved` | no     |

## Focus areas

| Focus area         | Result                                                                                                                                                       |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Correctness        | Both kinds of merge refuse a broken file that is committed at the head with exit `1` and no traceback. IMPL-0100 is the one path that a story command opens. |
| Clean Architecture | The refusal sits in the check that reads the file, as `story_testing_yaml_refusal` does for the story merge.                                                 |
| SOLID              | Five functions read the same file again. IMPL-0100 suggests one read, which would also make the order of the checks unimportant.                             |
| Maintainability    | The refusal names the branch and says that the test suite did not run.                                                                                       |
| Consistency        | The line follows `BLOCK testing-yaml:` of the story merge. The message says "the branch must repair its own file", which fits both kinds of merge.           |

## Verification

```bash
uv run --directory /home/matthiasdaues/Documents/datenschoenheit/agent_factory/.current-work/feature/crap-gate-trusted-source/story/BUG-0138 pytest -q -n auto tests/factory/test_crap_gate_premerge.py tests/factory/test_premerge_check.py tests/factory/test_run_lifecycle_premerge.py tests/factory/test_run_lifecycle_close.py tests/factory/test_dispatch_merge_safety.py tests/factory/test_run_lifecycle_dispatch.py
bash /tmp/claude-1000/-home-matthiasdaues-Documents-datenschoenheit-agent-factory/89fd1670-49e4-4a59-97db-e1035150aa04/scratchpad/qa/repeat-feature-merge-bug0138.sh
uv run --directory /home/matthiasdaues/Documents/datenschoenheit/agent_factory/.current-work/feature/crap-gate-trusted-source/story/BUG-0138 python /tmp/claude-1000/-home-matthiasdaues-Documents-datenschoenheit-agent-factory/89fd1670-49e4-4a59-97db-e1035150aa04/scratchpad/bug0138/probe.py /home/matthiasdaues/Documents/datenschoenheit/agent_factory/.current-work/feature/crap-gate-trusted-source/story/BUG-0138
```

The first command passed 348 tests. The second shows the feature merge before and after the fix. The third reproduces IMPL-0100.
