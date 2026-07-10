---
id: FAGAN-0018
source: fagan-review
severity: major
category: defect
artifact: src/orchestrator/adapters/copilot.py#_invoke_interactive
status: resolved
traces: [BR-018, BR-020]
---

# Interactive mode never sets auth/config error flags

**What is wrong:** Interactive invocations always return `auth_error=False` and `config_error=False` regardless of the actual outcome. An adapter auth failure or config error in interactive mode is misclassified as a generic author failure and sent through `RetryOrHalt` instead of halting.

**Fix:** After the interactive subprocess exits, inspect stderr/exit code with the same auth/config regex patterns used in `_invoke_captured` to set the flags correctly.
