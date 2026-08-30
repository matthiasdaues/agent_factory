# Handoff: arc42 Projection Gating — Complete

**Date:** 2026-08-29
**From:** Session 01WdeNLa5RfUtkcWNL5zYNkr
**Status:** Merged to dev

## What shipped

Arc42 projection gating: a workspace-level `arc42.projected` property in
Structurizr DSL files that controls arch-lint behavior for projects that
have a DSL model but no projected arc42 prose chapters yet.

| Story   | Title                                         | Status |
| ------- | --------------------------------------------- | ------ |
| ST-0164 | Parser + gating logic in arch-lint            | done   |
| ST-0165 | Backfill existing DSL files                   | done   |
| ST-0166 | Agent + scaffold templates                    | done   |
| ST-0167 | Test coverage (10 tests in test_arch_lint.py) | done   |
| ST-0168 | Rules and documentation reconciliation        | done   |

## Key commit

`58ffeee` — `feat: arc42 projection gating — gate arch-lint on workspace property`
Merged to dev via fast-forward from `impl/arc42-projected-gating`.

## Files changed (24)

- `factory/scripts/arch-lint` — `dsl_workspace_property()` parser + gating logic
- `tests/factory/test_arch_lint.py` — 10 new tests (parser + behavior)
- `docs/arc42/architecture.dsl` — `"arc42.projected" "true"`
- `orchestrator/docs/architecture.dsl` — `"arc42.projected" "true"`
- `factory/fixtures/.../architecture.dsl` — `"arc42.projected" "false"`
- `factory/agents/architecture-agent.md` — provisioning + flip semantics
- `factory/skills/scaffold-arc42/STRUCTURIZR.md` — default property in template
- `factory/skills/scaffold-arc42/SKILL.md` — Step 2 note
- `factory/playbooks/brownfield-onboarding.md` — Step 2.2 note
- `factory/playbooks/greenfield-development.md` — Step 2.1 note
- `factory/rulebooks/rules.md` — MUST rule for provisioning
- `factory/skills/maintain-architecture/SKILL.md` — flip-on-projection note
- `backlog/ST-0163.md` — tier fix (simple → economy, pre-existing lint error)
- `backlog/ST-0164.md` through `ST-0168.md` — story files
- SVGs and INDEX.yaml — regenerated

## Test results

1005 passed, 0 failed (including 10 new arch-lint tests).

## Known issue surfaced

`arch-lint` `check_staleness()` line ~269 computes `docs_root = dsl_path.parent.parent`
assuming `<root>/arc42/architecture.dsl` layout. Breaks for flat layouts like
`orchestrator/docs/architecture.dsl`. Not yet filed as a defect story.

## Cleanup remaining

- Branches `impl/st-0164-st-0165-st-0166-and-2-more`, `impl/arc42-projected-gating`,
  `story/ST-0164` through `story/ST-0168`, `story/ST-0159` (orphaned from collision):
  all worktrees removed, branches can be deleted with `git branch -D`.
- Old dispatch handoff `handoff-arc42-projection-gating-dispatch-2026-08-29.md`
  is now superseded by this document.
