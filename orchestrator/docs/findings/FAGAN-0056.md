---
id: FAGAN-0056
source: fagan-review
severity: major
category: defect
artifact: orchestrator/src/orchestrator/adapters/gate_runner.py:_dirty_files
status: resolved
traces: [VR-025, ADR-0013]
---

# `_dirty_files()` ignores subprocess failures — confabulation can be hidden

**What is wrong:** `WorkingTreeGate._dirty_files()` calls `subprocess.run(["git", "status", "--porcelain"])` but does not check `result.returncode`. If `git status` fails (e.g. not a git repo, corrupt index, permission error), `result.stdout` is empty and the method returns an empty list — which `verify()` interprets as "clean tree". An exit-0 agent in a broken-git scenario would pass the gate instead of being caught as confabulation. Similarly, `artifacts_changed()` ignores return codes on `git diff` and `git ls-files`.

**Fix:** Check `result.returncode != 0` and either raise an exception or return a `GateResult(errored=True, ...)` so the caller can halt. Add test cases for subprocess failures.
