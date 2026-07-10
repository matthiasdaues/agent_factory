---
id: FAGAN-0001
source: fagan-review
severity: minor
category: defect
artifact: factory/scripts/merge-precommit-config#extract_marker_id
status: open
traces: []
---

# `extract_marker_id()` can pick up a hook id from a later, non-`repo: local` block

**What is wrong:** `extract_marker_id()` (added by `RECON-0001`, commit `6378652`)
sets `in_block = True` on matching the template's `- repo: local` block-start line
and never resets it. If that block's own `hooks:` list has no `- id: <name>` line
before the file's next top-level `- repo:` entry starts (e.g. a hosted repo added
after the local block — a normal `.pre-commit-config.yaml` shape, just not one any
current template in this repo happens to use), the function's scan carries on past
the block boundary and returns the first `- id:` line it finds in that *next*
`repo:` block instead, silently mislabelling a foreign hook as the local block's own
marker. Confirmed directly:

```python
template = """repos:
  - repo: local
    hooks: []
  - repo: https://github.com/foo/bar
    rev: v1.0
    hooks:
      - id: some-external-hook
"""
extract_marker_id(template.splitlines())  # returns "id: some-external-hook"
```

The new test suite (`orchestrator/tests/test_merge_precommit_config.py`,
`TestExtractMarkerId`) only exercises the happy path — a template whose sole
`repo:` entry is `repo: local` with a hook id present — so this boundary condition
has no regression coverage. Not currently triggered by either shipped template
(`factory/config/pre-commit-config.yaml`, `orchestrator/pre-commit-config.yaml`),
both single-block, but it is a real defect in code this range introduces, and
`docs/adr/0001-precommit-monorepo-scoping.md` designates this script as the
standard splicing mechanism every future subproject (`factory_api/` and beyond)
is expected to rely on — a template that pairs local hooks with a hosted repo is a
realistic shape for a future subproject to use.

**Fix:** In `extract_marker_id()`, stop scanning for a hook id once the block ends
(the next top-level `- repo:` line, matched the same way `find_repos_list_bounds()`
already detects a sibling top-level key) rather than scanning to EOF. Add a test
case with a template whose `repo: local` block has no matching hook id followed by
a second, non-local `repo:` block, asserting `extract_marker_id()` raises
`ValueError` (its own documented behaviour for "no `- id:` hook inside the block")
rather than returning the foreign block's id.
