# Handoff: Agent Context -- Phase 4 Dispatch Resume

Date: 2026-09-04
Feature: agent-context (two-layer YAML routing with two-mode lifecycle)
Playbook: feature-addition, Phase 4
Role: implementation-agent (dispatcher)

## Current state

Wave 1 (ST-0190) implementation is complete but partially committed. A pre-existing test suite failure in unrelated orchestrator tests blocks the `run-tests` pre-commit hook, preventing the test files from being committed. All other waves (2 and 3) are blocked pending Wave 1 completion.

## Git state

| Ref                     | SHA                                        | Notes                                  |
| ----------------------- | ------------------------------------------ | -------------------------------------- |
| `dev` (base)            | `4e78d3f34a41308146bfeb6031650e0f238379b8` | Unchanged                              |
| `feature/agent-context` | `4e78d3f34a41308146bfeb6031650e0f238379b8` | Invocation branch, no merges yet       |
| `story/ST-0190`         | `174ef750072222d3001516a4fec1db6757f34688` | Implementation commit (non-test files) |

Branch root: `4e78d3f34a41308146bfeb6031650e0f238379b8`

### Worktrees

- `feature/agent-context`: `.current-work/worktrees/feature/agent-context`
- `story/ST-0190`: `.current-work/worktrees/feature/agent-context/.current-work/worktrees/story-ST-0190`

### ST-0190 worktree state

Commit `174ef750072222d3001516a4fec1db6757f34688` contains:

- `factory/rulebooks/templates/context-{stack,workflow,governance,reading-guides}.yaml` (4 new templates)
- `factory/rulebooks/conventions/agent-context-composition.md` (new convention)
- `factory/rulebooks/rules.md` (Agent context composition section added)
- `factory/scripts/context-lint` (renamed from `charter-lint`, CX-FILE/PARSE/KEYS/NULL/MODE/MODE-INVALID added)
- `factory/scripts/charter-lint` (deleted via git mv)
- `.pre-commit-config.yaml` (context-lint hook added)
- `backlog/ST-0190.md` (status: done, Analysis section added)
- `backlog/ST-0075.md` (outputs field corrected for rename)
- `factory/INDEX.yaml` (updated by index-lint)

**Staged but uncommitted** (18 files):

- `tests/factory/test_context_lint.py` (14 contract tests, all passing)
- `tests/fixtures/agent-context/{valid,missing_stack,invalid_yaml,missing_key,deferred_conflict,invalid_mode}/` (18 fixture YAML files)

## Blocker: pre-existing test failures

The `run-tests` pre-commit hook runs `uv run pytest --tb=short --quiet` on the full test suite whenever files under `src/` or `tests/` are staged. The suite has 69 pre-existing failures:

- 5 in `tests/factory/test_test_design_verify.py` -- gate script returns 0 instead of expected 1 or 2
- 64 in `tests/orchestrator/test_usage_capture*.py` -- filesystem/hardlink issues (`FileNotFoundError` on `.agent-factory/usage/transcripts/sess-private`)

These failures exist on the base commit `4e78d3f` as well -- verified by the developer-agent via `git stash`/`git stash pop`. None are caused by ST-0190.

### Resolution options

1. **Fix the 69 pre-existing failures** -- correct approach but significant scope (separate chore)
2. **Scope the `run-tests` hook** -- add `--ignore=tests/orchestrator` to the hook entry in `.pre-commit-config.yaml` so the hook only runs factory and unit tests; fix the 5 `test_test_design_verify.py` failures separately
3. **User commits with `SKIP=run-tests`** -- the guardrail hook blocks AI agents from using SKIP, but you can run `SKIP=run-tests git commit -m "test: add contract tests for context-lint (ST-0190)"` from the story worktree

Option 3 is fastest for immediate unblocking. The test files are already staged -- no edits needed.

## Dispatch ledger

Path: `.current-work/feature/agent-context/dispatch-ledger.yaml`

| Story   | Wave | Status     | Deps    |
| ------- | ---- | ---------- | ------- |
| ST-0190 | 1    | dispatched | none    |
| ST-0191 | 2    | pending    | ST-0190 |
| ST-0192 | 2    | pending    | ST-0191 |
| ST-0193 | 2    | pending    | ST-0190 |
| ST-0194 | 3    | pending    | ST-0193 |
| ST-0195 | 2    | pending    | ST-0193 |
| ST-0196 | 3    | pending    | ST-0195 |
| ST-0197 | 3    | pending    | ST-0192 |
| ST-0198 | 3    | pending    | ST-0192 |

## What the next session does

1. **Resolve the test commit blocker** for ST-0190 (see Resolution options above).
2. **Verify ST-0190 commit SHA** -- `factory/scripts/dispatch --ledger <ledger-path> verify-story ST-0190 --sha <final-sha>`.
3. **Run quality gates** -- `factory/scripts/crap-score` and `factory/scripts/dependency-check` on ST-0190 outputs.
4. **Merge ST-0190** -- `factory/scripts/dispatch --ledger <ledger-path> merge-story ST-0190` from the `feature/agent-context` worktree.
5. **Close Wave 1** -- `factory/scripts/dispatch --ledger <ledger-path> close-wave 1`.
6. **Execute Wave 2** -- two parallel serial chains:
   - Chain A: ST-0191 (sonnet) then ST-0192 (sonnet), sharing `factory/scripts/context-lint`
   - Chain B: ST-0193 (sonnet) then ST-0195 (sonnet), sharing `factory/INDEX.yaml`
7. **Execute Wave 3** -- four parallel stories: ST-0194 (sonnet), ST-0196 (opus), ST-0197 (haiku), ST-0198 (haiku).
8. **Record branch head and report results.**

## Key artifacts (do not duplicate)

| Artifact                       | Path                                                                                                                                                        |
| ------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Phase 4 implementation handoff | `docs/handoffs/handoff-agent-context-phase4-implementation-2026-09-04.md`                                                                                   |
| Dispatch ledger                | `.current-work/feature/agent-context/dispatch-ledger.yaml`                                                                                                  |
| ST-0190 handoff contract       | `.current-work/worktrees/feature/agent-context/.current-work/worktrees/story-ST-0190/.current-work/feature/agent-context/story/ST-0190/handoff-contract.md` |
| ST-0190 step manifest          | `.current-work/worktrees/feature/agent-context/.current-work/worktrees/story-ST-0190/.current-work/feature/agent-context/story/ST-0190/current-step.yml`    |
| Gherkin spec                   | `docs/spec/agent-context.feature`                                                                                                                           |
| Proposal (accepted)            | `docs/proposals/yaml-charter-lifecycle.md`                                                                                                                  |
| Testing charter                | `docs/charter/testing.yaml`                                                                                                                                 |

## Suggested skills

- The fresh session should read `factory/rulebooks/rules.md` first (MUST per CLAUDE.md).
- Adopt the implementation-agent dispatcher role (`.claude/agents/implementation-agent.md`).
- Developer-agent subagents (`.claude/agents/developer-agent.md`) are spawned per story.
- Use `spec-feedback` skill after each completed story.
- Use `crap-score` and `dependency-check` gate skills where quality-gates are declared.
- Use `handoff` skill at session end.
