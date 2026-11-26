---
title: hook-subset
type: reference
status: implemented
description: Select and run the pre-commit hooks that apply to a set of files.
---

# hook-subset

## Name

`hook-subset` — Select and run the pre-commit hooks that apply to a set of files.

## Synopsis

```text
.agent-factory/factory/scripts/hook-subset <command> [<arguments> ...]
```

Use `--help` for argument values and defaults supported by your installed version.

## Subcommands

- `present`. print hooks grouped by outcome, as JSON
- `generate`. print the filtered consumer template

## Arguments and options across subcommands

- `--pre-commit`
- `--metadata`
- `--repo-root`
- `--approve`

## See also

- [Command source](../../../scripts/hook-subset)
