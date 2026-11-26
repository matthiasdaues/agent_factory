---
title: update-factory
type: reference
status: implemented
description: Refresh an installation from the selected Factory source.
---

# update-factory

## Name

`update-factory` — Refresh an installation from the selected Factory source.

## Synopsis

```text
.agent-factory/factory/scripts/update-factory [<arguments> ...]
```

Use `--help` for argument values and defaults supported by your installed version.

## Arguments and options

- `--target`
- `--source`. agent_factory checkout whose factory/ is the new state (default: the source recorded in the install manifest)
- `--force`. proceed even when user modifications are detected; changed files are preserved under .agent-factory/user-changes/<timestamp>/
- `--check`. report user modifications and exit without updating
- `--from-remote`. update from a different remote base URL; a source kind or URL change requires separate consent (ST-0286)
- `--from-local`. update from a local checkout; a source kind change requires separate consent (ST-0286)

## See also

- [Command source](../../../scripts/update-factory)
- [Workflow guide](../installation-and-updates/update-the-factory.md)
