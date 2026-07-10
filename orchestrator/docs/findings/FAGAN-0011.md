---
id: FAGAN-0011
source: fagan-review
severity: major
category: defect
artifact: src/orchestrator/approval_service.py#approve
status: resolved
traces: [VR-012, UC-04, BR-013]
---

# Stale artifacts only refused, not re-gated

**What is wrong:** When `approve()` detects stale artifacts, it raises `ValueError` and refuses the approval. UC-04 extension 3a says the orchestrator should re-run the gate before allowing approval — not just refuse. The operator has no automated path to re-gate; they must manually run a phase command.

**Fix:** Instead of raising, trigger a re-gate flow: re-enter the gating sub-state for the current phase, run the gate, and if it passes, proceed with approval. Or provide a clear CLI command to re-gate.
