---
title: premerge-check
type: reference
status: implemented
description: Check a branch and its required evidence before merge.
---

# premerge-check

## Name

`premerge-check` — Check a branch and its required evidence before merge.

## Synopsis

```text
.agent-factory/factory/scripts/premerge-check <target> <branch> [<options> ...]
```

Use `--help` for argument values and defaults supported by your installed version.

## Arguments and options

- `target`. merge target branch, e.g. dev
- `branch`. finished branch being considered for merge
- `--scope`. declared path prefix the dispatch said it would touch; repeatable
- `--scope-glob`. gitignore-style glob pattern for scope matching; repeatable
- `--max-files`. file-count blowout threshold (default 20; the feature merge has no limit without it)

## See also

- [Command source](../../../scripts/premerge-check)
