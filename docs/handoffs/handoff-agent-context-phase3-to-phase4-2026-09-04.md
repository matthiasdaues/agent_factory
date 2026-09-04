# Handoff: Agent Context -- Phase 3 (Planning) to Phase 4 (Implementation)

Date: 2026-09-04
Feature: agent-context (two-layer YAML routing with two-mode lifecycle)
Playbook: feature-addition
Branch: `dev`
Local tip: `a1b4f176df80dad6ba88686d3a74574169736147`
Upstream: `1915488d0167fc06e5bbbc44dcb49eb01476efa9`
Ahead: 1 commit

## What was done

Phase 3 (planning) of the feature-addition playbook is complete. The planning-agent produced:

- `backlog/epics.md` -- 5 EPICs covering the full agent-context scope
- `backlog/ST-0190.md` through `backlog/ST-0200.md` -- 11 stories, all `status: pending`
- Proposal estimate reforecast at `docs/proposals/yaml-charter-lifecycle.md` (confidence raised from low to medium, basis updated to story-level decomposition)

All artifacts committed to `dev` at `a1b4f17`. `backlog-lint` reports 0 errors.

## Backlog summary

| Story   | Title                                                                    | EPIC | Priority    | Tier     | Size | Deps                      |
| ------- | ------------------------------------------------------------------------ | ---- | ----------- | -------- | ---- | ------------------------- |
| ST-0190 | Create YAML templates, codify convention, validate with core CX-\* codes | 1    | must-have   | standard | L    | --                        |
| ST-0191 | Validate source pointers and reading-guide references (CX-SRC/GUIDE-REF) | 1    | must-have   | standard | M    | ST-0190                   |
| ST-0192 | Detect context format, validate legacy charters, testing.yaml carve-out  | 1    | must-have   | standard | L    | ST-0190                   |
| ST-0193 | Initialize greenfield agent context with capture-context --init          | 2    | must-have   | standard | S    | ST-0190                   |
| ST-0194 | Onboard brownfield documentation with capture-context --init --scan      | 2    | must-have   | standard | XL   | ST-0193                   |
| ST-0195 | Update agent-context fields and source pointers with update-context      | 3    | must-have   | standard | M    | ST-0190                   |
| ST-0196 | Transition agent context from primary to index mode                      | 3    | must-have   | strong   | M    | ST-0195                   |
| ST-0197 | Update factory scripts, hooks, and configuration for agent-context paths | 4    | must-have   | economy  | M    | ST-0192                   |
| ST-0198 | Update factory agents, skills, and playbooks to reference agent-context  | 4    | should-have | economy  | M    | ST-0192                   |
| ST-0199 | Grill stakeholder to shape the agent-context user interface              | 5    | must-have   | strong   | S    | ST-0190, ST-0193, ST-0195 |
| ST-0200 | Write agent-context guidance in factory documentation                    | 5    | should-have | standard | S    | ST-0199                   |

### Wave structure (dependency-derived)

- Wave 1: ST-0190
- Wave 2: ST-0191, ST-0192, ST-0193, ST-0195 (all depend only on ST-0190)
- Wave 3: ST-0194, ST-0196, ST-0197, ST-0198, ST-0199
- Wave 4: ST-0200

## Key artifacts (do not duplicate -- read these)

| Artifact                              | Path                                                                 |
| ------------------------------------- | -------------------------------------------------------------------- |
| Proposal (accepted)                   | `docs/proposals/yaml-charter-lifecycle.md`                           |
| Gherkin spec                          | `docs/spec/agent-context.feature`                                    |
| Gaps report                           | `docs/spec/agent-context-gaps.md`                                    |
| QA strategy with contract-owner table | `docs/spec/agent-context-qa-strategy.md`                             |
| Architecture (DSL + ADRs 0013, 0014)  | `docs/arc42/architecture.dsl`                                        |
| Prior handoff (Phase 2 to Phase 3)    | `docs/handoffs/handoff-agent-context-phase2-to-phase3-2026-09-03.md` |
| EPICs                                 | `backlog/epics.md`                                                   |

## Explicitly deferred (do NOT implement)

- Automated migration tool (`docs/charter/` to `docs/agent-context/` rename + file transform)
- Spec, arc42, and ADR document updates (reconciliation pass after implementation)
- Backlog story path updates (bulk find-replace, separate chore)
- SVG diagram regeneration
- Gigacron pilot migration

## Constraints for the implementing session

- `testing.yaml` is lifecycle-exempt -- CX-PARSE only, no mode checks, no CX-FORMAT for its location.
- The reading-guide template is a new file, not a rename of any existing file.
- Stories ST-0193, ST-0194, ST-0195 produce markdown skill definitions (LLM-executed prose), not standalone scripts. quality-gates are empty for those.
- ST-0199 requires a live grilling session with the stakeholder -- cannot be parallelized with code stories.
- ST-0196 has `risk_domains: [data_integrity]` and `tier: strong` -- the atomic mode flip across three files demands the strongest model.

## Suggested skills

- `run-step` -- derive the next action from the playbook FSM; Phase 4 entry point.
- The implementation-agent dispatcher should read the wave structure above and schedule accordingly. ST-0190 is the sole wave-1 story; wave-2 stories are parallelizable (file-disjoint). ST-0199 (grilling) blocks on stakeholder availability and should be scheduled independently of code waves.

## What the next session does

Launch the implementation-agent for the agent-context feature. The dispatcher reads `backlog/epics.md` and the individual story files, schedules waves respecting dependency and file-overlap constraints, and spawns developer-agent subagents on feature branches per the feature-addition playbook.
