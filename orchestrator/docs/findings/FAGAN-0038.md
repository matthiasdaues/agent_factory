---
id: FAGAN-0038
source: fagan-review
severity: major
category: defect
artifact: src/orchestrator/phase_runner.py#run_phase
status: resolved
traces: [UC-02, UC-04]
---

# Interactive empty-commit deadlocks at approval

**What is wrong:** In interactive mode, an empty-commit gate result sets `AWAITING_APPROVAL` with `last_gate.hook='empty-commit'` and `last_gate.passed=False`. But `ApprovalService.approve()` requires `last_gate.passed == True`, and `resume` re-pauses immediately. This path deadlocks — the operator cannot approve or resume.

**Fix:** Represent interactive empty-commit as a distinct resumable state, or teach `approve()`/`resume` how to complete that path without requiring `last_gate.passed=True`. One option: set a sentinel on the phase record (e.g. `interactive_pause=True`) so approval can bypass the gate-passed check for this specific case.
