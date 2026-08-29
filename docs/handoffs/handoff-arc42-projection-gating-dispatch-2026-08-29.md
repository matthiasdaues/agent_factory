# Handoff: arc42 Projection Gating Dispatch

**Date:** 2026-08-29
**From:** Implementation Agent (Dispatcher)
**Next session focus:** Resume dispatch of ST-0159 through ST-0163 (arc42 Projection Gating epic)

## Current State

### Branch topology

| Ref                                       | Full SHA                                   | Note                                                       |
| ----------------------------------------- | ------------------------------------------ | ---------------------------------------------------------- |
| `dev`                                     | `9063ce6c0bcbc05c0ee333f8f056bf9b735653a7` | Baseline commit from `dispatch init`                       |
| `impl/st-0159-st-0160-st-0161-and-2-more` | `9063ce6c0bcbc05c0ee333f8f056bf9b735653a7` | Invocation branch, same as dev                             |
| `story/ST-0159`                           | `9063ce6c0bcbc05c0ee333f8f056bf9b735653a7` | Feature branch, no commits yet (work on disk, uncommitted) |

Pre-dispatch dev HEAD was `069c6d6bc51c7d7cbd7c73d5eeedf80b284b4fa1`; `dispatch init --baseline-commit` advanced dev to `9063ce6c`.

### Worktrees

- Invocation: `.current-work/worktrees/impl/st-0159-st-0160-st-0161-and-2-more`
- ST-0159: `.current-work/worktrees/impl/st-0159-st-0160-st-0161-and-2-more/.current-work/worktrees/story-ST-0159`

### Dispatch ledger

Path: `.current-work/impl/st-0159-st-0160-st-0161-and-2-more/dispatch-ledger.yaml`

| Story   | Wave | Status       | Note                                  |
| ------- | ---- | ------------ | ------------------------------------- |
| ST-0159 | 1    | `dispatched` | Implementation on disk, not committed |
| ST-0160 | 2    | `pending`    | Blocked on ST-0159                    |
| ST-0161 | 2    | `pending`    | Blocked on ST-0159                    |
| ST-0162 | 2    | `pending`    | Blocked on ST-0159                    |
| ST-0163 | 2    | `pending`    | Blocked on ST-0159                    |

### Old branches renamed

Prior dispatch run left unmerged branches. Renamed to clear namespace:

- `story/ST-0159` -> `old/story/ST-0159`
- `story/ST-0160` -> `old/story/ST-0160`
- `story/ST-0161` -> `old/story/ST-0161`
- `story/ST-0162` -> `old/story/ST-0162`

Old worktrees (under `retrospective-dispatch-qa-robustness`) removed.

## ST-0159 Implementation Status

### What is done

The developer-agent completed the implementation in the story worktree but could not commit due to a platform conflict (see Blocker below). All changes are on disk:

**`factory/scripts/arch-lint`** (the only declared output):

- Added `dsl_workspace_property(dsl, key)` function: extracts workspace-level properties from DSL preamble (before `model {`), uses existing `_block` helper, regex-matches key-value pairs. Returns `"true"`, `"false"`, or `None`.
- Gated missing-ch5 check: `projected=true` -> ERROR (unchanged); `projected=false/absent` -> INFO.
- Gated diagram export (staleness check): `projected=true` -> runs export (unchanged); `projected=false/absent` -> skipped with INFO.
- Coupling check: runs unconditionally when both DSL and ch5 exist (correct).
- ADR check and `structurizr validate`: unaffected (correct).
- Module docstring updated to document the property.

**`backlog/ST-0159.md`**: Analysis section added. Status left at `pending` (no commit happened).

### Verification performed by developer-agent (ad hoc, no permanent tests)

- Parser unit checks: true/false/absent/element-level scoping all correct
- Subprocess end-to-end: `projected=false` + no ch5 -> exit 0; `projected=true` + no ch5 -> exit 1; both present + `projected=false` -> coupling runs
- Self-lint against `docs/arc42/`: exit 0, 0 errors
- `uvx ruff check`: 3 pre-existing findings on untouched lines

### To finish ST-0159

From the story worktree (`...story-ST-0159`):

1. Set `status: done` in `backlog/ST-0159.md`
2. `git add factory/scripts/arch-lint backlog/ST-0159.md`
3. `git commit -m "feat: gate arch-lint staleness/ch5 checks on arc42.projected property (ST-0159)"`
4. Run quality gate: `factory/scripts/arch-lint --docs-dir docs/arc42` from the worktree
5. Call `dispatch verify-story ST-0159 --sha <commit-sha>` with the ledger path
6. Call `dispatch merge-story ST-0159` with the ledger path
7. Call `dispatch close-wave 1` with the ledger path

## Blocker Encountered and Resolution

**Root cause:** The `Agent` tool was called with `isolation: "worktree"`, which creates a Claude-Code-native worktree (`/.claude/worktrees/agent-<id>`). This double-worktree layering prevents the subagent from running `git` commands in Factory's dispatch-prepared worktree. All git operations are blocked by Claude Code's native isolation enforcement.

**Resolution for next session:** Do NOT use `isolation: "worktree"` on the `Agent` tool when Factory's dispatch already provides its own worktree. Spawn developer-agents without the `isolation` parameter. The Factory dispatch worktree is sufficient isolation.

## Wave Plan (unchanged)

- **Wave 1** (serial): ST-0159
- **Wave 2** (parallel, all file-disjoint): ST-0160, ST-0161, ST-0162, ST-0163

See `backlog/ST-0159.md` through `backlog/ST-0163.md` for full story details. Key design context is in the original dispatch task message.

### Model mapping

- ST-0159: standard -> sonnet
- ST-0160: simple -> haiku
- ST-0161: standard -> sonnet
- ST-0162: standard -> sonnet
- ST-0163: simple -> haiku

### Ledger path (pass to all dispatch commands)

```
--ledger /home/matthiasdaues/Documents/datenschoenheit/agent_factory/.current-work/impl/st-0159-st-0160-st-0161-and-2-more/dispatch-ledger.yaml
```

## Suggested Skills

- **`handoff`** -- read this document to recover state
- **`run-step`** -- if using the step-manifest workflow for individual stories
- **`spec-feedback`** -- after each story completes, for traceability
- **`tdd`** -- for developer-agents implementing stories (especially ST-0162)
- **`crap-score`** / **`dependency-check`** -- quality gates for stories that declare them
