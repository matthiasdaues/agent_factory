# Handoff: Agent Context — Phase 2 (Architecture) to Phase 2.2 (Architecture Review)

**Date:** 2026-09-03\
**From:** Architecture phase (architecture-agent)\
**To:** Architecture review (architecture-review-agent)\
**Playbook:** [feature-addition.md](../../factory/playbooks/feature-addition.md)\
**Proposal:** [yaml-charter-lifecycle.md](../proposals/yaml-charter-lifecycle.md)

## Current State

**Branch:** `dev`\
**Local tip:** `43ad983c68ae901d455d134e4c2bf5626917dd9b`\
**Upstream tip (`agent_factory/dev`):** `a8762bce6839c54497d57fc87a41696e550c0066`\
**Ahead:** 7 commits\
**Behind:** 0 commits\
**Working tree:** clean (one untracked generated file: `docs/spec/traceability.json`)

### Commits in this phase (oldest first)

| SHA (display) | Description                                                             |
| ------------- | ----------------------------------------------------------------------- |
| `43ad983`     | Architecture update for agent-context feature -- DSL, ADRs, arc42 prose |

### Phase 2.1 gate result

- `factory/scripts/validate` -- pass (0 errors)
- `factory/scripts/structurizr validate` -- pass (warnings about EOL theme only)
- Pre-commit hooks -- all pass (mdformat, link-check, mermaid-lint, arch-lint)
- Open `ATAM-*` findings -- none (no review yet)

## What was produced

| Artifact                                          | Path                                                                                                       |
| ------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| Updated architecture.dsl (context-lint component) | `docs/arc42/architecture.dsl`                                                                              |
| ADR-0013: YAML replaces markdown charter          | `docs/adr/0013-yaml-agent-context-replaces-markdown-charter.md`                                            |
| ADR-0014: Two-layer routing, two-mode lifecycle   | `docs/adr/0014-two-layer-routing-with-two-mode-lifecycle.md`                                               |
| Updated building block view (ch. 5)               | `docs/arc42/05_building_block_view.md`                                                                     |
| Updated runtime view (ch. 6)                      | `docs/arc42/06_runtime_view.md`                                                                            |
| Updated crosscutting concepts (ch. 8)             | `docs/arc42/08_crosscutting_concepts.md`                                                                   |
| Updated ADR index (ch. 9)                         | `docs/arc42/09_architecture_decisions.md`                                                                  |
| Re-exported SVG diagrams                          | `docs/assets/images/{Containers,SystemContext,ValidationComponents,SemanticGateLoop,TestGatePresence}.svg` |

### DSL changes

- Added `contextLint` component to the Validator container with description covering CX-\* codes, format detection fallback to CH-\* codes for legacy markdown
- Updated Validator container description: "charter-declared" to "project-declared" and "agent-context structure"
- Updated `blockDangerousGit` description to mention format-detected testing.yaml
- Added relationships: `cliAgent -> contextLint`, `git -> contextLint`

### ADR decisions

- **ADR-0013** (evaluation: pugh-matrix): YAML vs. markdown vs. JSON for project context files. YAML dominates (+10 weighted total vs. baseline 0 and JSON +4). Format detection provides backward compatibility.
- **ADR-0014** (evaluation: none): Two-layer routing (reading guide over index files) and two-mode lifecycle (primary to index). No genuine alternatives -- the designs resolve concrete failures from the single-layer predecessor and the greenfield-to-mature constraint.

### Arc42 prose changes

- **Chapter 5**: New section 5.2.5 (agent context validation), context-lint in interfaces table, updated 5.2.1 for format-detection references
- **Chapter 6**: New section 6.5 (agent-context mode transition) with two Mermaid sequences (6.5.1: mode transition via update-context, 6.5.2: context-lint validates mode compliance)
- **Chapter 8**: New section 8.11 (agent context as cross-cutting concern), updated 8.3 title and description for format detection
- **Chapter 9**: ADR index rows for 0013 and 0014, Key Decisions summary paragraph

### Incidental fixes

- Fixed pre-existing broken links to archived UC files in chapters 5 and 6 (`../spec/use_cases/` to `../~archive/spec/use_cases/`)

## What the architecture-review-agent should do

1. Review the DSL changes for completeness and consistency with Phase 1 artifacts.
2. Review ADR-0013 and ADR-0014 for correctness, completeness, and alignment with the proposal.
3. Review arc42 prose updates for consistency with the DSL and ADRs.
4. Verify that all Phase 1 spec artifacts (entity model, state machines, validation rules, interface contracts) are accurately reflected in the architecture documentation.
5. Check for missing architectural concerns that the agent-context cross-cutting feature should address.

## Open decisions

None. All design decisions were resolved in the proposal and recorded in ADRs.

## Next action

Start new session and run architecture-review-agent against `docs/` to complete Phase 2.2.

## Suggested skills

- `adversarial-review` -- review architecture quality (ATAM)
- `maintain-architecture` -- if findings require DSL or prose corrections
