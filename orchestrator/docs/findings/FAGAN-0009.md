---
id: FAGAN-0009
source: fagan-review
severity: major
category: defect
artifact: src/orchestrator/phase_runner.py
status: resolved
traces: [BR-018, BR-020]
---

# Reviewer auth/config errors not halted immediately

**What is wrong:** When a reviewer invocation returns `auth_error=True` or `config_error=True`, `PhaseRunner` treats these as ordinary reviewer failures and sends them through `RetryOrHalt`. BR-018 and BR-020 require adapter auth/config failures to halt immediately without consuming an iteration, just as they do for the author.

**Fix:** Add the same auth/config precedence checks after reviewer invocation that exist after author invocation. Halt immediately on auth or config error.
