---
type: code-review
title: Code review of BUG-0147, the usage runtime through a failed build or update
date: 2026-11-24
status: pass
reviewer: code-review-agent
findings_filed: 2
story: BUG-0147
run:
branch: story/BUG-0147
branch_base: ad2436a3defae5e18141531f73d7e5b2896d1615
branch_head: ada2cabdf62d766e2d48da26279af8204ae3fa0c
---

# Code review of BUG-0147, the usage runtime through a failed build or update

## Verdict

BUG-0147 passes the code review on the repeat pass. The first pass filed two findings, and `ada2cabd` fixes both. The review checked each fix and keeps both statuses at `resolved`:

- [IMPL-0114](../findings/IMPL-0114.md), major: a full `init-factory` run now finds the earlier runtime in the preserve folder. After a failed build it prints the cause, keeps the hooks, and says that capture keeps the previous runtime.
- [IMPL-0115](../findings/register/code/IMPL-0115.json), minor: the copy of the runtime now lies in `.agent-factory/`, outside `usage/`. The rollback checks the copy before it moves anything.

CAL-07-IT-03 passes. Two notes remain in [Findings](#findings). Neither blocks.

Next, the developer agent commits this report on `story/BUG-0147`. Then the implementation agent runs the gate-check step.

## Scope

The first pass covered `ad2436a3..2f94f9da`. That commit stopped deleting the marker `.requirements-sha256` before a build. It also added the copy of the runtime before the sourced `init-factory` runs, the restore of that copy on rollback, and three tests.

The repeat pass covers `2f94f9da..ada2cabd`, the one commit `ada2cabd`:

- `packages/factory/scripts/init-factory`: `provision_usage_runtime` returns a state and a cause: `ready`, `kept`, or `unavailable`. It takes `previous`, the runtime in the preserve folder `.agent-factory/.preserve-usage-*` during a full run (T-0011). `_report_usage_state` prints the state with the cause, outside the quiet block, at both call sites.
- `packages/factory/scripts/update-factory`: `_set_runtime_aside` copies the runtime to `.agent-factory/usage-runtime-backup-<uuid>.partial` and renames the copy when it is complete. `_restore_runtime` raises before any rename when the copy is gone. The discard folder lies in `.agent-factory/`. The header describes the new place.
- `tests/factory/test_usage_capture_paths.py`: a test that runs the real `init-factory` twice, the second time with a failing `uv`.
- `tests/factory/test_update_factory.py`: tests that the copy lies outside `usage/` during the run, that a rollback without the copy keeps the runtime, and that a failed copy refuses the update. Both earlier update tests now also check that no `usage-runtime-*` folder stays in `.agent-factory/`.
- `docs/spec/work/spec-feedback-BUG-0147.md`: the three drift rows name the new place of the copy and the two paths of a kept runtime.

## The update path

The table follows one update in which the build fails. "Copy" is the copy that `update-factory` makes, and "preserve folder" is `.agent-factory/.preserve-usage-*`.

| Step                                                | What lies at `usage/runtime`                       | Where the copy lies                 | Capture                                           |
| --------------------------------------------------- | -------------------------------------------------- | ----------------------------------- | ------------------------------------------------- |
| `_set_runtime_aside` copies the runtime             | old runtime                                        | `.agent-factory/`                   | on                                                |
| `init-factory` runs `backup_preserved_dirs`         | nothing; all of `usage/` is in the preserve folder | `.agent-factory/`, not moved        | off for the length of the run (T-0011, earlier)   |
| `provision_usage_runtime` fails                     | nothing                                            | `.agent-factory/`                   | state `kept`, because `previous` has its marker   |
| `restore_preserved_dirs` runs in `finally`          | old runtime with its marker                        | `.agent-factory/`                   | on, hooks installed                               |
| `init-factory` exits `0`, `update-factory` succeeds | old runtime                                        | deleted                             | on                                                |
| `init-factory` exits non-zero, rollback             | the copy, renamed into place                       | gone, because it is now the runtime | on                                                |
| `init-factory` killed without `finally`, rollback   | the copy, renamed into place                       | gone, because it is now the runtime | on; the usage records stay in the preserve folder |

The killed case changed with IMPL-0115. The copy no longer travels into the preserve folder, so the rollback finds it and puts it back.

## Scratch cases on `ada2cabd`

The scripts lie in `/tmp/claude-1000/-home-matthiasdaues-Documents-datenschoenheit-agent-factory/89fd1670-49e4-4a59-97db-e1035150aa04/scratchpad/bug0147-review/`. Each one works only on scratch projects in that folder.

| Script                            | First pass, `2f94f9da`                                                                 | Repeat pass, `ada2cabd`                                                                                                                                   |
| --------------------------------- | -------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `repro-1-update-path.sh`          | run 2 prints "runtime unavailable, hooks inactive" and no cause; marker and hooks stay | run 2 prints "runtime not rebuilt — hash mismatch for tiktoken (fake uv); capture keeps the previous runtime, hooks installed"; marker and two hooks stay |
| `repro-2-restore-without-copy.py` | `FileNotFoundError`; no runtime, only the discard folder in `usage/`                   | `FileNotFoundError`; the runtime stays, and `usage/` holds only `runtime`                                                                                 |
| `check-3-copy-fails.py`           | `shutil.Error`; no partial copy; marker unchanged                                      | `shutil.Error`; no partial copy in `.agent-factory/`; marker unchanged                                                                                    |

## The copy in `.agent-factory/`

The coordinator asked whether a script can mistake the copy for something else. The review searched `update-factory`, `init-factory` and `remove-factory` for scans of `.agent-factory/`:

- `remove-factory` deletes `.agent-factory/` as a whole, so it removes a copy left behind without reading it.
- The staging of `update-factory` writes `factory-staging-<uuid>`, the factory backup is `factory-backup-<uuid>`, and remote downloads use `factory-remote-<uuid>`. No code globs `.agent-factory/` by a prefix that matches `usage-runtime-`.
- `backup_preserved_dirs` moves only `usage` and `user-changes`, so it leaves the copy alone.
- The block that `init-factory` writes into `.gitignore` ignores `/.agent-factory/`, so a copy left behind never shows in `git status`.

After a successful update and after a rollback, `.agent-factory/` holds no `usage-runtime-*` folder. The two earlier update tests now assert this. A copy left behind by a crash stays until the next `remove-factory`; see the notes.

## The decision to keep the old runtime

The hook wrapper `usage-capture-runtime` checks only the marker and `bin/python`. It compares no digest. `usage-capture` imports only the standard library at the top and imports `tiktoken` inside a function, so an old runtime keeps capturing. A later release that adds a package which the capture imports at the top would break every capture on a kept runtime. The printed line now names the kept runtime and the cause, so the operator learns that the rebuild failed and can run the update again.

## The tests

| Test                                                                     | Fails on the fault it names?                                                                                                                                                                       |
| ------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `test_impl_0114_full_run_reports_the_kept_runtime_and_the_cause`         | Yes. It runs the real `init-factory` twice and asserts the cause, "capture keeps the previous runtime", no "hooks inactive", the marker, and the hook. Code at `2f94f9da` prints "hooks inactive". |
| `test_bug_0147_failed_build_keeps_the_runtime_and_its_marker`            | Yes, for `--add`: it asserts the state `kept` and the cause.                                                                                                                                       |
| `test_impl_0115_the_copy_lies_outside_the_usage_folder`                  | Yes. A fake `init-factory` lists `usage/` during the run, and a copy inside `usage/` would appear in the listing.                                                                                  |
| `test_impl_0115_rollback_without_the_copy_keeps_the_runtime`             | Yes. With the order of `2f94f9da`, the runtime moves to the discard folder.                                                                                                                        |
| `test_bug_0147_failed_copy_refuses_the_update`                           | Yes. It asserts exit `1`, "no changes made", the kept marker, and no leftover copy or staging folder.                                                                                              |
| `test_bug_0147_rollback_restores_the_usage_runtime` and the success test | Yes. They also assert that no `usage-runtime-*` folder stays in `.agent-factory/`.                                                                                                                 |
| CAL-07-IT-03                                                             | Passes on `ada2cabd`.                                                                                                                                                                              |

## Findings

| Finding                                                                                                                                                                                                                                                                                                                          | Artifact                                          | Category   | Type      | Severity | Basis                                                                                    | Filed as                                                          |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------- | ---------- | --------- | -------- | ---------------------------------------------------------------------------------------- | ----------------------------------------------------------------- |
| In a full `init-factory` run the new branch of `provision_usage_runtime` was not reached. A failed build printed "runtime unavailable, hooks inactive" and no cause. Fixed in `ada2cabd`, checked with `repro-1-update-path.sh`.                                                                                                 | `packages/factory/scripts/init-factory:1561-1571` | defect     | function  | major    | `in_use: false`, `harms_downstream: false`, `fails_purpose: true`, `raises_cost: true`   | [IMPL-0114](../findings/IMPL-0114.md), `resolved`                 |
| `_restore_runtime` moved the runtime away before it checked the copy, and the copy lay inside `usage/`. Fixed in `ada2cabd`, checked with `repro-2-restore-without-copy.py`.                                                                                                                                                     | `packages/factory/scripts/update-factory:804-819` | defect     | algorithm | minor    | `in_use: false`, `harms_downstream: false`, `fails_purpose: false`, `raises_cost: true`  | [IMPL-0115](../findings/register/code/IMPL-0115.json), `resolved` |
| A crash of `update-factory` itself leaves `usage-runtime-backup-<uuid>` or its `.partial` folder in `.agent-factory/`, about 9 MB each, and no run removes it. Only `remove-factory` does. The factory backup `factory-backup-<uuid>` has the same gap. A later update could delete leftovers of both prefixes before it starts. | `packages/factory/scripts/update-factory:1724`    | suggestion | algorithm | note     | `in_use: false`, `harms_downstream: false`, `fails_purpose: false`, `raises_cost: false` | report only                                                       |
| Ctrl-C during the sourced `init-factory` raises `KeyboardInterrupt` in `update-factory`, and `except Exception` does not catch it. No rollback runs, and the copy stays. The factory backup has the same gap, so this commit adds one more leftover.                                                                             | `packages/factory/scripts/update-factory:1759`    | suggestion | algorithm | note     | `in_use: false`, `harms_downstream: false`, `fails_purpose: false`, `raises_cost: false` | report only                                                       |

The first pass also had notes on an untested failed copy, on a header sentence, and on the drift row for ADR-0007. `ada2cabd` covers all three: it adds `test_bug_0147_failed_copy_refuses_the_update`, rewrites the header, and rewrites the row.

## Focus areas

| Focus area         | Result                                                                                                                                             |
| ------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| Correctness        | A failed build keeps the old runtime and its hooks in both paths and prints the cause. The rollback restores the runtime, and CAL-07-IT-03 passes. |
| Clean Architecture | The copy and the restore stay in `update-factory`. The copy now lies outside the folder that `init-factory` moves.                                 |
| SOLID              | `provision_usage_runtime` builds and returns a state. `_report_usage_state` owns the printed line. The two call sites share it.                    |
| Maintainability    | The three states are named constants. The docstrings name BUG-0147, IMPL-0114, IMPL-0115, and T-0011.                                              |
| Consistency        | The copy lies beside `factory-backup-<uuid>`, follows its naming, and is gitignored with it.                                                       |

## Verification

```bash
uv run --directory /home/matthiasdaues/Documents/datenschoenheit/agent_factory/.current-work/feature/crap-gate-self-host/story/BUG-0147 pytest -q tests/factory/test_update_factory.py tests/factory/test_usage_capture_paths.py
```

The run passed 114 tests on `ada2cabd`: 98 in `test_update_factory.py`, CAL-07-IT-03 among them, and 16 in `test_usage_capture_paths.py`. The three scratch cases ran on `ada2cabd`, as [Scratch cases on `ada2cabd`](#scratch-cases-on-ada2cabd) shows.
