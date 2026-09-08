---
schema_version: 2
title: Dispatch Lifecycle Close and Mechanical Enforcement
status: implemented
owner: Matthias Daues
created: 2026-09-08
updated: 2026-09-08
supersedes:

impact:
  scope: cross_project
  architecture_change: false
  external_contract_change: true
  boundaries:
    - factory/rulebooks/conventions/dispatch-contract.md
    - factory/rulebooks/conventions/branching-policy.md
    - factory/rulebooks/conventions/commit-conventions.md
    - factory/rulebooks/rules.md
    - factory/agents/implementation-agent.md
    - factory/config/hooks/block-dangerous-git.sh
    - factory/scripts/verify-base
    - factory/scripts/index-lint
    - factory/scripts/dispatch

governance:
  assurance: routine
  risk_domains:
    - operations

estimate:
  as_of: 2026-09-08
  basis: judgment
  confidence: medium
  human_review_hours:
    min: 1.0
    max: 2.0
  normalized_tokens:
    min: 5000
    max: 12000
  estimated_consumption:
    min: 75000
    max: 180000
    overhead_multiplier: 15
    playbook: feature-addition
---

# Feature Request: Dispatch Lifecycle Close and Mechanical Enforcement

## Summary

Add an explicit close and abandon procedure to the factory's dispatch contract, gate
story-branch commits on dispatch-ledger existence, break the stale-factory chain that
forces `update-factory --force` after hook-modified files, and close the gap where QA
in a worktree diverges from pre-commit validation in the installed copy. Combines
convention amendments with mechanical enforcement — both address real waste observed
across two production dispatches where 28+ worktrees were orphaned, an implementation
agent bypassed `dispatch init`, and 25 tests failed post-merge due to a stale installed
factory copy.

## Motivation

The dispatch contract (dispatch-contract.md) requires maintaining a ledger and verifying
every story reaches a terminal state before the next wave. The branching policy requires
removing clean worktrees after verification. But neither document defines what happens
when a dispatch is **abandoned** — cancelled mid-flight, superseded by a rework, or
simply forgotten. In the observed case, a story-title-update dispatch created 21
per-story worktrees and branches, none of which were merged or cleaned, and no dispatch
ledger was created. The rules were not violated because no dispatch formally started —
but the tooling pattern (worktree-per-story) was used without the ceremony that tracks
it.

Separately, the commit conventions provide no guidance on how to handle multiple failure
modes in the same file. A developer fixing run-dev.sh committed six times, each
addressing one symptom. A single reviewed commit addressing the script as a whole would
have been cheaper to review and bisect.

## Core Principles

- A dispatch has a defined beginning and end. If it begins, it must close — either as
  completed or as abandoned.
- Worktrees created by a dispatch are owned by that dispatch. When the dispatch closes,
  the worktrees close with it.
- When multiple failure modes surface in one file, the fix is one commit that addresses
  the file as a whole.

## Design

### 1. Dispatch close ceremony

Add a "Close" section to dispatch-contract.md with two terminal paths:

**Completed close:**

1. Verify every story in the dispatch has a terminal status in the ledger (merged or
   blocked).
2. Run `git worktree prune` to remove stale worktree references.
3. For each worktree owned by the dispatch: if merged, `git worktree remove` and
   `git branch -d`. If blocked, record the block reason in the ledger and leave the
   branch for manual resolution.
4. Commit the final ledger state.

**Abandoned close:**

1. Record the abandonment reason in the ledger. If no ledger exists, create one with
   all stories set to `abandoned` and the reason.
2. For each worktree owned by the dispatch: `git worktree remove --force` and
   `git branch -D` (the work is abandoned, not preserved).
3. Commit the ledger.

### 2. Batch-fix guidance

Add a paragraph to commit-conventions.md:

> When multiple failure modes surface in the same file or script, read and understand
> the file as a whole before committing a fix. Prefer one commit that addresses all
> known failure modes over a series of incremental patches. Incremental symptom-chasing
> produces commits that are individually correct but collectively hard to review, bisect,
> and reason about.

### 3. Dispatch-ledger gate

Gate story-branch commits on dispatch-ledger existence. The
implementation agent in the 2026-09-07 progressive-fitting dispatch
created story branches directly without running `dispatch init`,
bypassing invocation-branch creation and ledger setup. No mechanical
gate caught this — only a post-hoc observation.

Two layers, both required:

1. **Prompt discipline.** Add a MUST to the implementation-agent
   definition requiring `dispatch init` as its first action before
   creating any story branches.
2. **Mechanical gate.** Extend `block-dangerous-git.sh` to deny
   `git commit` on `story/*` branches when no dispatch ledger exists.
   The ledger lives in the main checkout at
   `.current-work/<feature-branch>/dispatch-ledger.yaml`, not in the
   story worktree. The hook resolves the main checkout path from the
   worktree's `commondir` (via `git rev-parse --git-common-dir`) and
   checks for the ledger there. This catches cases where a model
   ignores the MUST.

### 4. Worktree cleanup on close

Post-merge branch and worktree cleanup is currently manual. After the
progressive-fitting merge, 28 worktrees and 38 branches had
accumulated. Orphaned `worktree-agent-*` branches from subagent runs
require `git branch -D` because they are not merged into dev — the
guardrail blocks this.

Options:

- Add a `dispatch close` command to `factory/scripts/dispatch` that
  prunes worktrees, deletes merged branches, and force-deletes
  `worktree-agent-*` branches owned by the dispatch.
- Allowlist `worktree-agent-*` branch deletion in
  `block-dangerous-git.sh` — these are ephemeral subagent branches,
  never long-lived work.

### 5. Stale installed factory after merge

When `packages/factory/` changes are merged to dev, the installed
`factory/` copy goes stale. Tests import from the installed copy, so
new functions are missing and tests fail at pre-commit time — after QA
already passed in the worktree where `packages/factory/` was the
source. The freshness hook warns but does not auto-update when
`update-factory` would need `--force` (hook-modified files like
INDEX.yaml).

The root cause is that `init-factory` copies `factory/` with
`shutil.copytree(symlinks=False)`, creating regular files. When
index-lint writes INDEX.yaml with `Path.write_text()`, the write
follows the symlink in `.pi/` but creates a regular file in `.claude/`,
`.github/`, and `.codex/` where `copytree` already made them regular.
Subsequent `update-factory` runs detect checksum mismatches on these
hook-modified files and require `--force`.

Exclude hook-regenerated files from `update-factory` checksums. Maintain
a list of known hook-regenerated paths (initially `INDEX.yaml` per CLI
directory) in `init-factory`'s manifest. `update-factory` skips checksum
comparison for listed paths and overwrites them unconditionally — the
source copy is always authoritative, and the hook will regenerate them on
the next commit anyway. This is the smallest change that breaks the
`--force` chain without altering `copytree` semantics or adding
checksum-awareness to `index-lint`.

### 6. QA-in-worktree vs pre-commit divergence

QA ran in the worktree against `packages/factory/scripts/init-factory`
(source), but pre-commit hooks ran against `factory/scripts/init-factory`
(installed copy). QA passed; pre-commit failed with 25 test failures.
The qa-agent should note when it is running in a worktree that the
installed factory copy may diverge from the source, or the dispatch
contract should require an `update-factory` step before final merge.

## Scope

**In the first release:**

- Amend dispatch-contract.md with a Close section (completed and abandoned paths)
- Amend branching-policy.md to reference the close ceremony for worktree cleanup
- Amend commit-conventions.md with batch-fix guidance
- Amend rules.md with a MUST rule for dispatch close
- Add dispatch-ledger MUST to implementation-agent definition
- Add dispatch-ledger mechanical gate to block-dangerous-git.sh
- Fix the stale-factory / checksum-mismatch chain (see open question 1)
- Add dispatch-contract guidance on QA-in-worktree vs installed-copy divergence

**In a follow-up release:**

- `factory/scripts/dispatch close` command (automated cleanup)
- Post-merge `update-factory` hook or pre-merge workflow step
- Allowlist `worktree-agent-*` branch deletion in guardrail

**Explicitly deferred (do NOT plan stories for these):**

- CI enforcement of worktree hygiene
- `--check` / `--dry-run` on init-factory (separate proposal)

## Completion Criteria

- dispatch-contract.md contains a Close section with completed and abandoned paths.
- branching-policy.md references the dispatch close for worktree removal.
- commit-conventions.md contains batch-fix guidance.
- rules.md contains a MUST rule requiring dispatch close on completion or abandonment.
- implementation-agent.md contains a MUST requiring `dispatch init` before story branches.
- block-dangerous-git.sh denies commits on `story/*` branches without a dispatch ledger.
- The stale-factory chain is broken so `update-factory` runs without `--force` after hook-modified files.
- dispatch-contract.md or qa-agent.md documents that QA in a worktree does not validate the installed factory copy.

## Open Questions

1. ~~**Stale-factory fix mechanism.**~~ **Resolved:** exclude hook-regenerated files
   from `update-factory` checksums. See design item 5.
2. **Worktree cleanup scope tier.** Design item 4 lists options (dispatch-close script
   vs guardrail allowlist) but both are in follow-up. Is manual cleanup acceptable for
   the first release, or should one option move forward?
3. **QA divergence: contract guidance vs qa-agent behavior.** Design item 6 can be
   addressed by adding a note to the dispatch contract (convention), or by making the
   qa-agent detect worktree context and warn (code change). First release targets
   convention; code change is follow-up unless the convention alone is insufficient.

## Guiding Rule

A dispatch that begins without ending is a leak. Close it or record why it stopped.

## Review — 2026-09-08

Reviewer: proposal-review-agent
Reviewed commit: 33342580116a5b8b132528cd3a7346cf8aa6930e
Disposition: findings

### Findings

| ID      | Severity | Check | Status   | Finding                                                                                                                                                                                                                                                                                                                            |
| ------- | -------- | ----- | -------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| PROP-01 | minor    | 01    | resolved | Completion criterion 5 ("Story-branch commits are gated on dispatch-ledger existence") does not specify where the gate lives. Design item 3 presents an unresolved OR (MUST in implementation-agent vs mechanical check in verify-base/block-dangerous-git.sh). A planner cannot write a story without knowing the mechanism.      |
| PROP-02 | info     | 01    | resolved | Status is `draft` but proposal was submitted for adversarial review. If grilling is complete, status should move to `open`.                                                                                                                                                                                                        |
| PROP-03 | major    | 02    | resolved | Design item 6 (QA-in-worktree vs pre-commit divergence) has no scope assignment — not in first release, follow-up, or deferred. The scope boundary cannot classify work for this item.                                                                                                                                             |
| PROP-04 | minor    | 02    | resolved | Follow-up scope includes "`--check` / `--dry-run` on init-factory" with no corresponding design item. Scope items without design backing are not decomposable.                                                                                                                                                                     |
| PROP-05 | major    | 03    | resolved | Design item 3 presents an unresolved OR — MUST in implementation-agent vs extending verify-base/block-dangerous-git.sh. Prompt-discipline and mechanical gate are fundamentally different approaches. Planning cannot decompose without resolving the choice.                                                                      |
| PROP-06 | minor    | 04    | resolved | `external_contract_change: false` but the proposal adds a MUST rule to rules.md and a mandatory Close section to dispatch-contract.md — both are contracts consumed by all factory-adopting projects.                                                                                                                              |
| PROP-07 | minor    | 05    | resolved | `factory/scripts/verify-base` is referenced as a candidate for modification in design item 3 but is not listed in `impact.boundaries`.                                                                                                                                                                                             |
| PROP-08 | minor    | 05    | resolved | The claim that index-lint "overwrites symlinks with regular files" is not supported by the code. `index-lint` uses `Path.write_text()` (follows symlinks) and `init-factory` uses `shutil.copytree(symlinks=False)` (creates regular files). The actual root cause appears to be that index-lint modifies a checksum-tracked file. |
| PROP-09 | major    | 06    | resolved | Open Questions section is missing entirely. The template requires every section to be filled or removed with justification. Three unresolved design choices (items 3, 4, 5) are embedded as inline ORs in the Design section instead of being surfaced as open questions.                                                          |
| PROP-10 | minor    | 08    | resolved | `overhead_multiplier: 10` is below the template's stated typical range of 15-25x for feature-addition. Six design items across 8+ boundary files suggest 15-20x is more realistic (estimated_consumption would shift from 40k-120k to approximately 75k-240k).                                                                     |

### Summary

Three major findings block planning readiness: design item 6 has no scope assignment (PROP-03), design item 3 is not decomposable due to an unresolved OR between prompt-discipline and mechanical enforcement (PROP-05), and the Open Questions section is missing while unresolved design choices sit inline in the Design (PROP-09). Additionally, the index-lint symlink claim does not match the code — the root cause is likely checksum-tracking interference, not symlink overwrite (PROP-08). Address these four items and the proposal is close to plannable.

## Review — 2026-09-08 (repeat pass)

Reviewer: proposal-review-agent
Reviewed commit: 33342580116a5b8b132528cd3a7346cf8aa6930e
Disposition: findings

### Prior Findings

All ten findings from the initial review (PROP-01 through PROP-10) are resolved in the current text. Status cells updated to "resolved" in the table above.

### Findings

| ID      | Severity | Check | Status | Finding                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| ------- | -------- | ----- | ------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| PROP-11 | major    | 03    | open   | Design item 5 (stale installed factory after merge) is not decomposable. The Design section describes the root cause chain but says "Options (see Open Questions)" and provides no implementation approach. Open Question 1 lists three candidate fixes (a: index-lint checksum-aware, b: copytree preserve symlinks, c: exclude hook-regenerated files from checksums) without resolving to one. A planner cannot write a story without knowing which approach to implement.                                                                                                                                                                                                            |
| PROP-12 | minor    | 02    | open   | Scope cross-reference error. "Fix the stale-factory / checksum-mismatch chain (see open question 2)" at line 194 references Open Question 2 (worktree cleanup scope tier). The corresponding open question is number 1 (stale-factory fix mechanism).                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| PROP-13 | minor    | 03    | open   | Design item 3's mechanical gate states "deny git commit on story/\* branches when no dispatch ledger (.current-work/dispatch-ledger.yaml) exists in the worktree root." The dispatch ledger lives in the main checkout at .current-work/\<feature-branch>/dispatch-ledger.yaml (per dispatch-contract.md and dispatch script cmd_init), not in the story worktree. The hook's $TOP in a linked worktree resolves to the worktree root, where no ledger exists. The design should specify either a per-worktree marker approach (like the existing verify-base-ok pattern written by prepare-wave) or how the hook resolves the path from a story worktree to the main checkout's ledger. |
| PROP-14 | minor    | 08    | open   | Estimated consumption max (240,000) does not match normalized_tokens max (12,000) multiplied by the stated overhead_multiplier (15), which yields 180,000. The 240,000 figure implies an effective multiplier of 20x at the upper bound. Either adjust the max to 180,000 or state the multiplier as a range (15-20x).                                                                                                                                                                                                                                                                                                                                                                   |

### Summary

All prior findings are resolved. Six of eight checks pass cleanly. One major finding remains: design item 5 (stale-factory fix) delegates the solution entirely to an unresolved open question with three candidate approaches, making it not decomposable into stories (PROP-11). Three minor findings: a scope cross-reference points to the wrong open question number (PROP-12), the dispatch-ledger gate's worktree-path assumption does not match the actual ledger location (PROP-13), and the consumption estimate max is arithmetically inconsistent with the stated multiplier (PROP-14). Resolve Open Question 1 (pick a fix approach for the stale-factory chain) and the proposal is ready to plan.
