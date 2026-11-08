---
type: fagan-review
title: Fagan inspection of finding-classification
date: 2026-11-08
status: pass
reviewer: qa-agent
findings_filed: 1
branch: feature/finding-classification
branch_base: 2e4cd6fb975db9b1bffbfab56696284ebbe66c68
branch_head: 107bd1dee469710ef3eac740bdfbfd56d55e2520
---

# Fagan inspection of finding-classification

## Result

The inspection found no blocking defect of its own, one minor defect, and one note. The two major defects of this QA pass came from running the code, so they are in [the bug hunt report](bug-hunt-2026-11-08-finding-classification.md).

The severity rules of `finding-lint` match the rulebook for all five classes. The stop subcommands in `dispatch_lib.py` match the two lists of BR-091.

## Scope

The inspection covered `git diff dev...feature/finding-classification`. It read these in full: `guard-human-fields`, `finding-lint`, the Pi extension, the OpenCode plugin, the rulebook `finding-classification.md`, and the diffs of `dispatch`, `dispatch_lib.py`, `premerge-check`, `next-id`, `init-factory`, and the hook registration files.

Two story checks passed:

- All 22 stories, ST-0386 to ST-0407, trace to a `.feature` file. So none of them needs a `test-design-pass` field. ST-0404 traces to `counter-ids-fitting.feature`, and the others to `finding-classification.feature`.
- All 91 test identifiers of the QA strategy, from the form `FC-01-CT-01` on, appear in `tests/factory/` or in the tests under `packages/factory/config/`.

## Not checked

The inspection did not read the test modules line by line, and it did not run them, because the guardrail hook refuses `uv run pytest`. The changed playbooks, skills, and agent definitions were not inspected again, because the code review of 2026-11-08 covered them and they did not change after it. The Markdown under `docs/spec/` was outside this inspection.

## Findings

| Finding                                                                                                                                                              | Artifact                                               | Category   | Severity | Filed as      |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------ | ---------- | -------- | ------------- |
| `finding-lint` and `dispatch_lib.py` each parse `## Possible damage`, and they disagree on `* ` bullets. Let one function own the parse.                             | `packages/factory/scripts/dispatch_lib.py:1882-1899`   | Defect     | minor    | FAGAN-0034    |
| YAGNI: `check_call` also reads the argument keys `javascript` and `script`, and no row of the guard contract names them. Remove the two keys until a CLI needs them. | `packages/factory/config/hooks/guard-human-fields:124` | Suggestion | note     | `report only` |
