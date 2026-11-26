---
title: Scripts and manpages
type: concept
status: implemented
order: 75
description: Find script entry points, source code, and maintenance commands.
---

# Scripts and manpages

Start with the [Factory script manpages](../../../packages/factory/docs/handbook/scripts/index.md) for commands under `packages/factory/scripts/`. The linked source is the code to edit. To run a command directly from a Factory checkout, use its source path in place of the installed path when the command supports checkout operation.

Agents can call the same commands you run in a terminal. [How a Factory run works](../architecture/how-a-factory-run-works.md) traces one call from an agent to its linter. [Testing](../testing/index.md) explains how to choose a check for a script change. Update the command's page when you change its interface or effects.

The usage add-on has three additional checks under `packages/usage/scripts/`. Run them from the repository root.

<!-- handbook-index:start -->

## Reference

- [usage-contract-check](usage-contract-check.md): Validate usage JSON Lines records against the usage contract.
- [usage-dependency-check](usage-dependency-check.md): Check that the usage package declares its required dependencies.
- [usage-ui-doc-check](usage-ui-doc-check.md): Check the usage browser documentation against the SQL and code.

<!-- handbook-index:end -->
