---
id: FAGAN-0050
status: open
severity: minor
category: contract
artifact: orchestrator/src/orchestrator/adapters/gate_runner.py
pass: 3-review
---

# Auto-fix hook that edits a non-declared file leaves untracked worktree dirt

Follow-up to \[[FAGAN-0046]\] (resolved). The one-shot auto-fix re-stage pass diffs and stages only files in the declared artifact set. If an auto-fixing pre-commit hook rewrites a file outside that set, the change is neither staged nor reverted; it lingers in the worktree. The current gate returns normally, but the next gate's `_reject_outside_dirt` (from \[[FAGAN-0044]\]) sees the stray file and errors `dirty-worktree` — a failure the operator cannot attribute to its cause.

Two narrower siblings: a hook that stages its own fix (`git add`) defeats the modified-file detector and leaves a dirty index; and a non-idempotent auto-fixer that rewrites on every run and still exits non-zero is misclassified as an infrastructure error rather than a findings result.

**Suggested fix**: after the auto-fix rerun, detect and either revert or explicitly surface hook edits outside the declared set; and classify a second-run modification distinctly from a crash.

Severity is minor: these are edge conditions around non-declared hook edits. The 0046 amend and one-shot-retry path itself was reviewed correct.
