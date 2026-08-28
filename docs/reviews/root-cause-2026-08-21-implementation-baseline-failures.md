# Root Cause Analysis: Implementation Baseline Failures

Date: 2026-08-21

Baseline: `c3ff02d402a34d6b4a9f59f6e1ac2a16641b1e11`

## Summary

The implementation run stopped after ST-0086 because the full-suite gate found
ten failures that predate and do not exercise the ST-0086 output. The ten test
failures reduce to six root causes:

1. four failures from an unguarded optional abort signal;
2. two failures from stale orientation text expectations;
3. one failure from changed Codex installation semantics;
4. one failure from artifact validation that stages untracked files;
5. one failure from a stale worktree-path test case; and
6. one failure from a cancellation-test race.

The baseline is therefore unsuitable as a clean merge gate until these causes
are repaired or the affected expectations are deliberately updated.

## Impact

- ST-0087 and ST-0088 cannot proceed through the required full-suite gate.
- ST-0086 is not implicated by these failures.
- Four dispatch tests fail before exercising their intended behavior, reducing
  confidence in aggregate result and cleanup contracts.
- Orientation and initialization tests no longer state one coherent contract.

## Root Causes

### RC-1: `dispatch-wave` assumes an abort signal is always present

Affected tests:

- `test_dispatch_wave_returns_aggregate_envelope_and_item_runtime_metadata`
- `test_UC_10_dispatch_wave_blocks_child_with_canonical_tracked_report`
- `test_dispatch_wave_returns_while_capture_is_stalled`
- `test_nested_dispatch_records_survive_merged_worktree_removal`

The tool execution tests omit the optional abort signal. `dispatch-wave.ts`
passes that value into `spawnPi`, whose early-cancellation branch reads
`signal.aborted` without checking whether `signal` exists. Execution therefore
ends with `TypeError: Cannot read properties of undefined (reading 'aborted')`
before the behavior under test runs.

Root cause: the boundary declares or supplies the signal as optional, while the
callee implements it as mandatory.

Repair: make the contract consistent. Prefer accepting an optional signal and
using `signal?.aborted` plus guarded listener registration, because ordinary
tool execution without cancellation is valid. Add a focused unit test for both
an omitted signal and an already-aborted signal.

### RC-2: Orientation requirements changed without updating all tests and text

Affected tests:

- `test_first_prompt_acknowledges_rulebook_ingestion`
- `test_fresh_install_creates_codex_discovery_layout_and_native_agents`

The canonical orientation requires rulebook ingestion before the first answer,
but it does not contain the exact acknowledgement sentence expected by the
first test. A second test searches for the older phrase `before ANY Skill/Agent call`, which is also absent. These are exact-text assertions against wording
that has evolved.

Root cause: the orientation contract and its phrase-level regression tests were
changed independently. The tests encode prose rather than one stable semantic
marker.

Repair: decide the intended user-visible contract, update the canonical
orientation once, and assert ordering and meaning with stable markers. Avoid
maintaining two different phrases for the same session-start obligation.

### RC-3: Codex initialization behavior conflicts with preservation semantics

Affected test:

- `test_project_owned_codex_content_and_root_orientation_are_preserved`

The test creates a project-owned `AGENTS.md` and requires byte-for-byte
preservation. Current initialization prepends the Factory orientation block.
Both behaviors cannot hold simultaneously.

Root cause: initialization moved from "skip and instruct the user" toward
automatic orientation integration, but the preservation contract and test were
not revised.

Repair: choose and document one ownership rule. The safer default is to preserve
project-owned content and report the integration step, unless the initializer
has an explicit, idempotent managed-block contract. Update implementation and
test together.

### RC-4: Artifact validation changes repository state before checking tracking

Affected test:

- `test_run_agent_rejects_exit_zero_without_canonical_tracked_artifacts`

`validateChildResultArtifacts` runs `git add -- <path>` before `git ls-files --error-unmatch`. An untracked artifact becomes staged and then passes the
tracking check. The validator therefore accepts the exact state it is meant to
reject and also mutates the child's worktree during validation.

Root cause: "stageable" and "already Git-tracked" were treated as equivalent.
They are different repository states.

Repair: perform the non-mutating `git ls-files --error-unmatch -- <path>` check
first and do not stage from a validator. If staged-but-new result artifacts are
valid, state that explicitly in the contract and test index membership with a
separate, non-mutating command.

### RC-5: The guardrail test uses a now-forbidden worktree location

Affected test:

- `test_noncreating_branch_operations_remain_allowed[git worktree add -b feat/x /tmp/feat-x main]`

The command does create a branch and places its worktree under `/tmp`. Current
Factory rules require every worktree under `.current-work/worktrees/`. The
guardrail returns exit 2 correctly under that rule, while the test classifies
the command as a permitted non-creating operation.

Root cause: the test fixture predates the worktree-location policy and is also
misclassified: `git worktree add -b` is branch creation.

Repair: move this case to the blocked-command tests and add an allowed case that
uses `.current-work/worktrees/feat-x`.

### RC-6: Cancellation can occur before the fixture records its descendant

Affected test:

- `test_BUG_0004_UC_10_run_agent_cancellation_terminates_and_cleans`

The fixture records `child-started` before spawning the descendant and writing
`descendant-pid`. The test may abort as soon as the first marker appears. It can
then try to read `descendant-pid` before that file exists, producing
`FileNotFoundError`.

Root cause: the readiness marker represents child startup, not completion of the
process tree that the assertions require.

Repair: write a readiness marker only after both PID files exist, or wait
explicitly for `descendant-pid` before cancelling. Keep a bounded timeout so a
real descendant-spawn failure remains visible.

## Recommended Repair Order

1. Fix RC-1 because one defect accounts for four failures and masks dispatch
   behavior.
2. Fix RC-4 because validation currently mutates state and weakens the durable
   artifact contract.
3. Fix RC-6 to make the cancellation regression deterministic.
4. Resolve the intended orientation and initializer contracts, then fix RC-2
   and RC-3 together.
5. Update the obsolete guardrail case for RC-5.
6. Run each owning test during repair, then run the complete suite before
   resuming ST-0087 and ST-0088.

## Exit Criteria

- All ten named tests pass from the invocation baseline plus the repair commits.
- The complete test suite passes with warnings treated as errors.
- Artifact validation performs no implicit staging.
- Dispatch works with an omitted, active, and already-aborted signal.
- Codex orientation installation has one documented ownership policy reflected
  by both implementation and tests.
