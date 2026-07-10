---
id: FAGAN-0032
source: fagan-review
severity: critical
category: defect
artifact: src/orchestrator/cli.py#_new_run
status: resolved
traces: [BR-016, BR-017, VR-016, VR-017, UC-02, UC-03]
---

# Run branch never created or selected

**What is wrong:** The orchestrator records a dedicated run-branch name in `Run.branch` but never creates or checks out that branch before gating. `PreCommitGateRunner` now verifies the current branch matches the expected branch, so a real phase run will fail at the first gate unless the operator manually switched branches beforehand.

**Fix:** Add run bootstrap logic that creates/selects the dedicated run branch before any phase work starts, and persist/run only on that branch. This belongs in `_new_run()` or a new `RunStateStore.create_branch()` method.
