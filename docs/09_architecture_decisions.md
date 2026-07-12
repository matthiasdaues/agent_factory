[back to index](README.md)

# 9. Architecture Decisions

All architecture decisions are documented as ADRs (Architecture Decision Records) following the Nygard format. Each ADR includes frontmatter declaring whether alternatives were formally evaluated via Pugh Matrix (`evaluation: pugh-matrix`) or whether the decision was the direct application of an existing principle (`evaluation: none`).

## Decision Index

| ID   | Title                                                                                                                   | Status   | Evaluation  |
| ---- | ----------------------------------------------------------------------------------------------------------------------- | -------- | ----------- |
| 0001 | [Pre-commit monorepo scoping](adr/0001-precommit-monorepo-scoping.md)                                                   | accepted | none        |
| 0002 | [Factory owns flow control; orchestrator is a trigger](adr/0002-factory-owns-flow-control-orchestrator-is-a-trigger.md) | accepted | pugh-matrix |
| 0003 | [Test execution via unavoidable hooks only](adr/0003-test-execution-via-hooks.md)                                       | accepted | none        |

## Key Decisions

### Ownership and Control

**ADR-0002** establishes that `factory/scripts/{transition-lint,phase,trigger}` and the `run-step` skill own flow control state (the marker, FSM, gates). `orchestrator/` is one possible trigger among peers (human operator, orchestrator CLI). This inversion makes playbook runs CLI-agnostic and resume-from-observable-state by design.

### Validation Strategy

**ADR-0001** and **ADR-0003** establish the hook-triggered validation pattern:

- **Pre-commit hooks** gate which files may be staged (`transition-lint`) and whether tests pass (`run-tests --changed-only`).
- **Pre-push hooks** enforce full test suite passage (`run-tests --full`) before work leaves local machine.
- **PreToolUse hooks** block destructive git commands and test commands before they execute (`block-dangerous-git.sh`).
- **FSM gates** (`script_exit_zero`) integrate test execution into phase advance entry conditions.

All follow the "Agentic Creation, Deterministic Validation" principle: agents create, hooks validate, no self-validation.

### Monorepo Scoping

**ADR-0001** declares one root `.pre-commit-config.yaml` for the monorepo, with each subproject's hooks namespaced (e.g., `-orchestrator` suffix) and path-scoped (`files: ^orchestrator/`). `factory/scripts/merge-precommit-config` splices subproject hook blocks into the root file.

## Superseded Decisions

None yet.

## Referenced from

- [04_solution_strategy.md](04_solution_strategy.md) — solution strategy derives from these decisions
- [05_building_block_view.md](05_building_block_view.md) — building blocks implement these decisions
- [08_crosscutting_concepts.md](08_crosscutting_concepts.md) — principles codified here
