# Spec Review — 2026-08-18 — Proposal: Mechanize Dispatch Orchestration

**Artifact under review:** [docs/proposals/mechanize-dispatch-orchestration.md](../proposals/mechanize-dispatch-orchestration.md) (status: draft, schema_version 2)
**Review type:** semantic-only pass of the inspect-spec workflow, adapted to a design-origin proposal. `spec-lint` not applicable (proposal, not spec chain).
**References:** [dispatch-contract.md](../../factory/rulebooks/conventions/dispatch-contract.md), [branching-policy.md](../../factory/rulebooks/conventions/branching-policy.md), [implementation-agent.md](../../factory/agents/implementation-agent.md), [proposal template](../../factory/rulebooks/templates/proposal.md), [premerge-check](../../factory/scripts/premerge-check), [verify-base](../../factory/scripts/verify-base), [block-dangerous-git.sh](../../factory/config/hooks/block-dangerous-git.sh)

## Verdict

**Fail.** The proposal is well-motivated, template-conformant, terminology-consistent, and scoped with discipline (no significant YAGNI violations). Its core diagnosis — deterministic orchestration assigned to a probabilistic executor — is sound, and the pre-spawn verify-base move genuinely closes the named failure modes. However, the subcommand semantics contradict the mechanical marker rules in branching-policy, the subcommand set cannot close the ledger lifecycle for non-`done` stories, and the post-merge test step is both already decided by an existing MUST and underspecified for a stdlib script. Four Major findings must be fixed before this proposal can move `draft → open`.

## Findings

| Finding                                                                                                                                                                                                                                                                                              | Artifact                                           | Category   | Severity |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------- | ---------- | -------- |
| verify-story/merge-story split breaks the premerge-check marker pairing rule; execution checkout unspecified — move premerge-check into merge-story, state the worktree ([SPEC-007](../findings/SPEC-007.md))                                                                                        | docs/proposals/mechanize-dispatch-orchestration.md | Defect     | Major    |
| No subcommand records blocked/failed stories; the ledger lifecycle cannot close under the proposal's own "script-only ledger writes" criterion — add mark-blocked/mark-failed ([SPEC-008](../findings/SPEC-008.md))                                                                                  | docs/proposals/mechanize-dispatch-orchestration.md | Defect     | Major    |
| verify-story omits the mandated `premerge-check --scope <story outputs>`, regressing the out-of-scope check that targets failure mode #1 — derive scopes from the story file's `outputs:` ([SPEC-009](../findings/SPEC-009.md))                                                                      | docs/proposals/mechanize-dispatch-orchestration.md | Defect     | Major    |
| merge-story test step: Open Question 1 is already answered by rules.md's "MUST run the full test suite after every merge", and "the test suite" is undefined for the script — close the question inline, specify test-command discovery and red-suite recovery ([SPEC-010](../findings/SPEC-010.md)) | docs/proposals/mechanize-dispatch-orchestration.md | Defect     | Major    |
| `prepare-wave` runs verify-base without specifying `--expect-base <declared-base>`; at creation time the not-behind-target check passes trivially, so the declared-base half is the one that matters — pass it explicitly                                                                            | docs/proposals/mechanize-dispatch-orchestration.md | Defect     | Minor    |
| `prepare-wave` omits the per-story `git worktree list --porcelain` verification that rules.md and implementation-agent Step 3 require before a subagent is considered dispatched — absorb this MUST into the subcommand                                                                              | docs/proposals/mechanize-dispatch-orchestration.md | Defect     | Minor    |
| `init` "reports" untracked target directories, but Core Principles forbid the LLM from running git — who makes the baseline commit is ambiguous; clarify ownership                                                                                                                                   | docs/proposals/mechanize-dispatch-orchestration.md | Question   | Minor    |
| The rewritten workflow sketch does not state that non-mechanized dispatch-contract clauses survive: sub-agent addressing (instance IDs), the wave cap (default six), and the envelope-error-is-not-failure check — say so explicitly                                                                 | docs/proposals/mechanize-dispatch-orchestration.md | Defect     | Minor    |
| "Each subcommand is atomic" is claimed, but idempotency and mid-merge failure recovery (conflict leaves MERGING state) are unspecified — a prerequisite for the deferred retry model; state per-subcommand idempotency                                                                               | docs/proposals/mechanize-dispatch-orchestration.md | Defect     | Minor    |
| `dispatch status` is borderline YAGNI — the ledger is readable YAML and the LLM can read it directly; cheap and read-only, so keep or drop deliberately                                                                                                                                              | docs/proposals/mechanize-dispatch-orchestration.md | Suggestion | Minor    |

## Contradictions with existing MUST rules (explicit flags)

1. **branching-policy.md § Pre-Merge Diff Check** ("each `premerge-check` call must be immediately followed by that branch's own `git merge`") and **rules.md § Git workflow** (merge blocked without the marker): the proposed verify-all-then-merge-all sequence is mechanically denied by `block-dangerous-git.sh`. → SPEC-007.
2. **rules.md § Branching** ("MUST run the full test suite after every merge, before the next"): Open Question 1 entertains a separate `dispatch test` subcommand, which this MUST forecloses. → SPEC-010.
3. **rules.md § Branching** ("MUST verify every new branch-to-worktree mapping with `git worktree list --porcelain` before doing work"): `prepare-wave` as specified does not absorb this per-story check. → Minor finding.
4. **dispatch-contract.md § Hard Checkpoint Per Story / § Dispatch Ledger** (terminal states include blocked/failed with reasons): the subcommand set cannot produce two of the four terminal states. → SPEC-008.

## Open Questions assessment

- **Q1 (inline tests vs `dispatch test` subcommand):** *Already answered.* The existing Branching MUST requires the full suite after every merge, before the next. The "atomicity" framing is also misleading — the merge commit exists before tests run. Close the question; the genuine gap is test-command discovery (SPEC-010).
- **Q2 (`--dry-run` on destructive subcommands):** *Genuinely unresolved.* Reasonable to carry into planning; not contract-foreclosed.

## Characteristic-by-characteristic summary

- **Consistent:** No — see MUST contradictions above (SPEC-007, SPEC-008, SPEC-010).
- **Unambiguous:** Mostly; baseline-commit ownership and execution checkout are ambiguous.
- **Verifiable:** Completion criteria are concrete, but the test-suite criterion and the missing `--scope`/`--expect-base` specifications block verification (SPEC-009, SPEC-010).
- **Complete:** No — the lifecycle lacks blocked/failed transitions; minor coverage gaps against the implementation-agent workflow it rewrites.
- **Feasible:** Stdlib-only Python is credible (matches existing lint scripts); the atomicity claim is overstated without idempotency and failure-recovery semantics.
- **Necessary (YAGNI):** Good — deferred list is disciplined; only `dispatch status` is borderline.
- **Terminology:** Good — ledger, wave, invocation branch, declared base used correctly; the notable absence is any mention of the `premerge-check-ok` marker, which is precisely where the design breaks (SPEC-007).

## Template conformance

Frontmatter complete per schema_version 2 (`supersedes:` empty rather than `null` — trivial). All required body sections present. The optional "Design Details" section (failure behavior, idempotency) is absent — and is exactly where several findings land; adding it is the natural vehicle for the fixes.
