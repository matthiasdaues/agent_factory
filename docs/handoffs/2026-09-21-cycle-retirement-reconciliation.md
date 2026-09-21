# Handoff: Cycle Retirement Reconciliation

**Date:** 2026-09-21
**Branch:** dev
**Local tip:** `986c5456f2c4969422ac4f9538e9539dc9e1e8e6`
**Uncommitted changes:** `docs/arc42/05_building_block_view.md`, `docs/arc42/architecture.dsl` (plus re-exported SVGs)
**Untracked:** `docs/findings/RECON-cycle-retirement.md`

## Current state

The documentation is badly out of sync with the code after the activity-graph-orchestration work (ST-0262 through ST-0278) retired two entire state-management layers. A reconciliation agent produced a 145-finding inventory at `docs/findings/RECON-cycle-retirement.md`. That inventory understates the problem because it treated the FSM/phase harness as active. **The user confirmed both layers are dead.**

### What is dead

Everything below has no active consumers. Some scripts and files remain on disk but are dead code.

| Mechanism                                                                                                      | Artifacts on disk                                                                                                                                        |
| -------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Cycle model (select, retry, routes, trusted validators, delegation grants, attempt limits)                     | `packages/factory/scripts/cycle` was already deleted; `packages/factory/engine/models/delivery.yaml` is orphaned                                         |
| FSM / phase harness (phase advance/retry, transition-lint, entry conditions, gate conditions, playbook marker) | `packages/factory/scripts/phase`, `packages/factory/scripts/transition-lint`, `packages/factory/playbooks/*.fsm.yml`, `.current-work/playbook-state.yml` |
| Orchestrator CLI                                                                                               | `packages/orchestrator/` retired in ST-0276; `packages/factory/scripts/run-playbook` deleted this session                                                |
| Cycle state files, cycle schemas, old session bindings path                                                    | `.current-work/cycles/`, `.current-work/session-bindings/`                                                                                               |

### What is active

| Mechanism                                | Key files                                                                                                                                             |
| ---------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| Precondition-based eligibility           | `packages/factory/scripts/intent` (select, assess), `packages/factory/engine/eligibility.py`, `readiness.py`, `recommendations.py`, `agent_loader.py` |
| Workstream state v2 (immutable identity) | `packages/factory/engine/workstream.py`, stored under `.agent-factory/workstreams/`                                                                   |
| Session binding v2                       | `packages/factory/engine/session_binding.py`, stored under `.agent-factory/workstreams/sessions/`                                                     |
| Fence runner                             | `packages/factory/engine/fence.py`                                                                                                                    |
| All linters except transition-lint       | spec-lint, arch-lint, backlog-lint, concern-lint, matrix-lint, statemachine-lint, etc.                                                                |
| Dispatch                                 | `packages/factory/scripts/dispatch` with ledger                                                                                                       |
| Usage capture                            | All adapters (Claude, Copilot, Codex, Pi)                                                                                                             |
| Distribution                             | init-factory, update-factory, remove-factory                                                                                                          |

## What was done this session

1. **Fixed arch-lint failures** — removed `cycle select`/`cycle retry` from chapter 5 component table and interfaces summary.
2. **Fixed concern-lint failures** — moved "Factory source and packaging" heading from "Always (cross-cutting)" to "Technical concerns" in `docs/agent-context.md`.
3. **Fixed link-check failure** — corrected broken link in `docs/proposals/opencode-cli-integration.md`.
4. **Removed stale README content** — dropped FSM reference from test execution, removed "Automated playbook execution" section, deleted `packages/factory/scripts/run-playbook`.
5. **Updated DSL and chapter 5** — rewrote State Adapter container description and component rows for `phase` and `run-step` (partial — these edits assumed FSM was active; they need further revision now that FSM is also dead).
6. **Ran reconciliation agent** — produced `docs/findings/RECON-cycle-retirement.md` with 145 findings.

## What remains

### Uncommitted edits to review

The changes to `docs/arc42/05_building_block_view.md` and `docs/arc42/architecture.dsl` were made under the assumption that the FSM/phase harness was active. Now that the user confirmed it is also dead, these edits need further revision before committing. Specifically:

- The `phase` component row should be removed or marked as dead, not described as active.
- The `run-step skill` description still references "run-state marker and the playbook FSM."
- The State Adapter container itself may need restructuring or removal.

### Full reconciliation scope

The finding inventory at `docs/findings/RECON-cycle-retirement.md` covers 145 stale references but needs extending to include FSM/phase/transition-lint references it treated as active. Key additions:

- **Factory guide** `packages/factory/docs/factory-guide.md` lines 499-517: "Playbook phase gates" section is entirely dead.
- **Factory guide** lines 506-511: `transition-lint`, `phase advance`, `playbook-state.yml` components all dead.
- **Glossary** `docs/arc42/12_glossary.md`: FSM, Phase, Marker, Entry Condition, Gate Condition entries — remove "(Legacy)" labels AND the entries themselves (don't rehabilitate them; they're dead).
- **All playbooks**: `orchestrator run-phase` blocks (already in inventory) PLUS any references to `phase advance`, `transition-lint`, `.fsm.yml`, entry conditions.
- **architecture.dsl**: `phaseAdvance` and `transitionLint` components need removal or reclassification.
- **Chapter 8** `docs/arc42/08_crosscutting_concepts.md`: transition-lint row in validation table, gate condition references.
- **Dead code on disk**: `packages/factory/scripts/phase`, `packages/factory/scripts/transition-lint`, `packages/factory/playbooks/greenfield-development.fsm.yml`, `packages/factory/playbooks/bug-fix.fsm.yml`, `packages/factory/engine/models/delivery.yaml`.

### User guidance on doc style

- **Do not mention history.** Don't write "was superseded by" or "replaced X." Just describe what is current.
- Follow the memory rule at `feedback_no-pretense-in-prose.md`.

## Suggested skills

- **`reconcile-spec`** — the reconciliation agent's primary skill. Invoke to extend the finding inventory with the FSM/phase scope, then remediate file by file.
- **`validate`** — run after remediation to confirm all lints pass.
- **`commit`** — use for the final commit after remediation is approved.
- **`handoff`** — write a follow-up handoff if the work spans another session.

## References

- Finding inventory: `docs/findings/RECON-cycle-retirement.md`
- Retirement commits: ST-0276 (`6fa8b68`), ST-0277 (`2a28ceb`), ST-0262–ST-0278 merge (`53ecb8c`)
- Memory entries: `feedback_review-before-remediation.md`, `feedback_no-pretense-in-prose.md`, `feedback_edit-source-not-installed.md`
