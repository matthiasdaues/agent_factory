---
id: FAGAN-0030
source: fagan-review
severity: major
category: correctness
artifact: tests/test_dispatch_e2e.py
status: resolved
traces:
  - ST-0139
  - Proposal: Agentic Quality Gates — Layer 4 Smoke Tests
---

# Duplicate `test_smoke_failure_escalation_and_redispatch_to_completion` — first copy is dead code

**What is wrong:** `tests/test_dispatch_e2e.py` defined
`test_smoke_failure_escalation_and_redispatch_to_completion` twice (at line
331 and line 552 before the fix). The story commit `e0c800a` (ST-0139,
`feat: add failure escalation smoke test`) shipped the file with both
copies: the worktree that produced the story commit carried an earlier copy
of the test, and the merge combined the two definitions instead of
deduplicating. In Python the second definition shadows the first, so the
first copy (line 331) was never executed by pytest, and `ruff check`
flagged the redefinition (F811), failing the deterministic lint gate on
the branch head. The two copies are semantically identical apart from
formatting, so no asserted behavior was lost — but the file no longer
satisfied its own lint gate, and any future divergence between the two
copies would have silently reduced the acceptance coverage of the Smoke 2
failure/escalation journey.

**Fix:** Removed the dead first copy (lines 331–550) and kept the executed
second copy, which asserts the full journey: dispatch init → plan →
prepare-wave → mark-dispatching → first commit → mark-dispatched →
verify-story → mark-failed with `--class acceptance_unmet` → escalation
grant → tier bump → redispatch → second commit → verify → merge to
completion. Verified with `uvx ruff check` (F811 gone) and a full
`pytest --tb=short -q` run (273 passed).
