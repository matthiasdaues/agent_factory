# FAGAN-0027 — Read/Write Guard Path Prefixes

**Date:** 2026-08-26\
**Severity:** Trivial\
**Category:** Correctness\
**Status:** Not a defect — working as designed

______________________________________________________________________

## Summary

`step-guard` hardcodes allowed path prefixes for read operations (`factory/`, `.claude/`, `.github/`, `.pi/`, `.codex/`, `.current_work/`) and write operations (`docs/findings/`) plus specific allowed paths (gate markers). The implementation correctly denies ledger and manifest writes regardless of output globs.

## Evidence

```python
# factory/scripts/step-guard
READ_ALLOWED_PREFIXES = (
    "factory/",
    ".claude/",
    ".github/",
    ".pi/",
    ".codex/",
    ".current_work/",
)
WRITE_ALLOWED_PREFIXES = ("docs/findings/",)
WRITE_ALLOWED_PATHS = {
    ".current_work/verify-base-ok",
    ".current_work/premerge-check-ok",
}
WRITE_DENIED_PATHS = {
    ".current_work/dispatch-ledger.yaml",
    ".current_work/current-step.yml",
}
```

## Specification Alignment

From `mechanized-dispatch.md`:

> "Factory machinery paths are always allowed"\
> "Dispatch ledger is always denied to step agents"\
> "Step manifest file is always denied to step agents"

## Conclusion

This behavior is **correct per specification**. The security deny-list is implemented and working as intended.

## No Action Required

This is not a defect — it's an intentional security boundary.
