---
id: FAGAN-0054
source: fagan-review
severity: major
category: defect
artifact: orchestrator/src/orchestrator/phase_runner.py:_clean_tree
status: resolved
traces: [ADR-0001, ADR-0013, VR-026]
---

# `_clean_tree()` is direct I/O in the core layer — architecture violation

**What is wrong:** `PhaseRunner._clean_tree()` calls `subprocess.run(["git", "checkout", "."])` and `subprocess.run(["git", "clean", "-fd"])` directly. `PhaseRunner` is a core module; direct subprocess calls violate the Clean Architecture rule that the core layer has no I/O (ADR-0001, Dependency Inversion).

**Fix:** Add a `clean_tree(cwd: Path) -> None` method to the `GateRunner` port (or a new port if preferred). Implement it in `WorkingTreeGate`. Inject it into `PhaseRunner` via the existing `_gate` dependency. Replace the inline subprocess calls with `self._gate.clean_tree(self._cwd)`.
