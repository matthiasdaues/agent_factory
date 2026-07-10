---
id: FAGAN-0014
source: fagan-review
severity: major
category: defect
artifact: src/orchestrator/adapters/gate_runner.py#run
status: resolved
traces: [ADR-0003, BR-015]
---

# Missing pre-commit config treated as pass not error

**What is wrong:** When `.pre-commit-config.yaml` does not exist, the gate returns `passed=True`. ADR-0003 establishes pre-commit as the gate mechanism; a missing config means the gate infrastructure is absent, which should be an error, not a silent pass.

**Fix:** Return `GateResult(errored=True, hook="pre-commit")` when the config file is missing.
