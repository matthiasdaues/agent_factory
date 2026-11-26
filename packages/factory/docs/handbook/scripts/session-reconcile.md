---
title: session-reconcile
type: reference
status: implemented
description: Compare session audit records with repository artifacts.
---

# session-reconcile

## Name

`session-reconcile` — Compare session audit records with repository artifacts.

## Synopsis

```text
.agent-factory/factory/scripts/session-reconcile [<arguments> ...]
```

Use `--help` for argument values and defaults supported by your installed version.

## Arguments and options

- `--log`. session log path
- `--base`. branch-root ref (omit for worktree-only)
- `--head`. branch-head ref
- `--format`
- `--report-only`. always exit 0 (report without gating)

## See also

- [Command source](../../../scripts/session-reconcile)
