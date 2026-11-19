# Handoff: run lifecycle implementation, finished

The orchestrated run on `feature/run-lifecycle` is finished. All 24 stories are merged, and all ten waves are closed. The branch waits for the stakeholder's merge into `dev`.

## State

- Ledger: `.current-work/feature/run-lifecycle/dispatch-ledger.yaml`. Feature worktree: `.current-work/feature/run-lifecycle/invocation`, head `1e3822d7`.
- Stories: ST-0408 to ST-0431. ST-0431 came from a smoke run of the new scripts in a scratch repository after wave 9. The installed `dispatch` cannot add a story, so ST-0431 went into the ledger by hand, and `branch_head` moved to the feature tip by hand. The ledger before that edit is backed up in the session scratchpad.
- `dev` is 4 commits ahead. The merge has no conflict, and only `packages/factory/CHANGELOG.md` changed on both sides.
- The installed `premerge-check dev feature/run-lifecycle` refuses the stale base and 225 changed files over the default limit of 20. The installed copy does not know the feature merge yet. The stakeholder merges with an override.

## After the merge

1. Run `update-factory`, so that the installed copy gets the new scripts.
2. Run `dispatch close` for this run, then the one-time `dispatch close --orphans`. Compare its removal list with the proposal first, because the ST-0426 review counted about 13 merged worktrees that no ledger names. The `counter-ids-fitting` nested ledger now keeps its worktree.

## Decisions taken during the run (2026-11-19)

- Decision A on the refused amend: fixed in ST-0410, no critical finding filed.
- SPEC-0110: the dirty-worktree refusal applies only before a new merge, not on the rerun after a refused amend.
- `docs/testing.yaml` row `dispatch.refuse_dirty_feature_worktree: true` confirmed.
- Ignored files go with their worktree at `close` (BR-119): a worktree is throwaway.
- The default tier of a finding is `economy` (BR-117).
- The feature merge check shall not require the four feature reports. It shall run a scripted smoke test instead. How it is designed, and who designs it, is decided after this project.
- The three smoke-run defects and the `--class` gap go into ST-0431, with option (a) for the empty wave.

## Open decisions for the stakeholder

- BUG-0132: OpenCode minimum version. Recommendation: raise it to 2.2.7.
- `premerge-check` reads `docs/testing.yaml` at the story head. Recommendation: read the gate list from the target branch.
- Where BUG-0131 is fixed.
- `crap-score` stays off until crap-gate-setup lands.
- How the test-strategy agent resolves a mutant that no test should kill, and whether a `planning-agent` QA finding may also close through a story that adds the test.

## Follow-up work

- The scripted smoke test for the feature merge (decision above).
- The commit hook runs the full suite of about 4400 tests on every commit. A proposal should cut the hook to the affected tests and keep the full suite in `merge-story`.
- The usage capture copies the full main transcript on every hook and keeps every copy: `.agent-factory/usage/transcripts/` reached 56 GB and filled the disk during the ST-0431 merge. All records of one session carry the same key, so the main session and its subagents cannot be told apart.
- The Bash guard blocks only `uv run pytest`. Developers ran tests through `.venv/bin/python -m pytest` and `uv run python -m pytest`.
- Code follow-ups: IMPL-0058, IMPL-0059, IMPL-0060; untracked files in the by-hand `prepare-story` of a reused branch; four loose ends from the ST-0423 developer. The details are in `session-scratchpad.md`.
- Reconciliation: SPEC-0111, SPEC-0116 to SPEC-0119, SPEC-0121, SPEC-0122, the missing Scenarios for ST-0431, and the "calling checkout" wording in the QA strategy, ST-0414, `backlog/epics-run-lifecycle.md`, `docs/arc42/06_runtime_view.md` and ADR-0040.
- The ledger of `core-artifact-layout` cannot be parsed by PyYAML (line 181). `dispatch` reads it with its own loader.

## Token spend of the run

From 2026-11-18 19:31 (+01:00), main session and 97 subagent transcripts, all `claude-opus-5-5`: input 10,156; cache writes 17,065,906; cache reads 669,498,961; output 3,143,688. Normalized with `cl100k_base`: input 4,284,329; output 1,262,534; total 5,546,863.
