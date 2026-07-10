---
id: FAGAN-0039
status: resolved
severity: major
category: contract
artifact: orchestrator/src/orchestrator/approval_service.py
pass: 3
---

# Failed stale re-gate wedges run in awaiting-approval

If approval re-gating detects changed artifacts and the re-gate fails, the code updates `last_gate` and saves, but leaves the phase in `awaiting-approval`. After that, `approve` fails (`gate has not passed`) and `resume`/`run-phase` do not recover because `awaiting-approval` is treated as terminal. Violates UC-04 ext 3a / UC-06 recoverability.

**Suggested fix**: On failed re-gate, move the phase out of `awaiting-approval` into a resumable execution state (`gating` or a loop-back path), persist that state, and ingest deterministic findings if the failure is a findings result.
