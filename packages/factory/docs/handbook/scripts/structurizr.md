---
title: structurizr
type: reference
status: implemented
description: Validate the architecture workspace or export its views.
---

# structurizr

## Name

`structurizr` — Validate the architecture workspace or export its views.

## Synopsis

```text
.agent-factory/factory/scripts/structurizr {validate,export-svg,export-all,list-views} [<arguments> ...]
```

Requires Docker. Set `STRUCTURIZR_DOCS` or `STRUCTURIZR_WORKSPACE` to select the workspace. The export commands write SVG files.

## See also

- [Command source](../../../scripts/structurizr)
