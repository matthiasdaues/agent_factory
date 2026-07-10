---
id: FAGAN-0013
source: fagan-review
severity: major
category: defect
artifact: src/orchestrator/adapters/gate_runner.py#run
status: resolved
traces: [BR-016, VR-016]
---

# Gate runner ignores branch and allows unclean tree

**What is wrong:** `PreCommitGateRunner.run()` receives a `branch` parameter but never asserts the current git branch matches it. It also does not verify a clean index/worktree before staging, so unrelated staged changes can be committed alongside the phase artifacts. Git failures from `check=True` escape as Python exceptions instead of structured `GateResult.errored`.

**Fix:** Assert `git branch --show-current` matches `branch` before staging. Require a clean tree (`git status --porcelain` is empty) or at least a clean index. Wrap git subprocess failures in `GateResult(errored=True)` instead of raising exceptions.
