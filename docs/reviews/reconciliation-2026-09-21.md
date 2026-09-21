# Reconciliation Report — 2026-09-21

Repeat pass against [reconciliation-2026-09-20](reconciliation-2026-09-20.md) (52 findings).
Covers commits 96ceb69..HEAD.

## Prior findings verification

### Resolved (46/52)

| Domain | IDs              | Notes                                                                                                               |
| ------ | ---------------- | ------------------------------------------------------------------------------------------------------------------- |
| DOC    | 001–012          | All 12 resolved in tracked source (`packages/factory/`). Installed copy stale — `init-factory --update .` syncs it. |
| SPEC   | 001–012, 014–016 | 15 resolved.                                                                                                        |
| ARCH   | 001–013          | All 13 resolved. Cycle components removed, intent added, runtime views rewritten.                                   |
| META   | 001–009          | 9 resolved. Agent def paths, glossary entries, config paths all fixed in source.                                    |

### Acknowledged (1/52)

| ID        | Notes                                                                                                 |
| --------- | ----------------------------------------------------------------------------------------------------- |
| SPEC-0013 | `.agent-factory/checks/` does not exist yet — spec ahead of code by design (ST-0275/ST-0266 pending). |

### Closed as resolved this pass (5/52)

| ID         | Resolution                                                                                                                                      |
| ---------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| SPEC-0017  | **Fixed** — scope-map.md:82 changed "retired" to "dormant" to match feature file and stakeholder decision.                                      |
| SPEC-0008  | **Fixed** — newcomer-onboarding.feature:11 `@`-ref updated from redirect stub to canonical path `.agent-factory/factory/docs/factory-guide.md`. |
| META-0010  | **Deferred** — `project-context.json` linters array empty; resolved by `init-factory --update .` (user-owned).                                  |
| RECON-0019 | **Resolved** — FSM files already deleted from tracked source; only gitignored copies remain.                                                    |
| RECON-0023 | **Fixed** — 14 test-gate-presence Rules added to scope-map (see N-003 below).                                                                   |

### Carried (1/52)

| ID         | Notes                                                                                |
| ---------- | ------------------------------------------------------------------------------------ |
| RECON-0018 | Pre-commit-config.yaml omits changed-only test hook. Source unchanged; low severity. |

## New findings addressed this pass

| ID    | Sev  | Action taken                                                                                                                                                                         |
| ----- | ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| N-001 | HIGH | **Fixed** — scope-map.md:82 "retired" → "dormant".                                                                                                                                   |
| N-002 | LOW  | **Fixed** — scope-map.md:28 "from code and tests" → "from forensic evidence" to match feature file.                                                                                  |
| N-003 | HIGH | **Fixed** — 14 test-gate-presence Rules added to scope-map as `implemented` with Feature Links from `@`-refs.                                                                        |
| N-004 | MED  | **Fixed** — 3 engine modules added to architecture.dsl: Fence Runner (validator), Session Binding Manager (eligibility engine), Proposal Validator (validator). Relationships added. |
| N-005 | LOW  | **Fixed** — 4 orphaned SVGs deleted: StateAdapterComponents pair (cycle artifact), TestGatePresence pair (no DSL view, no live doc reference).                                       |
| N-006 | MED  | **Fixed** — 17 `@`-references backfilled: 4 in agent-context.feature, 7 in local-usage-processing-and-analysis.feature, 2 in activity-graph-orchestration.feature.                   |
| N-007 | MED  | **Deferred** — installed copy `.agent-factory/factory/` out of sync with source. User will run `init-factory --update .` manually.                                                   |

## Scope

### Code paths compared

- `packages/factory/engine/` (eligibility, readiness, recommendations, fence, session_binding, workstream, validators/)
- `packages/factory/scripts/` (intent, init-factory, update-factory, remove-factory, and gates)
- `packages/usage/src/usage/` (input_snapshot, accounting, preflight, adapters, parquet_exporter, explorer, registry)

### Spec files compared

- `docs/spec/scope-map.md`
- `docs/spec/activity-graph-orchestration.feature`
- `docs/spec/agent-context.feature`
- `docs/spec/local-usage-processing-and-analysis.feature`
- `docs/spec/newcomer-onboarding.feature`
- `docs/spec/test-gate-presence.feature`
- `docs/spec/test-design.feature`

### Architecture files compared

- `docs/arc42/architecture.dsl`
- `docs/arc42/06_runtime_view.md`
- `docs/arc42/08_crosscutting_concepts.md`
- `docs/arc42/09_architecture_decisions.md`

## Files updated

| File                                                    | Change                                                            |
| ------------------------------------------------------- | ----------------------------------------------------------------- |
| `docs/spec/scope-map.md`                                | N-001 (dormant), N-002 (forensic evidence), N-003 (14 rows added) |
| `docs/arc42/architecture.dsl`                           | N-004 (3 components + relationships)                              |
| `docs/spec/agent-context.feature`                       | N-006 (4 `@`-refs)                                                |
| `docs/spec/local-usage-processing-and-analysis.feature` | N-006 (7 `@`-refs)                                                |
| `docs/spec/activity-graph-orchestration.feature`        | N-006 (2 `@`-refs)                                                |
| `docs/spec/newcomer-onboarding.feature`                 | SPEC-0008 (`@`-ref canonical path)                                |
| `docs/arc42/05_building_block_view.md`                  | N-004 (3 components added to tables)                              |
| `docs/assets/images/StateAdapterComponents.svg`         | N-005 (deleted)                                                   |
| `docs/assets/images/StateAdapterComponents-key.svg`     | N-005 (deleted)                                                   |
| `docs/assets/images/TestGatePresence.svg`               | N-005 (deleted)                                                   |
| `docs/assets/images/TestGatePresence-key.svg`           | N-005 (deleted)                                                   |

## Code defects filed

None. All discrepancies were spec-stale or undocumented — no code defects found.

## Linter results

- `arch-lint`: 0 errors, 1 warning (ARCH-PARSE port extraction — pre-existing, not actionable)
- `mdformat`: all changed markdown files formatted

## Severity summary

| Severity | Prior open | New | Fixed this pass | Remaining               |
| -------- | ---------- | --- | --------------- | ----------------------- |
| HIGH     | 1          | 2   | 3               | 0                       |
| MEDIUM   | 1          | 3   | 3               | 1 (N-007, user-owned)   |
| LOW      | 3          | 2   | 4               | 1 (RECON-0018, carried) |
