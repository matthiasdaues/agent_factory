---
id: FAGAN-0011
source: fagan-review
severity: major
category: defect
artifact: factory/config/extensions/dispatch-wave.ts:442
status: resolved
traces: [ST-0067, UC-10, FR-K4, BR-040]
---

# Blocked waves emit an invalid child-result envelope

**What is wrong:** `aggregateEnvelope` returns an empty `artifact_paths` list
when every wave item fails before producing a valid child envelope. The same
change defines and enforces the canonical envelope contract as requiring a
non-empty artifact list, and its regression test explicitly expects the
invalid empty list. A parent therefore cannot validate or follow the result
contract on the error path, so the bounded envelope is not closed under a
realistic child failure.

**Fix:** Persist a canonical tracked wave report for blocked/error outcomes and
include that report path in the aggregate envelope. Update the negative-path
test to parse and validate the returned aggregate with the same canonical
envelope and artifact checks used for successful child results.

## Analysis

The `dispatch_wave` public tool-result boundary will remain the observation
seam. A Chicago-style regression will drive an invalid child envelope through
the installed extension and require the aggregate to have the exact BR-040
shape plus a non-empty list of canonical, existing, Git-tracked artifacts.

Blocked waves will write their bounded per-item diagnostics to the fixed,
tracked Factory wave-report artifact and append that path to any valid child
artifact paths already aggregated. The implementation and regression modify
`factory/config/extensions/dispatch-wave.ts`,
`factory/reports/dispatch-wave-blocked.md`, and
`orchestrator/tests/test_child_result_envelope.py`. No interface or business
rule changes are expected: this closes the existing error path under BR-040.

## Resolution

Blocked waves now persist their per-item transport diagnostics in
`factory/reports/dispatch-wave-blocked.md`, force-track the report when an
installed Factory directory is ignored, and include its path in the aggregate
envelope. The negative-path tracer validates the aggregate's exact BR-040
shape and proves every listed artifact is canonical, present, and Git-tracked.

## Spec Feedback

Compared the change with UC-10, FR-K4, BR-040, the child-result interface
contract, and the validation rules. The implementation repairs an error path
to meet the existing contract; it changes no business rule, interface shape,
entity, state transition, component boundary, or architecture decision. No
specification or ADR update is needed.

## Verification Evidence

- Focused child-result envelope suite: 7 passed.
- Relevant envelope plus Pi usage-capture suite: 38 passed, with two unrelated
  environment-sensitive failures in cancellation setup and the already-known
  nested-dispatch worktree-removal case; neither reaches or exercises the
  changed blocked-wave aggregation path.
- Ruff check and format, Markdown formatting, and `git diff --check` pass.
  `index-lint --check` could not acquire its managed cache or fetch its missing
  `tiktoken` wheel in the sandbox; the escalated retry was aborted.
