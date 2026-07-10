---
id: FAGAN-0053
source: fagan-review
severity: critical
category: defect
artifact: orchestrator/src/orchestrator/phase_runner.py:_halt
status: resolved
traces: [ADR-0015, VR-029]
---

# `_halt()` never sets `halted_from` — release command is inoperable

**What is wrong:** `PhaseRunner._halt()` sets `phase.status = HALTED` and `run.mode = HALTED` but never records the prior status into `phase.halted_from`. The `halted_from` field exists on `PhaseRecord` and the `release` command requires it (VR-029), but no production code path writes it. Every halt produces `halted_from=None`, making `release` refuse with "no halted_from recorded".

**Fix:** In `_halt()`, capture `phase.halted_from = phase.status` **before** setting `phase.status = PhaseStatus.HALTED`. This preserves the breadcrumb so `release` can restore it. Add a test that halts via a real code path and then verifies `halted_from` is set.
