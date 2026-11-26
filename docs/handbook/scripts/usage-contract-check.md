---
title: usage-contract-check
type: reference
status: implemented
description: Validate usage JSON Lines records against the usage contract.
---

# usage-contract-check

## Name

`usage-contract-check` — Validate usage JSON Lines records against the usage contract.

## Synopsis

```text
packages/usage/scripts/usage-contract-check <path> [<path> ...]
```

Run from the Factory source repository root.

Pass a JSON Lines input file or directory. Exit status 1 means a record failed validation. Status 2 means an operational error.

## See also

- [Command source](../../../packages/usage/scripts/usage-contract-check)
