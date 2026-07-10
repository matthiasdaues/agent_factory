---
id: FAGAN-0047
status: resolved
severity: major
category: error-handling
artifact: orchestrator/src/orchestrator/cli.py
pass: 3
---

# Halted runs still exit 0

`_handle_run_phase()`, `_handle_run_all()`, `_handle_resume()`, and `_auto_approve_chain()` always return `0` unless an exception is raised. A halted run therefore reports success, violating UC-07 ext 3a / postconditions.

**Suggested fix**: After phase/chain execution, inspect `run.mode` / returned result and return non-zero for `HALTED`; propagate that through auto-approve/resume paths.
