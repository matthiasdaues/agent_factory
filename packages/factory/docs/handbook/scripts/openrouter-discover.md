---
title: openrouter-discover
type: reference
status: implemented
description: Discover OpenRouter models for the Pi model matrix.
---

# openrouter-discover

## Name

`openrouter-discover` — Discover OpenRouter models for the Pi model matrix.

## Synopsis

```text
.agent-factory/factory/scripts/openrouter-discover [<arguments> ...]
```

Use `--help` for argument values and defaults supported by your installed version.

## Arguments and options

- `--list`. List the catalog by price.
- `--suggest`. Suggest pi.\* rows.
- `--check`. Validate pi.\* rows against the catalog.
- `--min-context`. Minimum context length filter.
- `--max-price`. Max prompt price per token (--list).
- `--json`. JSON output (--list).
- `--cli`. CLI whose tier rows to check (--check).
- `--model-conf`. Path to model.conf (--check).
- `--url`. Catalog URL override (testing).

## See also

- [Command source](../../../scripts/openrouter-discover)
