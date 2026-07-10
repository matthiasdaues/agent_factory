---
id: FAGAN-0028
source: fagan-review
severity: major
category: defect
artifact: src/orchestrator/cli.py#_handle_run_step
status: resolved
traces: [UC-03, FR-J, QS-13]
---

# run-step does not write invocation log entry

**What is wrong:** `_handle_run_step()` invokes the adapter directly and checks for declared outputs, but never writes an invocation-log entry via the `Logger` port. All other execution paths (`PhaseRunner`) log invocations. This breaks the observability contract (FR-J, QS-13).

**Fix:** Create an `AgentInvocation` record and call `logger.log()` after the `run-step` invocation completes.
