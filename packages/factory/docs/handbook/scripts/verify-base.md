---
title: verify-base
type: reference
status: implemented
description: Verify that a worktree is on its declared branch and base.
---

# verify-base

## Name

`verify-base` — Verify that a worktree is on its declared branch and base.

## Synopsis

```text
.agent-factory/factory/scripts/verify-base [<arguments> ...]
```

Use `--help` for argument values and defaults supported by your installed version.

## Arguments and options

- `target`. target branch HEAD must not be behind, e.g. dev
- `--expect-base`. SHA the dispatcher recorded as this worktree's declared base

## See also

- [Command source](../../../scripts/verify-base)
