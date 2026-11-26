---
title: context-lint
type: reference
status: implemented
description: Check context declarations for Factory artifacts.
---

# context-lint

## Name

`context-lint` — Check context declarations for Factory artifacts.

## Synopsis

```text
.agent-factory/factory/scripts/context-lint [<arguments> ...]
```

Use `--help` for argument values and defaults supported by your installed version.

## Arguments and options

- `--context-dir`. Validate this directory as the agent-context CX-\* check directly, bypassing format detection (default: resolve via --root instead).
- `--charter-dir`. Run the legacy CH-\* markdown-charter check against this directory directly, bypassing format detection.
- `--root`. Project root used for format detection and testing.yaml resolution when neither --context-dir nor --charter-dir is given (default: .)
- `--print-format`. Print the format-detection-chain result for --root and exit (agent-context, legacy-yaml, legacy-markdown, or none); runs no validation.
- `--template-dir`. Path to templates, used only with --charter-dir or the legacy-markdown fallback (default: .agent-factory/factory/rulebooks/templates)
- `--planning-gate`. Planning-gate mode (currently identical to default — CX-NULL is always an error)
- `--format`. Output format (default: text)
- `--report-only`. Always exit 0 (report without gating)

## See also

- [Command source](../../../scripts/context-lint)
