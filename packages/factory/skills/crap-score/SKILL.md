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
.agent-factory/factory/scripts/crap-score (--base <revision> | --all) [--story-id <id>] [--report-dir <folder>]
```

- `--base <revision>` judges the functions whose lines changed in the diff from the merge base of the revision and `HEAD` to `HEAD`. The revision is a branch or a commit. The gate-check step passes the feature branch.
- `--all` judges every measured function. Setup step 6 uses it.
- A call needs exactly one of `--base` and `--all`. A call with neither or both exits `2`.
- `--story-id` names the report. Without it, the name is `STORY_ID`, then the ID in the current branch name, such as `ST-0350` in `story/ST-0350`, then `adhoc`.
- `--report-dir` names the folder of the report. The default is `.current-work/crap-score/`.

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

## Measurement format

The gate runs the measures in list order, each from the root of the folder the gate runs in. It sets three environment variables for each measuring command:

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

| Code | Meaning                                                                                                                |
| ---- | ---------------------------------------------------------------------------------------------------------------------- |
| `0`  | Every judged function passes, also when the gate judges no function                                                    |
| `1`  | A judged function fails. The output names its file, its function, and its score                                        |
| `2`  | The gate cannot measure, such as for a wrong call, a missing setting, or a failed command. The message names the cause |

Exit `2` means that nobody judged the code. So it costs the story no attempt, and the story stops as `blocked` with the reason `gate cannot measure: crap-score`.

## Report

On exit `0` or `1`, the gate writes `<report-dir>/<story-id>.json`. The report holds one row per judged function: the six measurement fields plus `crap_score`, the rounded score, and `pass_fail`, which is `pass`, `fail`, or `accepted`. A new report replaces an earlier report of the same name. On exit `2`, the gate writes no report, and the earlier report stays.

A person reads the report. The verdict is the exit code, so `premerge-check` reads no report.

## Exceptions register

A person can accept a function above the threshold in the section `## CRAP score` of `docs/findings/exceptions.md`. The gate reads that section on the branch `dev`. A row names the file, the function, and the accepted score. A judged function above the threshold and at or below its accepted score gets `accepted`, which counts as a pass. Only the stakeholder writes the register, and agents never write it.

## Where the gate runs

Each measuring command measures the code of the folder the gate runs in:

| Run                                    | Folder                                                  |
| -------------------------------------- | ------------------------------------------------------- |
| Gate-check step of an orchestrated run | The worktree of the story                               |
| Gate-check step of a run by hand       | The primary checkout, with the story branch checked out |
| `premerge-check`                       | Its temporary worktree at the branch head               |
| `gate-setup-proof`                     | The temporary worktree of `gate-setup-proof`            |

The implementation agent runs `crap-score` in the gate-check step. The developer agent never runs it.
