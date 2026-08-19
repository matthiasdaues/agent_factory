# Spec Review — 2026-08-18 (repeat pass) — Proposal: Mechanize Dispatch Orchestration

**Artifact under review:** [docs/proposals/mechanize-dispatch-orchestration.md](../proposals/mechanize-dispatch-orchestration.md) (status: open, schema_version 2), as of commit c1507a17d7d898d7680ff84a3d1f7f98620fa4a8 on branch `dev`.
**Review type:** repeat pass per [review-loop-discipline.md](../../factory/rulebooks/conventions/review-loop-discipline.md) — prior findings verified individually, full semantic inspection re-run fresh. `spec-lint` not applicable (proposal, not spec chain).
**Prior pass:** [spec-review-2026-08-18.md](spec-review-2026-08-18.md) — fail, 4 Major + 6 Minor.
**References:** [dispatch-contract.md](../../factory/rulebooks/conventions/dispatch-contract.md), [branching-policy.md](../../factory/rulebooks/conventions/branching-policy.md), [implementation-agent.md](../../factory/agents/implementation-agent.md), [premerge-check](../../factory/scripts/premerge-check), [verify-base](../../factory/scripts/verify-base), [block-dangerous-git.sh](../../factory/config/hooks/block-dangerous-git.sh), [config/project.json](../../config/project.json)

## Verdict

**Fail.** All four Major findings and all six Minor findings from the first pass are fixed, and the fixes are of high quality — the marker-pairing rationale, the pre-spawn `--expect-base` justification, and the red-suite recovery semantics are stated more precisely than the findings asked for. However, the fresh full inspection found one new Major defect introduced by the rewrite: `prepare-wave` prepares all of a wave's stories upfront, but a serial-chain story's declared base is its predecessor's merge commit, which cannot exist at prepare time. As specified, the mechanized workflow cannot execute serial chains — a core feature of the overlap-aware dispatch design it replaces. One Major must be fixed before this proposal can proceed to stakeholder approval.

## Prior findings — individual verification

### Major findings (all resolved)

- **[SPEC-007](../findings/SPEC-007.md) — resolved.** `verify-story` now keeps only the SHA checks, with an explicit note explaining why `premerge-check` is excluded (one-slot marker keyed to branch head; check must immediately precede its own merge). `merge-story` runs `premerge-check` immediately before its own `git merge` in the same invocation. The Design section states that all git-mutating subcommands execute in the invocation-branch worktree, citing the marker mechanics of [block-dangerous-git.sh](../../factory/config/hooks/block-dangerous-git.sh). Fix verified against proposal text and the hook.
- **[SPEC-008](../findings/SPEC-008.md) — resolved.** `dispatch mark-blocked` / `dispatch mark-failed` added: ledger update, story-file status in a dedicated status-update commit per [dispatch-contract.md § Story Status Commit Rule](../../factory/rulebooks/conventions/dispatch-contract.md#story-status-commit-rule), both committed. The deadlock rationale is stated; both subcommands are in Scope and Completion Criteria.
- **[SPEC-009](../findings/SPEC-009.md) — resolved.** `merge-story` step 1 reads the story file's `outputs:` globs and passes repeated `--scope`; the proposal states that omitting `--scope` would silently skip the out-of-scope check and commits to never calling `premerge-check` without scopes. Completion criterion added. Consistent with [premerge-check](../../factory/scripts/premerge-check)'s `--scope` semantics.
- **[SPEC-010](../findings/SPEC-010.md) — resolved.** Open Question 1 closed (only `--dry-run` remains, correctly assessed as genuinely open). Tests run inline citing the rules.md Branching MUST; command discovery via a `test_command` key in `config/project.json`; non-zero exit with a diagnostic when undeclared; red-suite recovery specified (ledger `blocked`, merge SHA noted, wave blocks, dispatcher repairs). Note: `docs/charter/` does not exist in this project — re-pointing discovery at `config/project.json` is correct.

### Minor findings from pass 1 (all resolved)

1. **`--expect-base` mandatory:** `prepare-wave` step 3 passes `--expect-base <declared-base>` explicitly and explains why the declared-base half is the load-bearing check at creation time. Verified against [verify-base](../../factory/scripts/verify-base)'s two checks. Resolved.
2. **Per-story worktree mapping verification:** `prepare-wave` step 2 runs `git worktree list --porcelain` per story, matching path and branch against what was requested, and cites the rules.md MUST it absorbs. Resolved.
3. **Baseline-commit ownership:** `init` fails its precondition on untracked target directories; re-running with `--baseline-commit` makes the script itself create the baseline commit on the base branch, before the invocation branch exists. Ownership is unambiguous. Resolved.
4. **Surviving non-mechanized clauses:** explicitly listed — sub-agent addressing, the wave cap (default six) with pre-flight cost estimation, and the envelope-error-is-not-failure check — each with an anchored link. Resolved.
5. **Idempotency / failure behavior:** new "Failure behavior and idempotency" section states per-subcommand idempotency semantics and the general failure rule (ledger unchanged, non-zero exit, stderr diagnosis); `merge-story` runs `git merge --abort` on conflict so no MERGING state survives. Completion criterion added. Resolved.
6. **`dispatch status` YAGNI:** kept deliberately with a stated reason (read-only pre-flight checkpoint, zero write paths, cheap). The first pass asked for a deliberate keep/drop decision; the author made one. Resolved.

## Findings (this pass)

| Finding                                                                                                                                                                                                                                                                                                                                                                    | Artifact                                           | Category | Severity |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------- | -------- | -------- |
| `prepare-wave` prepares every wave-N story upfront, but a serial-chain story's declared base is its predecessor's merge commit, which does not exist at prepare time — serial chains are unexecutable as specified; make chain-link preparation lazy ([SPEC-011](../findings/SPEC-011.md))                                                                                 | docs/proposals/mechanize-dispatch-orchestration.md | Defect   | Major    |
| Post-merge red suite leaves contradictory records: the merge commit already set the story file's `status: done` (step 3 precedes step 4), yet the ledger records the story `blocked`; no path re-opens the story if the dispatcher chooses revert — state the record semantics explicitly and specify the revert path                                                      | docs/proposals/mechanize-dispatch-orchestration.md | Defect   | Minor    |
| Test-command preflight timing and scope: `merge-story` should check the `test_command` key's presence **before** merging (fail fast), not after the merge commit exists; `config/project.json` exists but has no `test_command` key today, and `impact.boundaries` omits `config/project.json` — add the key to Scope/boundaries and preflight it                          | docs/proposals/mechanize-dispatch-orchestration.md | Defect   | Minor    |
| Script-generated commit message formats unspecified: the script produces merge commits carrying story implementations, ledger commits, status-update commits, and baseline commits — [commit-conventions.md](../../factory/rulebooks/conventions/commit-conventions.md) requires `<type>: <description> (<ID>)` on implementation commits; state the format per subcommand | docs/proposals/mechanize-dispatch-orchestration.md | Question | Minor    |

## Regression check on the rewritten sections

The pass-2 rewrite added: `mark-blocked`/`mark-failed`, `premerge-check` inside `merge-story`, `--scope` derivation from `outputs:`, `test_command` discovery, the idempotency/failure-behavior section, and the surviving-clauses list. Checked each against the contracts it touches:

- **Marker pairing:** the new `merge-story` ordering (check → merge in one invocation) satisfies [branching-policy.md § Pre-Merge Diff Check](../../factory/rulebooks/conventions/branching-policy.md#pre-merge-diff-check) and the hook's marker match. The workflow sketch's verify-all-then-merge-all sequence is now safe because `verify-story` no longer touches the marker. Clean.
- **verify-base marker:** `prepare-wave` runs `verify-base` in the story worktree before spawn; the hook's commit gate (marker head must be an ancestor of HEAD) still holds once the subagent commits on top. Clean.
- **Ledger lifecycle:** `pending → prepared → dispatched → done | blocked | failed` closes; `prepare-wave` and `close-wave` gates now reachable from every path. Clean.
- **Serial chains:** broken — see SPEC-011. This is the one regression the rewrite introduced: the first pass's `verify-story`-centric sketch merged serial chains one at a time in Step 2 order, and nothing in the old text pretended to prepare all branches upfront; the new `prepare-wave` design does, and that is precisely where serial chains break.

## Open Questions assessment

- **`--dry-run` on destructive subcommands:** still genuinely unresolved, still reasonable to carry into planning. Not contract-foreclosed.

## Characteristic-by-characteristic summary

- **Consistent:** Almost — one internal contradiction remains: `prepare-wave`'s upfront base selection vs. the non-existence of serial-chain merge commits at prepare time (SPEC-011).
- **Unambiguous:** Good — execution checkout, baseline-commit ownership, and marker rationale are now explicit. Residual ambiguity: story-file vs. ledger status after a red suite, and script commit-message formats (Minors).
- **Verifiable:** Good — completion criteria are concrete and each maps to a script behavior; the criteria now cover `--scope` derivation, `--expect-base`, idempotency, and red-suite recovery.
- **Complete:** Good — lifecycle closes for all four terminal states; the surviving-clauses list prevents silent contract regressions. Gap: serial-chain preparation (SPEC-011).
- **Feasible:** Good — stdlib-only Python matches existing lint scripts; idempotency semantics are stated at the right level of abstraction for a proposal.
- **Necessary (YAGNI):** Good — deferred list remains disciplined; every retained subcommand, including `status`, carries a justification.
- **Terminology:** Good — ledger, wave, invocation branch, declared base, terminal, prepared used consistently with [dispatch-contract.md](../../factory/rulebooks/conventions/dispatch-contract.md).

## Template conformance

Frontmatter complete per schema_version 2. All required body sections present; the formerly absent design-details content (failure behavior, idempotency) now exists and is where the first pass said it belonged. One omission: `impact.boundaries` should include `config/project.json` once the `test_command` key is part of the design (Minor, folded into the findings table above).
