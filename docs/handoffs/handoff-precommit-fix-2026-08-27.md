# HANDOFF — Pre-commit Fix Session, 2026-08-27

Branch: `dev` @ `63e73cd`. All changes staged, NOT yet committed — pre-commit hook blocks due to pre-existing dispatch test failures.

## What was done

Fixed 13 test failures (across 5 root causes) that blocked pre-commit. All 969 tests pass when run directly via `factory/scripts/run-tests --full` (except ~30 pre-existing dispatch worktree failures and 1 stale INDEX.yaml, both predating this session).

### Completed fixes (all staged, uncommitted)

| Root cause                                                      | Files changed                                                                                                                               | What                                                                                                                                                                                                                                     |
| --------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Ruff version drift                                              | `.pre-commit-config.yaml`, `factory/config/pre-commit-config.yaml`, `pyproject.toml`                                                        | Pinned `uvx ruff@0.16.5` in all 8 entries; added per-file-ignores for test noise rules (`PLW1510`, `RUF012`)                                                                                                                             |
| dispatch-wave.ts signal TypeError + Node.js v24 unsettled await | `factory/config/extensions/dispatch-wave.ts`                                                                                                | `signal: AbortSignal` → `AbortSignal \| undefined` + optional chaining; removed `child.unref()` so event loop waits for "close"                                                                                                          |
| run-agent.ts artifact validation order                          | `factory/config/extensions/run-agent.ts`                                                                                                    | Swapped `git add` / `git ls-files --error-unmatch` order — `add` before `ls-files` silently staged untracked files                                                                                                                       |
| Worktree path convention                                        | `factory/config/hooks/block-dangerous-git.sh`, `tests/orchestrator/test_guardrail_parser.py`                                                | `.agent-factory/worktrees/` → `.current-work/`                                                                                                                                                                                           |
| AGENTS.md assertion drift                                       | `tests/orchestrator/test_factory_orientation.py`                                                                                            | Updated stale assertion to match current AGENTS.md content                                                                                                                                                                               |
| Trivial code fixes                                              | `tests/orchestrator/test_phase_advance.py`, `tests/orchestrator/test_schema_validate.py`, `tests/orchestrator/test_usage_capture_pi_e2e.py` | 5 `_msg` renames, 2 `dict \| None` fixes, 1 redundant noqa removal                                                                                                                                                                       |
| **init-factory Codex step-guard dedup bug**                     | `factory/scripts/init-factory` (line ~1089)                                                                                                 | `already_wired` check matched by command only; Edit and Write share `GUARD_TYPE=write` command → Write entry silently skipped. Fixed: check `(matcher, command)` pair                                                                    |
| **remove-factory step-guard event mismatch**                    | `factory/scripts/remove-factory` (line ~275)                                                                                                | Stripped step-guard hooks from `"PreToolUse"` but init-factory puts Claude step-guards under per-tool events (Read/Edit/Write/Bash). Fixed: `"PreToolUse"` → `event`                                                                     |
| Stale test assertions (6 tests)                                 | `tests/orchestrator/test_init_factory_step_guard.py`, `tests/orchestrator/test_init_factory_codex.py`                                       | Claude: assert per-tool events not PreToolUse; Codex: check `(matcher, command)` counts; orientation: expect injection not skip; AGENTS.md: `"before ANY Skill/Agent call"` → `"resolve skill invocations through the INDEX.yaml first"` |
| INDEX.yaml stale                                                | `factory/INDEX.yaml`                                                                                                                        | Regenerated via `factory/scripts/index-lint`                                                                                                                                                                                             |

### Test file renames (also staged, from a prior session)

~70 test files moved from `orchestrator/tests/` → `tests/orchestrator/` and `tests/` → `tests/factory/`. These were already in the staging area at session start — they are NOT this session's work but are entangled in the commit.

## What blocks the commit

The pre-commit hook runs `run-tests --changed-only` which invokes `pytest --lf`. With all renames staged, pytest picks up ALL renamed tests as "changed". ~30 dispatch/prepare/merge integration tests fail with:

```
fatal: Unable to create '.../.agent-factory/worktrees/story-ST-xxx/.git/index.lock': Not a directory
```

These are **pre-existing failures** — they fail before my session's changes and are NOT caused by my fixes. They're in:

- `tests/factory/test_dispatch_e2e.py`
- `tests/factory/test_dispatch_init_integration.py`
- `tests/factory/test_dispatch_merge_integration.py`
- `tests/factory/test_dispatch_prepare_integration.py`
- `tests/factory/test_dispatch_status_integration.py`
- `tests/factory/test_manifest_lifecycle_integration.py`
- `tests/orchestrator/test_child_result_envelope.py` (envelope format assertions)
- `tests/orchestrator/test_premerge_check.py`

The root cause: `git worktree add` to `.agent-factory/worktrees/` fails inside `/tmp/pytest-*` repos with `index.lock: Not a directory`. This may be a git version incompatibility or a missing directory scaffold in the test fixtures.

## How to proceed

**Option A — Split the commit**: Unstage the test renames, commit only the 9 non-test files + the 7 test files I modified (as renames). This still triggers pre-commit on the renamed tests but avoids the dispatch tests. Caveat: the non-renamed tests (`tests/test_*`) still exist on disk at new paths and are gone from old paths, so pre-commit stashing creates module import collisions. To make this work, you'd need to either (a) also stage ALL the renames, or (b) temporarily restore the old test paths before committing.

**Option B — Fix dispatch worktree tests first**: Investigate the `.agent-factory/worktrees/` `index.lock` error. The prepare-wave script creates worktrees under that path. The error suggests `.git` inside the worktree is a file (expected) but the gitdir it points to doesn't exist or has a path component that's a file instead of a directory. Likely a change in how prepare-wave scaffolds the worktree parent directory.

**Option C — Commit with test-rename split**: Stage everything but unstage just the failing test files. This leaves some renames uncommitted but lets the passing tests through. Risk: if the hook stashes, the module collision problem returns.

**Recommended**: Option B is the right fix. The dispatch worktree issue is a real bug that needs fixing anyway. Start by running one failing test in isolation to understand the directory layout it expects.

## Current staging state

```
git diff --cached --stat  # 85 files changed, 777 insertions(+), 129 deletions(-)
```

All code fixes + all test renames are staged. No unstaged modifications. Two untracked files: `factory/agents/proposal-review-agent.md`, `factory/skills/draft-proposal/` (unrelated).

## Key code locations

- init-factory step-guard: `factory/scripts/init-factory` lines 1088–1107
- remove-factory step-guard: `factory/scripts/remove-factory` lines 274–276
- CLAUDE_STEP_GUARD_HOOK_COMMANDS: `factory/scripts/init-factory` lines 143–148
- CODEX_STEP_GUARD_HOOK_COMMANDS: `factory/scripts/init-factory` lines 168–173
- dispatch worktree creation: `factory/scripts/prepare-wave` (not modified, investigate here)
- pre-commit test hook: `.pre-commit-config.yaml` → `run-tests` hook → `factory/scripts/run-tests --changed-only`

## Suggested skills

- **bug-fix** — if pursuing Option B (dispatch worktree test failures)
- **commit** — once the blocking tests are resolved, to commit the staged changes
- **handoff** — if session runs long and needs to hand off again
