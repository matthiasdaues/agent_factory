---
id: FAGAN-0048
status: resolved
severity: minor
category: consistency
artifact: orchestrator/src/orchestrator/cli.py
pass: 3
---

# resume --yes can keep persisted mode as paused while running

In `resume --yes`, after auto-approval reloads the run from disk, the code calls `chain_runner.run_all()` on a run that may still have `mode=paused`. Subsequent saves can persist `paused` while execution is active, making `status` misleading.

**Suggested fix**: Set `run.mode = RunMode.RUNNING` after reloading and before calling `chain_runner.run_all(run)`.
