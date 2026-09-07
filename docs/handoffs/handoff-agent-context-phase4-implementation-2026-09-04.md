# Handoff: Agent Context -- Phase 4 Implementation (Waves 1--3)

Date: 2026-09-04
Feature: agent-context (two-layer YAML routing with two-mode lifecycle)
Playbook: feature-addition, Phase 4
Role: implementation-agent (dispatcher)
Branch: `dev`
Local tip: `4e78d3f34a41308146bfeb6031650e0f238379b8`
Upstream: `1915488d0167fc06e5bbbc44dcb49eb01476efa9`
Ahead: 5 commits

## What this session does

Launch the implementation-agent dispatcher for the agent-context feature, executing Waves 1 through 3. The dispatcher reads the backlog, schedules waves respecting dependency and file-overlap constraints, and spawns developer-agent subagents on feature branches.

**Explicitly excluded from this run:** ST-0199 (grilling session, requires live stakeholder) and ST-0200 (depends on ST-0199).

## Git state

- Current branch: `dev`
- HEAD: `4e78d3f34a41308146bfeb6031650e0f238379b8`
- Untracked: `docs/spec/traceability.json` (irrelevant to this feature)
- No uncommitted changes
- Invocation branch to create: `feature/agent-context` (cut from `dev`)

## Wave plan with file-overlap analysis

### Wave 1: ST-0190 (solo)

| Story   | Title                                                                    | Tier     | Size | Deps | Outputs                                                                                                                                                                                                                                                                                                                                                           |
| ------- | ------------------------------------------------------------------------ | -------- | ---- | ---- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| ST-0190 | Create YAML templates, codify convention, validate with core CX-\* codes | standard | L    | none | `factory/rulebooks/templates/context-stack.yaml`, `context-workflow.yaml`, `context-governance.yaml`, `context-reading-guides.yaml`, `factory/rulebooks/conventions/agent-context-composition.md`, `factory/rulebooks/rules.md`, `factory/scripts/context-lint`, `.pre-commit-config.yaml`, `tests/factory/test_context_lint.py`, `tests/fixtures/agent-context/` |

Foundation story. Must complete before any Wave 2 story launches.

### Wave 2: ST-0191, ST-0192, ST-0193, ST-0195

**File-overlap analysis yields two serial chains that run in parallel:**

| Chain | Stories          | Shared file                    | Order         |
| ----- | ---------------- | ------------------------------ | ------------- |
| A     | ST-0191, ST-0192 | `factory/scripts/context-lint` | ST-0191 first |
| B     | ST-0193, ST-0195 | `factory/INDEX.yaml`           | ST-0193 first |

Chains A and B are file-disjoint and dispatch in parallel. Within each chain, stories merge serially in the listed order.

| Story   | Title                                                                    | Tier     | Size | Chain | Quality gates                |
| ------- | ------------------------------------------------------------------------ | -------- | ---- | ----- | ---------------------------- |
| ST-0191 | Validate source pointers and reading-guide references (CX-SRC/GUIDE-REF) | standard | M    | A     | crap-score, dependency-check |
| ST-0192 | Detect context format, validate legacy charters, testing.yaml carve-out  | standard | L    | A     | crap-score, dependency-check |
| ST-0193 | Initialize greenfield agent context with capture-context --init          | standard | S    | B     | none (markdown prose)        |
| ST-0195 | Update agent-context fields and source pointers with update-context      | standard | M    | B     | none (markdown prose)        |

### Wave 3: ST-0194, ST-0196, ST-0197, ST-0198

**File-overlap analysis: all four stories are file-disjoint. Full parallel dispatch.**

| Story   | Title                                                                    | Tier     | Size | Deps    | Quality gates | Notes                                         |
| ------- | ------------------------------------------------------------------------ | -------- | ---- | ------- | ------------- | --------------------------------------------- |
| ST-0194 | Onboard brownfield documentation with capture-context --init --scan      | standard | XL   | ST-0193 | none          | Markdown prose skill definition               |
| ST-0196 | Transition agent context from primary to index mode                      | strong   | M    | ST-0195 | crap-score    | `risk_domains: [data_integrity]`, atomic flip |
| ST-0197 | Update factory scripts, hooks, and configuration for agent-context paths | economy  | M    | ST-0192 | none          | Path updates in bash/Python scripts           |
| ST-0198 | Update factory agents, skills, and playbooks to reference agent-context  | economy  | M    | ST-0192 | none          | Mechanical find-replace across ~25 md files   |

## Model selection

From `factory/config/model.conf` -- Claude Code has no explicit entries, so the dispatcher uses Claude Code's native model routing:

| Tier     | Model  | Stories                                              |
| -------- | ------ | ---------------------------------------------------- |
| economy  | haiku  | ST-0197, ST-0198                                     |
| standard | sonnet | ST-0190, ST-0191, ST-0192, ST-0193, ST-0194, ST-0195 |
| strong   | opus   | ST-0196                                              |

## Key artifacts (read these, do not duplicate)

| Artifact                              | Path                                                                 |
| ------------------------------------- | -------------------------------------------------------------------- |
| Proposal (accepted)                   | `docs/proposals/yaml-charter-lifecycle.md`                           |
| Gherkin spec                          | `docs/spec/agent-context.feature`                                    |
| QA strategy with contract-owner table | `docs/spec/agent-context-qa-strategy.md`                             |
| Gaps report                           | `docs/spec/agent-context-gaps.md`                                    |
| Architecture (DSL + ADRs 0013, 0014)  | `docs/arc42/architecture.dsl`                                        |
| EPICs                                 | `backlog/epics.md`                                                   |
| Prior handoff (Phase 3 to Phase 4)    | `docs/handoffs/handoff-agent-context-phase3-to-phase4-2026-09-04.md` |
| Testing charter                       | `docs/charter/testing.yaml`                                          |

## Critical constraints

1. **testing.yaml is lifecycle-exempt.** CX-PARSE only, no mode checks, no CX-FORMAT for its location.
2. **Reading-guide template is a NEW file.** Not a rename of any existing file.
3. **ST-0193, ST-0194, ST-0195 produce markdown skill definitions** (LLM-executed prose), not standalone scripts. `quality-gates` are empty for those stories.
4. **ST-0196 demands `tier: strong`** and `risk_domains: [data_integrity]`. The atomic mode flip across three files is the highest-risk change in this feature.
5. **Legacy markdown charter backward compatibility** must be preserved throughout. Format detection handles both locations.
6. **model.conf has no Claude Code entries.** The dispatcher maps tiers directly: `economy` to haiku, `standard` to sonnet, `strong` to opus.
7. **context-lint is a rename of charter-lint.** Preserve existing CH-\* validation logic for legacy fallback.

## Explicitly deferred (do NOT implement)

- Automated migration tool (`docs/charter/` to `docs/agent-context/` rename + file transform)
- Spec, arc42, and ADR document updates (reconciliation pass after implementation)
- Backlog story path updates (bulk find-replace, separate chore)
- SVG diagram regeneration
- Gigacron pilot migration
- ST-0199 (grilling session -- requires live stakeholder, separate session)
- ST-0200 (depends on ST-0199)

## Dispatch mechanics

- Invocation branch: `feature/agent-context` (cut from `dev`)
- Story branches: `story/ST-NNNN` (cut from `feature/agent-context`)
- Worktrees: `.current-work/worktrees/story-ST-NNNN/`
- Dispatch ledger: `.current-work/dispatch-ledger.yaml`
- Scripts: `factory/scripts/dispatch` (init, plan, prepare-wave, mark-dispatching, mark-dispatched, verify-story, merge-story, close-wave)
- Pre-spawn: `factory/scripts/verify-base`
- Pre-merge: `factory/scripts/premerge-check`
- Gate scripts: `factory/scripts/crap-score`, `factory/scripts/dependency-check`

## Suggested skills

- The fresh session should invoke `factory/rulebooks/rules.md` (read first, per CLAUDE.md MUST).
- The implementation-agent dispatcher (`.claude/agents/implementation-agent.md`) should be spawned or adopted.
- Developer-agent subagents (`.claude/agents/developer-agent.md`) are spawned per story.
- `spec-feedback` skill for each completed story (developer-agent workflow).
- `crap-score` and `dependency-check` gate skills where quality-gates are declared.

## What the next session does

1. Read `factory/rulebooks/rules.md`.
2. Create invocation branch `feature/agent-context` from `dev` with `factory/scripts/dispatch init`.
3. Dispatch Wave 1 (ST-0190), verify, gate-check, merge.
4. Dispatch Wave 2 (two parallel serial chains: A=[ST-0191, ST-0192], B=[ST-0193, ST-0195]), verify, gate-check, merge each.
5. Dispatch Wave 3 (four parallel stories: ST-0194, ST-0196, ST-0197, ST-0198), verify, gate-check, merge each.
6. Record branch head and report results.
7. Hand off to reconciliation-agent, then QA, with `--base <branch-root> --head <branch-head>`.
