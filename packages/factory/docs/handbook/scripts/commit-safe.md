---
title: commit-safe
type: reference
status: implemented
description: Stage selected files and retry a commit if formatting hooks change them.
---

# commit-safe

## Name

`commit-safe` — Stage selected files and retry a commit if formatting hooks change them.

## Synopsis

```text
.agent-factory/factory/scripts/commit-safe -m "<message>" [<path> ...]
```

Run from the repository root. The command stages files and creates a Git commit.

## See also

- [Command source](../../../scripts/commit-safe)
