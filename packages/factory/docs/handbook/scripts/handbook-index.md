---
title: handbook-index
type: reference
status: implemented
description: Regenerate the page lists in both Factory handbooks.
---

# handbook-index

## Name

`handbook-index` — Regenerate the page lists in both Factory handbooks.

## Synopsis

```text
packages/factory/scripts/handbook-index [<arguments> ...]
```

Run from the Factory source repository root.

Use `--help` for argument values and defaults supported by your installed version.

## Arguments and options

- `--check`. write nothing; name each stale page list

## Exit status

```text
  0  every page list is written or, with --check, current
  1  a refusal, or with --check a page list that differs
```

## See also

- [Command source](../../../scripts/handbook-index)
