---
id: FAGAN-0035
source: fagan-review
severity: major
category: defect
artifact: src/orchestrator/cli.py#_handle_light_command
status: resolved
traces: [UC-04, UC-03, BR-007]
---

# Explicit approve does not continue the chain

**What is wrong:** `orchestrate approve` marks the current phase complete and advances `current_phase`, but it does not actually continue the chain. The run is persisted as `mode=running` while no phase is executing. UC-04 requires "the orchestrator shall record the approval and continue the chain". The `--yes` auto-approve path correctly continues via `_auto_approve_chain`, but explicit approval does not.

**Fix:** After a successful explicit approval, invoke the chain runner (or resume path) automatically, or at minimum persist `mode=paused` so that `resume` can correctly pick up the next phase. Currently the orphaned `mode=running` state confuses the single-run invariant.
