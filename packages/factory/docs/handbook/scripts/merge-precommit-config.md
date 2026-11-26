---
title: merge-precommit-config
type: reference
status: implemented
description: Merge Factory hook entries into a project's pre-commit configuration.
---

# merge-precommit-config

## Name

`merge-precommit-config` — Merge Factory hook entries into a project's pre-commit configuration.

## Synopsis

```text
.agent-factory/factory/scripts/merge-precommit-config [<arguments> ...]
```

Use `--help` for argument values and defaults supported by your installed version.

## Arguments and options

- `--target`
- `--template`
- `--update`. strip the existing factory block and re-splice from the current template (used by update-factory to refresh hook entries)

## See also

- [Command source](../../../scripts/merge-precommit-config)
