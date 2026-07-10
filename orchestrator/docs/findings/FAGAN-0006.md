---
id: FAGAN-0006
source: fagan-review
severity: critical
category: defect
artifact: src/orchestrator/cli.py#_new_phase_record
status: resolved
traces: [VR-011, BR-006]
---

# Missing reviewer silently downgraded to gate-only

**What is wrong:** `_new_phase_record()` catches any `ValueError` from reviewer agent resolution and silently sets `reviewer=None`. If `spec-review-agent.md`, `architecture-review-agent.md`, or `qa-agent.md` is missing from the agents directory, the phase is silently downgraded to a gate-only phase with no reviewer. This violates VR-011 (fail-fast on unknown agent) and BR-006 (defined phase model).

**Fix:** Only set `reviewer=None` for phases explicitly defined without a reviewer (planning). For all other phases, let the `ValueError` propagate as a fail-fast error.
