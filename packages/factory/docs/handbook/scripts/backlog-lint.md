---
title: backlog-lint
type: reference
status: implemented
description: Check backlog story files, their metadata, and their dependencies.
---

# backlog-lint

## Name

`backlog-lint` — Check backlog story files, their metadata, and their dependencies.

## Synopsis

```text
.agent-factory/factory/scripts/backlog-lint [<arguments> ...]
```

Use `--help` for argument values and defaults supported by your installed version.

## Arguments and options

- `--backlog-dir`
- `--format`
- `--report-only`. always exit 0 (report without gating)
- `--exclude`. skip files whose name matches GLOB (repeatable)

## See also

- [Command source](../../../scripts/backlog-lint)
