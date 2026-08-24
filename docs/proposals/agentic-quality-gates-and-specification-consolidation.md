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
  architecture_change: true
  external_contract_change: false
  boundaries:
    - factory/rulebooks/conventions/testing-strategy.md (amended)
    - factory/skills/derive-spec/SKILL.md (superseded by derive-feature)
    - factory/agents/requirements-agent.md
    - factory/agents/qa-agent.md
    - factory/agents/developer-agent.md
    - factory/agents/implementation-agent.md
    - factory/agents/reconciliation-agent.md
    - factory/scripts/premerge-check
    - factory/playbooks/feature-addition.md
    - factory/rulebooks/templates/story.md

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

Close two gaps in the Factory's process model: (1) add **semantic deterministic gates** (cyclomatic complexity, mutation testing, dependency-rule enforcement) that operate on code meaning, not just format; and (2) enrich the requirements phase output with a **consolidated Gherkin feature file** and a **per-feature QA strategy document** so the specification is actionable by both coders and QA without re-reading prose use cases. Also eliminate the waterfall hinge by replacing the manual `architecture_change` declaration with a deterministic script that reads the existing `architecture.dsl`, derives the module map, and compares it against the feature's declared outputs — routing through the architecture phase only when the feature actually changes module boundaries, dependency directions, or public interfaces.

## Motivation

### The semantic gate gap

The Factory's `validate` skill and `transition-lint` pre-commit hook run **syntactic** checks — formatting, frontmatter schema, naming conventions. They catch cosmetic violations. They do not catch code that is syntactically valid but semantically degraded: high cyclomatic complexity, shallow modules, missing test coverage, surviving mutants. These are the defects that matter most in agentic workflows, where code is produced faster than any human reviewer can inspect it.

The operational principle: agents are fast enough to run **CRAP analysis** (cyclomatic complexity weighted against coverage), **mutation testing** (flip every `<` to `>`, every `==` to `!=`, expect the test suite to fail), and **dependency-rule checking** (module A must not import module B — enforced mechanically) at machine speed. The Factory's current gate model trusts agents to self-report on these qualities. The sub-agent self-report is not reliable; the Factory has the [dispatch contract](../../factory/rulebooks/conventions/dispatch-contract.md) to prevent false reports, but it lacks the semantic checks that would make a false report detectable.

The practical consequence: without semantic gates, the reconciliation-agent and qa-agent carry the entire semantic quality burden. Each review cycle burns tokens on findings that a deterministic gate could have caught and flagged automatically, or that the coder's own workflow could have been forced to fix before committing.

### The specification-as-actionable-artifact gap

The `derive-spec` skill (Step 2) produces Gherkin acceptance criteria **inside each `UC-XX-short-name.md`** under Cockburn format. This buries the feature scenarios where the coder never looks — they are scoped to a single use case, not cross-referenced, not deduped, and not available as a single file to paste into a test runner.

The `qa-agent` bug-hunt loop already references "verify **Gherkin** criteria" but has no canonical source file to read. The current contract: the QA agent must re-read every `UC-XX-short-name.md` to extract the scenarios. This is token waste and a quality risk — important scenarios can be missed.

A **per-feature QA strategy document** does not exist at all. The `testing-strategy.md` convention tells agents how to write tests generally; it does not say what the QA plan is for a specific feature. The `Completion Criteria` in proposals leave "what done looks like from a QA standpoint" to stakeholder negotiation rather than encoding it in the spec. This creates review ambiguity at Phase 5.

### The waterfall hinge

The `feature-addition` playbook routes through Phase 2 (Architecture) whenever `impact.architecture_change` is declared `true`. In practice, non-trivial features routinely set this flag and go through spec → architecture → review → fix → review → planning — a six-gate sequence before a line of code. This is a waterfall-shaped gate pattern applied to agentic work.

The counterpoint: with deterministic verification in place, the cost of refactoring has collapsed to near zero. Heavy upfront planning is more expensive than incremental agile with automated gates. The Factory already has the `impact.architecture_change: false` escape hatch, but it requires manual declaration and is not enforced against the actual code change. A feature that adds a new API endpoint to an existing module — touching no module boundaries, no dependency directions, no DSL model — is currently routed through Phase 2 anyway.

## Core Principles

1. **Agents create; deterministic gates verify.** Semantic quality checks are no different from formatting checks in this respect. If a gate can be automated, it must be — no agent self-report, no human trust.

2. **Short, independently verifiable transmissions.** Per Eichhorst's Principle. The consolidated Gherkin file and QA strategy document are both single-file artifacts that a coder or QA agent can read in one pass without re-synthesising from a dozen prose documents.

3. **Architecture is a concern, not a phase.** A feature that changes no module boundaries should not trigger the full architecture phase. Phase routing should be driven by the module graph's actual state, not by a manual declaration.

4. **Impose values, not human disciplines.** Quality gates encode *values* (cyclomatic complexity bounded, mutation coverage 100%, dependency direction fixed) without prescribing the mechanical procedure the agent used to achieve them.

## Design

### 1. Semantic Quality Gate Skill — `quality-gate`

Three independent skills, each callable alone and chainable by the caller. The recommended sequence is CRAP → mutation → dependency, but each skill is self-contained and useful in isolation.

#### `crap-score` — Structural quality

CRAP scoring combines cyclomatic complexity with test coverage into a single risk metric: `CRAP(m) = comp(m)^2 × (1 - cov(m)/100)^3 + comp(m)`. A high CRAP score means the function is too complex for its level of test coverage. The cheapest way to pass is to keep code small — reducing complexity lowers CRAP faster than adding coverage.

|                      |                                                                                                                           |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| **Skill file**       | `factory/skills/crap-score/SKILL.md`                                                                                      |
| **Tool candidates**  | `radon` + `coverage` (Python), `gjstest` (Go), composite script                                                           |
| **What it enforces** | CRAP ≤ threshold per function; threshold tunable per project (`house-rules.md` when charter exists, else Factory default) |
| **Inputs**           | Source files, coverage data                                                                                               |
| **Outputs**          | JSON report per function (CRAP score, pass/fail), logged to `.agent-factory/crap-score/<story-id>.json`                   |

#### `mutation-analysis` — Behavioral quality

Verifies that test coverage is real — not just line-hit but behaviorally meaningful. Every surviving mutant requires action: remove dead code or add the missing test. If neither applies, file a finding for QA. The gate blocks until zero mutants survive; unresolved mutation findings block the merge.

|                      |                                                                                                                                |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| **Skill file**       | `factory/skills/mutation-analysis/SKILL.md`                                                                                    |
| **Tool candidates**  | `mutmut` (Python; reference implementation for first release). Other languages (`mutant` for Rust, `pitest` for Java) deferred |
| **What it enforces** | Every surviving mutant resolved: dead code removed, missing contract tested, or finding filed for QA. Zero survivors to pass   |
| **Inputs**           | Source files, test suite                                                                                                       |
| **Outputs**          | JSON report per mutant (killed/survived, resolution action), logged to `.agent-factory/mutation-analysis/<story-id>.json`      |

#### `dependency-check` — Architectural integrity

Enforces module dependency directions declared in `architecture.dsl`. Neither TDD nor the testing strategy addresses dependency direction; this skill fills an unoccupied gap.

|                      |                                                                                                                 |
| -------------------- | --------------------------------------------------------------------------------------------------------------- |
| **Skill file**       | `factory/skills/dependency-check/SKILL.md`                                                                      |
| **Tool candidates**  | `deptrack` (general), `dependency-cruiser` (JS/TS), `arch-pkg` (Go)                                             |
| **What it enforces** | Module dependency directions match `architecture.dsl` declarations                                              |
| **Inputs**           | `docs/arc42/architecture.dsl`, source files                                                                     |
| **Outputs**          | JSON report per rule (pass/fail, violating import), logged to `.agent-factory/dependency-check/<story-id>.json` |

#### Invocation model — developer/gate separation

The three gate skills are deterministic scripts that run on committed artifacts. The developer agent never runs them itself — it acts on their output. This prevents context contamination from gate output, analysis, and fix attempts accumulating in one agent's window.

1. The `developer-agent` writes code and tests, commits.
2. The `implementation-agent` dispatcher runs each gate script (`crap-score`, `mutation-analysis`, `dependency-check`) on the committed artifacts. Each produces a JSON report.
3. If any gate fails, the dispatcher spawns a **fresh developer agent** with only the gate reports and affected files as input.
4. The fresh developer fixes, commits. Back to step 2.
5. When all gates pass, the dispatcher proceeds to `premerge-check` and merge.

**Dispatcher extension:** The `implementation-agent` already owns wave scheduling, branch/merge ordering, and completion tracking. This proposal extends its per-story loop with a gate-check step between the developer's commit and the merge. The extension is internal to the dispatcher's existing per-story workflow — it does not add a new container or component to `architecture.dsl`. The dispatcher calls the gate scripts directly (they are CLI scripts under `factory/scripts/`), reads their JSON output, and decides whether to spawn a fix iteration or proceed to merge. The maximum number of fix iterations before the story is marked as blocked is a tunable default (3), overridable in `house-rules.md`.

Each developer iteration starts with a clean context. The `premerge-check` script lists all three as independent hard gates before merge.

**Coherence with [testing-strategy.md](../../factory/rulebooks/conventions/testing-strategy.md):** The Factory's testing strategy says *"Test count and coverage percentage are diagnostics, not quality targets."* This proposal amends that convention to clarify that composite structural risk scores — such as CRAP — that use coverage as one input to a risk metric are not coverage targets and are admissible as acceptance gates. The three skills respect the amended convention:

- **CRAP score** is a composite structural gate. Coverage enters as a counterweight to cyclomatic complexity; the gate threshold is on the composite score, not on coverage itself. The pressure it applies is toward smaller code, not higher coverage numbers.
- **Mutation analysis** is a code-smell gate, not a coverage target. A surviving mutant means code does something no test observes. The response is investigation (remove dead code or add the missing contract test), not unconditional test creation. When the developer agent cannot resolve a survivor through either action, it files a finding for the QA agent — the developer does not self-suppress.
- **Dependency check** enforces what `architecture.dsl` already declares. Neither TDD nor the testing strategy addresses dependency direction; this skill fills an unoccupied gap.

### 2. Specification as Gherkin Feature File — `derive-feature`

A replacement for the current `derive-spec` → `consolidate-gherkin` chain. Instead of producing intermediate Cockburn documents (actor-goal list, persona UCs, system UCs) and then extracting Gherkin from them, the requirements-agent uses the Cockburn reasoning sequence as an internal working process and writes the `.feature` file directly.

**Trigger:** After the proposal is accepted, the requirements-agent runs `derive-feature` as its primary specification step.

**Internal reasoning process (Cockburn chain as working discipline, not document production):**

1. **Identify actors and goals** — enumerate who interacts with the feature and what they want. Hold in working context; do not commit as a separate artifact.
2. **For each actor-goal pair, derive a Rule** — each Rule in the `.feature` file corresponds to one actor-goal pair. The Rule name states the goal; a comment line below it identifies the actor.
3. **Under each Rule, enumerate Scenarios** — decompose the goal into Given/When/Then scenarios, applying the Cockburn workflow-to-edge-case progression: main success path first, then extensions and failure modes.
4. **Cross-check completeness** — every actor-goal pair must have at least one Rule; every Rule must have at least one Scenario. Failures go to the gaps report.
5. **Detect ambiguous Given/When/Then wording** — flag as an open question in the gaps report, do not silently fix.

**Output structure:**

```gherkin
Feature: <feature-name>

  Rule: <actor-goal statement>
    # actor: <who>

    Scenario: <main success path>
      Given ...
      When ...
      Then ...

    Scenario: <extension or failure mode>
      Given ...
      When ...
      Then ...

  Rule: <next actor-goal statement>
    # actor: <who>
    ...
```

Reading the Rules gives the actor-goal matrix. Reading the Scenarios under each Rule gives the behavioral specification. The `.feature` file IS the traceability artifact — the Cockburn chain's completeness-checking power is preserved without intermediate documents.

**Output location:** `docs/spec/<feature-name>.feature` and `docs/spec/<feature-name>-gaps.md`

The `.feature` file becomes the primary input for:

- `developer-agent` — reads it instead of re-reading UCs for acceptance criteria
- `qa-agent` — the bug-hunt step ("Hunt: break the system, verify Gherkin criteria") now reads this file directly

**Gaps report** contains:

- The actor-goal matrix derived during step 1 (traceability evidence that the completeness check ran)
- Actor-goal pairs without a corresponding Rule (missing use cases)
- Rules without Scenarios (identified but unspecified behavior)
- Ambiguous wording flagged during step 5

Each gap is either a missing scenario (turns into a story acceptance criterion) or an unspecified actor-goal pair (turns into a clarification requirement before the feature goes to planning).

**Scope map and slice lifecycle:**

The `.feature` files are transient implementation artifacts — they live on the feature branch, merge to dev with the code, and are removable from dev/main after the slice's tests become the durable behavioral spec. A persistent **scope map** at `docs/spec/scope-map.md` tracks all Rules across all slices:

```markdown
| Rule                                      | Status      | Slice | Feature file              |
| ----------------------------------------- | ----------- | ----- | ------------------------- |
| Rule: User authenticates via SSO          | implemented | 1     | ~archive/slice-1.feature  |
| Rule: Admin configures tenant settings    | specified   | 2     | docs/spec/slice-2.feature |
| Rule: System exports audit log            | deferred    | —     | —                         |
```

The Rule column is parseable — the `reconciliation-agent` can grep `^  Rule:` in every `.feature` file and diff against the scope map. This reconciliation step catches drift in both directions:

- A `.feature` file contains a Rule not in the scope map → a new actor-goal pair was discovered during implementation. The reconciliation step surfaces it so the scope map is updated and the new Rule enters the backlog.
- The scope map has a Rule marked `specified` but the `.feature` file dropped it → a scenario was found unnecessary or merged into another Rule. The reconciliation step flags it so the scope map reflects reality.

Rules with status `deferred` have no `.feature` file. Rules with status `specified` point to a live `.feature` file on a feature branch or dev. Rules with status `implemented` point to an archived `.feature` file under `~archive/`.

**Slice workflow:**

1. The requirements-agent derives the scope map from the accepted proposal (all actor-goal pairs as Rules, all initially `deferred`).
2. For each slice, the requirements-agent produces a per-slice `.feature` file containing only the Rules being implemented in that slice, with full Scenarios. The scope map is updated: those Rules move from `deferred` to `specified`, with a link to the `.feature` file.
3. After implementation, the slice's `.feature` file is moved to `~archive/` and the scope map is updated: Rules move from `specified` to `implemented`.

The scope map is the persistent artifact that survives across slices. The `.feature` files are consumed during implementation and archived afterward.

**Effect on `derive-spec`:** The current `derive-spec` skill is superseded. The supplementary specs (`interface-contracts.md`, `entity-model.md`) are still produced — they carry structural facts the `.feature` file does not. The UC-XX document chain is no longer produced.

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

**Source inputs:** `docs/spec/<feature-name>.feature` (the Rule groupings provide the actor-goal matrix), `docs/spec/supplementary_specs/entity-model.md`, `docs/spec/supplementary_specs/interface-contracts.md`

**What it is not:** It is not a generic testing policy. It is not `testing-strategy.md` reformatted. It is a per-feature QA plan that tells the `qa-agent` how to specialise the generic strategy for this feature's specific contracts and risk profile.

**Effect on phase routing:** Phase 5 (QA) receives the `qa-strategy.md` as a formal input alongside `docs/spec/<feature-name>.feature` and `src/`. The qa-agent reads it at the top of its workflow and uses it to scope its Fagan inspection, security review, and bug hunt. The phase gate remains; the phase is better informed.

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
  2. Read the feature's Phase 1 outputs:
     - docs/spec/supplementary_specs/interface-contracts.md — new or changed interfaces
     - docs/spec/supplementary_specs/entity-model.md — new entities
  3. For each interface or entity declared by the feature:
     - Map it to the module(s) in the DSL it belongs to
     - Check if it targets a module not present in the DSL (new module)
     - Check if it changes a public interface already declared in the DSL
     - Check if it introduces or inverts a dependency direction between modules
  4. If any of the above is true → set impact.architecture_change: true, enter Phase 2
     Otherwise → skip Phase 2, go directly to Phase 3
```

This check uses Phase 1 outputs only — it does not depend on story files or implementation artifacts. After implementation, the existing `reconciliation-agent` reconciles `architecture.dsl` and the arc42 documentation against the code-as-built. This two-pass model — coarse structural routing from requirements, precise reconciliation from code — requires no new post-implementation infrastructure.

**Effect on workflow:**

- The `feature-addition` playbook's Step 0.3 routing decision gains a new "Mechanical check" step between the declaration and the decision.
- The `planning-agent` can receive this signal and include module-boundary work in Epic 0 if the feature is the first to touch a new module.
- The `reconciliation-agent` catches any module-graph changes that the Phase 1 check missed — a feature that appeared intra-module at requirements time but crossed a boundary during implementation is reconciled post-hoc.

**Enforcement:** The mechanical check is a deterministic script run by the orchestrating session before Phase 3 starts. Its output is a boolean `architecture_change` flag recorded in the phase handoff. The flag can be overridden manually (a stakeholder may want Phase 2 for documentation reasons even if the module graph is unchanged), but the default is the machine result.

## Scope

**In the first release:**

- `factory/skills/crap-score/SKILL.md` — CRAP scoring skill (cyclomatic complexity × coverage)
- `factory/skills/mutation-analysis/SKILL.md` — mutation analysis skill (mutant generation, test execution, survivor classification)
- `factory/skills/dependency-check/SKILL.md` — dependency-rule enforcement skill
- `factory/scripts/crap-score` — CLI wrapper for the CRAP skill, callable from premerge-check
- `factory/scripts/mutation-analysis` — CLI wrapper for the mutation skill, callable from premerge-check
- `factory/scripts/dependency-check` — CLI wrapper for the dependency skill, callable from premerge-check
- `factory/skills/derive-feature/SKILL.md` — new skill superseding `derive-spec`; uses Cockburn reasoning as internal process, outputs Gherkin directly with Rule-per-actor-goal structure
- `docs/spec/scope-map.md` — persistent scope map tracking all Rules across slices (status, slice assignment, feature file link)
- `docs/spec/<feature-name>.feature` — per-slice Gherkin feature file, structured by Cockburn Rules; transient (archived after implementation)
- `docs/spec/<feature-name>-gaps.md` — completeness report: actor-goal matrix, missing Rules, empty Rules, ambiguous wording (invoke via requirements-agent)
- `docs/spec/<feature-name>-qa-strategy.md` — per-feature QA strategy output (invoke via requirements-agent)
- Updated `factory/agents/requirements-agent.md`: replace `derive-spec` invocation with `derive-feature`; add scope map, `.feature` file, gaps report, and QA strategy to the outputs list
- Updated `factory/agents/developer-agent.md` workflow: developer produces code and tests; gate scripts run on committed artifacts; dispatcher spawns fresh developer for fixes
- Updated `factory/scripts/premerge-check`: add `crap-score`, `mutation-analysis`, and `dependency-check` as independent hard gates
- Updated `factory/rulebooks/templates/story.md`: add `quality-gates` field (which gates apply to this story's outputs)
- Updated `feature-addition.md` Step 0.3: mechanical module-graph check before Phase 2 routing
- Amended [testing-strategy.md](../../factory/rulebooks/conventions/testing-strategy.md): clarify that composite structural risk scores using coverage as one input are admissible as acceptance gates

**Delivery order within the release:** The scope is one release, but stories should be sequenced by dependency:

1. Amend `testing-strategy.md` (unblocks CRAP gate design)
2. `derive-feature` skill + QA strategy document (supersedes `derive-spec` for features; unblocks QA agent update)
3. `quality-gates` story field in `story.md` (unblocks dispatcher gate loop)
4. Three semantic gate scripts (`crap-score`, `mutation-analysis`, `dependency-check`)
5. Dispatcher gate-check loop extension in `implementation-agent`
6. `premerge-check` integration
7. Module-graph mechanical check + `feature-addition.md` Step 0.3 update

**Explicitly deferred:**

- Per-language mutation testing toolchain (the skill supports `mutmut` for Python as the reference implementation; other languages need tool discovery and threshold calibration)
- Per-language dependency-rule toolchain (different ecosystems have different tools; the skill structure is language-agnostic but the tool calls are not)
- Gate integration into the brownfield-onboarding pipeline (the onboarding reads `architecture.dsl` after it's built; the gates could run against the existing codebase to establish baseline quality scores)
- Automated module map update when a new directory is created (currently the DSL is the source of truth; there is no auto-update on `mkdir`)
- Mutation testing performance flags (`--fast-only`, `--jobs N`) — collect experience from real usage first

### 5. Gate Execution Lifecycle

Each gate fires at a distinct point in the workflow. The table below maps every gate to its trigger, its owner, and what blocks on failure.

| Gate                        | Fires when                                        | Owner                             | On failure                                                                             |
| --------------------------- | ------------------------------------------------- | --------------------------------- | -------------------------------------------------------------------------------------- |
| `crap-score`                | After developer-agent commits, before merge       | `implementation-agent` dispatcher | Dispatcher spawns fresh developer with gate report; story blocked after max iterations |
| `mutation-analysis`         | After developer-agent commits, before merge       | `implementation-agent` dispatcher | Same as `crap-score`; unresolved survivors filed as QA findings                        |
| `dependency-check`          | After developer-agent commits, before merge       | `implementation-agent` dispatcher | Same as `crap-score`                                                                   |
| `premerge-check` (existing) | Before merge, after all three semantic gates pass | `implementation-agent` dispatcher | Merge blocked until investigated                                                       |
| Module-graph check          | End of Phase 1, before Phase 3                    | Orchestrating session             | Routes to Phase 2 if module boundaries change; otherwise skips to Phase 3              |

The three semantic gates run **per-story, on each commit, before merge** — not on every push, not only at PR time. The module-graph check runs **once per feature, at the Phase 1 → Phase 3 boundary**.

### 6. Performance Model

**Mutation testing** is the most expensive gate. For a Python module with ~500 lines of production code and a fast test suite (~10s), `mutmut` generates approximately 200–400 mutants. At ~10s per mutant (running the relevant test subset), a full run takes 30–70 minutes. This is acceptable as a pre-merge gate that runs once per story, not on every save.

Mitigations for larger codebases (all deferred to collect real usage data first):

- `--fast-only`: stop at first killed test per mutant (reduces runtime ~3×)
- `--jobs N`: parallel mutant execution
- Scope restriction: run only against files changed in the story's diff

**CRAP scoring** and **dependency checking** are fast — seconds per invocation. They do not require performance mitigation.

**Gate invocation frequency:** Gates run after the developer-agent's commit, triggered by the dispatcher. They do not run on every keystroke, every push, or every CI build. A story that takes three fix iterations runs each gate three times.

### 7. Quality-Gates Story Field

The `quality-gates` field in [story.md](../../factory/rulebooks/templates/story.md) declares which semantic gates apply to the story's outputs. It is a list of gate names; each name corresponds to a CLI script under `factory/scripts/`.

```yaml
quality-gates:
  - crap-score
  - mutation-analysis
  - dependency-check
```

**Defaults:** When the field is absent, all three gates apply (fail-closed). A story may exclude a gate by listing only the applicable ones. Exclusion requires a justification line in the story's `notes:` field.

**Per-project overrides:** `docs/charter/house-rules.md` may set project-level defaults: which gates are active, threshold values for `crap-score`, and scope restrictions for `mutation-analysis`. The story-level field overrides the project default for that story only.

**Effect on dispatch:** The `implementation-agent` reads `quality-gates` from the story file before spawning the developer-agent. After the developer commits, the dispatcher runs only the listed gates. The `premerge-check` script also reads the field to know which gate results to require before allowing the merge.

## Resolved Questions

1. **Threshold calibration:** Thresholds live in `docs/charter/house-rules.md` as project-level settings. The Factory provides defaults; each project overrides in its charter. *Assumption: the project charter does not exist yet. Threshold defaults are hardcoded in each gate skill (`crap-score`, `mutation-analysis`, `dependency-check`) until a charter is scaffolded; the skills read `house-rules.md` overrides when present.*

2. **Mutation testing on slow test suites:** Deferred. The first release runs mutation testing in its default mode without `--fast-only` or `--jobs N` flags. Collect experience from real usage before deciding on fast-mode semantics and parallelisation defaults.

3. **Consolidated Gherkin file naming:** `docs/spec/<feature-name>.feature`. Discoverability over rename-stability — the file name matches the proposal and feature name as understood at requirements time.

4. **QA strategy document scoping:** One QA strategy document per consolidated `.feature` file. A cross-component feature that produces one `.feature` gets one `<feature-name>-qa-strategy.md` alongside it.

5. **Architecture mechanical check override authority:** Any human in the loop (the current session host) can override the mechanical module-graph check in either direction. The machine result is the default; the override is an explicit act by the session host, not an agent decision.

## Resolved Questions (from grilling 2026-08-24)

5. **Mutation testing scope restriction:** `mutation-analysis` runs against all production files in the story's diff, not only files the story's tests import. Excluding untested files defeats the gate's purpose — a surviving mutant in an untested file is the highest-signal finding the gate can produce. The performance cost is bounded by the diff size and acceptable for a once-per-story pre-merge gate.

6. **Gate iteration cap:** 3 iterations is the correct Factory default for the inner fix loop (developer commits → gate fails → fresh developer with gate report). When the cap is hit, the story receives `mark-failed --class acceptance_unmet`, feeding into the evidence-gated escalation predicate from [cost-aware-agent-delegation.md](cost-aware-agent-delegation.md). A stronger model gets one shot at the same gates with the same 3-iteration cap. Effective maximum: 6 developer spawns (3 x current tier + 3 x tier+1) before the story is terminal. The cap is tunable per project in `house-rules.md`.

7. **Module-graph check granularity:** A new entity in an existing module does not trigger Phase 2. The mechanical check tests module-graph topology only: new modules, changed public interfaces, and inverted dependency directions. A misplaced entity is a specification defect, caught by spec review or by the reconciliation-agent post-implementation — routing it through architecture review is the wrong mechanism.

8. **Scope-map reconciliation timing:** The reconciliation-agent diffs scope-map Rules against `.feature` file Rules when the feature branch merges to dev — one feature branch = one slice = one `.feature` file = one reconciliation pass. This avoids partial-Rule noise from individual story merges and aligns with the reconciliation-agent's Phase 5 pass on the branch.

9. **Auto-status of newly discovered Rules:** Rules found in the `.feature` file but absent from the scope map enter as `implemented` (the code exists; the scope map is descriptive). The reconciliation-agent files a finding for each discovery. If the PR against dev is opened by an agent, the PR body includes the discovery so the human reviewer sees the scope change before approving.

## Completion Criteria

- [ ] `factory/skills/crap-score/SKILL.md` exists and documents the CRAP scoring gate
- [ ] `factory/scripts/crap-score` runs against a test project with known high-CRAP functions and detects all of them
- [ ] `factory/skills/mutation-analysis/SKILL.md` exists and documents the mutation analysis gate
- [ ] `factory/scripts/mutation-analysis` runs against a test project, mutates every operator, and blocks until zero mutants survive — each survivor resolved by the developer (dead code removed or test added) or by QA (finding adjudicated); unresolved mutation findings block the merge
- [ ] `factory/skills/dependency-check/SKILL.md` exists and documents the dependency-rule gate
- [ ] `factory/scripts/dependency-check` runs against a project with a known dependency violation and flags it
- [ ] `premerge-check` blocks a merge when any of the three gate scripts fails independently
- [ ] `factory/skills/derive-feature/SKILL.md` exists and documents the Cockburn-as-Rules reasoning process, scope map lifecycle, and slice workflow
- [ ] `requirements-agent` produces `docs/spec/scope-map.md` with all Rules from the accepted proposal, each with status, slice, and feature-file link
- [ ] `requirements-agent` produces `docs/spec/<feature-name>.feature` with Rule-per-actor-goal structure for the current slice (no intermediate UC documents)
- [ ] `.feature` file Rules map 1:1 to actor-goal pairs; each Rule has at least one Scenario
- [ ] `reconciliation-agent` diffs scope-map Rules against `.feature` file Rules: surfaces new Rules in `.feature` not in scope map, and scope-map Rules marked `specified` but absent from `.feature`
- [ ] `requirements-agent` produces `docs/spec/<feature-name>-gaps.md` with actor-goal matrix and at least one detected gap (missing Rule or empty Rule)
- [ ] `requirements-agent` produces `docs/spec/<feature-name>-qa-strategy.md` with all template sections filled for a test feature
- [ ] `qa-agent` bug-hunt step reads `docs/spec/<feature-name>.feature` and references it in bug findings (not UC files)
- [ ] `feature-addition.md` Step 0.3 mechanical check skips Phase 2 for a feature that touches no module boundaries
- [ ] `feature-addition.md` Step 0.3 mechanical check routes to Phase 2 for a feature that creates a new module directory
- [ ] `testing-strategy.md` amended to admit composite structural risk scores as acceptance gates
- [ ] `story.md` template includes `quality-gates` field with documentation of defaults and override semantics
- [ ] `implementation-agent` dispatcher gate-check loop documented and implemented (commit → gate → fix-or-merge)
- [ ] Module-graph check script runs against `interface-contracts.md` and `entity-model.md`, not `story.outputs`
- [ ] All new artifacts pass `factory/scripts/validate`

## Guiding Rule

A feature is not ready for the planning phase unless the specification is a single-file artifact that a coder can read in one pass, the QA strategy is written from a QA manager's perspective (not derived from generic convention), and the module graph does not change without explicit architectural review.
