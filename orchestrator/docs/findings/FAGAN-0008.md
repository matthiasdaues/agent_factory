---
id: FAGAN-0008
source: fagan-review
severity: major
category: defect
artifact: src/orchestrator/phase_runner.py#run_phase
status: resolved
traces: [UC-02, VR-001, VR-014]
---

# Deterministic gate findings never ingested

**What is wrong:** When the gate fails with `passed=False`, `PhaseRunner` immediately loops the author. It never ingests the deterministic findings (e.g., `spec-lint --format json` output) from the gate. The `GateRunner` port returns only `GateResult` with no findings payload. The author is looped without knowing what to fix, and finding-store counts are wrong.

**Fix:** Extend the gate contract: either add a `findings` field to `GateResult`, or add a `gate_findings()` method to `GateRunner`. Ingest and tag deterministic findings before loop-back, so the author prompt includes them.
