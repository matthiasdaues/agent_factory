# Architecture Documentation — Factory Flow Control

arc42 architecture documentation for **Factory Flow Control** — the deterministic state-machine harness, CLI-agnostic dispatch mechanism, and generated catalog that govern how Agent Factory playbooks run.

This documentation derives from the specification in [`spec/`](spec/prd.md). The domain vocabulary used throughout is defined in [12_glossary.md](12_glossary.md).

## Table of Contents

| #   | Chapter                                                    |
| --- | ---------------------------------------------------------- |
| 1   | [Introduction and Goals](01_introduction_and_goals.md)     |
| 2   | [Architecture Constraints](02_architecture_constraints.md) |
| 3   | [System Scope and Context](03_system_scope_and_context.md) |
| 4   | [Solution Strategy](04_solution_strategy.md)               |
| 5   | [Building Block View](05_building_block_view.md)           |
| 6   | [Runtime View](06_runtime_view.md)                         |
| 7   | [Deployment View](07_deployment_view.md)                   |
| 8   | [Cross-cutting Concepts](08_crosscutting_concepts.md)      |
| 9   | [Architecture Decisions](09_architecture_decisions.md)     |
| 10  | [Quality Requirements](10_quality_requirements.md)         |
| 11  | [Risks and Technical Debt](11_risks_and_technical_debt.md) |
| 12  | [Glossary](12_glossary.md)                                 |

## Model and diagrams

- [`architecture.dsl`](architecture.dsl) — the Structurizr C4 model (versioned source of truth).
- [`assets/images/`](assets/images/) — exported diagrams (derived artifacts).
- [`adr/`](adr/) — Architecture Decision Records (Nygard format + Pugh Matrix where genuine alternatives existed).

## Referenced from

- [Agent Factory README](../README.md) (repo root)
- [docs/spec/prd.md § Referenced from](spec/prd.md#referenced-from)
- [docs/concepts.md § The phase chain](concepts.md#the-phase-chain)

## See also

- [factory/README.md](../factory/README.md) — the toolset (agents, skills, playbooks)
- [orchestrator/README.md](../orchestrator/README.md) — optional CLI for automated playbook execution
