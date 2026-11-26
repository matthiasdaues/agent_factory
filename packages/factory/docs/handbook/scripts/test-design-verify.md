---
title: test-design-verify
type: reference
status: implemented
description: Check that required test evidence is present for a story.
---

# test-design-verify

## Name

`test-design-verify` — Check that required test evidence is present for a story.

## Synopsis

```text
.agent-factory/factory/scripts/test-design-verify [<arguments> ...]
```

Use `--help` for argument values and defaults supported by your installed version.

## Arguments and options

- `--story`. path to the story file
- `--story-id`. story identifier for the JSON report filename (default: story's own id: frontmatter, then filename stem)
- `--scope-map`
- `--spec-dir`
- `--repo-root`. root used to resolve waiver/prior-test module paths (default: .)
- `--report-dir`
- `--epics`

## See also

- [Command source](../../../scripts/test-design-verify)
