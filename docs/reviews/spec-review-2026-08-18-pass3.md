# Spec Review — 2026-08-18 (pass 3) — Proposal: Mechanize Dispatch Orchestration

**Artifact under review:** [docs/proposals/mechanize-dispatch-orchestration.md](../proposals/mechanize-dispatch-orchestration.md) (status: open, schema_version 2), as of commit c49f5890ef9f2270869a9067dca63b9745179f17 on branch `dev`.
**Review type:** repeat pass per [review-loop-discipline.md](../../factory/rulebooks/conventions/review-loop-discipline.md) — prior findings verified individually, full semantic inspection re-run fresh. `spec-lint` not applicable (proposal, not spec chain).
**Prior passes:** [spec-review-2026-08-18.md](spec-review-2026-08-18.md) — fail, 4 Major + 6 Minor; [spec-review-2026-08-18-pass2.md](spec-review-2026-08-18-pass2.md) — fail, 1 new Major ([SPEC-011](../findings/SPEC-011.md)) + 3 report-only Minors.
**References:** [dispatch-contract.md](../../factory/rulebooks/conventions/dispatch-contract.md), [branching-policy.md](../../factory/rulebooks/conventions/branching-policy.md), [commit-conventions.md](../../factory/rulebooks/conventions/commit-conventions.md), [implementation-agent.md](../../factory/agents/implementation-agent.md), [premerge-check](../../factory/scripts/premerge-check), [verify-base](../../factory/scripts/verify-base), [block-dangerous-git.sh](../../factory/config/hooks/block-dangerous-git.sh), [config/project.json](../../config/project.json)

## Verdict

**Pass.** [SPEC-011](../findings/SPEC-011.md) is fixed exactly along the finding's option (a): `prepare-wave` now prepares only base-available stories (parallel-safe stories and serial-chain heads), and a new `dispatch prepare-story` subcommand prepares each chain link lazily from its predecessor's merge commit, with mandatory `verify-base --expect-base` against that SHA. All three pass-2 report-only Minors are also fixed — red-suite record semantics, `test_command` preflight plus the `config/project.json` boundary, and script-generated commit formats. The fresh full inspection found no new Major or Critical defect and no regression in the rewritten sections; three low-impact Minors remain, report-only, none blocking. The proposal is ready for stakeholder approval.

## Prior findings — individual verification

### [SPEC-011](../findings/SPEC-011.md) (Major) — resolved

The finding asked for lazy chain-link preparation via either of two options, plus matching workflow-sketch and completion-criteria updates, with `--expect-base` pointed at the freshly recorded merge-commit SHA. The fix implements option (a) in full:

- `prepare-wave` now prepares "only the stories in wave N whose declared base exists at prepare time: **parallel-safe stories and serial-chain heads**, both cut from the invocation branch tip"; step 1 no longer pretends to cut a chain link from a not-yet-existing merge commit. Chain links stay `pending`, and the output now lists them with their predecessors.
- New `dispatch prepare-story <story-id>` validates wave membership, `pending` status, and predecessor `done`; cuts the branch from the predecessor's merge commit; runs `verify-base <invocation-branch> --expect-base <predecessor's merge SHA>` (mandatory, as the finding required); records `prepared` with `declared_base` and the `verify_base` result. It explicitly cites the current serial-chain rule it mirrors ([implementation-agent.md § Workflow, Step 3](../../factory/agents/implementation-agent.md#workflow)).
- The workflow sketch gained step f (prepare-story → spawn → mark-dispatched → verify-story → merge-story, one link at a time), and the dispatch-contract-updates list now covers implementation-agent.md Step 3.
- Completion criteria added for both halves: `prepare-wave` prepares only base-available stories (chain links stay `pending`); `prepare-story` exits non-zero unless the predecessor is `done` and passes `--expect-base` against the merge SHA.
- The ledger-lifecycle section explains what a `pending` link in an active wave means ("waiting for its predecessor to merge", not "forgotten"), so the wave gate cannot misread it.

Verified against [verify-base](../../factory/scripts/verify-base): a branch cut from the predecessor's merge commit passes both checks at creation time (the invocation tip is the merge commit, so not-behind-target holds; the declared-base half is the load-bearing one, as pass 1 already established). Serial chains — the core overlap-aware feature the pass-2 rewrite broke — are executable again. Finding file set to `resolved`.

### Pass-2 report-only Minors (all resolved)

1. **Red-suite record semantics — resolved.** `merge-story` step 4 now states the semantics explicitly: the merge commit already set the story file to `done`, so on a red suite the script makes a dedicated status-correction commit setting the story file back to `blocked`, records `blocked` in the ledger with reason `post-merge test failure` (merge SHA noted), and commits ledger and story file together. The dedicated commit is permitted by [dispatch-contract.md § Story Status Commit Rule](../../factory/rulebooks/conventions/dispatch-contract.md#story-status-commit-rule), which the text cites. The revert path is stated: manual, user-approved, exceptional, outside the dispatch lifecycle, not automated in the first release; the story is re-dispatchable only once the invocation branch is green again. Story file and ledger can no longer contradict each other after a red suite.
2. **Test-command preflight + `config/project.json` boundary — resolved.** `init` preflights the `test_command` key (present and non-empty) at dispatch start, with the fail-fast rationale stated. `merge-story` step 1 re-checks the key **before** merging, guarding against mid-dispatch config edits. `config/project.json` is now in `impact.boundaries` and in Scope ("add the `test_command` key (absent today)"). Confirmed against [config/project.json](../../config/project.json): it carries only `project_id` and `project_name` — no `test_command` key today, so the Scope entry's "absent today" claim is accurate. Completion criterion added.
3. **Script-generated commit formats — resolved.** The new "Script-generated commits" section states the format per subcommand — merge commit, ledger commit, status-update/status-correction commit, baseline commit — each following `<type>: <description> (<ID>)` per [commit-conventions.md](../../factory/rulebooks/conventions/commit-conventions.md). The `merge:` type matches this repository's established merge-commit practice (e.g. `merge: story/ST-0084 — …` in history), now tightened with the story-ID suffix the conventions require.

## Regression check on the pass-3 changes

Checked the new `prepare-story` subcommand, the wave gates, the workflow sketch, the red-suite status-correction commit, the `test_command` preflight, and the Script-generated commits section against the contracts they touch:

- **Ledger lifecycle:** `pending → prepared → dispatched → done | blocked | failed` still closes. A chain link parked at `pending` is reachable via `prepare-story` once its predecessor is `done`, and via `mark-blocked`/`mark-failed` if the predecessor never reaches `done` — `close-wave` and the `prepare-wave N+1` gate see only terminal states, so no wave can close or advance on a forgotten link. Clean.
- **Wave gates:** `prepare-wave N` gates on waves < N only, so `pending` chain links inside wave N do not false-trip the gate; `close-wave N` gates on wave N itself. Consistent.
- **verify-base marker:** `prepare-story` runs `verify-base` in the new story worktree before spawn, writing `verify-base-ok` at that worktree's toplevel; the hook's commit gate (marker head ancestor of HEAD) then holds for the subagent's commits exactly as in `prepare-wave`. Clean.
- **premerge-check marker pairing:** unchanged by this pass — check and merge still paired inside `merge-story`. The red-suite path exits after the merge commit, so no marker/merge pairing issue arises. Clean.
- **Red-suite status-correction commit:** lands on the invocation branch in the invocation-branch worktree, consistent with the "all git-mutating subcommands execute in the invocation-branch worktree" rule. Clean.
- **`init --baseline-commit`:** still creates the baseline commit on the base branch before the invocation branch exists; the new preflight adds no interaction with it. Clean.
- **One latent enforcement note (not a finding):** [block-dangerous-git.sh](../../factory/config/hooks/block-dangerous-git.sh) is a PreToolUse hook — it inspects agent-typed commands, not git invocations made by the script's own subprocesses. The proposal's marker-pairing rationale therefore matters as defense-in-depth (it keeps markers correct for any direct agent git), not as the script's primary correctness mechanism. The design's stated rationale slightly overstates the hook's reach but under-specifies nothing.

## Findings (this pass)

All Minor, report-only per [finding-format.md § When to file](../../factory/rulebooks/conventions/finding-format.md#when-to-file) (blocking severity for this review is Major); none blocks approval.

| Finding                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | Artifact                                           | Category   | Severity |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------- | ---------- | -------- |
| `prepare-story`'s implicit ordering constraint: because `verify-base <invocation-branch>` requires the invocation tip to be an ancestor of the new link's HEAD, `prepare-story` must run after its predecessor's `merge-story` and **before any other** `merge-story` — an interleaved merge makes it fail BASE_STALE. The failure is safe (mechanical halt, no corruption) and the workflow sketch implies the order ("one link at a time"), but the constraint is never stated — state it | docs/proposals/mechanize-dispatch-orchestration.md | Defect     | Minor    |
| Wave-level ledger commit label unspecified: the Script-generated commits section says wave-level records "use the wave label", but no label format is given and [commit-conventions.md](../../factory/rulebooks/conventions/commit-conventions.md) defines no wave-ID format — give an example (e.g. `chore: dispatch ledger — wave 2 closeout (ST-0074,...)`) or point at the wave's story IDs                                                                                             | docs/proposals/mechanize-dispatch-orchestration.md | Suggestion | Minor    |
| Red-suite path leaves the merged story's worktree and branch in place: `merge-story` exits at step 4 on a red suite, so step 5's cleanup never runs for a merged-but-blocked story. Harmless (idempotent re-run or the repair story can collect it), but one sentence would close it                                                                                                                                                                                                        | docs/proposals/mechanize-dispatch-orchestration.md | Suggestion | Minor    |

## Open Questions assessment

- **`--dry-run` on destructive subcommands:** unchanged, still genuinely unresolved, still reasonable to carry into planning.

## Characteristic-by-characteristic summary

- **Consistent:** Yes — the upfront-preparation contradiction ([SPEC-011](../findings/SPEC-011.md)) is gone; `prepare-wave`, `prepare-story`, the lifecycle section, the workflow sketch, the contract-updates list, and the completion criteria all tell the same story.
- **Unambiguous:** Good — red-suite record semantics and the revert path are now explicit. Residual ambiguity limited to the three Minors above.
- **Verifiable:** Good — the new completion criteria (base-available-only preparation, `prepare-story` predecessor gate, `test_command` preflight at `init` and `merge-story`) are each mechanically checkable against the future script.
- **Complete:** Good — serial chains are executable end to end; all four terminal states reachable; the lifecycle closes for chain links on both the success and the predecessor-failure paths.
- **Feasible:** Good — `prepare-story` reuses the `prepare-wave` step sequence verbatim; no new machinery beyond one validated entry point.
- **Necessary (YAGNI):** Good — `prepare-story` is the minimal addition the defect required; the revert path is deliberately *not* automated; the deferred list is untouched.
- **Terminology:** Good — chain head, chain link, `pending`/`prepared`, declared base used consistently with [dispatch-contract.md](../../factory/rulebooks/conventions/dispatch-contract.md) and [branching-policy.md](../../factory/rulebooks/conventions/branching-policy.md).

## Template conformance

Frontmatter complete per schema_version 2; `impact.boundaries` now includes `config/project.json`, closing the pass-2 omission. All required body sections present; the new Script-generated commits section sits correctly in the design-details position.
