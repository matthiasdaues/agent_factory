---
title: crap-score
type: reference
status: implemented
description: Measure change risk using function complexity and test coverage.
---

# crap-score

## Name

`crap-score` — Measure change risk using function complexity and test coverage.

## Synopsis

```text
.agent-factory/factory/scripts/crap-score (--base <revision> | --all)
    [--story-id <id>] [--report-dir <folder>] [--settings-from-folder]
```

Use `--help` for argument values and defaults supported by your installed version.

## Arguments and options

- `--base`. judge the functions changed since the merge base of this revision and HEAD
- `--all`. judge every measured function
- `--story-id`. the name of the report file
- `--report-dir`. the folder of the report file
- `--settings-from-folder`. take threshold, files and exclude from the folder; only gate-setup-proof passes it

## Exit status

- `0`. The gate passed.
- `1`. A measured function exceeded the threshold without a matching exception.
- `2`. The gate could not measure.

## See also

- [How an implementation run earns trust](../quality-and-review/implementation-run.md#what-the-gates-add)

- [Command source](../../../scripts/crap-score)
