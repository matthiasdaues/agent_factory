---
id: FAGAN-0046
status: resolved
severity: major
category: contract
artifact: orchestrator/src/orchestrator/adapters/gate_runner.py
pass: 3
---

# Auto-fixing hook re-stage/re-run path is missing

UC-02 ext 5c / building-block view require one re-stage/re-commit/re-run pass for auto-fixing hooks. The current runner commits once, runs pre-commit once, and classifies immediately; it never detects rewritten files and retries once.

**Suggested fix**: After the first non-zero pre-commit run, detect modified files in the declared artifact set, re-stage/amend, and rerun pre-commit once before classifying the result.

> **Follow-up:** the primary defect is fixed; residual edge cases are tracked in \[[FAGAN-0050]\].
