---
id: FAGAN-0002
source: fagan-review
severity: critical
category: defect
artifact: src/orchestrator/phase_runner.py#run_phase
status: resolved
traces: [UC-06, VR-005, ATAM-R07]
---

# run_phase() ignores persisted sub-state on resume

**What is wrong:** `run_phase()` always resets the phase to `AUTHORING` on entry regardless of the persisted `phase.status`. If the orchestrator resumes a run where a phase was in `GATING`, `REVIEWING`, or `AWAITING_APPROVAL`, it replays authoring from scratch instead of resuming from the checkpoint. This violates UC-06 (resume from last checkpoint) and the resume-idempotency notes in `interface-contracts.md` and `state-machines.md` (ATAM-R07/T-17).

**Fix:** Check `phase.status` on entry and resume from the persisted sub-state: if `GATING`, re-run the gate; if `REVIEWING`, re-run the reviewer; if `AWAITING_APPROVAL`, return immediately. Only enter `AUTHORING` from `PENDING` or after an explicit loop-back.
