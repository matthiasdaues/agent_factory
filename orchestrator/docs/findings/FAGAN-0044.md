---
id: FAGAN-0044
status: resolved
severity: major
category: contract
artifact: orchestrator/src/orchestrator/adapters/gate_runner.py
pass: 3
---

# git reset HEAD cleans only the index; dirty worktree still accepted

The FAGAN-0033 fix resets the index but does not enforce the spec's "clean tree" requirement. Unrelated tracked/untracked changes remain in the worktree while gate commits proceed. Violates BR-016 / UC-02 preconditions.

**Suggested fix**: Fail fast on a non-clean worktree (`git status --porcelain`) before touching the index, or reject dirt outside the declared artifact set.
