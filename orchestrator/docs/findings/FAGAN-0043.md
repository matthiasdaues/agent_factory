---
id: FAGAN-0043
status: resolved
severity: major
category: contract
artifact: orchestrator/src/orchestrator/phase_runner.py
pass: 3
---

# Resume from REVIEWING can duplicate reviewer work/findings

The resume path for `REVIEWING` always re-invokes the reviewer and re-ingests findings. There is no check for "current-cycle findings already ingested", despite the resume spec explicitly requiring reviewer idempotency. This can duplicate semantic findings.

**Suggested fix**: Before invoking the reviewer on a resumed `REVIEWING` phase, detect whether the current cycle's review has already been ingested and skip straight to the open-findings decision.

> **Follow-up:** the primary defect is fixed; a residual edge case is tracked in \[[FAGAN-0049]\].
