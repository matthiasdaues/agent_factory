---
title: spec-lint
type: reference
status: implemented
description: Check specification artifacts for structural consistency.
---

# spec-lint

## Name

`spec-lint` — Check specification artifacts for structural consistency.

## Synopsis

```text
.agent-factory/factory/scripts/spec-lint [<arguments> ...]
```

Use `--help` for argument values and defaults supported by your installed version.

## Arguments and options

- `--spec-dir`
- `--glossary`. the glossary whose table terms GLOSS001 checks
- `--format`
- `--gate-todos`. treat unresolved todos as an error
- `--report-only`. always exit 0 (report without gating)

## See also

- [Command source](../../../scripts/spec-lint)
