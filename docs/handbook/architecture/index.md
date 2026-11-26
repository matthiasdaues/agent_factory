---
title: Architecture
type: concept
status: implemented
order: 20
description: This chapter explains the packages, the install model, and the engine of the factory.
---

# Architecture

Start with [How a Factory run works](how-a-factory-run-works.md) to see how the instructions and executable code work together. For usage changes, start with [From CLI session to usage report](from-cli-session-to-usage-report.md).

<!-- handbook-index:start -->

## Concepts

- [From CLI session to usage report](from-cli-session-to-usage-report.md): Trace token counts from CLI events through capture and analysis.
- [How a Factory run works](how-a-factory-run-works.md): Follow a specification review from the playbook to the reviewer and its checks.
- [The usage add-on pipeline](usage-add-on.md): How the usage add-on turns JSONL records into six views in four stages.

## How-to guides

- [Run the usage add-on from source](run-usage-add-on-from-source.md): Install, query, and explore the usage add-on from a checkout of the factory repository.

## Reference

- [Repository layout](repository-layout.md): The top-level folders of the factory repository, with the source of the factory and its installed copy.
- [Usage add-on structure](usage-add-on-structure.md): The directory tree of packages/usage/, the wrapper scripts that find it, and the documents that describe it.

<!-- handbook-index:end -->
