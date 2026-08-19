---
id: SPEC-010
source: spec-review
severity: major
category: defect
artifact: docs/proposals/mechanize-dispatch-orchestration.md#dispatch-merge-story-story-id
status: resolved
traces: []
---

# merge-story's post-merge test step is already decided by a MUST and is underspecified for implementation

**What is wrong:** Two defects in one. (a) Open Question 1 — "should `dispatch merge-story` run the full test suite after merge, or should that be a separate `dispatch test` subcommand?" — is not genuinely open: [rules.md § Branching](../../factory/rulebooks/rules.md#branching) states "**MUST** run the full test suite after every merge, before the next", and the current workflow already does a full test run after each merge. A separate, independently callable test subcommand would violate that MUST unless it were mandatory and sequenced, at which point it is inline testing with extra steps. The question is already answered by the contract the proposal's impact section claims to update. (b) Even with the inline answer, "the test suite" is nowhere defined: the proposal requires a stdlib-only Python script to "exit non-zero if the test suite fails", but specifies no test command, no discovery mechanism, and no config source — the completion criterion "`dispatch merge-story` ... test suite fails after merge" is not verifiable as written. The framing "running tests inline makes the merge atomic" is also misleading: the merge commit already exists before tests run, so a red suite leaves a merged, broken invocation branch with no specified recovery.

**Fix:** Close Open Question 1 in favor of inline post-merge tests, citing the existing MUST. Specify how the script discovers the test command (e.g. a key in `config/model.conf`-adjacent config or the charter's development section) and what happens on a red suite after the merge commit exists (block the wave, record the story non-terminal, leave repair to the dispatcher).

**Resolution (2026-08-18, repeat pass):** Fixed in commit c1507a1. Open Question 1 is closed — the Open Questions section now carries only the genuinely open `--dry-run` question. `merge-story` step 4 runs the full test suite inline, citing the rules.md Branching MUST; discovers the command from a `test_command` key in `config/project.json`; and exits non-zero with a diagnostic rather than guessing when no command is declared. Red-suite recovery is specified: the story is recorded `blocked` with reason `post-merge test failure` and merge SHA noted, the ledger is committed, the subcommand exits non-zero, and repair (fix-forward or revert) is the dispatcher's call. Verified against the current proposal text. One residual wrinkle — the story file already reads `done` from the merge commit while the ledger says `blocked` — is filed as a Minor finding in the repeat-pass report, not a re-open of this finding.
