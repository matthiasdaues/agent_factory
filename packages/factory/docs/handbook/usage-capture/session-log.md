---
title: Session log
type: reference
status: implemented
order: 50
description: The optional audit log of gate runs, its record fields, and the session-reconcile command that compares it with git.
---

# Session log

The session log is an optional audit trail of gate runs that only grows. It lets you compare what an agent claims it did in a session with what changed on disk. By default it changes and blocks nothing.

## Turn it on

| Setting                 | Effect                                                                                                                                                                          |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `AF_SESSION_LOG` unset  | Logging does nothing and writes nothing.                                                                                                                                        |
| `AF_SESSION_LOG=<path>` | `.agent-factory/factory/scripts/_session_log.py` appends one line per gate run to that path and creates the parent folder when needed. It reads the variable fresh on each run. |

Only `spec-lint` writes to the log today. No other gate does yet.

## Record fields

Each JSON Lines entry holds:

| Field           | Value                                                                                                                   |
| --------------- | ----------------------------------------------------------------------------------------------------------------------- |
| `ts`            | A UTC timestamp from the script's own process clock, never from the agent                                               |
| `script`        | The name of the gate                                                                                                    |
| `argv`          | The arguments of the call                                                                                               |
| `exit_code`     | The gate's exit code                                                                                                    |
| `files_changed` | The difference between `git status --porcelain` before and after the run, which shows what changed on disk              |
| `summary`       | Present when the gate supplies one. `spec-lint` adds the error, warning, and info counts of its `--format json` output. |

## `session-reconcile`

`.agent-factory/factory/scripts/session-reconcile` compares the log with the real git state.

| Option          | Effect                                                                                 |
| --------------- | -------------------------------------------------------------------------------------- |
| `--log`         | The log file. Default: `.current-work/session-log.jsonl`.                              |
| `--base`        | The first commit of the range to compare. Leave it out to check only the working tree. |
| `--head`        | The last commit of the range. Default: `HEAD`.                                         |
| `--report-only` | Exit 0 whatever the findings.                                                          |

| Finding             | Severity | Meaning                                                                             |
| ------------------- | -------- | ----------------------------------------------------------------------------------- |
| `RECON-UNEXPLAINED` | error    | A change in the working tree that no logged run and no commit explains              |
| `RECON-DRIFT`       | warning  | A run logged a change that is now neither committed nor present in the working tree |
| `RECON-STALE`       | warning  | `docs/spec/` changed, but `spec-lint` never ran in this session                     |

The exit code is the number of error findings, unless `--report-only` is set.

The log file lives under `.current-work/`, which is git-ignored. It is local machine state: it does not travel with the repository and is not meant for review. The proposal "Session log addendum" (`docs/proposals/session-log-addendum.md`) in the Agent Factory repository holds the reasons for the design.
