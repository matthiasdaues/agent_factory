---
title: usage-query
type: reference
status: implemented
description: Query the views provided by the optional usage add-on.
---

# usage-query

## Name

`usage-query` — Query the views provided by the optional usage add-on.

## Synopsis

```text
.agent-factory/factory/scripts/usage-query <view> [<options> ...]
```

Run from the project root. The wrapper finds the usage add-on and passes the arguments to its query command.

## Examples

```bash
.agent-factory/factory/scripts/usage-query session_usage --format table
.agent-factory/factory/scripts/usage-query session_usage --persist usage.duckdb
```

The first command prints a table. The second writes a DuckDB file. See the [view and option reference](../usage-capture/usage-add-on-reference.md) for other query forms.

## See also

- [Command source](../../../scripts/usage-query)
- [Workflow guide](../usage-capture/query-usage-views.md)
