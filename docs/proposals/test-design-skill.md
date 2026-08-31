---
schema_version: 2
title: "Test Design Skill"
status: accepted
owner: md@matthiasdaues.de
created: 2026-09-01
updated: 2026-09-01
accepted: 2026-09-01
supersedes:

impact:
  scope: cross_component
  architecture_change: false  # manual override — no boundary change despite new gate script and YAML schema extension; mechanical detection flagged pre-existing architecture.dsl gaps
  external_contract_change: true
  boundaries:
    - factory/skills/create-backlog/SKILL.md
    - factory/skills/create-backlog-stories/SKILL.md
    - factory/skills/create-backlog-write-epics/SKILL.md
    - factory/agents/developer-agent.md
    - docs/charter/testing.yaml
    - factory/rulebooks/conventions/testing-strategy.md
    - factory/rulebooks/templates/charter-testing.yaml
    - factory/skills/crap-score/SKILL.md
    - factory/scripts/crap-score
    - factory/agents/implementation-agent.md
    - docs/adr/0012-dispatcher-owned-semantic-gate-loop.md

governance:
  assurance: elevated
  risk_domains:
    - reliability

estimate:
  as_of: 2026-09-01
  basis: judgment
  confidence: medium
  human_review_hours:
    min: 0.5
    max: 1.5
  normalized_tokens: unknown
  estimated_consumption:
    min: unknown
    max: unknown
    overhead_multiplier: unknown
    playbook: feature-addition
---

# Feature Request: Test Design Skill

## Summary

Build a `test-design` skill in the planning category that designs test scenarios for a backlog after epic slicing, before stories are cut. It enriches `backlog/epics.md` with per-contract test ownership, risk-class classification, and concrete failure scenarios. The `create-backlog-stories` skill (step 4) then carries these into individual story files as the developer-agent's TDD RED phase input. Risk classes — convention-level defaults in the testing strategy, overridable per project in `testing.yaml` — determine the failure-scenario format and test budget for each contract. A `gates` section in `docs/charter/testing.yaml` centralises gate configuration. A new `test-design-verify` gate script validates that owned contracts have assertions.

## Motivation

The developer-agent does TDD, but invents its own RED phase. Without guidance from the `.feature` contracts and scope map, it defaults to obvious happy-path and validation tests that pass, cover lines, keep CRAP low, and prove nothing about the actual behavioral invariants the specification intended. The merge gates — CRAP score, mutation testing — catch hollow tests only after the fact, when the implementation is already merged and the coverage numbers look healthy. By that point the cost of rework is high and the signal is ambiguous: the gate says "this function is risky" but not "this contract was never tested."

The `create-backlog-stories` skill (step 4 of the create-backlog sequence) already cross-references stories against the testing regime to populate the `tests:` frontmatter field and identify target suites. But it does not design tests — it discovers pre-existing ones and names where new ones should go. The developer-agent still decides *what* to test, and it decides wrong.

The test-design skill closes this gap. It reads the `.feature` contracts and scope map, assigns each contract to exactly one test owner, classifies it by risk class, and writes concrete failure scenarios. The developer-agent's RED phase becomes prescribed: it writes exactly the scenarios the test-design skill specified as failing tests, then implements to make them pass. The result is a suite where every test traces to a contract and every contract has one owner — not a suite where every story invented its own coverage.

## Core Principles

- Test design is a planning concern. The contracts that must be tested are known at epic-slicing time — waiting until implementation to decide what to test is why the tests are hollow.
- The `.feature` contracts are the authority for what to test. The test-design skill reads them; it does not invent scenarios beyond what the specification declares.
- One contract, one test owner. No contract is tested twice at the same layer. Non-owning stories that trace the same contract inherit the owner's tests as regression gates.
- The developer-agent's RED phase is prescribed. It writes exactly the failure scenarios the test-design skill specified — it never invents its own test cases.

## Design

### 1. New `test-design` skill

A new skill at `factory/skills/test-design/SKILL.md` in the planning category. It runs after `create-backlog-write-epics` (step 2 of the create-backlog sequence) and before `create-backlog-story-slices` (step 3). It is also invocable standalone on an existing backlog that already has `backlog/epics.md`.

**Inputs:**

- `backlog/epics.md` — confirmed epic slicing with building-block inventory
- `docs/spec/*.feature` — consolidated Gherkin behavioral contracts
- `docs/spec/scope-map.md` — contract IDs and architecture owners
- `docs/charter/testing.yaml` — suites, runners, markers, link to the testing strategy, and gate configuration

**Prerequisite:** `detect-test-regime` must have been run so that `testing.yaml` contains the `testing_strategy:` link and `suites:` records. If `testing_strategy:` is absent, the skill fails with a message telling the user to run `detect-test-regime` first.

**Procedure:**

01. Read the testing strategy document (linked from `testing_strategy:` in `testing.yaml`). Adopt its risk-class definitions, failure-scenario formats, budget rules, and admit-a-test gate as design constraints. Read project-level risk-class overrides from `testing.yaml`'s `risk_classes:` section if present; otherwise use the convention defaults from the testing strategy.
02. Collect all trace IDs across the epic's building-block inventory (DOM-01, OBS-04, ADR-005, etc.).
03. For each traced contract: read the `.feature` rule and its scenarios; read the scope-map architecture owner.
04. Assign one test owner per contract — the story that introduces the contract's infrastructure or first exercises it. Ownership is backlog-wide, resolved in a single pass across all epics.
05. Classify each contract by risk class using the precedence chain: `testing.yaml` `risk_classes:` overrides > project-linked strategy document > Factory convention defaults (see Design Details § Risk-class definitions).
06. For `critical` contracts: write `#### Failure scenarios` (Given/When/Then/Forbidden format) into the owning story's section within `epics.md`. These are the developer-agent's RED phase input — it writes exactly these as failing tests, then implements to make them pass.
07. For `standard` contracts: write concrete scenario text with expected inputs and assertions into the owning story's section within `epics.md`, within the failure-mode budget defined by the testing strategy.
08. `structural` contracts are linter-owned — the test-design skill emits no scenarios for them, as they are already covered by the deterministic linter layer.
09. For non-owning stories that trace the same contract: write a `#### Prior Tests` section listing the test modules and specific test functions from the owning story. The developer-agent runs these as its first RED check — its implementation must keep them green. No new tests for the non-owned contract.
10. Populate the `tests:` key with the test modules the story owns, not just touches.

**Output in `backlog/epics.md`:**

Each story's building-block entry in `epics.md` gains:

- `tests:` — only owned test modules
- `#### Test Design` section — owned contracts with risk class, layer, and concrete failure scenarios that serve as TDD RED input
- `#### Prior Tests` section — test modules and functions from earlier stories that the developer-agent must run first and keep green; these are inherited RED tests, not new work

### 2. Update to `create-backlog-stories` (step 4)

The `create-backlog-stories` skill already cross-references stories against the testing regime. This proposal adds: when `backlog/epics.md` contains test-design sections (produced by the test-design skill in step 2.5), carry them into the corresponding `backlog/ST-NNNN.md` story files:

- The `tests:` value from the epic building-block entry populates the story's `tests:` frontmatter field.
- The `#### Test Design` section is written verbatim into the story body.
- The `#### Prior Tests` section is written verbatim into the story body.

When `epics.md` contains no test-design sections (the skill was not run, or is invoked standalone later), `create-backlog-stories` behaves exactly as it does today — no change to existing behavior.

### 3. Update to `create-backlog` parent skill

The operational sequence table in `create-backlog/SKILL.md` adds a new row between phases 2 and 3:

| Phase | Skill         | What happens                         | Output                                     |
| ----- | ------------- | ------------------------------------ | ------------------------------------------ |
| 2.5   | `test-design` | Design test scenarios from contracts | Test-design sections in `backlog/epics.md` |

The skill is optional — the sequence proceeds to step 3 whether or not test-design was run. When test-design output exists in `epics.md`, step 4 carries it forward; when it does not, step 4 behaves as today.

The `create-backlog-write-epics` skill (step 2) adds a prompt at its end: "Before proceeding to step 3, you may invoke `test-design` to enrich the epics with test scenarios from the `.feature` contracts. This prescribes the developer-agent's TDD RED phase — without it, the developer-agent invents its own tests." This surfaces the option in the user's decision flow.

### 4. `gates` section in `docs/charter/testing.yaml`

Add a `gates` section to the existing `testing.yaml` schema, centralising gate configuration that currently lives in scattered places (story template defaults, house-rules overrides):

```yaml
gates:
  crap_score:
    enabled: true
    threshold: 8
  mutation_testing:
    enabled: false
```

The `crap-score` script currently contains a `read_threshold_from_house_rules()` function that looks for `docs/charter/house-rules.md`, but this file has never existed in the repository — the script falls back to a hardcoded default of 30. This proposal creates the first functioning external configuration point for the CRAP threshold: the `crap-score` skill reads `gates.crap_score.threshold` from `testing.yaml`, replacing the dead-code lookup path with a live one.

Mutation testing is disabled by default. The `enabled` flag flips to `true` when the project's mutation-testing infrastructure is ready (after a pilot validates the approach). The dispatcher reads `gates.mutation_testing.enabled` to decide whether to run the mutation-analysis gate.

### 5. `test-design-verify` gate script

A new gate script at `factory/scripts/test-design-verify` that validates test-design completeness.

**Resolution path:** The gate resolves each story's contract coverage through a multi-step chain:

1. Read the story's `traces:` frontmatter (e.g., `[DOM-01, OBS-04]`).
2. For each trace ID, look up the corresponding entry in `docs/spec/scope-map.md` to find the `.feature` file and rule that owns it.
3. Read the `.feature` file and collect the individual Scenarios under that rule.
4. Verify that each reachable Scenario has a corresponding entry in the story's `#### Test Design` section (for owning stories) or `#### Prior Tests` section (for non-owning stories).

**Validation rules:**

- Every `.feature` scenario reachable through the resolution chain has an owning test assertion in the story's `#### Test Design` section, or a waiver.
- Every non-owning story that traces a contract has a `#### Prior Tests` entry pointing to the owner's test module and function.
- Waivers reference passing owners — a waiver is not valid without naming the test that does own the contract.

**Waiver format:** A blockquote line within the `#### Test Design` section:

```markdown
> Waiver: DOM-01 — owned by tests/test_domain.py::test_entity_uniqueness
```

The gate parses these lines and verifies the named test module exists. A waiver without a resolvable owner path fails validation.

Exit codes follow the existing gate convention: 0 = pass, 1 = validation failure, 2 = configuration error.

The gate is a configuration item within the dispatcher's gate loop, not a competing sequence definition. ADR-0012 owns the gate execution ordering; the `gates` section in `testing.yaml` provides per-gate configuration (enabled/disabled, thresholds). The gate runs when test-design output exists in the story. When no test-design sections exist (the skill was not run), the gate is skipped — it does not block stories that predate the test-design skill.

### 6. Developer-agent behavior change

The developer-agent's step 3 (Red-Green-Refactor) currently says: "If `tests:` is absent or empty, follow the full Red-Green-Refactor cycle." This is where it invents its own RED phase.

This proposal adds a new condition before that fallback:

- If the story has a `#### Test Design` section, the developer-agent's RED phase comes entirely from that section. It writes exactly the failure scenarios specified — no additions, no substitutions. The section's risk-class and layer assignment determine where the test lives and what infrastructure it uses.
- If the story has a `#### Prior Tests` section, the developer-agent runs those tests first, before writing any new code. Its implementation must keep them green. These are pre-existing RED tests from the owning story.
- If neither section exists, the developer-agent falls back to the current behavior (inventing its own RED phase). This preserves backward compatibility with stories that predate the test-design skill.

### 7. Gate configuration in `testing.yaml`

The `gates` section in `testing.yaml` configures individual gates — enabled/disabled flags and thresholds. It does not define the execution ordering; ADR-0012 owns the dispatcher's gate sequence. The configuration items:

- **`crap_score`** — `enabled: true`, `threshold: 8`. Per-function complexity times coverage risk.
- **`mutation_testing`** — `enabled: false`. `standard`-class kill rate validates tests are not hollow. Flips to `true` when the project's mutation infrastructure is ready.
- **`test_design_verify`** — `enabled: true` (implicit; always on when test-design output exists in the story, skipped otherwise). Validated by the `test-design-verify` gate script.

The dispatcher (implementation-agent) currently hardcodes its gate list. This proposal requires the dispatcher to read `testing.yaml`'s `gates` section for per-gate enabled/threshold configuration instead. ADR-0012 is amended to document the `test_design_verify` gate as a conditional entry in the sequence — active when test-design output exists, skipped otherwise. Both the implementation-agent and ADR-0012 are in boundaries and scope.

## Scope

**In the first release:**

- The `test-design` skill at `factory/skills/test-design/SKILL.md`, with the procedure described in Design section 1.
- The `create-backlog` parent skill updated with the test-design step in its operational sequence table.
- The `create-backlog-write-epics` skill (step 2) updated to surface the test-design option before the user proceeds to step 3.
- The `create-backlog-stories` skill updated to carry test-design sections from `epics.md` into story files (Design section 2).
- The testing strategy at `factory/rulebooks/conventions/testing-strategy.md` extended with risk-class definitions (`critical`, `standard`, `structural`), their failure-scenario formats, and budget rules.
- The `gates` section added to `docs/charter/testing.yaml` and the template at `factory/rulebooks/templates/charter-testing.yaml`, including an optional `risk_classes:` override section.
- The `crap-score` skill and script updated to read the threshold from `testing.yaml`'s `gates.crap_score.threshold`, replacing the dead-code `read_threshold_from_house_rules()` path.
- The `test-design-verify` gate script at `factory/scripts/test-design-verify`.
- The developer-agent updated to consume test-design output as its RED phase (Design section 6).
- The implementation-agent (dispatcher) updated to read `testing.yaml`'s `gates` section for per-gate enabled/threshold configuration instead of hardcoding the gate list.
- ADR-0012 amended to document `test_design_verify` as a conditional gate in the dispatcher's sequence.

**Explicitly deferred (do NOT plan stories for these):**

- Automated Gherkin runner integration (behave, cucumber) — the test-design skill assigns test ownership and writes failure scenarios; it does not execute `.feature` files.
- Per-contract mutation-testing classification — covered by the accepted `test-gate-presence-over-test-execution` proposal's mutation-analysis rework.
- Visual test-coverage traceability dashboard — the traceability is in the stories and `epics.md`, not a separate UI.
- Retroactive test-design for stories that predate the skill — the developer-agent's fallback behavior handles these.

## Design Details

### Risk-class definitions

Risk classes group contracts by failure-mode complexity to determine the test-design treatment. They are orthogonal to layers: a layer says *where* the test lives; the risk class says *how thorough* the test design must be.

This proposal adds three default risk classes to `factory/rulebooks/conventions/testing-strategy.md`. Projects can override or extend them in `testing.yaml`'s `risk_classes:` section. Precedence: `testing.yaml` inline > project-linked strategy document > Factory convention defaults.

| Risk class   | Characteristics                                                               | Test-design treatment                                                    |
| ------------ | ----------------------------------------------------------------------------- | ------------------------------------------------------------------------ |
| `critical`   | Atomicity, concurrency, protocol compliance, security invariants, idempotency | Given/When/Then/Forbidden; must name the specific failure mode           |
| `standard`   | CRUD operations, input validation, read APIs                                  | Concrete scenarios with expected inputs and assertions; budget-capped    |
| `structural` | Declarative structure, formatting, schema conformance                         | Linter-owned; test-design skill emits no scenarios (deterministic layer) |

Projects may add custom risk classes — for example, a fintech project might add `financial` with double-entry invariants and a stricter failure-scenario format.

**Project override schema in `testing.yaml`:**

```yaml
risk_classes:
  critical:
    format: forbidden          # Given/When/Then/Forbidden
    budget: unbounded          # every distinct failure mode gets a scenario
  standard:
    format: scenario           # concrete input/output pairs
    budget: equivalence        # one per equivalence class + boundaries
  structural:
    format: linter             # no test-design output; linter owns it
  financial:                   # project-specific addition
    format: forbidden
    budget: unbounded
    requires:
      - double_entry_invariant
      - idempotent_retry
```

Fields per risk class:

- `format` — `forbidden` (Given/When/Then/Forbidden) or `scenario` (concrete inputs and assertions) or `linter` (no test-design output).
- `budget` — `unbounded` (every distinct failure mode) or `equivalence` (one per equivalence class plus boundaries and distinct failure modes).
- `requires` (optional) — named invariants the contract must demonstrate. Project-specific.

### Failure-scenario format

`critical` contracts use the Given/When/Then/Forbidden format:

```
Given <precondition describing the system state>
When <action that triggers the contract>
Then <expected outcome under normal conditions>
Forbidden <the specific failure mode this test catches>
```

The `Forbidden` line is the test's reason for existence. If the test designer cannot state what failure mode the test catches, the test should not exist.

`standard` contracts use concrete scenario text with expected inputs and assertions. The admit-a-test budget applies: one representative per equivalence class plus boundary values and distinct failure modes.

### Ownership resolution

When a contract spans multiple stories, ownership goes to the story that introduces the contract's infrastructure or first exercises it — determined by dependency order in `deps:`. A story that depends on the owner inherits the owner's tests as prior tests, not as new work.

When a contract spans multiple epics, the test-design skill resolves ownership in a single backlog-wide pass through `epics.md`. The skill sees all epics at once because the output lives in one file.

### Budget enforcement

The testing strategy's admit-a-test gate applies: a proposed test is admitted only if it protects a new observable contract, covers a distinct security or process boundary, exercises an integration seam the owning contract test cannot reach, or replaces weaker coverage while reducing total maintenance. The test-design skill enforces this budget before the developer-agent writes any code.

### Backward compatibility

Stories without test-design sections are handled by the developer-agent's existing behavior. The `create-backlog-stories` skill's existing testing-regime cross-reference continues to work. The `test-design-verify` gate skips stories that have no test-design output. No existing workflow breaks.

## Open Questions

None. The design resolves the key questions:

- **Where does the test-design output live?** In `backlog/epics.md`, carried into stories by step 4. One file, one pass, backlog-wide ownership resolution.
- **What happens to stories without test-design output?** The developer-agent falls back to its current behavior. The gate skips them.
- **Where does the CRAP threshold live?** In `testing.yaml`'s `gates.crap_score.threshold`, single source of truth. The dead-code `read_threshold_from_house_rules()` path is replaced.
- **Where do risk-class definitions live?** Convention-level defaults in `testing-strategy.md`, overridable per project in `testing.yaml`'s `risk_classes:` section. Same pattern as layers.
- **What about `testing_strategy:` and `suites:` in testing.yaml?** These are populated by `detect-test-regime`, not by this proposal. The test-design skill requires them as a prerequisite and fails with a clear message if they are absent.

## Completion Criteria

- The `test-design` skill exists at `factory/skills/test-design/SKILL.md` with the procedure described in Design section 1, including the `detect-test-regime` prerequisite guard.
- The testing strategy at `factory/rulebooks/conventions/testing-strategy.md` defines three default risk classes (`critical`, `standard`, `structural`) with their failure-scenario formats and budget rules.
- The `create-backlog` parent skill's operational sequence table includes the test-design step between phases 2 and 3.
- The `create-backlog-write-epics` skill (step 2) surfaces the test-design option before the user proceeds to step 3.
- The `create-backlog-stories` skill carries `tests:`, `#### Test Design`, and `#### Prior Tests` from `epics.md` into story files when those sections exist.
- `docs/charter/testing.yaml` and the template at `factory/rulebooks/templates/charter-testing.yaml` include a `gates` section with `crap_score` (enabled, threshold) and `mutation_testing` (enabled), and an optional `risk_classes:` override section.
- The `crap-score` skill and script read the threshold from `testing.yaml`'s `gates.crap_score.threshold`, replacing the dead-code `read_threshold_from_house_rules()` path.
- The `test-design-verify` gate script exists at `factory/scripts/test-design-verify`, resolves the trace → scope-map → `.feature` → Scenario chain, and validates that owned contracts have assertions, waivers (blockquote format with owner path) reference passing owners, and non-owning stories have `#### Prior Tests` entries.
- The developer-agent's step 3 consumes `#### Test Design` as its RED phase when present, runs `#### Prior Tests` first when present, and falls back to existing behavior when neither exists.
- Every `.feature` scenario reachable through an epic's traces has exactly one test owner across the backlog — no contract tested twice at the same layer.
- Every non-owning story that traces a contract has a `#### Prior Tests` entry pointing to the owner's test.
- The developer-agent never invents its own test cases when test-design output exists.
- The implementation-agent reads gate configuration (enabled/threshold) from `testing.yaml`'s `gates` section instead of hardcoding the gate list.
- ADR-0012 documents `test_design_verify` as a conditional gate — active when test-design output exists in the story, skipped otherwise.
- The `testing.yaml` template includes a `risk_classes:` section with the schema defined by example (format, budget, optional requires).

## Guiding Rule

The contracts say what to test; the test-design skill says who tests each one, how, and where. The developer-agent writes the tests it was told to write, not the tests it thinks of.

## Consult Review — 2026-09-01

Reviewer: proposal-review-agent
Reviewed commit: 898abfa85485c2577ff5faf1dc3e46cfc820708f

### Observations

**1. Missing boundaries: crap-score skill and script.**
The proposal explicitly changes where the crap-score gate reads its threshold — from `docs/charter/house-rules.md` to `testing.yaml`'s `gates.crap_score.threshold`. But neither `factory/skills/crap-score/SKILL.md` nor `factory/scripts/crap-score` appears in `impact.boundaries`. Both will need modification: the skill's documentation says "Threshold overrides from `docs/charter/house-rules.md`" and the script's `read_threshold_from_house_rules()` function implements that lookup. A planning agent reading this proposal would not generate a story for updating those files unless they are declared as boundaries.

**2. Cluster A/B definitions do not exist in the testing strategy.**
The test-design skill's procedure says "Classify each contract as Cluster A or Cluster B, using the testing strategy's cluster definitions" (step 5). The testing strategy at `factory/rulebooks/conventions/testing-strategy.md` defines five layers, the one-contract-one-owner principle, and the admit-a-test gate, but it does not define "Cluster A" or "Cluster B" by those names or by the risk characteristics described in the Design Details section. The same applies to the Given/When/Then/Forbidden failure-scenario format — it is original to this proposal, not existing vocabulary from the testing strategy. Consider one of two approaches: (a) add the cluster definitions and failure-scenario format to the testing strategy document first, then reference them from the skill, which means `testing-strategy.md` becomes a modified boundary; or (b) define them as original work in the test-design skill itself and remove the claim that the skill "uses the testing strategy's cluster definitions." Either way, a planning agent currently cannot implement step 5 because the referenced definitions do not exist at the referenced location.

**3. The test-design skill assumes `testing.yaml` fields that do not yet exist.**
The current `docs/charter/testing.yaml` has three fields: `test_command`, `test_staged_command`, and `layers.contract_test`. The test-design skill's procedure reads the testing strategy document "linked from `testing_strategy:` in `testing.yaml`" (step 1) and reads suites, runners, and markers from it. None of these fields exist in the current testing.yaml. The `testing_strategy:` and `suites:` fields are introduced by the `detect-test-regime` skill, and the `gates:` section is introduced by this proposal itself. This creates an implicit dependency chain: detect-test-regime must run before test-design can read its inputs. The proposal should either (a) list this dependency explicitly, (b) specify fallback behavior when `testing_strategy:` or `suites:` are absent, or (c) add detect-test-regime as a prerequisite step in the procedure.

**4. Merge gate battery (Design section 7) introduces a sequence that may conflict with the dispatcher.**
The gate sequence is currently owned by the implementation-agent dispatcher per ADR-0012. Section 7 describes a four-step "merge gate battery, read from `testing.yaml`'s `gates` section" with a defined ordering. This creates a potential second source of truth for the gate sequence: the dispatcher's gate loop (ADR-0012) and the `gates` section in testing.yaml. The test-gate-presence proposal (accepted) reduced the dispatcher's sequence from three gates to two. This proposal adds a third gate (test-design-verify) and describes the full four-gate ordering. Consider clarifying whether the `gates` section in testing.yaml configures individual gates (enabled/disabled, thresholds) or also defines the execution ordering. If it is configuration only, section 7 describes the dispatcher's behavior and should reference ADR-0012 as the authority for gate ordering. If it defines the ordering, then ADR-0012 needs updating and should be in boundaries.

**5. `house-rules.md` does not exist — the change is less a migration than a creation.**
The crap-score script contains a `read_threshold_from_house_rules()` function that looks for `docs/charter/house-rules.md`, but this file has never existed in the repository. The script falls back to its hardcoded default of 30. The proposal characterizes this as "The CRAP score threshold is currently read from `docs/charter/house-rules.md` as a fallback. This proposal makes `testing.yaml` the single source of truth." More precisely, this proposal creates the first functioning external configuration point for the CRAP threshold. The distinction matters for the scope item that says "Updated to read its threshold from testing.yaml instead of house-rules" — the "instead of" implies an active path being moved, whereas the practical effect is a dead-code path being replaced by a live one. A small clarification prevents a planning agent from looking for an existing integration to migrate.

**6. The `test-design-verify` gate's resolution path is underspecified.**
The gate script validates that "Every `.feature` scenario reachable through the story's traces has an owning test assertion." The resolution chain is: story `traces:` field (e.g., `DOM-01`) to `docs/spec/scope-map.md` entry to `.feature` file to individual Scenario. The proposal specifies the what (every scenario has an owning assertion) but not the how (how the gate script resolves trace IDs through the scope map to specific `.feature` scenarios). This multi-step resolution is the gate's core logic and should be described well enough for a planning agent to write a story for it. Similarly, the waiver mechanism ("a waiver is not valid without naming the test that does own the contract") needs enough structure to validate mechanically — what does a waiver look like in the story file? A YAML field? A comment? A section?

**7. Optional step discovery in the create-backlog sequence.**
The test-design skill is an optional step 2.5 that the user must invoke between steps 2 and 3. The parent skill's updated sequence table shows the row, but the parent skill's operational procedure does not describe when or how the user learns about this option. The current create-backlog flow ends each phase with "present to user for confirmation, then the user invokes the next skill." If test-design is optional, the parent skill or the step-2 skill needs to surface the option — for example, "Before proceeding to step 3, you may optionally invoke `test-design` to enrich the epics with test scenarios." Without this, the step exists in the sequence table but not in the user's decision flow.

**8. Estimate: consider populating `estimated_consumption`.**
The template expects `estimated_consumption` with an `overhead_multiplier` and `playbook`. The proposal sets both `normalized_tokens` and `estimated_consumption` to `unknown`. Given that the scope spans seven in-scope items across six boundary files, creating two new artifacts (a skill and a gate script) and modifying four existing ones, a rough estimate would help calibrate expectations even at low confidence. If the estimate genuinely cannot be made, `unknown` is fine — but the template also asks for `playbook`, which for a feature-addition would be `feature-addition`. Including the playbook even with `unknown` consumption helps future calibration.

**9. Consider whether `testing-strategy.md` belongs in boundaries.**
The proposal's Design Details section defines Cluster A/B and the failure-scenario format — definitions that are either derived from the testing strategy or extend it. If the intent is for these definitions to live only in the test-design skill, the testing strategy and the skill will diverge: the strategy defines layers and the admit-a-test gate; the skill adds clusters and failure scenarios on top, without the strategy knowing about them. If the intent is to add these to the testing strategy, the document should be in boundaries. Either path is fine, but the choice should be explicit so the planning agent knows whether there is a testing-strategy update story.

## Review — 2026-09-01

Reviewer: proposal-review-agent
Reviewed commit: 898abfa85485c2577ff5faf1dc3e46cfc820708f
Disposition: findings

### Findings

| ID      | Severity | Check | Status   | Finding                                                                                                                                                                                                                                                                                                                                                                                               |
| ------- | -------- | ----- | -------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| PROP-01 | minor    | 03    | resolved | Dispatcher integration underspecified: the design says "The dispatcher reads these flags and thresholds when executing its gate loop per ADR-0012" (sections 5 and 7), but neither the implementation-agent nor ADR-0012 appears in boundaries or scope. A planning agent cannot determine whether the dispatcher already reads `testing.yaml`'s `gates` section or needs code changes to support it. |
| PROP-02 | minor    | 03    | resolved | The `risk_classes:` override section in `testing.yaml` lacks a YAML schema example. The `gates` section provides a concrete YAML block; the `risk_classes:` schema must be derived from the convention-level table in Design Details. A planning agent writing the template update would need to infer field names and types.                                                                         |

### Summary

Six of eight checks pass cleanly: completion criteria are testable and specific, scope boundaries sharply partition in from deferred, impact classification is consistent with the design, all nine boundary references resolve, open questions are genuinely resolved with concrete design decisions, motivation justifies timing with a specific workflow gap, and the estimate is honest about uncertainty. Check 3 (design decomposable) surfaces two minor gaps — the dispatcher's relationship to the new `gates` config is described but not placed in scope or boundaries, and the `risk_classes:` override schema needs a concrete YAML example to be implementable without re-derivation.

## Review — 2026-09-01 (repeat pass)

Reviewer: proposal-review-agent
Reviewed commit: 898abfa85485c2577ff5faf1dc3e46cfc820708f
Disposition: clean

### Prior findings

| ID      | Severity | Check | Status   | Resolution                                                                                                                                                                                                                                                                                                         |
| ------- | -------- | ----- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| PROP-01 | minor    | 03    | resolved | `factory/agents/implementation-agent.md` and `docs/adr/0012-dispatcher-owned-semantic-gate-loop.md` added to boundaries. Scope includes implementation-agent update and ADR-0012 amendment. Design section 7 clarifies that `testing.yaml` provides per-gate configuration while ADR-0012 owns execution ordering. |
| PROP-02 | minor    | 03    | resolved | Design Details now includes a concrete YAML example with `format`, `budget`, and optional `requires` fields, plus field-level documentation. Completion criteria require the schema-by-example in the template.                                                                                                    |

### Eight checks

| Check | Name                             | Status | Notes                                                                                                                                                                                                             |
| ----- | -------------------------------- | ------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 01    | Completion criteria testable     | pass   | All 15 criteria name a file, field, or behavior to verify without asking the author.                                                                                                                              |
| 02    | Scope boundary sharp             | pass   | 11 in-scope items and 4 deferred items cleanly partition the space. No item reads as belonging to either list.                                                                                                    |
| 03    | Design decomposable              | pass   | Both prior gaps resolved. Each design section provides concrete detail sufficient for a planning agent to write INVEST stories without re-deriving the design.                                                    |
| 04    | Impact classification consistent | pass   | `cross_component` fits the 11-boundary span. `architecture_change: false` correct — gate loop extended, not restructured. `external_contract_change: true` matches new `testing.yaml` schema and agent contracts. |
| 05    | Boundary references exist        | pass   | All 11 boundary paths resolve at the reviewed commit.                                                                                                                                                             |
| 06    | Open questions genuine           | pass   | All five resolved with concrete design decisions. No padding disguised as uncertainty.                                                                                                                            |
| 07    | Motivation justifies timing      | pass   | Identifies a specific active workflow failure — hollow tests from uninstructed RED phase — present in every current dispatch.                                                                                     |
| 08    | Estimate plausible               | pass   | `unknown` for tokens and consumption is honest given the scope. `playbook: feature-addition` recorded. Human review hours (0.5–1.5) reasonable.                                                                   |

### Summary

All eight checks pass. Both prior findings are resolved: PROP-01 (dispatcher integration underspecified) addressed by adding the implementation-agent and ADR-0012 to boundaries and scope with concrete design text clarifying the configuration-vs-ordering relationship; PROP-02 (risk_classes schema example missing) addressed by a YAML example with field-level documentation. The proposal is ready to plan from.
