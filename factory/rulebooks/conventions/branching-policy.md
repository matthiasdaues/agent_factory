---
title: Branch and Worktree Scoping
category: implementation
enforcement: implementation-agent dispatch logic (T-35)
version: 2.1.0
---

# Branch and Worktree Scoping

Governs how every local branch is created, used, and merged — **not** how released code is tagged. Distinct from [versioning-policy.md](versioning-policy.md): that rule governs branch/tag naming once code ships; this rule governs in-progress work, before any release exists. Overlapping scope (both are about branches), different concern (release identity vs. workspace safety) — kept as separate files rather than merged.

## Project-Specific Rules

Canonical statements: [rules.md § Branching](../rules.md#branching). This section carries the rationale and detail behind each one.

### Branch Per Unit Of Work

Shared integration files (a composition root, a domain-entities module, a ports file) are typically touched by stories across many different epics. A branch scoped to a coarser label collects several stories' edits to the same shared file independently — every grouping's branch then collides with every other grouping's branch, all at once, at merge-back. A branch scoped to one story collides with at most the other stories that genuinely touch the same file, one at a time, in a determinable order.

### Every Branch Has A Worktree

Creating a branch and creating its linked worktree are one atomic operation. This applies to **every** local branch type: invocation, story, bug, review, reconciliation, fix, experiment, spike, release-preparation, and manually created branches. There are no exceptions for sequential work or branches used by only one agent.

```bash
git worktree add -b <branch> .current-work/worktrees/<branch> <base>
git worktree list --porcelain
```

All worktrees live under `.current-work/worktrees/`, named after their branch. This directory is gitignored and holds project-work ephemera. Never place a worktree in the repository root, a sibling directory, or an arbitrary path.

Do not use standalone branch creation (`git branch <name>`, `git switch -c/-C`, or `git checkout -b/-B`) and do not create a branch in the current checkout before adding a worktree later. Existing branches may be attached with `git worktree add .current-work/worktrees/<branch> <branch>` when recovering or resuming work, but new branches must use the atomic `worktree add -b` form. Verify the branch-to-path mapping before doing work there.

The checkout in which a command starts remains on its existing branch. Work on the new branch happens only in the new worktree. This prevents branch switching from moving or contaminating a shared checkout and makes branch ownership observable from Git state.

### Indexed Artifacts On Dev

All indexed artifacts — backlog stories (`ST-NNNNNN`), findings (`PROP-NNNN`, `RECON-NNNNNN`), proposals, and any other file with a sequential ID — are always committed to `dev`. The `dev` branch is the single canonical index so that parallel sessions never collide on IDs. Implementation work never touches `dev` directly; it lands on a feature branch and merges back after gates pass.

The sequence is:

1. **Planning agent** commits proposals and indexed artifacts (all `status: pending`) to `dev`.
2. **Implementation agent** creates the invocation branch from `dev`.
3. Story branches are cut from the invocation branch.
4. After all stories pass gates, the invocation branch merges back to `dev`.

### Invocation Branch

The invocation branch is created from `dev` using `feature/<proposal-title>` as the branch name. Every story branch for an invocation is cut from this invocation branch, not from `dev` directly — the invocation branch is what makes the branch-root/branch-head SHA pair (below) well-defined. The invocation branch itself is created with its own linked worktree under the rule above.

### Worktree Isolation

A feature branch name is not a working directory. The universal branch/worktree rule above guarantees that every new branch is born in a dedicated worktree; dispatch adds the requirement to confirm — via `git worktree list --porcelain`, not the subagent's own report — that the worktree exists and is checked out to the correct branch before considering that subagent dispatched. See [implementation-agent.md § Workflow, Step 3 ("Dispatch: one feature branch per story")](../../agents/implementation-agent.md#workflow) for the enforcing workflow step. Motivating example: the 2026-07-10 `implementation-agent` dispatch, where a subagent's first git command ran against the shared main checkout instead of its own worktree, chain-renaming the main branch through four story names before being caught.

### Verify-Base Preamble

Worktree isolation guarantees a subagent's commands run in the right *directory*; it does not guarantee that directory's HEAD is actually caught up with the branch it was meant to be cut from. A worktree can materialize against a stale base and reason against code that no longer exists on the target branch — a full agent run's worth of tokens spent before anyone notices. This recurred across three phases of the 2026-07-12 session, twice costing a full discarded run.

The verify-base invocation is now **script-owned**, not prompt-owned. `factory/scripts/dispatch prepare-wave` and `factory/scripts/dispatch prepare-story` must run the fixed pre-spawn check before any developer-agent is launched:

```bash
factory/scripts/verify-base <target-branch> [--expect-base <declared-base-SHA>]
```

Exit `0` means the dispatcher may spawn the subagent into that prepared worktree. Any non-zero exit means: **stop — do not spawn the subagent.** Report the script's printed diagnosis and resolve the base mismatch before continuing. Dispatch prose may mention that the workspace already passed verify-base, but it must not rely on the developer-agent to remember and rerun the check manually.

### Declared Base SHA

Not-behind-target (checked by the preamble above with no `--expect-base`) proves a worktree isn't missing commits — it does not prove the worktree was cut from the commit the dispatcher actually intended, if the target branch has kept moving. The dispatcher closes that gap by recording the exact SHA each feature branch is meant to be cut from — its **declared base** — in the dispatch record, and passing it to the script-owned verify-base call as `--expect-base`. This is the 2026-07-10 retro's action item #1 (phase branches with a recorded base/head SHA pair), narrowed to the one assertion that catches a wrong-base dispatch on the subagent's first tool call instead of after a full run.

### Merge Order Is Overlap-Aware

Overlap is determined via declared or inferred output paths:

- File-disjoint branches: merge in parallel, any order.
- File-overlapping branches: merge one at a time, in dependency order.

A conflict or regression after a merge means the overlap analysis missed a real collision — resolve before continuing to the next merge.

### Pre-Merge Diff Check

Before merging any finished branch, run:

```bash
factory/scripts/premerge-check <target> <branch> [--scope <declared-output-path> ...]
```

Exit `0` means clean to merge. Exit non-zero means **block the merge** and investigate — a stale base or unrequested out-of-scope work, not a real overlap collision. Both contaminated diffs in the 2026-07-12 session were real; both were caught only because someone remembered to run `git diff --stat` by hand, after the branch's full run had already finished. This check makes that habit a required, scripted step instead of something the dispatcher must remember, and runs it on the finished branch as a second, independent gate on top of the Verify-Base Preamble the subagent ran on its own first tool call.

`premerge-check`'s pass marker is one slot per checkout, keyed to the branch just checked — so each `premerge-check <branch>` call must be immediately followed by that branch's own `git merge`, one pair at a time, before checking the next branch. Batching checks ahead of merges overwrites the marker and the earlier merges get denied. This isn't a new constraint: a single working tree can only merge one branch at a time anyway (git's own index lock serializes it); the marker just now enforces the ordering mechanically instead of assuming the dispatcher follows it.

### Two SHAs Tracked Per Invocation

- **branch root** — the SHA on `main`/trunk the invocation branch was cut from.
- **branch head** — the SHA of the last merge commit on the invocation branch, once every feature branch for the invocation has merged.

Downstream review/QA agents are invoked with `--base <branch-root> --head <branch-head>` so they inspect exactly the delta this invocation introduced.

### Commits On Feature Branches

Feature-branch commits follow [commit-conventions.md](commit-conventions.md) — `<type>: <description> (<ID>)` — same as any other commit in the project. Branching does not change commit format.

## Enforcement

Standalone branch creation is mechanically denied by the shared shell and Pi Git guardrails. `git worktree add -b <branch> .current-work/worktrees/<branch> <base>` is the supported creation primitive. Overlap-safe merge sequencing is enforced by the implementation-agent's own dispatch algorithm, not a git hook — it needs live backlog state (every ready story's declared outputs) that no static hook has access to. This rulebook states the **what** (branch/worktree pairing, branch scope, merge-order constraint, SHA tracking); `agents/implementation-agent.md` (Steps 1–5) and T-35 own the **how** — the actual overlap-detection and wave-planning algorithm.

The base-safety checks are mechanically enforced, per [foundational-principles.md § Agentic Creation, Deterministic Validation](foundational-principles.md#agentic-creation-deterministic-validation): `factory/scripts/dispatch` owns the pre-spawn `verify-base` call, and `factory/scripts/premerge-check` owns the pre-merge scope check. Their success markers are written on success, and `factory/config/hooks/block-dangerous-git.sh` denies `git commit` (inside a linked worktree with no `verify-base-ok` marker) and `git merge <branch>` (with no `premerge-check-ok` marker for that branch's current head) — a `PreToolUse` hook, not agent compliance with a prompt instruction.

## Example

**Wrong** (per-EPIC) — from the TUI addendum dispatch (2026-07-08): the composition root (`cli.py`) is touched by stories in the TUI Presentation, Configuration, Adapter Registry & Model Resolution, Skill-Scoped Execution, and Status & Backlog Views epics. Branching by epic would give each of those five branches its own independent edit to `cli.py`, all colliding at once when merged back:

```
epic/tui-presentation        <- touches cli.py
epic/configuration           <- touches cli.py
epic/adapter-registry        <- touches cli.py
epic/skill-scoped-execution  <- touches cli.py
epic/status-backlog-views    <- touches cli.py
# five independent edits to the same file, collide together at merge-back
```

**Right** (per-story, overlap-aware order) — what actually ran:

```
story/ST-0040 -> story/ST-0044 -> story/ST-0047 -> story/ST-0048   # serial: all touch cli.py
story/ST-0021, story/ST-0051, story/ST-0054, story/ST-0056          # parallel: no shared outputs
```

## References

- [commit-conventions.md](commit-conventions.md) — commit format on feature branches
- [versioning-policy.md](versioning-policy.md) — related but distinct: governs release tags, not in-progress branches
- [dispatch-contract.md](dispatch-contract.md) — sub-agent addressing and dispatch scope/checkpointing, the non-branching half of the dispatch contract this rulebook's Verify-Base Preamble and Pre-Merge Diff Check sections belong to
- [implementation-agent.md § Workflow](../../agents/implementation-agent.md#workflow) — the enforcing agent's workflow
- [verify-base](../../scripts/verify-base) — Verify-Base Preamble / Declared Base SHA enforcement
- [premerge-check](../../scripts/premerge-check) — Pre-Merge Diff Check enforcement
- [docs/reviews/retro-2026-07-12.md](../../../docs/reviews/retro-2026-07-12.md) and [docs/reviews/retro-2026-07-10.md](../../../docs/reviews/retro-2026-07-10.md) — the sessions that motivated these sections
