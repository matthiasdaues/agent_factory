---
title: dependency-check
type: reference
status: implemented
description: Check source imports against declared dependency rules.
---

# dependency-check

## Name

`dependency-check` — Check source imports against declared dependency rules.

## Synopsis

```text
.agent-factory/factory/scripts/dependency-check [<arguments> ...]
```

Use `--help` for argument values and defaults supported by your installed version.

## Arguments and options

- `--dsl-path`. path to dependency rules DSL (default: docs/spec/dependency-rules.dsl)
- `--source-root`. root directory to scan for Python files (default: current directory)
- `--story-id`. story identifier for the JSON log file (default: env/branch/adhoc)
- `--report-dir`. directory where JSON reports are written

## See also

- [Command source](../../../scripts/dependency-check)
