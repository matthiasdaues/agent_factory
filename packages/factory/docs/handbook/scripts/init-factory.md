---
title: init-factory
type: reference
status: implemented
description: Install the Factory and wire it into the selected coding CLIs.
---

# init-factory

## Name

`init-factory` — Install the Factory and wire it into the selected coding CLIs.

## Synopsis

```text
.agent-factory/factory/scripts/init-factory [<arguments> ...]
```

Use `--help` for argument values and defaults supported by your installed version.

## Arguments and options

- `--source`. agent_factory checkout to copy from (default: the checkout this script itself lives in)
- `--target`. project directory to initialize (default: cwd)
- `--usage-transcript-retention`
- `--project-name`. non-empty project name (prompted for on a fresh interactive install)
- `--cli`. which CLI(s) to wire (default: auto-detect or ask interactively)
- `--with-usage`. also install the usage-analysis component
- `--add`. add CLI wiring or a component to an existing install
- `--remove`. remove CLI wiring or a component from an existing install
- `--update`. update an installed component (compatible version only)

## See also

- [Command source](../../../scripts/init-factory)
- [Workflow guide](../installation-and-updates/index.md)
