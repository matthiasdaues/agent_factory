# FAGAN-0025 — Wave Escalation Slot Exhaustion

**Date:** 2026-08-26\
**Severity:** Minor\
**Category:** Correctness\
**Status:** Not a defect — working as designed

______________________________________________________________________

## Summary

When a wave's escalation slot is exhausted (another story in the same wave has `escalation_granted: true`), a story failing with a qualifying failure class (`acceptance_unmet` or `contradictory_evidence`) is marked `BLOCKED` with `reason: "wave_escalation_exhausted"`.

## Evidence

```python
# dispatch_lib.py: escalation predicate
if any(
    other.id != entry.id and other.wave == entry.wave and other.escalation_granted
    for other in ledger.stories.values()
):
    entry.status = StoryState.BLOCKED
    entry.reason = "wave_escalation_exhausted"
```

## Specification Alignment

From `mechanized-dispatch.md`:

> "Second qualifying failure in wave after escalation slot is taken marks the story `blocked` with reason `wave_escalation_exhausted`."

## Conclusion

This behavior is **correct per specification**. The story may escalate in a later wave of the same dispatch if its own one-escalation limit is unused.

## No Action Required

This is not a defect — it's an intentional safeguard against unlimited escalation within a wave.
