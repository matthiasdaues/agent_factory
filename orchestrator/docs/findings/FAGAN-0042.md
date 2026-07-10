---
id: FAGAN-0042
status: resolved
severity: major
category: contract
artifact: orchestrator/src/orchestrator/phase_runner.py
pass: 3
---

# Resume from GATING is not idempotent

The resume path for `GATING` always re-runs `GateRunner.run()`, which stages and commits again. That breaks ATAM-R07 / UC-06 idempotency: if the checkpoint commit already exists, resume degenerates into a spurious `empty-commit` "no progress" path instead of resuming cleanly.

**Suggested fix**: Persist/check a gate-complete checkpoint and skip re-commit when the current iteration's artifact commit already exists; add a `GateRunner` path that gates the existing HEAD without creating a new commit.

> **Follow-up:** implemented; a latent hardening item is tracked in \[[FAGAN-0051]\].
