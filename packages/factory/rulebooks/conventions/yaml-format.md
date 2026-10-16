---
title: YAML Document Start
category: implementation
enforcement: yamllint document-start rule (this repository) + tests/factory/test_yaml_document_start.py (factory writers and YAML examples)
version: 1.0.0
---

# YAML Document Start

## Rule

Every YAML file begins with the document marker `---`. The stakeholder
decided this on 2026-10-15.

The rule covers three things:

1. Every YAML file in this repository. `yamllint` enforces it.
2. Every YAML file the factory creates in a target project, such as
   `docs/testing.yaml`, a new `.pre-commit-config.yaml`, the dispatch
   ledger, and `INDEX.yaml`.
3. Every YAML example the factory gives agents in a skill, template, or
   rulebook, including front matter excerpts. Agents copy examples, so an
   example without the marker spreads the gap.

Write `---` on the first line. Comments follow it.

## Exceptions

- A YAML file that belongs to the developer stays as it is. When the
  factory merges hooks into an existing `.pre-commit-config.yaml`, it does
  not add the marker.
- The factory does not enforce the marker inside target projects.
