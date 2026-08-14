---
id: RECON-0004
source: reconcile-spec
severity: major
category: defect
artifact: orchestrator/tests/test_backlog_lint.py:20
status: resolved
---

**Resolution (verified 2026-07-21, research + pi.dev reconciliation pass):** Fixed by commit `31c7997` ("fix: repoint orchestrator test fixtures at factory/scripts and factory/agents"); the two files were subsequently removed in the orchestrator restructuring. `uvx pytest --collect-only` inside `orchestrator/` now reports 270 tests collected with 0 collection errors, and no `parents[2] / "scripts"` stale-path pattern remains in `orchestrator/tests/`. The defect no longer manifests.

# Two orchestrator test files fail collection: they still resolve gate scripts at the pre-pivot `scripts/` path

**What is wrong:** `orchestrator/tests/test_backlog_lint.py:20` and `orchestrator/tests/test_matrix_lint.py:17` each load their target script directly off disk via `SourceFileLoader`, computing the path as `Path(__file__).resolve().parents[2] / "scripts" / "<name>"` — repo-root-relative to a bare `scripts/` directory. That directory hasn't existed since `95c36c6` ("the great pivot — move all into the factory folder"), a root-level, whole-repo restructuring decision that relocated every gate script to `factory/scripts/`. Both files error during collection (`FileNotFoundError: .../scripts/backlog-lint`, `.../scripts/matrix-lint`), not just at test-run time — `uv run pytest --collect-only` inside `orchestrator/` reports "Interrupted: 2 errors during collection," meaning neither file's tests execute at all today. This is the same stale-path class already fixed elsewhere this session (`ST-0065`, `ST-0066`, `RECON-0003` orchestrator) but was missed there because those fixes were scoped to specific stories/findings, not a full-repo sweep for the pattern.

**Fix:** Update both `_SCRIPT` computations to point at `factory/scripts/backlog-lint` and `factory/scripts/matrix-lint` respectively (i.e. insert a `"factory"` path segment). Re-run `uv run pytest --collect-only` inside `orchestrator/` afterward to confirm collection succeeds with 0 errors, and grep `orchestrator/tests/*.py` for the same `parents[2] / "scripts"` pattern in case other test files share it silently (not just these two, which were only found because they error loudly at collection — a test that imports the stale path but tolerates a missing file could fail quietly instead).
