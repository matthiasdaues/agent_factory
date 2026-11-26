---
title: resolve-model
type: reference
status: implemented
description: Resolve a model from a CLI and tier in the model matrix.
---

# resolve-model

## Name

`resolve-model` — Resolve a model from a CLI and tier in the model matrix.

## Synopsis

```text
.agent-factory/factory/scripts/resolve-model [<arguments> ...]
```

Use `--help` for argument values and defaults supported by your installed version.

## Arguments and options

- `--agent`. Agent name (frontmatter tier is read from it).
- `--tier`. Tier override; skips reading the agent file.
- `--cli`. Target CLI, e.g. pi, claude, copilot.
- `--model-conf`. Path to model.conf (default: <repo-root>/config/model.conf).
- `--agents-dir`. Directory of agent markdown files.

## See also

- [Command source](../../../scripts/resolve-model)
