# QA Report: Dispatch Lifecycle Close and Mechanical Enforcement

Branch: `impl/st-0212-st-0213-st-0215` vs `dev`
Date: 2026-09-08
Stories: ST-0212, ST-0213, ST-0214, ST-0215, ST-0216

## Verdict

**QA passed.** One minor Fagan defect found and fixed in this commit. No security findings. No bugs from exploratory hunt. All 20 contract tests pass.

## Test Verification

```
20 passed in 3.31s
```

| Suite                       | Tests | Result   |
| --------------------------- | ----- | -------- |
| test_update_factory.py      | 15    | All pass |
| test_block_dangerous_git.py | 5     | All pass |

Test coverage spans: constant declaration and cross-script consistency, `_should_checksum` exclusion logic, `_compute_checksums` / `compute_factory_checksums` integration, `_detect_modifications` invisibility of hook-regenerated files, `main()` force-gate bypass for INDEX.yaml-only changes, force-gate preservation for genuine user changes, ledger gate deny/allow on story branches, non-story branch passthrough, main-checkout passthrough, and denial message content.

## Fagan Inspection

### Correctness

One defect found and fixed:

| ID           | Severity | File                                                                   | Description                                                                                                                                                                                                                                           | Resolution                                             |
| ------------ | -------- | ---------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------ |
| FAGAN-QA-001 | Minor    | `packages/factory/rulebooks/conventions/dispatch-contract.md` line 236 | Parenthetical says "(the work is on main)" but at dispatch-close time stories are merged to the invocation/feature branch, not main. Line 232 was corrected by reconciliation to say "the target branch" but line 236's summary paragraph was missed. | Fixed: changed to "(the work is on the target branch)" |

### Clean Architecture and Consistency

- dispatch-contract.md Close section uses consistent terminology with the rest of the file (terminal state, ledger, worktree).
- Abandoned Close's `git branch -D` / `git worktree remove --force` is appropriate for abandoned work and does not contradict existing guardrail rules (the guardrail blocks agent-initiated `branch -D`; the close procedure is a human/script action).
- QA-in-Worktree Divergence accurately names the `packages/factory/` vs `factory/` path pair and the correct mitigation.
- branching-policy.md cross-reference to `dispatch-contract.md#close` is correctly anchored.
- commit-conventions.md Batch Fix heading level (H3) matches surrounding sections.
- rules.md dispatch-close MUST is in the correct section, no duplication with existing rules.
- implementation-agent.md MUST clause for `dispatch init` is clear and includes the `--feature-branch` flag documentation.
- HOOK_REGENERATED_PATHS constant is identical between init-factory (line 264) and update-factory (line 91); test `test_constants_match_between_scripts` enforces this.

## Security Review (OWASP)

**No findings.** All inputs to the new hook code are git-internal values (branch name from `git rev-parse --abbrev-ref HEAD`, directory paths from `git rev-parse --git-common-dir` and `pwd`). Variable expansions are properly double-quoted. The glob operates on a script-controlled directory structure under `.current-work/`. The `--no-verify` bypass is already blocked by the existing DANGEROUS_PATTERNS array. No command injection, path traversal, or bypass vectors meet the >=0.8 confidence threshold.

## Exploratory Bug Hunt

Six edge cases investigated, zero bugs:

| #   | Edge Case                                                                                | Result                                                                                                                                                        |
| --- | ---------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | Hook runs outside a git worktree                                                         | Correct: ledger gate is inside the `git-dir != git-common-dir` guard (line 49), so main-checkout commits skip it entirely. Test confirms.                     |
| 2   | `.current-work/` exists but has no subdirectories                                        | Correct: glob fails to match, commit denied. No dispatch is active, so denial is the right behavior.                                                          |
| 3   | COMMON_DIR is empty                                                                      | Not a bug: unreachable because line 49 already confirmed `git-common-dir` succeeded. The `-n` guard is belt-and-suspenders.                                   |
| 4   | MAIN_ROOT resolution via `cd "$COMMON_DIR" && cd .. && pwd`                              | Correct for all supported layouts (standard worktrees under `.current-work/worktrees/`). Exotic `--separate-git-dir` layouts are outside project constraints. |
| 5   | HOOK_REGENERATED_PATHS suffix-match breadth                                              | By design: documented in ST-0215 Analysis section. Future additions should use path-unique filenames.                                                         |
| 6   | Naming differences between scripts (`_compute_checksums` vs `compute_factory_checksums`) | By design: init-factory exposes public API for external callers; update-factory is self-contained.                                                            |

### Pre-existing Observation (Not a Regression)

rules.md line 120 reads `.current-work/dispatch-ledger.yaml` (flat path) but the actual path is `.current-work/<feature-branch>/dispatch-ledger.yaml` (nested). This predates the current PR -- the diff does not touch this line. Noted for a future cleanup.

## Files Reviewed

| File                                                         | Type                   |
| ------------------------------------------------------------ | ---------------------- |
| packages/factory/rulebooks/conventions/dispatch-contract.md  | Convention doc         |
| packages/factory/rulebooks/conventions/branching-policy.md   | Convention doc         |
| packages/factory/rulebooks/conventions/commit-conventions.md | Convention doc         |
| packages/factory/rulebooks/rules.md                          | Rules                  |
| packages/factory/agents/implementation-agent.md              | Agent definition       |
| packages/factory/config/hooks/block-dangerous-git.sh         | Shell hook             |
| packages/factory/scripts/init-factory                        | Python script          |
| packages/factory/scripts/update-factory                      | Python script          |
| tests/factory/test_block_dangerous_git.py                    | Contract tests         |
| tests/factory/test_update_factory.py                         | Contract tests         |
| packages/factory/INDEX.yaml                                  | Hook-regenerated index |
| docs/reviews/reconciliation-dispatch-close-and-batch-fix.md  | Reconciliation report  |

## Fixes Applied in This Commit

1. `packages/factory/rulebooks/conventions/dispatch-contract.md` line 236: Changed "(the work is on main)" to "(the work is on the target branch)" to match the corrected text on line 232.
