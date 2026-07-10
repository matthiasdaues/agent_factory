---
id: FAGAN-0040
status: resolved
severity: major
category: contract
artifact: orchestrator/src/orchestrator/approval_service.py
pass: 3
---

# Approval checks findings on the wrong iteration/cycle

Approval re-checks `open_count(phase.name, phase.iteration)`, but findings are tagged to the latest review cycle as `iteration + 1` per the finding contract. This is an off-by-one check against BR-007 / UC-04's "latest-iteration open-findings count is zero".

**Suggested fix**: Query the latest review cycle explicitly (`phase.iteration + 1`) or persist the last-reviewed cycle in run state and use that for approval/status checks.
