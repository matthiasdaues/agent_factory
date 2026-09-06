# Handoff: Agent Context -- Phase 4 Dispatch Complete (Waves 1--3)

Date: 2026-09-04
Feature: agent-context (two-layer YAML routing with two-mode lifecycle)
Playbook: feature-addition, Phase 4
Role: implementation-agent (dispatcher)
Branch: `feature/agent-context`
Tip: `c7dba03e022a06e6745add376704852d13cb03b5`
Base: `dev` at `e1f78be92ce592ba55d09fd709e6b64eb70f4bc9`
Ahead of dev: 27 commits
Tests: 287 passing

## What was done

All 9 implementation stories (ST-0190 through ST-0198) dispatched across 3 waves, implemented, tested, and merged into `feature/agent-context`. The dispatch ledger at `.current-work/feature/agent-context/dispatch-ledger.yaml` records every story as `status: done` with merge SHAs.

### Wave summary

| Wave | Stories                                                           | Merge order |
| ---- | ----------------------------------------------------------------- | ----------- |
| 1    | ST-0190 (foundation: templates, context-lint, conventions, rules) | solo        |
| 2    | ST-0191 → ST-0192 (chain A: capture-context + format-detection)   | serial      |
| 2    | ST-0193 → ST-0195 (chain B: reading-guides + update-context)      | serial      |
| 3    | ST-0194 (brownfield onboarding mode for capture-context)          | parallel    |
| 3    | ST-0196 (mode transition logic for update-context)                | parallel    |
| 3    | ST-0197 (script/hook updates for format detection)                | parallel    |
| 3    | ST-0198 (agent/skill/playbook reference migration)                | parallel    |

### Key artifacts produced

- `factory/rulebooks/templates/context-*.yaml` — YAML templates for stack, workflow, governance, reading-guides
- `factory/rulebooks/conventions/agent-context-composition.md` — composition convention
- `factory/scripts/context-lint` — extended with FORMAT_CHAIN, detect_format(), resolve_testing_yaml(), CX-FORMAT
- `factory/skills/capture-context/SKILL.md` — v1.1.0 with Mode 2 brownfield onboarding
- `factory/skills/update-context/SKILL.md` — renamed from update-charter; mode-aware writes + transition logic
- `tests/factory/test_*.py` — 8 new/extended test modules, 12 fixture directories
- 6 agent files, ~10 skill SKILL.md files, 3 playbook files — updated from hardcoded `docs/charter/` to `docs/agent-context/`

## What was NOT done

- **ST-0199** (stakeholder grilling session): held per instruction — requires live stakeholder interview. This is the next step.
- **ST-0200** (depends on ST-0199): blocked until ST-0199 completes.
- **Feature branch not merged to dev** — that happens after all stories complete and pass reconciliation/QA.
- **pyyaml test dependency**: `test_mode_transition.py` imports `yaml` — requires `--with pyyaml` in the uv run invocation. Not a blocker (287 tests pass with it), but should be added to pyproject.toml dev dependencies.

## Git state on `dev`

The `dev` branch has uncommitted files from prior sessions (spec review, proposals, test files). These are unrelated to the agent-context feature and should not block resumption. See `git status` on dev for the full list.

## Known issues for future dispatches

### Worktree isolation mismatch

Developer-agents spawned with `isolation: "worktree"` get their own `.claude/worktrees/agent-*` worktree but cannot write to the dispatcher's `.current-work/worktrees/story-*` worktrees. Workarounds used in this run:

1. Complete work manually from the dispatcher session after the agent finishes analysis
2. Use forks (`subagent_type: "fork"`) without isolation for economy-tier mechanical work
3. Implement directly in the dispatcher session for standard/strong-tier stories

### Two-pass commit pattern

Pre-commit hooks (ruff, mdformat, index-lint) rewrite files on commit. Every commit requires: `git commit` → hooks modify → `git add -u` → `git commit` again. This is established procedure per feedback memory `deterministic-commit-after-hooks`.

### Premerge-check gates

- `--max-files` may need raising beyond default 20 for stories with many fixtures
- `crap-score` gate results must be written into the story worktree's `.current-work/`, not the main repo's

## Suggested skills for next session

- `run-step` — resume the feature-addition playbook at the appropriate phase
- `handoff` — read this document to pick up context
- `validate` — run lints across the feature branch
- `grilling` — for ST-0199 stakeholder interview when ready
- `scratchpad` — for session notes

## Dispatch ledger

`.current-work/feature/agent-context/dispatch-ledger.yaml` — authoritative record of all 9 stories, wave assignments, merge SHAs, and completion status.
