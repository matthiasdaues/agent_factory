---
id: FAGAN-0012
source: fagan-review
severity: major
category: defect
artifact: src/orchestrator/approval_service.py#approve
status: resolved
traces: [UC-04]
---

# approve() sets RUNNING but does not advance chain

**What is wrong:** For non-final phases, `approve()` writes `run.mode = RUNNING` but does not advance `current_phase` or continue the chain. The persisted state says "running" while no phase is executing, and UC-04's postcondition ("continues the chain to the next phase") is not met by `ApprovalService` alone.

**Fix:** Either have `approve()` advance `current_phase` and invoke the chain runner, or keep the run paused until the CLI caller explicitly continues it. The latter is already how `_handle_approval` + `_auto_approve_chain` works in `cli.py`, so the `ApprovalService` contract should document that "continue" is the caller's responsibility.
