# Reconciliation Report — 2026-09-20

Code is truth. 52 findings across 4 domains.

## Stakeholder decisions

1. **Orchestrator** (SPEC-0015/0017): Cancelled for now. Remove retirement scenario from spec. `packages/orchestrator/` stays on disk but is not active. Will be revisited later.
2. **Gate result persistence** (SPEC-0013): Not a discrepancy. Decided in the [activity-graph-orchestration proposal](../proposals/activity-graph-orchestration.md) (lines 826–833), specified, traced in the gaps report, and cut into backlog stories ST-0275 (layout consolidation, `pending`) and ST-0266 (fence runner, `pending`, blocked on ST-0262). The spec is correct; the code hasn't caught up. Leave the spec scenario as-is.
3. **`cycle` script** (ARCH-0006): Orphaned, not a design decision. Engine modules deleted in commit 578ae36 (ST-0263, 2026-09-18). Replacement `intent` built in commit 965db12 (ST-0264, same day). No story covered deleting or rewriting the dead `cycle` script. Fix: delete `packages/factory/scripts/cycle`.
4. **Phantom DSL components** (ARCH-0001/0002/0003/0004): Cycle model is retired, superseded by the activity graph. Remove Cycle Model Loader, Route Recommender, Delegation Evaluator, Retry Evaluator from DSL. All retired with the cycle model in ST-0263.

## Systemic patterns

Three root causes explain 80% of findings:

### P1: `.agent-factory/factory/` migration not propagated (23 findings)

The install path moved from `factory/` to `.agent-factory/factory/`, but docs, spec, and some agent definitions still reference the old path. Affects factory-guide.md (64 occurrences), README.md (13), scope-map (2), PRD (3), newcomer-tour SKILL.md (2), agent definitions (2), ADR index (1), pre-commit guard example (1).

### P2: Session menu ABCD → HKPO not propagated (7 findings)

The session menu changed from A/B/C/D to H/K/P/O with different labels and structure. Affects factory-guide.md, README.md, newcomer-onboarding.feature (4 scenarios), guided-tour SKILL.md, newcomer-tour SKILL.md description.

### P3: Engine rewrite not reflected in architecture (13 findings)

The engine was rewritten from cycle/route vocabulary to precondition-based agent eligibility. Four DSL components are phantom (code deleted/never existed), the `cycle` script is broken (4/5 imports fail), the working entry point (`intent`) is absent from architecture, and two runtime view sequences describe non-functional flows.

______________________________________________________________________

## Domain 1: Documentation (12 findings)

| ID      | File                   | What                                                                            | Sev  |
| ------- | ---------------------- | ------------------------------------------------------------------------------- | ---- |
| DOC-001 | factory-guide.md       | 64× stale `factory/` paths → `.agent-factory/factory/`                          | HIGH |
| DOC-002 | factory-guide.md       | ABCD menu → actual HKPO                                                         | HIGH |
| DOC-003 | factory-guide.md       | Directory tree missing 5 entries (CHANGELOG, contracts, engine, tests, VERSION) | MED  |
| DOC-004 | factory-guide.md       | Config paths `config/project.json` → `.agent-factory/config/project.json`       | MED  |
| DOC-005 | factory-guide.md       | Manifest filename `factory-install.json` → `install.json`                       | MED  |
| DOC-006 | factory-guide.md       | Pre-commit guard `[ -d factory ]` → `[ -d .agent-factory ]`                     | HIGH |
| DOC-007 | README.md              | 13× stale `factory/` paths                                                      | HIGH |
| DOC-008 | README.md              | L85 vs L155 manifest name contradiction                                         | MED  |
| DOC-009 | README.md              | ABCD → HKPO                                                                     | HIGH |
| DOC-010 | README.md              | Config paths need `.agent-factory/` prefix                                      | MED  |
| DOC-011 | newcomer-tour SKILL.md | Option A → option H                                                             | LOW  |
| DOC-012 | newcomer-tour SKILL.md | Config paths need `.agent-factory/` prefix                                      | LOW  |

## Domain 2: Specification (17 findings)

| ID        | File                              | What                                                                                      | Sev  | Decision                                                           |
| --------- | --------------------------------- | ----------------------------------------------------------------------------------------- | ---- | ------------------------------------------------------------------ |
| SPEC-0001 | scope-map.md:20                   | Feature link `factory/scripts/init-factory` → `packages/factory/scripts/init-factory`     | HIGH | Fix                                                                |
| SPEC-0002 | scope-map.md:21                   | Phantom link: `run-tests` script doesn't exist                                            | HIGH | Fix                                                                |
| SPEC-0003 | scope-map.md:22                   | Path `.agent-factory/factory/pi/extensions/run-agent/` → `config/extensions/run-agent.ts` | HIGH | Fix                                                                |
| SPEC-0004 | scope-map.md:28                   | Link to redirect stub `beginner-intro.md` → factory-guide.md                              | MED  | Fix                                                                |
| SPEC-0005 | scope-map.md:31                   | Phantom agents: `chat-agent.md`, `kit-manager.md` never created                           | HIGH | Fix                                                                |
| SPEC-0006 | scope-map.md:65                   | Same as SPEC-0001                                                                         | HIGH | Fix                                                                |
| SPEC-0007 | newcomer-onboarding.feature:15    | Option A → lane H                                                                         | HIGH | Fix                                                                |
| SPEC-0008 | newcomer-onboarding.feature:17    | `beginner-intro.md` → factory-guide.md via newcomer-tour skill                            | HIGH | Fix                                                                |
| SPEC-0009 | newcomer-onboarding.feature:60-66 | Full ABCD menu scenario → rewrite for HKPO                                                | HIGH | Fix                                                                |
| SPEC-0010 | newcomer-onboarding.feature:76-77 | Phantom `@` references: chat-agent.md, kit-manager.md                                     | HIGH | Fix                                                                |
| SPEC-0011 | newcomer-onboarding.feature:80-94 | Scenarios for phantom chat-agent, kit-manager → rewrite for VIRGIL                        | HIGH | Fix                                                                |
| SPEC-0012 | activity-graph.feature:483        | `testing.yaml` path wrong (`.agent-factory/config/` → `docs/`)                            | MED  | Fix                                                                |
| SPEC-0013 | activity-graph.feature:496-499    | `.agent-factory/checks/` doesn't exist yet; pending ST-0275/ST-0266                       | MED  | Not a discrepancy — spec is ahead of code                          |
| SPEC-0014 | activity-graph.feature:507        | DuckDB path `.agent-factory/usage/store.duckdb` → `.agent-factory/usage.duckdb`           | MED  | Fix                                                                |
| SPEC-0015 | activity-graph.feature:524-527    | Orchestrator retirement specified but still exists                                        | HIGH | Cancelled — remove retirement scenario, orchestrator stays dormant |
| SPEC-0016 | prd.md:71,94,110                  | Bare `config/model.conf` × 3 → `.agent-factory/config/model.conf`                         | MED  | Fix                                                                |
| SPEC-0017 | scope-map + feature               | Orchestrator retirement decision                                                          | HIGH | Cancelled — see SPEC-0015                                          |

## Domain 3: Architecture (13 findings)

| ID        | File                       | What                                                | Sev  | Decision                                    |
| --------- | -------------------------- | --------------------------------------------------- | ---- | ------------------------------------------- |
| ARCH-0001 | architecture.dsl:25        | Phantom: Cycle Model Loader (code deleted)          | HIGH | Remove — retired with cycle model           |
| ARCH-0002 | architecture.dsl:27        | Phantom: Route Recommender (no logic exists)        | HIGH | Remove — retired with cycle model           |
| ARCH-0003 | architecture.dsl:28        | Phantom: Delegation Evaluator (never implemented)   | HIGH | Remove — retired with cycle model           |
| ARCH-0004 | architecture.dsl:29        | Phantom: Retry Evaluator (never implemented)        | HIGH | Remove — retired with cycle model           |
| ARCH-0005 | architecture.dsl:26        | Readiness Evaluator API mismatch                    | HIGH | Fix to match `derive_readiness()`           |
| ARCH-0006 | scripts/cycle              | Broken script: 4/5 imports fail                     | HIGH | Rewrite for intent (missed rewrite)         |
| ARCH-0007 | architecture.dsl           | `intent` script absent from architecture            | HIGH | Add to DSL                                  |
| ARCH-0008 | 09_arch_decisions.md:42    | Stale path `docs/charter/testing.yaml`              | MED  | Fix                                         |
| ARCH-0009 | 09_arch_decisions.md:94    | Stale `factory/` path                               | MED  | Fix                                         |
| ARCH-0010 | architecture.dsl:24        | Cycle Engine container description overstates       | HIGH | Rewrite for actual capabilities             |
| ARCH-0011 | 06_runtime_view.md:19-43   | §6.2 describes non-functional `cycle select` flow   | HIGH | Rewrite for intent                          |
| ARCH-0012 | 06_runtime_view.md:44-69   | §6.2.2 delegated transition uses phantom components | HIGH | Remove — retired with cycle model           |
| ARCH-0013 | 08_crosscutting.md:233-268 | §8.13 describes unimplemented orchestration model   | HIGH | Rewrite — separate implemented from retired |

## Domain 4: Meta-artifacts (10 findings)

| ID        | File                       | What                                                                 | Sev  |
| --------- | -------------------------- | -------------------------------------------------------------------- | ---- |
| META-0001 | 4 agent defs               | Reference `docs/arc42/CONTEXT.md` → actual `docs/CONTEXT.md`         | HIGH |
| META-0002 | 2 agent defs               | Reference `config/model.conf` → `.agent-factory/config/model.conf`   | HIGH |
| META-0003 | factory-guide.md           | 72 lines with stale `factory/` paths (overlaps DOC-001)              | HIGH |
| META-0004 | factory-guide.md           | ABCD menu (overlaps DOC-002)                                         | HIGH |
| META-0005 | guided-tour SKILL.md:27-30 | Stale ABCD menu → HKPO                                               | MED  |
| META-0006 | README.md                  | 22 stale `factory/` paths (overlaps DOC-007)                         | HIGH |
| META-0007 | 12_glossary.md             | `mutation-analysis` → actual skill is `mutation-testing`             | LOW  |
| META-0008 | 12_glossary.md             | `docs/spec/use_cases/` → archived to `docs/~archive/spec/use_cases/` | LOW  |
| META-0009 | agent-context.md           | Duplicate concern: same Read paths under cross-cutting and technical | MED  |
| META-0010 | project-context.json       | Reports no linters, but ruff config exists in pyproject.toml         | LOW  |

______________________________________________________________________

## Severity summary

| Severity | Count |
| -------- | ----- |
| HIGH     | 33    |
| MEDIUM   | 14    |
| LOW      | 5     |

## Deduplication notes

META-0003/0004/0006 overlap with DOC-001/002/007 (same files, same findings from different angles). Net unique findings after dedup: ~48.
