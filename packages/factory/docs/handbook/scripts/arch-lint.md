---
title: arch-lint
type: reference
status: implemented
description: Check the structure of the project's arc42 documentation and architecture references.
---

# arch-lint

## Name

`arch-lint` — Check the structure of the project's arc42 documentation and architecture references.

## Synopsis

```text
.agent-factory/factory/scripts/arch-lint [<arguments> ...]
```

Use `--help` for argument values and defaults supported by your installed version.

## Arguments and options

- `--dsl`. Structurizr workspace (default: docs/spec/architecture.dsl)
- `--docs-dir`. arc42 folder with chapter 5 (default: docs/arc42)
- `--no-validate`. skip structurizr validate
- `--no-export`. skip the auto-export of stale diagrams; tests use it so a run never rewrites docs/assets/images (T-0019)
- `--allow-missing-docs-dir`. warn instead of exit 2 when --docs-dir does not exist

## See also

- [Command source](../../../scripts/arch-lint)
- [Workflow guide](../quality-and-review/gate-scripts.md)
