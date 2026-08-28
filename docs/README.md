# Architecture Documentation — Factory Flow Control

arc42 architecture documentation for **Factory Flow Control** — the deterministic state-machine harness, CLI-agnostic dispatch mechanism, and generated catalog that govern how Agent Factory playbooks run.

This documentation derives from the specification in [`spec/`](spec/prd.md). The domain vocabulary used throughout is defined in [12_glossary.md](arc42/12_glossary.md).

## Table of Contents

| #   | Chapter                                                      |
| --- | ------------------------------------------------------------ |
| 5   | [Building Block View](arc42/05_building_block_view.md)       |
| 6   | [Runtime View](arc42/06_runtime_view.md)                     |
| 8   | [Cross-cutting Concepts](arc42/08_crosscutting_concepts.md)  |
| 9   | [Architecture Decisions](arc42/09_architecture_decisions.md) |
| 12  | [Glossary](arc42/12_glossary.md)                             |

## Model and diagrams

- [`architecture.dsl`](arc42/architecture.dsl) — the Structurizr C4 model (versioned source of truth).
- [`assets/images/`](assets/images/) — exported diagrams (derived artifacts).
- [`adr/`](adr/) — Architecture Decision Records (Nygard format + Pugh Matrix where genuine alternatives existed).

## Referenced from

- [Agent Factory README](../README.md) (repo root)
- [docs/spec/prd.md § Referenced from](spec/prd.md#referenced-from)
- [docs/arc42/concepts.md § The phase chain](arc42/concepts.md#the-phase-chain)

## See also

- [factory/README.md](../factory/README.md) — the toolset (agents, skills, playbooks)
- [orchestrator/README.md](../orchestrator/README.md) — optional CLI for automated playbook execution (work in progress — not yet operational)
