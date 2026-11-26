---
title: module-graph-check
type: reference
status: implemented
description: Check module dependencies against the allowed module graph.
---

# module-graph-check

## Name

`module-graph-check` — Check module dependencies against the allowed module graph.

## Synopsis

```text
.agent-factory/factory/scripts/module-graph-check [<arguments> ...]
```

Use `--help` for argument values and defaults supported by your installed version.

## Arguments and options

- `--dsl-path`. path to architecture.dsl (default: docs/spec/architecture.dsl)
- `--interface-contracts`. path to interface-contracts.md (default: docs/spec/interface-contracts.md)
- `--entity-model`. path to entity-model.md (default: docs/spec/entity-model.md)
- `--proposal`. path to the proposal file whose frontmatter is updated
- `--story-id`. story identifier for the JSON log file
- `--report-dir`. directory where JSON reports are written

## See also

- [Command source](../../../scripts/module-graph-check)
