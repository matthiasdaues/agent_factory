---
id: FAGAN-0041
status: resolved
severity: minor
category: consistency
artifact: orchestrator/src/orchestrator/approval_service.py
pass: 3
---

# Advancing current_phase does not sync run.iteration

After approval advances `current_phase`, `run.iteration` stays on the previous phase's value until a later `run_all` mutates it. That leaves `run.json` with a mismatched checkpoint.

**Suggested fix**: When advancing `current_phase`, also load the next `PhaseRecord` and set `run.iteration = next_phase.iteration` before saving.
