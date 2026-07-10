---
id: RECON-0001
source: reconcile-spec
severity: major
category: defect
artifact: src/orchestrator/approval_service.py#approve
status: resolved
traces: [VR-012, UC-04, BR-013]
---

# Artifact staleness check missing from ApprovalService.approve()

**What is wrong:** UC-04 extension 3a and VR-012 require that `approve()` re-verifies artifacts have not changed since the gate before allowing approval. The current implementation checks only that the gate passed and open findings equal zero, but does not compare the current artifact state against the gate checkpoint. A stale approval could advance a phase whose artifacts were modified after the gate ran.

**Fix:** Add a staleness check to `ApprovalService.approve()` that compares the current working tree (or the staged diff of declared artifact paths) against the run branch HEAD. If artifacts differ, refuse the approval and direct the Operator to re-run the gate (as specified in UC-04 extension 3a). This will require injecting the `GateRunner` (or a lighter artifact-hash check) into `ApprovalService`. The same check should apply in `_handle_resume` for the resume path (VR-012).
