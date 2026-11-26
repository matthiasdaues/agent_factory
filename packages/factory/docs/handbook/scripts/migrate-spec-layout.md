---
title: migrate-spec-layout
type: reference
status: implemented
description: Move older specification files into the supported layout.
---

# migrate-spec-layout

## Name

`migrate-spec-layout` — Move older specification files into the supported layout.

## Synopsis

```text
.agent-factory/factory/scripts/migrate-spec-layout [<arguments> ...]
```

Use `--help` for argument values and defaults supported by your installed version.

## Arguments and options

- `target`. Project root (default: current directory)
- `--dry-run`. Print the planned moves; change no file

## Exit status

```text
    0  success, no work, or --dry-run
    1  a step failed partway; every change of the run is undone
    2  refused before the first change: busy repository, a destination that
       already exists, two planned moves that still share a destination, or
       bad arguments
```

## See also

- [Command source](../../../scripts/migrate-spec-layout)
