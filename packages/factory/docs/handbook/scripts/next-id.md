---
title: next-id
type: reference
status: implemented
description: Allocate the next ID for a Factory artifact.
---

# next-id

## Name

`next-id` — Allocate the next ID for a Factory artifact.

## Synopsis

```text
.agent-factory/factory/scripts/next-id [<arguments> ...]
```

## Arguments and options

- `--seed`. create the counter once
- `--plan-seed`. print the seed command that continues every ID sequence
- `--move-to-origin`. move the local counter of agent-factory.counterRemote to origin
- `--remote`. the remote URL; the default is the git setting agent-factory.counterRemote, then the URL of origin
- `arguments`. <PREFIX>, or <number> \[<PREFIX>=<n> …\]

## See also

- [Command source](../../../scripts/next-id)
