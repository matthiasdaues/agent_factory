---
title: Kinds of playbooks
type: concept
status: implemented
order: 20
description: Beginner, onboarding, and delivery playbooks, and what each one covers.
---

# Kinds of playbooks

A playbook is a recipe in `.agent-factory/factory/playbooks/` for one situation. It says which agents run, in what order, and what to check between them. The playbooks fall into three kinds. [Survey research and falsification research](../research/survey-and-falsification.md) describes the two research playbooks.

## Beginner playbooks

Start with these. They touch little, have few steps, and need no setup:

| Playbook                                                                | For                                                                                                                                                                                                            |
| ----------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`poc-spike.md`](../../../playbooks/poc-spike.md)                       | "Does this basic idea work at all?" No specification, no architecture, and no checks: one file, thrown away by default. It is the fastest way to see an agent and your CLI work together.                      |
| [`technical-poc.md`](../../../playbooks/technical-poc.md)               | A real technical risk, usually a comparison of two or more candidate approaches. It is heavier than `poc-spike`, with several candidates and a Pugh Matrix that feeds an ADR, and lighter than the full chain. |
| [`bug-fix.md`](../../../playbooks/bug-fix.md)                           | One reported defect, in four steps: file the bug, fix it with tests, let QA check the fix, and mark it resolved.                                                                                               |
| [`documentation-update.md`](../../../playbooks/documentation-update.md) | Documentation that drifted from the code, in two steps: reconcile and validate.                                                                                                                                |

## Onboarding playbooks

Greenfield and brownfield bring a project to the point where `feature-addition` takes over. Both end with the same four anchor files: the scope map `docs/spec/scope-map.md`, the architecture model `docs/spec/architecture.dsl`, the glossary `docs/spec/glossary.md`, and the agent context `docs/agent-context.md`. They differ in where they start and how far they go:

| Playbook                                                                    | Starts from                                                                   | Ends with                                                                                                             |
| --------------------------------------------------------------------------- | ----------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| [`greenfield-development.md`](../../../playbooks/greenfield-development.md) | A new project with no code and no documentation.                              | A scope map with every Rule `deferred`, `architecture.dsl`, and the arc42 prose.                                      |
| [`brownfield-onboarding.md`](../../../playbooks/brownfield-onboarding.md)   | An existing codebase with no specification and no architecture documentation. | A scope map with its Rules filled in as `implemented`, an `architecture.dsl` read from the code, and the arc42 prose. |

Brownfield has two stages. Stage 1 produces the four anchor files: the scope map with the `reverse-map` skill, the glossary `docs/spec/glossary.md`, the architecture DSL, and the agent context `docs/agent-context.md`.

Stage 1 ends with an explicit exit, so you can start `feature-addition` from this light baseline. Stage 2 is optional and goes deeper: it extracts the full specification, resolves the components, and runs an ATAM review and a reconciliation.

After either playbook, or after Stage 1 of brownfield, all feature work starts with `feature-addition`.

## Feature delivery and other full-chain playbooks

These playbooks describe the reference paths for a project that the factory already manages. The typical chain runs requirements, architecture, planning, implementation, and quality. The order follows from the inputs each agent needs, as [Five kinds of work](../concepts/kinds-of-work.md) explains.

| Playbook                                                              | For                                                                                                                                                                                                                               |
| --------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`feature-addition.md`](../../../playbooks/feature-addition.md)       | A feature for a managed project, from an accepted proposal. The declared impact routes the specification and architecture work. It runs the mechanical architecture check, and the implementation agent runs the gate-check step. |
| [`refactoring.md`](../../../playbooks/refactoring.md)                 | Restructured code without changed behaviour, with a measured baseline and a safety net.                                                                                                                                           |
| [`architecture-review.md`](../../../playbooks/architecture-review.md) | A review of existing architecture documentation against quality attributes.                                                                                                                                                       |
