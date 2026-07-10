---
id: FAGAN-0052
source: fagan-review
severity: critical
category: defect
artifact: orchestrator/src/orchestrator/approval_service.py:56
status: resolved
traces: [ADR-0013, VR-012, UC-04]
---

# Stale gate API — approval_service still calls removed `run()` method

**What is wrong:** `ApprovalService.approve()` calls `self._gate_runner.run(outputs, branch, phase)` at line 56, but the `GateRunner` port was changed to `verify(cwd, exit_code)` and the old `run()` method no longer exists on `WorkingTreeGate`. Any stale-approval re-gate path will raise `AttributeError` at runtime.

**Fix:** Replace the `run()` call in `approval_service.py` with the new `verify(cwd, exit_code)` contract. The stale-approval re-gate needs to check working-tree cleanliness (not run pre-commit hooks), so call `verify(cwd, exit_code=0)` and handle the four-cell result. Update the approval service tests accordingly.
