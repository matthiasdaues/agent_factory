---
id: FAGAN-0033
source: fagan-review
severity: major
category: defect
artifact: src/orchestrator/adapters/gate_runner.py#run
status: resolved
traces: [BR-016, VR-016, UC-02]
---

# Gate runner does not enforce a clean worktree before staging

**What is wrong:** The gate runner stages declared artifacts and commits them without first proving the worktree/index is clean. Unrelated local changes can be swept into the phase commit, violating commit hygiene (BR-016) and corrupting the gate input.

**Fix:** Enforce a clean tree/index before staging, or refuse the run with a structured gate error that tells the operator to clean the tree first. Check `git status --porcelain` before staging declared artifacts.
