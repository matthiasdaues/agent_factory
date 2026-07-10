---
id: FAGAN-0029
source: fagan-review
severity: major
category: defect
artifact: tests/
status: resolved
traces: []
---

# No handler-level tests for CLI commands

**What is wrong:** CLI tests cover only argument parsing and `init` scaffolding. There are no tests for the handler functions (`_handle_run_step`, `_handle_run_phase`, `_handle_run_all`, `_handle_resume`, `_handle_approval`). The composition-root wiring defects are therefore untested.

**Fix:** Add `main()` / handler tests with fakes for runtime, stores, locks, and adapter. Test the actual command dispatch path, not just argument parsing.
