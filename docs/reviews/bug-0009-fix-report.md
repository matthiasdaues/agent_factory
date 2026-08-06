---
title: "BUG-0009 Fix Report"
date: 2026-08-06
source: developer-agent
severity: major
status: resolved
---

# BUG-0009 Fix Report

## Summary

Fixed stale `_SURVEY_DESIGN` path in `orchestrator/tests/test_research_survey_playbook.py`
(line 13). The design document was relocated from `factory/docs/design/research-survey-mode.md`
to `docs/proposals/implemented/research-survey-mode.md` (commits 5f92617 / e620890),
but the test path was not updated.

## Change

Updated line 13:

- **Old:** `_ROOT / "factory" / "docs" / "design" / "research-survey-mode.md"`
- **New:** `_ROOT / "docs" / "proposals" / "implemented" / "research-survey-mode.md"`

## Verification

All 8 tests in `test_research_survey_playbook.py` pass, including
`test_FAGAN0009_design_records_the_implemented_schema_boundary`.

## Commit

`fix: correct stale _SURVEY_DESIGN path to docs/proposals/implemented (BUG-0009)`
on branch `bug/run-agent-envelope-recovery`.
