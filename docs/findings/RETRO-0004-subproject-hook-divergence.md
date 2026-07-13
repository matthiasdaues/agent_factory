---
id: RETRO-0004
title: Subproject hooks diverged from factory pattern
status: open
severity: minor
category: consistency
date: 2026-07-13
found_by: session-retrospective
tags: [retro, pre-commit, subproject]
---

# RETRO-0004: Subproject hooks diverged from factory pattern

The orchestrator pre-commit hooks initially used `uv run --project orchestrator mdformat` and `uv run --project orchestrator ruff`, requiring a `pyproject.toml` in the orchestrator subproject. The factory hooks use `factory/scripts/mdformat` (which calls `uvx` internally) and `uvx ruff`. The inconsistency caused a build failure, a false-start `pyproject.toml`, and three hook rewrites.

**Fix:** Document the rule in `factory/docs/factory-guide.md` § Pre-commit hooks: subproject hooks must use `factory/scripts/` wrappers and `uvx`, not `uv run --project`. When adding a subproject, copy hook entries from the factory section and change only the `files:` pattern.
