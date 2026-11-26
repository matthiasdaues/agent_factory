---
title: intent
type: reference
status: implemented
description: Report which agents can run or assess the artifacts in a project.
---

# intent

## Name

`intent` — Report which agents can run or assess the artifacts in a project.

## Synopsis

```text
.agent-factory/factory/scripts/intent select [--workstream ID] [--agents-dir DIR]
.agent-factory/factory/scripts/intent assess [--workstream ID] [--format text|json]
```

Use `--help` for argument values and defaults supported by your installed version.

## Subcommands

- `select`. List agents with precondition evidence.
- `assess`. Validate artifacts and report results.

## Arguments and options across subcommands

- `--workstream`. Workstream ID for scope filtering
- `--agents-dir`. Path to agents directory (default: .agent-factory/factory/agents)
- `--format`. Output format (default: text)

## See also

- [Command source](../../../scripts/intent)
