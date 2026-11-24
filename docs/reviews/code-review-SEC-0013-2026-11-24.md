---
type: code-review
title: Code review of SEC-0013, crap-measure-typescript installs ESLint from a lock
date: 2026-11-24
status: pass
reviewer: code-review-agent
findings_filed: 0
story: SEC-0013
run:
branch: story/SEC-0013
branch_base: 302dfa27296c0553fe43e9c16b1e3d859ea40409
branch_head: 870d4068d64f961e0f5ab4e78433f9f9b2afa0f1
---

# Code review of SEC-0013, crap-measure-typescript installs ESLint from a lock

## Verdict

SEC-0013 passes the code review, and the review files no new finding. The install path is correct: the cache key, the rename and the error messages behave as the header of the command says. Each of the six new tests fails on the fault it names. The review records three notes.

Next, the developer agent commits this report on `story/SEC-0013`. Then the implementation agent runs the gate-check step.

## Scope

The review covers the diff `302dfa27..870d4068`. It reads `installEslint` and its caller in `scripts/crap-measure-typescript`, and the six new tests with their helpers in `tests/factory/test_crap_gate_repository.py`. The lock, the pins, the install scripts and a changed lock are the work of the [security review](security-review-2026-11-24.md), and this review does not repeat them.

The probes lie in `/tmp/claude-1000/-home-matthiasdaues-Documents-datenschoenheit-agent-factory/89fd1670-49e4-4a59-97db-e1035150aa04/scratchpad/sec13-cr/`. `repo/` holds the measure, a stub lock and a planted `src/a.ts`. `bin/npm` is the stub that each probe swaps.

## The install path

| Part                 | Result                                                                                                                                                                                                                                                                                              |
| -------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Cache key            | The folder name is the SHA-256 of `package-lock.json` alone. `package.json` is not part of it. This is sound, because `npm ci` fails when the two disagree, and no install lands in the cache then.                                                                                                 |
| Reuse                | `existsSync(bin)` counts only a folder that a rename put there, so a partial install never counts. A second run starts no npm (the test of reuse shows it).                                                                                                                                         |
| Rename               | `npm ci` fills `.<hash>-<random>` inside the cache folder, so the rename stays on one file system. When a second run won the race, the rename fails, `bin` exists, and the loser returns the winner's install. The `finally` removes the loser's folder and does nothing after a successful rename. |
| Early exit           | The install runs only when `codeFiles` finds a file, so a story that changes only Python starts no npm.                                                                                                                                                                                             |
| Install before tests | A story with a failing test and no network now names the install first. Both cases exit `1` with no rows, so the verdict does not change.                                                                                                                                                           |

## The tests

| Test                                                                | Fails on                                                                                                                                                                                                                      |
| ------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `the_typescript_command_starts_no_npx`                              | any `npx` in the text of the command, even in a comment. It checks the text, and the stub `npx` of the install test checks the run.                                                                                           |
| `the_eslint_lock_pins_every_package_with_an_integrity_hash`         | a package without a `sha512-` hash, an `eslint` version other than `10.14.0`, or another range in `package.json`.                                                                                                             |
| `the_command_installs_eslint_with_npm_ci_without_install_scripts`   | a missing `ci`, `--ignore-scripts` or `--prefer-offline`; an install straight into the cache folder (the folder of the call equals the cache folder); a left-over temporary folder; a key other than the SHA-256 of the lock. |
| `a_second_run_reuses_the_eslint_cache_without_npm`                  | a second `npm` call.                                                                                                                                                                                                          |
| `a_failed_eslint_install_exits_non_zero_with_the_cause_and_no_rows` | a swallowed failure, a message without the npm text, a left-over folder in the cache.                                                                                                                                         |
| `npm_that_cannot_start_exits_non_zero_and_writes_no_rows`           | a message without "npm cannot start". The old "ESLint cannot start" no longer matches.                                                                                                                                        |

The 31 tests of `test_crap_gate_repository.py` pass on `870d4068`.

## Findings

| Finding                                                                                                                                                                                                                                                                                                                                                                                                                                 | Artifact                                     | Category   | Type     | Severity | Basis                                                                                    | Filed as    |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------- | ---------- | -------- | -------- | ---------------------------------------------------------------------------------------- | ----------- |
| When npm dies from a signal, `run.status` is `null`, so the message reads "npm ci exited null:" with nothing after the colon. Probe `bin/npm` with `kill -9 $$` gives exactly that. The run still exits `1` and writes no rows. Test `run.signal` and print it.                                                                                                                                                                         | `scripts/crap-measure-typescript:294`        | suggestion | function | note     | `in_use: false`, `harms_downstream: false`, `fails_purpose: false`, `raises_cost: false` | report only |
| A cache folder that the user cannot write (read-only `XDG_CACHE_HOME`) throws a plain `EACCES` from `mkdirSync` or `mkdtempSync`. `main` rethrows it, so the run ends with a stack trace instead of "cannot measure". The exit code is still non-zero and no rows exist. Probe: `XDG_CACHE_HOME` set to a folder of mode 555. Wrap the two calls in the same `CannotMeasure` as the other install steps.                                | `scripts/crap-measure-typescript:281-282`    | suggestion | checking | note     | `in_use: false`, `harms_downstream: false`, `fails_purpose: false`, `raises_cost: false` | report only |
| No test covers the claim that "a killed install leaves no cache that counts", and none covers the unwritable cache. A stale `.<hash>-<random>` folder that holds `eslint.js` would not change any of the six tests if `existsSync(bin)` were widened to scan the cache. The security review showed the claim by hand (its N-7 names the left-over folder). A fixture with such a folder and a stub npm that exits at once would pin it. | `tests/factory/test_crap_gate_repository.py` | suggestion | test     | note     | `in_use: false`, `harms_downstream: false`, `fails_purpose: false`, `raises_cost: false` | report only |

## Focus areas

| Focus area         | Result                                                                                                                                         |
| ------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| Correctness        | The install follows SEC-0013 and BUG-0148: no `npx`, no registry call on a warm cache, a failed install exits `1` with the cause and no rows.  |
| Clean Architecture | `installEslint` does one thing and returns the path. `runEslint` takes the path as a parameter, so it no longer knows how ESLint arrives.      |
| SOLID              | No violation. The install and the run are two functions with one reason to change each.                                                        |
| Maintainability    | The header names the cache, the key and the rename. The four error messages begin with the same words, so a reader finds the step that failed. |
| Consistency        | Errors use `CannotMeasure`, as the rest of the command does. Only the unwritable cache, the second note, escapes it.                           |

## Verification

```bash
uv run --directory /home/matthiasdaues/Documents/datenschoenheit/agent_factory/.current-work/feature/crap-gate-self-host/story/SEC-0013 pytest -q tests/factory/test_crap_gate_repository.py
```

The run passed 31 tests on `870d4068`.
