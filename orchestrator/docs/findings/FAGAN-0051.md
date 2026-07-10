---
id: FAGAN-0051
status: open
severity: minor
category: robustness
artifact: orchestrator/src/orchestrator/adapters/gate_runner.py
pass: 3-review
---

# Gate commit subject lacks iteration/run-id, weakening resume checkpoint detection

Follow-up to \[[FAGAN-0042]\] (resolved). The idempotent-resume checkpoint (`head_is_gate_commit`) identifies "the artifact commit already exists" by matching HEAD's commit subject `orchestrator: {phase} iteration` together with a clean declared-artifact tree. The subject carries no iteration number and no run-id, so it cannot distinguish the current iteration's commit from a prior iteration's — or a previous run's — same-subject commit on a reused branch.

This is exploitable only when the tree is clean, the author produced zero net change, and a stale same-subject commit sits at HEAD. That combination overlaps the empty-commit "no progress" condition, so the practical damage is bounded; the gap is latent rather than a live defect.

**Suggested fix**: stamp the gate commit subject (or a commit trailer) with the iteration number and run-id, and match on those in `head_is_gate_commit`. This ripples the iteration and run-id into the `PreCommitGateRunner.run` / `gate_head` / `head_is_gate_commit` signatures and their `phase_runner` call sites — a small but cross-file change, deferred deliberately so the review-remediation batch could stay parallel-safe.
