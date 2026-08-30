# FAGAN-0026 — Premerge-Check Scope Validation

**Date:** 2026-08-26\
**Severity:** Minor\
**Category:** Correctness\
**Status:** Not a defect — working as designed

______________________________________________________________________

## Summary

`premerge-check` receives glob patterns via `--scope-glob` and validates changed files against the story's `outputs`. The story's `outputs` globs are passed to `premerge-check` for gitignore-style matching.

## Evidence

From `tests/test_dispatch_merge_integration.py::test_premerge_check_receives_scope_globs`:

```python
def test_premerge_check_receives_scope_globs(tmp_git_repo):
    # Story has outputs ["docs/spec/use_cases/UC-*.md"]
    # dispatch merge-story passes --scope-glob for each glob
    # premerge-check validates changed files against these globs
    ...
```

## Specification Alignment

From `mechanized-dispatch.md`:

> "premerge-check receives output globs via --scope-glob and uses gitignore-style matching (not prefix matching)"

## Conclusion

This behavior is **correct per specification**. The glob matching is enforced by the shared `dispatch_lib.glob_match()` implementation.

## No Action Required

This is not a defect — it's an intentional design to prevent scope violations at merge time.
