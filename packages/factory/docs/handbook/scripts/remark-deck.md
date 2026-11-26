---
title: remark-deck
type: reference
status: implemented
description: Build a remark.js deck from its slide source.
---

# remark-deck

## Name

`remark-deck` — Build a remark.js deck from its slide source.

## Synopsis

```text
.agent-factory/factory/scripts/remark-deck <command> [<arguments> ...]
```

Use `--help` for argument values and defaults supported by your installed version.

## Subcommands

- `new`

## Arguments and options across subcommands

- `dir`
- `--title`
- `--topic`. slug for the file name; defaults to the title
- `--lang`
- `--sample`. start from the ten sample slides

## Exit status

```text
  0  done; for check and build, no problem found
  1  the grid check found a problem; build writes no page
  2  a precondition failed: slides.txt exists on new, slides.txt is missing on
     check or build, or the date header is not YYYY-MM-DD
```

## See also

- [Command source](../../../scripts/remark-deck)
