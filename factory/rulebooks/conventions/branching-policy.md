---
title: Feature Branch Scoping
category: implementation
enforcement: implementation-agent dispatch logic (T-35)
version: 1.0.0
---

# Feature Branch Scoping

Governs how feature branches are created and merged during implementation dispatch — **not** how released code is tagged. Distinct from [versioning-policy.md](versioning-policy.md): that rule governs branch/tag naming once code ships; this rule governs in-progress work, before any release exists. Overlapping scope (both are about branches), different concern (release identity vs. dispatch safety) — kept as separate files rather than merged.

## Project-Specific Rules

Canonical statements: [rules.md § Branching](../rules.md#branching). This section carries the rationale and detail behind each one.

### Branch Per Unit Of Work

Shared integration files (a composition root, a domain-entities module, a ports file) are typically touched by stories across many different epics. A branch scoped to a coarser label collects several stories' edits to the same shared file independently — every grouping's branch then collides with every other grouping's branch, all at once, at merge-back. A branch scoped to one story collides with at most the other stories that genuinely touch the same file, one at a time, in a determinable order.

### Invocation Branch

Every feature branch for an invocation is cut from that invocation's own branch, not from `main` directly — the invocation branch is what makes the branch-root/branch-head SHA pair (below) well-defined.

### Worktree Isolation

A feature branch name is not a working directory: cutting the branch does not, by itself, guarantee any subagent's commands run against it rather than against the shared/main checkout. Before dispatching a developer-agent subagent, the dispatcher must materialize its feature branch into a dedicated git worktree (e.g. via the Agent tool's `isolation: "worktree"` parameter) and confirm — via `git worktree list`, not the subagent's own report — that the worktree exists and is checked out to the correct branch before considering that subagent dispatched. See `agents/implementation-agent.md` Step 3 ("Dispatch: one feature branch per story") for the enforcing workflow step. Motivating example: the 2026-07-10 `implementation-agent` dispatch, where a subagent's first git command ran against the shared main checkout instead of its own worktree, chain-renaming the main branch through four story names before being caught.

### Merge Order Is Overlap-Aware

Overlap is determined via declared or inferred output paths:

- File-disjoint branches: merge in parallel, any order.
- File-overlapping branches: merge one at a time, in dependency order.

A conflict or regression after a merge means the overlap analysis missed a real collision — resolve before continuing to the next merge.

### Two SHAs Tracked Per Invocation

- **branch root** — the SHA on `main`/trunk the invocation branch was cut from.
- **branch head** — the SHA of the last merge commit on the invocation branch, once every feature branch for the invocation has merged.

Downstream review/QA agents are invoked with `--base <branch-root> --head <branch-head>` so they inspect exactly the delta this invocation introduced.

### Commits On Feature Branches

Feature-branch commits follow [commit-conventions.md](commit-conventions.md) — `<type>: <description> (<ID>)` — same as any other commit in the project. Branching does not change commit format.

## Enforcement

Enforced by the implementation-agent's own dispatch algorithm, not a git hook — the check that a merge sequence was genuinely overlap-safe needs live backlog state (every ready story's declared outputs) that no static hook has access to. This rulebook states the **what** (branch scope, merge-order constraint, SHA tracking); `agents/implementation-agent.md` (Steps 1–5) and T-35 own the **how** — the actual overlap-detection and wave-planning algorithm.

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
- `agents/implementation-agent.md` — the enforcing agent's workflow
