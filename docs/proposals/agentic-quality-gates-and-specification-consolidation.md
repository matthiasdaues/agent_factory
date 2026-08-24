---
schema_version: 2
title: "Agentic Quality Gates and Requirements Consolidation"
status: open
owner: matthiasdaues
created: 2026-08-24
updated: 2026-08-24
supersedes:

impact:
  scope: cross_component
  architecture_change: false
  external_contract_change: false
  boundaries:
    - factory/rulebooks/conventions/testing-strategy.md
    - factory/skills/derive-spec/SKILL.md
    - factory/agents/requirements-agent.md
    - factory/agents/qa-agent.md

governance:
  assurance: elevated
  risk_domains:
    - reliability
    - data_integrity
    - compatibility

estimate:
  as_of: 2026-08-24
  basis: analogous_change
  confidence: medium
  human_review_hours:
    min: 2.0
    max: 4.0
  normalized_tokens:
    min: 8000
    max: 18000
  estimated_consumption:
    min: 120000
    max: 270000
    overhead_multiplier: 15
    playbook: feature-addition
---

# Feature Proposal: Agentic Quality Gates and Requirements Consolidation

## Summary

Close two gaps between the Factory's process model and Bob Martin's agentic coding tenets: (1) add **semantic deterministic gates** (cyclomatic complexity, mutation testing, dependency-rule enforcement) that operate on code meaning, not just format; and (2) enrich the requirements phase output with a **consolidated Gherkin feature file** and a **per-feature QA strategy document** so the specification is actionable by both coders and QA without re-reading prose use cases. Also eliminate the waterfall hinge by routing through the architecture phase only when the feature changes the module graph.

## Motivation

### The semantic gate gap

The Factory's `validate` skill and `transition-lint` pre-commit hook run **syntactic** checks — formatting, frontmatter schema, naming conventions. They catch cosmetic violations. They do not catch the defects that Bob Martin identifies as the failure mode for agentic workflows: code that is syntactically valid but semantically degraded (high cyclomatic complexity, shallow modules, missing test coverage, surviving mutants).

Martin's operational insight: agents are fast enough to run **crap analysis** (cyclomatic complexity + coverage scoring), **mutation testing** (flip every `<` to `>`, every `==` to `!=`, expect the test suite to fail), and **dependency-rule checking** (module A must not import module B — enforced mechanically) at machine speed. The Factory's current gate model trusts agents to self-report on these qualities. The sub-agent self-report is not reliable; the Factory has the dispatch contract to prevent false reports, but it lacks the semantic checks that would make a false report detectable.

The practical consequence: without semantic gates, the reconciliation-agent and qa-agent carry the entire semantic quality burden. Each review cycle burns tokens on findings that a deterministic gate could have caught and flagged automatically, or that the coder's own workflow could have been forced to fix before committing.

### The specification-as-actionable-artifact gap

The `derive-spec` skill (Step 2) produces Gherkin acceptance criteria **inside each `UC-XX-short-name.md`** under Cockburn format. This buries the feature scenarios where the coder never looks — they are scoped to a single use case, not cross-referenced, not deduped, and not available as a single file to paste into a test runner.

The `qa-agent` bug-hunt loop already references "verify **Gherkin** criteria" but has no canonical source file to read. The current contract: the QA agent must re-read every `UC-XX-short-name.md` to extract the scenarios. This is token waste and a quality risk — important scenarios can be missed.

A **per-feature QA strategy document** does not exist at all. The `testing-strategy.md` convention tells agents how to write tests generally; it does not say what the QA plan is for a specific feature. The `Completion Criteria` in proposals leave "what done looks like from a QA standpoint" to stakeholder negotiation rather than encoding it in the spec. This creates review ambiguity at Phase 5.

### The waterfall hinge

The `feature-addition` playbook routes through Phase 2 (Architecture) whenever `impact.architecture_change` is declared `true`. In practice, non-trivial features routinely set this flag and go through spec → architecture → review → fix → review → planning — a six-gate sequence before a line of code. This is a waterfall-shaped gate pattern applied to agentic work.

Martin's counterpoint: with deterministic verification in place, the cost of refactoring has collapsed to near zero. Heavy upfront planning is more expensive than incremental agile with automated gates. The Factory already has the `impact.architecture_change: false` escape hatch, but it requires manual declaration and is not enforced against the actual code change. A feature that adds a new API endpoint to an existing module — touching no module boundaries, no dependency directions, no DSL model — is currently routed through Phase 2 anyway.

## Core Principles

1. **Agents create; deterministic gates verify.** Semantic quality checks are no different from formatting checks in this respect. If a gate can be automated, it must be — no agent self-report, no human trust.

2. **Short, independently verifiable transmissions.** Per Eichhorst's Principle. The consolidated Gherkin file and QA strategy document are both single-file artifacts that a coder or QA agent can read in one pass without re-synthesising from a dozen prose documents.

3. **Architecture is a concern, not a phase.** A feature that changes no module boundaries should not trigger the full architecture phase. Phase routing should be driven by the module graph's actual state, not by a manual declaration.

4. **Impose values, not human disciplines.** Quality gates encode *values* (cyclomatic complexity bounded, mutation coverage 100%, dependency direction fixed) without prescribing the mechanical procedure the agent used to achieve them.

## Design

### 1. Semantic Quality Gate Skill — `quality-gate`

A new factory skill that wraps three existing tool categories:

| Gate                   | Tool candidates                                                        | What it enforces                                                                                                            |
| ---------------------- | ---------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| Complexity gate        | `radon` (Python), `gjstest` (Go), `complexity_report.py` (hand-rolled) | Cyclomatic complexity ≤ threshold per function; threshold tunable per project (Factory default: 6 for agents, 4 for humans) |
| Mutation coverage gate | `mutmut` (Python), `mutant` (Rust), `pitest` (Java)                    | 100% mutation coverage: every operator flip must kill a test                                                                |
| Dependency-rule gate   | `deptrack` (general), `dependency-cruiser` (JS/TS), `arch-pkg` (Go)    | Module A must not depend on module B — rules read from `architecture.dsl`                                                   |

The skill runs in the developer's TDD loop, not as a separate phase:

1. The `developer-agent` writes code and tests.
2. After each commit, `quality-gate` runs and reports.
3. If any gate fails, the agent loops internally until the gate passes — per Martin's "loop until the tool says it's okay" pattern.
4. The `premerge-check` script runs `quality-gate` as a hard blocker before merge.

**Skill file:** `factory/skills/quality-gate/SKILL.md`

Inputs: `docs/arc42/architecture.dsl`, project-specific threshold config (`docs/charter/house-rules.md` or `factory/config/quality.conf`)

Outputs: structured JSON report per gate (pass/fail per function, per mutant, per dependency rule), logged to `.agent-factory/quality-gate/<story-id>.json`

The skill is invoked by the `developer-agent` workflow as part of the red-green-refactor loop, not as a separate phase. It is also listed in `premerge-check` as a hard gate.

**Note on thresholds:** The Factory's `testing-strategy.md` convention already says *"Test count and coverage percentage are diagnostics, not quality targets."* The complexity and mutation gates are not coverage-percentage targets — they are per-function quality targets enforced by deterministic tools. They do not conflict with this convention; they replace the human judgment that would otherwise be applied to the same quality signal.

### 2. Consolidated Gherkin Feature File — `consolidate-gherkin`

A new step at the end of Phase 1 (Requirements), produced by the `requirements-agent`.

**Trigger:** After Step 4 of `derive-spec` completes (all `UC-XX-short-name.md` files written), invoke `consolidate-gherkin`.

**What it does:**

1. Read every `docs/spec/use_cases/UC-XX-short-name.md`.
2. Extract all `Gherkin` blocks (`gherkin ... ` fences).
3. Deduplicate scenarios that are identical across use cases.
4. Detect ambiguous Given/When/Then wording — flag as an open question, do not silently fix.
5. Detect coverage gaps: any UC without Gherkin, any Gherkin scenario not traceable to a UC.
6. Write `docs/spec/<feature-name>.feature` — a canonical `.feature` file in standard Gherkin format (Feature / Scenario / Background / Rule).
7. Write a coverage gap report as `docs/spec/<feature-name>-gaps.md`.

**Output location:** `docs/spec/<feature-name>.feature` and `docs/spec/<feature-name>-gaps.md`

The `.feature` file becomes the primary input for:

- `developer-agent` — reads it instead of re-reading UCs for acceptance criteria
- `qa-agent` — the bug-hunt step ("Hunt: break the system, verify Gherkin criteria") now reads this file directly

**Gaps report** feeds the completion criteria: each gap is either a missing scenario (turns into a story acceptance criterion) or a UC without Gherkin (turns into a clarification requirement before the feature goes to planning).

### 3. QA Strategy Document — `qa-strategy-from-spec`

A new document produced by the `requirements-agent` at the end of Phase 1, alongside the consolidated Gherkin file.

**File:** `docs/spec/qa-strategy.md` (or `docs/spec/<feature-name>-qa-strategy.md` for cross-component features)

**Template sections:**

```markdown
## Feature
Feature name, trace to proposal, trace to Gherkin file

## Test Layers in Scope
For each layer (deterministic linter / contract test / integration test / e2e smoke),
state whether this feature adds to it, strengthens it, or is not in scope.
State the owning layer per observable contract.

## Contract Owners
Table: Contract | Owner layer | Failure mode | Test strategy note

## Boundary Cases
Equivalence classes, edge values, security boundaries relevant to this feature.
Each entry maps to a Gherkin scenario or an explicit gap.

## Defect Severity Triage
What severity (blocking / fix-in-same-story / defer) maps to which impact class
for this feature's domain. Customised from the generic `testing-strategy.md`
convention for this feature's risk profile.

## Test Retention Policy
When this feature's tests are consolidated with overlapping coverage,
which owner survives and why. Reference to `testing-strategy.md § Delete
overlapping tests safely` as the protocol.
```

**Source inputs:** `docs/spec/actor-goal-list.md`, `docs/spec/<feature-name>.feature`, `docs/spec/supplementary_specs/entity-model.md`, `docs/spec/supplementary_specs/interface-contracts.md`

**What it is not:** It is not a generic testing policy. It is not `testing-strategy.md` reformatted. It is a per-feature QA plan that tells the `qa-agent` how to specialise the generic strategy for this feature's specific contracts and risk profile.

**Effect on phase routing:** Phase 5 (QA) receives the `qa-strategy.md` as a formal input alongside `docs/spec/use_cases/` and `src/`. The qa-agent reads it at the top of its workflow and uses it to scope its Fagan inspection, security review, and bug hunt. The phase gate remains; the phase is better informed.

### 4. Architecture Phase as Conditional Concern

Change the Phase 2 routing logic from **manual declaration** to **mechanical detection**:

**Current logic:**

```
Step 0.3 — Route from Declared Impact
  impact.architecture_change: true  → Phase 2
  impact.architecture_change: false → Skip Phase 2
```

The flag is set by the proposal author or estimated by requirements-agent. It is not verified against the actual code change.

**Proposed logic:**

At the end of Phase 1 (after the proposal is accepted), before Phase 3 begins:

```
Mechanical check:
  1. Read docs/arc42/architecture.dsl — derive the current module map
     (which directories own which modules, which modules depend on which)
  2. Read the feature's declared outputs: every path in story.outputs
  3. Map each output path to the module(s) it belongs to
  4. For each module touched:
     - Check if the feature adds a new module (new directory with no parent in the map)
     - Check if the feature changes a module's public interface (new/changed entry in interface-contracts.md)
     - Check if the feature inverts or changes a dependency direction
  5. If any of the above is true → set impact.architecture_change: true, enter Phase 2
     Otherwise → skip Phase 2, go directly to Phase 3
```

**Effect on workflow:**

- The `feature-addition` playbook's Step 0.3 routing decision gains a new "Mechanical check" step between the declaration and the decision.
- The `planning-agent` can receive this signal and include module-boundary work in Epic 0 if the feature is the first to touch a new module.
- The `implementation-agent` can use the module map to detect cross-module file overlaps (already partly implemented via `outputs:` glob analysis) and also detect cross-module *dependency* changes that would make two feature branches non-mergeable even if file-disjoint.
- The `premerge-check --scope` already checks diff scope; the new check feeds into the scope determination before dispatch, not after.

**Enforcement:** The mechanical check is a deterministic script run by the orchestrating session before Phase 3 starts. Its output is a boolean `architecture_change` flag recorded in the phase handoff. The flag can be overridden manually (a stakeholder may want Phase 2 for documentation reasons even if the module graph is unchanged), but the default is the machine result.

## Scope

**In the first release:**

- `factory/skills/quality-gate/SKILL.md` — skill file with complexity, mutation, and dependency-gate implementations
- `factory/scripts/quality-gate` — CLI wrapper (Python/shell) for the skill, callable from pre-commit and premerge-check
- `docs/spec/<feature-name>.feature` — consolidated Gherkin output per feature (invoke via requirements-agent)
- `docs/spec/<feature-name>-gaps.md` — coverage gap report (invoke via requirements-agent)
- `docs/spec/qa-strategy.md` — per-feature QA strategy output (invoke via requirements-agent)
- Updated `factory/agents/requirements-agent.md` frontmatter: add the three new outputs to the outputs list
- Updated `factory/agents/developer-agent.md` workflow: invoke `quality-gate` after each commit, loop until pass
- Updated `factory/scripts/premerge-check`: add `quality-gate` as a hard blocker
- Updated `factory/rulebooks/templates/story.md`: add `quality-gates` field (which gates apply to this story's outputs)
- Updated `feature-addition.md` Step 0.3: mechanical module-graph check before Phase 2 routing

**Explicitly deferred:**

- Per-language mutation testing toolchain (the skill supports `mutmut` for Python as the reference implementation; other languages need tool discovery and threshold calibration)
- `deptrack` integration for dependency-rule enforcement across language ecosystems (different ecosystems have different tools; the skill structure is language-agnostic but the tool calls are not)
- `quality-gate` integration into the brownfield-onboarding pipeline (the onboarding reads `architecture.dsl` after it's built; the gate could run against the existing codebase to establish baseline quality scores)
- Automated module map update when a new directory is created (currently the DSL is the source of truth; there is no auto-update on `mkdir`)

## Open Questions

1. **Threshold calibration:** The Factory's current default complexity threshold for agents is 6 (per Martin's observation that agents have a different threshold than humans). Should this be a project-level setting in `house-rules.md`, a per-story field in the story format, or a global default with a per-project override? *Decision needed: where thresholds live and who sets them.*

2. **Mutation testing on slow test suites:** Mutation testing runs the full test suite per mutant. For large projects with slow suites, this is expensive even at agent speed. The skill needs a `--jobs N` parallelisation flag and a `--fast-only` mode that skips integration-level mutants. *Decision needed: what the default mode is and when to use `--fast-only`.*

3. **Consolidated Gherkin file naming:** The file is per-feature, but the feature name may not be stable at requirements time (the proposal title may change after acceptance). Should the file be named `docs/spec/<proposal-name>.feature` (changes with title) or `docs/spec/<ST-NNNN>-<slug>.feature` (stable across rename)? *Decision needed: naming stability vs. discoverability.*

4. **QA strategy document scoping:** For a cross-component feature, should `qa-strategy.md` live at feature level (`docs/spec/<feature>-qa-strategy.md`) or at a shared location that multiple features contribute to? *Decision needed: one doc per feature or one doc per module.*

5. **Architecture mechanical check override authority:** The mechanical check can be overridden manually. Who has authority to override — the stakeholder, the orchestrating agent, or any human in the review loop? *Decision needed: override governance.*

## Completion Criteria

- [ ] `factory/skills/quality-gate/SKILL.md` exists and documents all three gate types
- [ ] `factory/scripts/quality-gate` runs against a test project with known complexity violations and detects all of them
- [ ] `factory/scripts/quality-gate` runs mutation testing against a project with 100% coverage and kills all surviving mutants
- [ ] `factory/scripts/quality-gate` runs dependency-rule check against a project with a known violation and flags it
- [ ] `premerge-check` blocks a merge when `quality-gate` fails on any gate
- [ ] `requirements-agent` produces `docs/spec/<feature-name>.feature` from two or more UC files
- [ ] `requirements-agent` produces `docs/spec/<feature-name>-gaps.md` with at least one coverage gap detected from a UC without Gherkin
- [ ] `requirements-agent` produces `docs/spec/qa-strategy.md` with all template sections filled for a test feature
- [ ] `qa-agent` bug-hunt step reads `docs/spec/<feature-name>.feature` and references it in bug findings (not UC files directly)
- [ ] `feature-addition.md` Step 0.3 mechanical check skips Phase 2 for a feature that touches no module boundaries
- [ ] `feature-addition.md` Step 0.3 mechanical check routes to Phase 2 for a feature that creates a new module directory
- [ ] All new artifacts pass `factory/scripts/validate`

## Guiding Rule

A feature is not ready for the planning phase unless the specification is a single-file artifact that a coder can read in one pass, the QA strategy is written from a QA manager's perspective (not derived from generic convention), and the module graph does not change without explicit architectural review.
