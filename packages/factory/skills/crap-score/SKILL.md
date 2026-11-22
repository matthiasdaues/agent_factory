---
name: crap-score
description: Compute CRAP (Change Risk Anti-Patterns) per function and block when any exceeds the threshold.
category: implementation
---

# CRAP Score

`crap-score` gives one verdict for the functions a story changed. A function with high complexity and little test coverage is risky to change. The CRAP score puts both numbers into one value per function, and the gate fails a changed function whose score lies above the threshold.

The project measures, and the Factory judges. `crap-score` holds no code of a language. The project owns one measuring command per part of its code, and `crap-score` runs these commands, computes the scores, and judges the changed functions. The skill `setup-crap-score` sets up the gate and its measuring commands.

## Call

```bash
.agent-factory/factory/scripts/crap-score (--base <revision> | --all) [--story-id <id>] [--report-dir <folder>] [--settings-from-folder]
```

- `--base <revision>` judges the functions whose lines changed in the diff from the merge base of the revision and `HEAD` to `HEAD`. The revision is a branch or a commit. The gate-check step passes the feature branch.
- `--all` judges every measured function. Setup step 6 uses it.
- A call needs exactly one of `--base` and `--all`. A call with neither or both exits `2`.
- `--story-id` names the report. Without it, the name is `STORY_ID`, then the ID in the current branch name, such as `ST-0350` in `story/ST-0350`, then `adhoc`.
- `--report-dir` names the folder of the report. The default is `.current-work/crap-score/`.
- `--settings-from-folder` takes `threshold`, `files` and `exclude` from `docs/testing.yaml` of the folder, because the setup checks values that are not committed yet. The exceptions register still comes from the integration branch. Only `gate-setup-proof` passes it. The gate-check step, `premerge-check` and `dispatch` never pass it.

The gate takes no threshold and no list of files as an argument. It reads its settings from `docs/testing.yaml`.

## Settings

The entry `gates.crap-score` in `docs/testing.yaml` holds the settings. The gate reads them on each run, also when `enabled` is `false`:

```yaml
---
gates:
  crap-score:
    enabled: true
    threshold: 8
    timeout_minutes: 10
    measures:
      - name: backend
        files: "packages/server/backend/src/**"
        exclude:
          - "**/db/alembic/versions/**"
        command: "scripts/crap-measure-backend"
        ready: "scripts/crap-ready-backend"
```

- `gates.crap-score.threshold`, `timeout_minutes` and `measures` are required. The gate has no built-in value for any of them. A missing value, an empty list `measures`, a measure without `name`, `files` or `command`, and two measures with one name make the gate exit `2` and name the cause.
- The test-strategy agent proposes each value, and a person decides it.
- `files` and `exclude` are glob patterns relative to the repository root. `*` matches within one path segment, and `**` matches any number of segments. The gate judges only the rows whose file matches `files` and no `exclude` pattern.
- The old key `crap_score` still counts. With both keys, the key with hyphens wins, and the gate prints a warning that names the old key.

## Trusted gate source

A story cannot decide what counts as accepted. So the gate reads `threshold`, the `files` and `exclude` of each measure, and the exceptions register from the integration branch, through one reader, the trusted gate source. The integration branch is the key `integration_branch` in `docs/factory-settings.yaml` of the folder, and `dev` by default, when the file or the key is missing. The gate reads the branch from its git ref `refs/heads/<integration branch>`. So a story that raises its threshold or adds an `exclude` pattern gets the same verdict as without that change.

- `enabled`, `timeout_minutes`, and the `name`, `command` and `ready` of each measure come from the folder, the story head. The folder still needs all three required values.
- A measure joins its entry on the branch by `name`. A measure that the branch does not name yet takes `files` and `exclude` from the folder, and the output names it as not yet trusted.
- A measure that the branch names and the folder lacks makes the gate exit `2`. Remove a measure on the integration branch first.
- Without the ref of the default `dev`, without `docs/testing.yaml` on the branch, or without `gates.crap-score` there, `threshold`, `files` and `exclude` come from the folder. The output then names the cause, so the first setup keeps working.
- A `docs/testing.yaml` on the branch that cannot be parsed, or an entry there without `threshold`, makes the gate exit `2`. So do an `integration_branch` that is not a non-empty string, a named branch that git does not hold, and a named branch whose tip is `HEAD`, the commit under judgement.

## Measurement format

The gate runs the measures in list order, each from the root of the folder the gate runs in. Each command gets the caller's environment without the environments of `uv run --script`, so `python` in a command starts the project's interpreter. The gate, `dispatch` and `premerge-check` each start through `uv run --script`, and uv keeps each of their environments in a folder with `pyvenv.cfg` under its cache folder: `UV_CACHE_DIR`, else `$XDG_CACHE_HOME/uv`, else `~/.cache/uv`. The gate removes every such `bin` folder from `PATH`, and `VIRTUAL_ENV` when it names such a folder. A project's own `.venv` lies outside the cache and stays. The gate sets three environment variables for each measuring command:

- `GATE_OUTPUT` holds a file path. The command writes its rows there.
- `GATE_FILES` holds the measure's `files` pattern.
- `GATE_EXCLUDE` holds the measure's `exclude` patterns, one pattern per line, and is empty without `exclude`.

A command may measure only the files that match `GATE_FILES` and no `GATE_EXCLUDE` pattern, so a file the measure leaves out cannot make it exit non-zero. The gate still applies `files` and `exclude` to the rows itself (DEC-10, DEC-65). A `files` or `exclude` pattern with a line break makes the gate exit `2`.

The command writes one JSON array to the path in `GATE_OUTPUT`, with one row per function:

| Field          | Content                                                                     |
| -------------- | --------------------------------------------------------------------------- |
| `file`         | Path relative to the repository root, also for a file without a file ending |
| `function`     | The qualified name, such as `Parser.parse` for a method                     |
| `start_line`   | First line of the function                                                  |
| `end_line`     | Last line of the function                                                   |
| `complexity`   | Cyclomatic complexity                                                       |
| `coverage_pct` | Share of the function that the tests cover, from 0 to 100                   |

A file that the command cannot parse gets one row with `file` and `parse_error`, the message of the parser. When the diff touches that file, the row fails the gate. A measuring command that exits non-zero makes the gate exit `2`, and the message names the measure, the command, and the command's own message. No later measure runs.

`docs/spec/schemas/measure-output-rows.json` defines the rows.

## Score and verdict

The score of a function is

```text
complexity² × (1 − coverage_pct/100)³ + complexity
```

rounded to two decimals, half up. A judged function passes when its rounded score is at or below `gates.crap-score.threshold`. With the threshold 8, a score of 8.004 rounds to 8.00 and passes, and a score of 8.006 rounds to 8.01 and fails.

With `--base`, a function is judged when its range from `start_line` to `end_line` holds a changed line. A deletion inside the range counts too. A deletion between two functions counts for both neighbours.

## Exit codes

| Code      | Meaning                                                                                                                                                  |
| --------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `0`       | Every judged function passes, also when the gate judges no function                                                                                      |
| `1`       | A judged function fails. The output names its file, its function, and its score                                                                          |
| `2`       | The gate cannot measure, such as for a wrong call, a missing setting, or a failed command. The message names the cause                                   |
| `128 + n` | The gate was stopped by signal `n`: `143` for `SIGTERM`, `130` for `SIGINT`, `129` for `SIGHUP`. It stops its running command first and gives no verdict |

Exit `2` means that nobody judged the code. So it costs the story no attempt, and the story stops as `blocked` with the reason `gate cannot measure: crap-score`. Exit `128 + n` gives no verdict either. The gate-check step runs the gate again and records no attempt (DEC-56).

## Report

On exit `0` or `1`, the gate writes `<report-dir>/<story-id>.json`. The report holds one row per judged function: the six measurement fields plus `crap_score`, the rounded score, and `pass_fail`, which is `pass`, `fail`, or `accepted`. A new report replaces an earlier report of the same name. On exit `2` and on exit `128 + n`, the gate writes no report, and the earlier report stays.

A person reads the report. The verdict is the exit code alone. After exit `1`, `premerge-check` reads the report only to name the failing functions in its refusal. After any other exit, it reads no report (DEC-54).

## Exceptions register

A person can accept a function above the threshold in the section `## CRAP score` of `docs/findings/exceptions.md`. The gate reads that section from the integration branch, `dev` by default, never from the folder. A row names the file, the function, and the accepted score. A judged function above the threshold and at or below its accepted score gets `accepted`, which counts as a pass. Only the stakeholder writes the register, and agents never write it.

## Where the gate runs

Each measuring command measures the code of the folder the gate runs in:

| Run                                    | Folder                                                  |
| -------------------------------------- | ------------------------------------------------------- |
| Gate-check step of an orchestrated run | The worktree of the story                               |
| Gate-check step of a run by hand       | The primary checkout, with the story branch checked out |
| `premerge-check`                       | Its temporary worktree at the branch head               |
| `gate-setup-proof`                     | The temporary worktree of `gate-setup-proof`            |

The implementation agent runs `crap-score` in the gate-check step. The developer agent never runs it.
