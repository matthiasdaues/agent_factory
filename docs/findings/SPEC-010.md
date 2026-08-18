---
id: SPEC-010
source: spec-review
severity: major
category: defect
artifact: docs/proposals/mechanize-dispatch-orchestration.md#dispatch-merge-story-story-id
status: open
traces: []
---

# merge-story's post-merge test step is already decided by a MUST and is underspecified for implementation

**What is wrong:** Two defects in one. (a) Open Question 1 — "should `dispatch merge-story` run the full test suite after merge, or should that be a separate `dispatch test` subcommand?" — is not genuinely open: [rules.md § Branching](../../factory/rulebooks/rules.md#branching) states "**MUST** run the full test suite after every merge, before the next", and the current workflow already does a full test run after each merge. A separate, independently callable test subcommand would violate that MUST unless it were mandatory and sequenced, at which point it is inline testing with extra steps. The question is already answered by the contract the proposal's impact section claims to update. (b) Even with the inline answer, "the test suite" is nowhere defined: the proposal requires a stdlib-only Python script to "exit non-zero if the test suite fails", but specifies no test command, no discovery mechanism, and no config source — the completion criterion "`dispatch merge-story` ... test suite fails after merge" is not verifiable as written. The framing "running tests inline makes the merge atomic" is also misleading: the merge commit already exists before tests run, so a red suite leaves a merged, broken invocation branch with no specified recovery.

**Fix:** Close Open Question 1 in favor of inline post-merge tests, citing the existing MUST. Specify how the script discovers the test command (e.g. a key in `config/model.conf`-adjacent config or the charter's development section) and what happens on a red suite after the merge commit exists (block the wave, record the story non-terminal, leave repair to the dispatcher).
