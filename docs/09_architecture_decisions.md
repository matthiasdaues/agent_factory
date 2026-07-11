[back to index](README.md)

# 9. Architecture Decisions

Architecture Decision Records (Nygard format), stored under [`adr/`](adr/). Every ADR carries `status` and `evaluation` (`pugh-matrix` or `none`) in its frontmatter — `evaluation: none` is a valid, common value, not an absence of one.

| ADR                                                                                                                                          | Status   | Evaluation  | Decision                                                                                                                                                                                                        |
| -------------------------------------------------------------------------------------------------------------------------------------------- | -------- | ----------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [0001 — Pre-commit monorepo scoping](adr/0001-precommit-monorepo-scoping.md)                                                                 | Accepted | none        | One shared root `.pre-commit-config.yaml`; each subproject's hooks are namespaced and path-scoped rather than relying on `pre-commit`'s single-config discovery.                                                |
| [0002 — Factory owns flow control; orchestrator is one trigger among peers](adr/0002-factory-owns-flow-control-orchestrator-is-a-trigger.md) | Accepted | pugh-matrix | `factory/scripts/{transition-lint,phase,trigger}` and `run-step` are the flow-control owner. `orchestrator/` is a peer trigger, not an owner — it invokes the same mechanisms a Human Operator invokes by hand. |

Both ADRs are whole-repo, cross-cutting decisions — this is why they live in `docs/adr/` (root), a separate sequence from `orchestrator/docs/adr/`'s own 20+ entries, per [ADR-0001's own rationale](adr/0001-precommit-monorepo-scoping.md#context).

## Referenced from

- [04_solution_strategy.md § 4.1](04_solution_strategy.md#41-the-central-decision-factory-owns-flow-control-orchestrator-is-a-trigger)
