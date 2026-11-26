---
title: move-docs
type: reference
status: implemented
description: Move Markdown documentation and rewrite affected links.
---

# move-docs

## Name

`move-docs` — Move Markdown documentation and rewrite affected links.

## Synopsis

```text
.agent-factory/factory/scripts/move-docs [<arguments> ...]
```

Use `--help` for argument values and defaults supported by your installed version.

## Arguments and options

- `--dry-run`. change no file
- `--root`. project root (default: .)
- `paths`. pairs of paths

## Exit status

```text
    0  success or --dry-run
    1  a step failed partway; every change of the run is undone
    2  refused before the first change: bad arguments, a missing OLD, a NEW
       that exists already, or two moves with the same NEW
```

## See also

- [Command source](../../../scripts/move-docs)
