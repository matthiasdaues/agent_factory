---
type: code-review
title: Code review of BUG-0147, the usage runtime through a failed build or update
date: 2026-11-24
status: fail
reviewer: code-review-agent
findings_filed: 2
story: BUG-0147
run:
branch: story/BUG-0147
branch_base: ad2436a3defae5e18141531f73d7e5b2896d1615
branch_head: 2f94f9daba0ffaabdf70c841430f9959646e1ffb
---

# Code review of BUG-0147, the usage runtime through a failed build or update

## Verdict

BUG-0147 does not pass the code review yet. The rollback half works: a failed update now puts the earlier usage runtime back, and CAL-07-IT-03 passes on the branch. The build half does not reach the update path. In a full `init-factory` run the runtime is already moved aside when `provision_usage_runtime` runs, so the new branch that keeps the old runtime never runs there. After a failed build the run still prints "runtime unavailable, hooks inactive", while capture keeps running on the restored runtime, and the cause of the failure is never printed. The review files this as the major finding [IMPL-0114](../findings/IMPL-0114.md).

The review also files one minor finding, [IMPL-0115](../findings/register/code/IMPL-0115.json): the rollback moves the current runtime away before it checks that the copy exists. Four notes follow in [Findings](#findings).

Next, the developer agent fixes IMPL-0114 on `story/BUG-0147` and commits this report with it. Then the code review runs again.

## Scope

The review covers the diff `ad2436a3..2f94f9da`, the one commit `2f94f9da`. It changes six files:

- `packages/factory/scripts/init-factory`: `provision_usage_runtime` no longer deletes the marker `.requirements-sha256` before the build. After a failed build it returns True and logs the cause when the marker is still there.
- `packages/factory/scripts/update-factory`: `_set_runtime_aside` copies `.agent-factory/usage/runtime` to `.agent-factory/usage/usage-runtime-backup-<uuid>` before the sourced `init-factory` runs. `_restore_runtime` puts the copy back on rollback. The success path deletes the copy. The header describes this.
- `tests/factory/test_usage_capture_paths.py`: one test with a fake `uv` that fails at `venv` or at `pip`.
- `tests/factory/test_update_factory.py`: two tests with a fake `_run_init` that rebuilds the runtime and exits `1` or `0`.
- `docs/findings/BUG-0147.md` and `docs/spec/work/spec-feedback-BUG-0147.md`: the status and three drift rows.

The review read BUG-0147, the spec feedback, the callers of `provision_usage_runtime`, `backup_preserved_dirs` and `restore_preserved_dirs` in `init-factory`, the hook wrapper `usage-capture-runtime`, and `_runtime_ready` in `housekeeping-about`.

## The update path

The review traced one update with a failed build, step by step. "Copy" is the copy that `update-factory` makes, and "preserve folder" is `.agent-factory/.preserve-usage-*`.

| Step                                                | What lies at `usage/runtime`                       | Where the copy lies      | Capture                                         |
| --------------------------------------------------- | -------------------------------------------------- | ------------------------ | ----------------------------------------------- |
| `_set_runtime_aside` copies the runtime             | old runtime                                        | `usage/`                 | on                                              |
| `init-factory` runs `backup_preserved_dirs`         | nothing; all of `usage/` is in the preserve folder | preserve folder          | off for the length of the run (T-0011, earlier) |
| `provision_usage_runtime` fails                     | nothing                                            | preserve folder          | off; the function returns False                 |
| `restore_preserved_dirs` runs in `finally`          | old runtime with its marker                        | `usage/`                 | on; the earlier hooks stay wired                |
| `init-factory` exits `0`, `update-factory` succeeds | old runtime                                        | deleted                  | on                                              |
| `init-factory` exits non-zero, rollback             | the copy, renamed into place                       | gone (it is the runtime) | on                                              |
| `init-factory` killed without `finally`, rollback   | renamed to `usage-runtime-discard-*`               | still in preserve folder | off; IMPL-0115                                  |

So the project keeps a runtime or a copy at every step that `init-factory` reports itself. The window in which capture is off during the run comes from T-0011, not from this commit.

`repro-1-update-path.sh` in the scratch folder runs the real `init-factory` twice with a fake `uv` and shows rows 3 to 5. The second run prints "usage capture: runtime unavailable, hooks inactive", prints no line with the cause, and leaves the marker and two capture hooks in `.claude/settings.json`.

## Crash safety and a full disk

The usage runtime of the primary checkout is 9.1 MB, read with `du` only. The build in `init-factory` needs space for one more runtime of that size, so a disk too full for the copy is too full for the build as well.

`check-3-copy-fails.py` makes the second file copy of `copytree` raise `ENOSPC`. `_set_runtime_aside` then raises `shutil.Error`, removes the partial copy, and leaves the runtime and its marker unchanged. `main` turns that into exit `1` with "no changes made", after it removes the staging folder. So a full disk refuses the update and leaves capture on. No test covers this path; see the notes.

A crash between the two renames of `_restore_runtime` leaves `usage/runtime` missing, with the copy and the discard folder beside it. Nothing recovers the copy on the next run. The window is two renames in one folder. The factory tree has the same window between its two renames in `main`, so the behavior matches the existing code.

## Usage records

`update-factory` moves, copies or deletes only `usage/runtime`, the copy, and the discard folder. The two update tests assert that `usage.jsonl` keeps the record that the fake `init-factory` appended, and that `usage/` holds only `runtime` and `usage.jsonl` afterwards. `init-factory` still moves all of `usage/` for its run (T-0011), and the copy travels with it. That move is older than this commit.

## The decision to return True

The hook wrapper `usage-capture-runtime` checks only that the marker exists and that `bin/python` is executable. It compares no digest. `usage-capture` imports only the standard library at the top and imports `tiktoken` inside a function. So an old runtime keeps capturing after a newer Factory is installed, unless a later release adds a package that the capture imports at the top. Then every capture fails with exit `1`, `housekeeping-about` still reports "healthy" with an old date, and nothing names the cause. Today that does not happen.

The report does not say clearly that capture runs on the old runtime. In `--add` the visible line after a failed build is "usage capture: hooks installed". In a full run it is "runtime unavailable, hooks inactive", which is false. The line that names the old runtime and the cause is logged while output is quiet, so the operator never sees it. IMPL-0114 covers both.

## The tests

| Test                                                          | Fails on the fault it names?                                                                                                                                                                                                                            |
| ------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `test_bug_0147_failed_build_keeps_the_runtime_and_its_marker` | Yes for `provision_usage_runtime` alone: with the old `ready.unlink()` the marker is gone, and without the new branch the function returns False. It runs with the runtime in place, which only `--add` produces, so it does not cover the update path. |
| `test_bug_0147_rollback_restores_the_usage_runtime`           | Yes: without `_restore_runtime` the runtime holds `new-digest`. The fake `init-factory` never moves `usage/`, so the test does not see the case of IMPL-0115.                                                                                           |
| `test_bug_0147_successful_update_leaves_no_set_aside_runtime` | Yes: without the delete on success, `usage/` holds the copy, and the listing check fails.                                                                                                                                                               |
| CAL-07-IT-03                                                  | Passes on `2f94f9da`.                                                                                                                                                                                                                                   |

## Findings

| Finding                                                                                                                                                                                                                                                                                                                                                                        | Artifact                                            | Category   | Type          | Severity | Basis                                                                                    | Filed as                                              |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------- | ---------- | ------------- | -------- | ---------------------------------------------------------------------------------------- | ----------------------------------------------------- |
| In a full `init-factory` run, `backup_preserved_dirs` moves the runtime aside before `provision_usage_runtime` runs, so the new branch is not reached. A failed build prints "runtime unavailable, hooks inactive" while capture runs on the restored runtime, and the cause is never printed. The test covers only the state of `--add`.                                      | `packages/factory/scripts/init-factory:1546-1552`   | defect     | function      | major    | `in_use: false`, `harms_downstream: false`, `fails_purpose: true`, `raises_cost: true`   | [IMPL-0114](../findings/IMPL-0114.md)                 |
| `_restore_runtime` renames the current runtime away before it checks that the copy exists. The copy lies inside `usage/`, which `init-factory` moves for its run, so an `init-factory` killed without `finally` leaves the project with no runtime after the rollback. Fix: put the copy at `.agent-factory/usage-runtime-backup-<uuid>` and check it before the first rename. | `packages/factory/scripts/update-factory:804-819`   | defect     | algorithm     | minor    | `in_use: false`, `harms_downstream: false`, `fails_purpose: false`, `raises_cost: true`  | [IMPL-0115](../findings/register/code/IMPL-0115.json) |
| No test covers the refusal after a failed copy. The review checked it with `check-3-copy-fails.py`. A test that patches the copy to raise `ENOSPC` and asserts exit `1`, "no changes made", the kept marker, and no leftover copy would hold it.                                                                                                                               | `packages/factory/scripts/update-factory:1709-1720` | suggestion | test          | note     | `in_use: false`, `harms_downstream: false`, `fails_purpose: false`, `raises_cost: false` | report only                                           |
| The header says the copy exists "so the project keeps a runtime at every point of the run". During the sourced `init-factory` the project has no runtime at `usage/runtime`, because `init-factory` moves `usage/` aside. The sentence can say that the project keeps a runtime or a copy it can restore.                                                                      | `packages/factory/scripts/update-factory:70-76`     | suggestion | documentation | note     | `in_use: false`, `harms_downstream: false`, `fails_purpose: false`, `raises_cost: false` | report only                                           |
| Ctrl-C during the sourced `init-factory` raises `KeyboardInterrupt` in `update-factory`, which `except Exception` does not catch. No rollback runs, and the copy of about 9 MB stays in `usage/`. The factory backup has the same gap, so the commit only adds one more leftover.                                                                                              | `packages/factory/scripts/update-factory:1735-1747` | suggestion | algorithm     | note     | `in_use: false`, `harms_downstream: false`, `fails_purpose: false`, `raises_cost: false` | report only                                           |
| The drift row for ADR-0007 says a failed rebuild keeps capture active on a previous runtime. That holds through `restore_preserved_dirs` and the earlier wiring, not through the True return, in a full run. The architecture agent can name both paths when it updates ADR-0007.                                                                                              | `docs/spec/work/spec-feedback-BUG-0147.md`          | suggestion | documentation | note     | `in_use: false`, `harms_downstream: false`, `fails_purpose: false`, `raises_cost: false` | report only                                           |

## Focus areas

| Focus area         | Result                                                                                                                                                                             |
| ------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Correctness        | The rollback restores the runtime, and CAL-07-IT-03 passes. The build half does not reach the update path, and the printed status after a failed build is false there (IMPL-0114). |
| Clean Architecture | The copy and the restore stay in `update-factory`, beside the factory backup. The copy lies inside `usage/`, which `init-factory` owns for its run (IMPL-0115).                    |
| SOLID              | `_set_runtime_aside` and `_restore_runtime` each do one job. `_rollback_update` takes one more tuple and keeps one responsibility.                                                 |
| Maintainability    | The constants name the prefixes, and the docstrings name BUG-0147. The test of the build half sets up a state that the main caller never produces.                                 |
| Consistency        | The copy and the rename follow the pattern of `factory-backup-<uuid>`. Unlike that backup, the copy lies in a folder that another script moves.                                    |

## Verification

```bash
uv run --directory /home/matthiasdaues/Documents/datenschoenheit/agent_factory/.current-work/feature/crap-gate-self-host/story/BUG-0147 pytest -q tests/factory/test_update_factory.py::TestFailedMigrationRollsTheUpdateBack::test_CAL_07_failed_migration_rolls_the_whole_update_back
uv run --directory /home/matthiasdaues/Documents/datenschoenheit/agent_factory/.current-work/feature/crap-gate-self-host/story/BUG-0147 pytest -q tests/factory/test_update_factory.py
uv run --directory /home/matthiasdaues/Documents/datenschoenheit/agent_factory/.current-work/feature/crap-gate-self-host/story/BUG-0147 pytest -q tests/factory/test_usage_capture_paths.py
```

CAL-07-IT-03 passed, `test_update_factory.py` passed 95 tests, and `test_usage_capture_paths.py` passed 15 tests, all on `2f94f9da`. The scripts lie in `/tmp/claude-1000/-home-matthiasdaues-Documents-datenschoenheit-agent-factory/89fd1670-49e4-4a59-97db-e1035150aa04/scratchpad/bug0147-review/`: `repro-1-update-path.sh` for IMPL-0114, `repro-2-restore-without-copy.py` for IMPL-0115, and `check-3-copy-fails.py` for the full disk. Each works only on scratch projects in that folder.
