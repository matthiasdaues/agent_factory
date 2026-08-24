---
id: 0011
status: accepted
evaluation: pugh-matrix
---

# Gherkin .feature as consolidated specification format

## Context

The Factory's `derive-spec` skill produces a chain of intermediate Cockburn documents: an actor-goal list, persona use cases, system use cases, and supplementary specs. Gherkin acceptance criteria are embedded inside each `UC-XX-short-name.md` file. This structure serves the Cockburn completeness-checking workflow but creates three problems in an agentic context:

1. **Token waste.** To extract the full behavioral specification, an agent must read every `UC-XX` file. Each file read is a separate transmission through a noisy channel (Eichhorst's Principle). More transmissions mean more token consumption and more opportunities for context loss.

2. **No executable artifact.** The Gherkin scenarios are prose inside Markdown. No test framework reads them directly. The QA agent must re-extract and re-assemble what the requirements agent already produced.

3. **No code traceability.** The UC documents carry no link from a scenario to the source code that implements it. Traceability exists only in the developer's working memory.

The proposal introduces a consolidated Gherkin `.feature` file that preserves Cockburn's actor-goal completeness reasoning as an internal discipline while producing a single, executable, code-linked output.

Three alternatives were evaluated.

## Decision

Use a consolidated Gherkin `.feature` file with Rule-per-actor-goal structure as the primary specification output from the requirements phase. The `derive-feature` skill supersedes `derive-spec` for producing the behavioral specification. Supplementary specs (`entity-model.md`, `interface-contracts.md`, `state-machines.md`, `validation-rules.md`) continue to be produced separately because they carry structural facts the `.feature` file does not encode.

The Cockburn reasoning sequence (identify actors, derive goals, enumerate scenarios by main-success-then-extensions) is retained as the skill's internal working discipline. It is not committed as intermediate artifacts.

Each Rule in the `.feature` file maps to one actor-goal pair. Scenarios under each Rule carry `@`-references to the implementing code when it already exists, and no reference when the behavior is new. After implementation and reconciliation, every Rule carries at least one `@`-reference.

### Pugh Matrix

| Criterion                                          | Weight | A: Cockburn UC chain (baseline) | B: Consolidated Gherkin .feature | C: Structured YAML |
| -------------------------------------------------- | ------ | ------------------------------- | -------------------------------- | ------------------ |
| Eichhorst's Principle (single-pass readability)    | 3      | 0                               | +1                               | +1                 |
| Agent token efficiency                             | 2      | 0                               | +1                               | +1                 |
| Executable specification (test framework runs it)  | 3      | 0                               | +1                               | -1                 |
| Code traceability (@-references)                   | 2      | 0                               | +1                               | +1                 |
| Tool ecosystem (standard format, existing runners) | 2      | 0                               | +1                               | -1                 |
| Human readability (stakeholder review)             | 1      | 0                               | 0                                | -1                 |
| Cockburn completeness checking preserved           | 2      | 0                               | 0                                | 0                  |
| **Weighted total**                                 |        | **0**                           | **+12**                          | **+1**             |

Option B dominates. The decisive criteria are executability (weight 3, Gherkin is natively runnable by `behave`, `cucumber`, `godog`) and tool ecosystem (weight 2, Gherkin has wide cross-language support). Option C (structured YAML) would require custom tooling for test execution and has no established runner ecosystem.

## Consequences

**Positive:**

- A single `.feature` file replaces a chain of `UC-XX` documents as the behavioral specification. Agents read one file instead of N.
- The `.feature` file is executable by standard Gherkin test frameworks. The QA agent runs it as an acceptance test; the developer agent runs it as part of the TDD cycle. No re-extraction step.
- Code traceability is embedded via `@`-references. The reconciliation agent fills missing references after implementation, producing a complete spec-to-code map.
- The scope map (`docs/spec/scope-map.md`) tracks all Rules across slices, providing a persistent cross-feature traceability record.

**Negative:**

- The `.feature` file does not carry structural information (entity lifecycles, validation rules, boundary schemas). Supplementary specs remain necessary as separate artifacts. The spec output is two concerns (behavioral and structural) rather than one unified chain.
- Cockburn's intermediate documents (actor-goal list, persona UCs, system UCs) are no longer produced. Projects that relied on them as review artifacts must use the `.feature` file's Rule structure and the gaps report instead.
- Existing projects with `derive-spec` output need a one-time migration via the `scope-map-migration` skill to establish the scope map from their existing UC documents.

## Referenced from

- [Proposal: Agentic Quality Gates and Requirements Consolidation](../proposals/agentic-quality-gates-and-specification-consolidation.md)
- [cross-reference-format.md](../../factory/rulebooks/conventions/cross-reference-format.md) (amended for `@`-reference notation)
- [testing-strategy.md](../../factory/rulebooks/conventions/testing-strategy.md) (amended for `.feature` as acceptance layer)
