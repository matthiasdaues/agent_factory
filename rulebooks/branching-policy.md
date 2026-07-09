---
title: Feature Branch Scoping
category: implementation
enforcement: implementation-agent dispatch logic (T-35)
version: 1.0.0
---

# Feature Branch Scoping

Governs how feature branches are created and merged during implementation dispatch — **not** how released code is tagged. Distinct from [versioning-policy.md](versioning-policy.md): that rule governs branch/tag naming once code ships; this rule governs in-progress work, before any release exists. Overlapping scope (both are about branches), different concern (release identity vs. dispatch safety) — kept as separate files rather than merged.

## Project-Specific Rules

### Branch Per Unit Of Work

**MUST**: One feature branch per story (or bug), never per a coarser grouping label (EPIC, sprint, wave).

Shared integration files (a composition root, a domain-entities module, a ports file) are typically touched by stories across many different epics. A branch scoped to a coarser label collects several stories' edits to the same shared file independently — every grouping's branch then collides with every other grouping's branch, all at once, at merge-back. A branch scoped to one story collides with at most the other stories that genuinely touch the same file, one at a time, in a determinable order.

**MUST NOT**:

- ❌ Branch by EPIC, sprint, or any grouping label broader than one unit of work
- ❌ Merge multiple unrelated stories' work into one shared feature branch

### Invocation Branch

**MUST**: Before creating any feature branch, create one invocation branch from `main` (or the project's trunk) and record its origin commit as the **branch root**. Every feature branch for that invocation is cut from the invocation branch, not from `main` directly.

### Merge Order Is Overlap-Aware

**MUST**: Before merging concurrently-branched work back into the invocation branch, determine which branches touch overlapping files (via declared or inferred output paths).

- File-disjoint branches: merge in parallel, any order.
- File-overlapping branches: merge one at a time, in dependency order.

**MUST NOT**: Use a grouping label (EPIC, wave, sprint) as a substitute for real file-overlap analysis when deciding merge order.

**MUST**: Run the full test suite after every single merge, before starting the next. A conflict or regression here means the overlap analysis missed a real collision — resolve before continuing.

### Two SHAs Tracked Per Invocation

**MUST**: Track exactly two commit IDs per invocation:

- **branch root** — the SHA on `main`/trunk the invocation branch was cut from.
- **branch head** — the SHA of the last merge commit on the invocation branch, once every feature branch for the invocation has merged.

Downstream review/QA agents are invoked with `--base <branch-root> --head <branch-head>` so they inspect exactly the delta this invocation introduced.

### Commits On Feature Branches

Feature-branch commits follow [commit-conventions.md](commit-conventions.md) — `<type>: <description> (<ID>)` — same as any other commit in the project. Branching does not change commit format.

## Enforcement

Enforced by the implementation-agent's own dispatch algorithm, not a git hook — the check that a merge sequence was genuinely overlap-safe needs live backlog state (every ready story's declared outputs) that no static hook has access to. This rulebook states the **what** (branch scope, merge-order constraint, SHA tracking); `agents/implementation-agent.md` (Steps 1–5) and [T-35](../orchestrator/docs/spec/todos.md) own the **how** — the actual overlap-detection and wave-planning algorithm.

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

- [T-35, orchestrator/docs/spec/todos.md](../orchestrator/docs/spec/todos.md) — origin of this policy
- [commit-conventions.md](commit-conventions.md) — commit format on feature branches
- [versioning-policy.md](versioning-policy.md) — related but distinct: governs release tags, not in-progress branches
- `agents/implementation-agent.md` — the enforcing agent's workflow
