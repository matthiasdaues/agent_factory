# UC-10 — Manage CLI Adapters and Model Dictionaries

Realizes: AG-10

## Scope

Agent Session Orchestrator

## Level

User goal

## Primary Actor

Operator

## Supporting Actors

- **Adapter registry** — persists registered runtime CLIs and their executable paths.
- **Model dictionary store** — persists per-adapter tier-to-model mappings.
- **Concrete CLI adapter binaries** — provide validation probes and, where supported, model discovery.
- **Agent registry** — exposes each agent's declared `tier` metadata for later model resolution.

## Stakeholders & Interests

- **Operator** — wants to discover, register, inspect, and remove runtime CLIs without corrupting configuration.
- **Orchestrator core** — needs a valid adapter registry and a trustworthy per-adapter model dictionary for later invocations.
- **Agent authors** — want an agent's declared `tier` to resolve predictably to a concrete model through the selected adapter.
- **Project maintainers** — want configuration mutations to be atomic, diagnosable, and reversible by deliberate operator action.

## Preconditions

- The Operator is in menu mode and can open `configure > cli-list` or `configure > cli > {adapter}`.
- The registry and model-dictionary stores are readable and writable.
- The system knows the supported adapter types and their safe validation probes.
- For adapter-specific model management, the target adapter is already registered.

## Postconditions

**Success Guarantee**: The registry reflects each confirmed adapter addition, discovery, edit, and removal exactly once. Each registered adapter has an explicit model-dictionary state, including whether tier coverage is complete. Removed adapters leave no orphaned model-dictionary entries. The registry and dictionaries are persisted by the orchestrator for menu display and management; agent `tier` metadata is resolved through the selected adapter's dictionary at execution time by `factory/`, subject to the configured fallback policy.

**Minimal Guarantee**: If validation, discovery, or persistence fails, the prior registry and model-dictionary state remains intact. The system reports the failed action and the reason with enough precision for the Operator to correct it.

## Trigger

The Operator decides to manage runtime CLI adapters or their model dictionaries.

## Main Success Scenario

01. The Operator opens `configure > cli-list`.
02. The system displays the registered adapters and the actions `auto-detect`, `add adapter`, and `remove adapter`.
03. The Operator selects `auto-detect`.
04. The system scans `$PATH` for known adapter binaries, validates each candidate, and atomically registers any newly discovered supported adapters.
05. The Operator selects `add adapter`.
06. The system prompts for adapter name and binary path.
07. The Operator enters the logical adapter name and binary path.
08. The system validates the proposed registration and atomically persists the adapter.
09. The Operator opens `configure > cli > {adapter}` for the target adapter.
10. The system displays `list models`, `auto-detect`, `add model`, and `remove model`.
11. The Operator selects `auto-detect`.
12. The system queries the adapter for available models, presents the discovered model identifiers, and prompts for tier assignment where needed.
13. The Operator confirms the discovered mappings.
14. The system atomically persists the adapter's model-dictionary changes.
15. The Operator selects `list models`.
16. The system displays a table of `model id` and `tier`, together with the adapter's current tier-coverage status.
17. The Operator selects `add model`.
18. The system prompts for `model id` and `tier` (`economy`, `standard`, or `strong`).
19. The Operator enters the mapping.
20. The system validates the entry and atomically persists it in the adapter's model dictionary.
21. The Operator selects `remove model`, chooses an existing mapping, and confirms removal.
22. The system atomically removes the mapping and refreshes the displayed coverage state.
23. The Operator returns to `configure > cli-list > remove adapter` and selects an obsolete adapter.
24. The system atomically removes the adapter and its model dictionary.
25. The system returns to the configuration menu with the updated registry available for later tier-based model resolution.

## Extensions

- **4a. No supported adapter binaries are found on `$PATH`**
  - 4a1. The system reports that no supported adapters were found.
  - 4a2. The registry remains unchanged.
- **4b. A detected binary fails validation**
  - 4b1. The system skips that candidate, records the reason, and continues scanning.
  - 4b2. Invalid candidates are not registered.
- **8a. The proposed adapter name already exists, or the binary path is already registered**
  - 8a1. The system rejects the registration and explains the conflict.
  - 8a2. No state changes are persisted.
- **8b. The proposed binary path does not exist, is not executable, or does not identify a supported adapter**
  - 8b1. The system rejects the registration and reports the validation failure.
  - 8b2. No state changes are persisted.
- **11a. The selected adapter does not support model discovery**
  - 11a1. The system reports that model auto-detect is unavailable for that adapter.
  - 11a2. The model dictionary remains unchanged.
- **13a. The Operator cancels the discovered-model confirmation**
  - 13a1. The system discards the proposed discovery result.
  - 13a2. The model dictionary remains unchanged.
- **20a. The selected tier already has a registered model**
  - 20a1. The system asks whether to replace the existing mapping.
  - 20a2. If the Operator confirms, the system atomically replaces the mapping.
  - 20a3. If the Operator declines, the dictionary remains unchanged.
- **22a. Removing a model leaves one or more tiers unmapped**
  - 22a1. The system persists the removal.
  - 22a2. The system marks the dictionary incomplete and warns that later model resolution may halt on the missing tier unless adapter-default fallback is explicitly enabled.
- **24a. The Operator cancels adapter removal**
  - 24a1. The system leaves the adapter and its model dictionary unchanged.
- **\*a. Any persistence step fails after validation succeeded**
  - \*a1. The system rolls back the attempted registry or model-dictionary mutation.
  - \*a2. The system reports the failure and preserves the last committed configuration.

## Special Requirements

- The use case shall realize **FR-R1** through **FR-R8** directly: registry maintenance, adapter discovery, manual registration, removal, per-adapter model dictionaries, listing, dictionary CRUD, and capability-sensitive model auto-detect.
- The use case shall preserve the separation of concerns required by **FR-R9**: it shall not edit or reinterpret the model-matrix policy artifact while managing adapter dictionaries.
- The persisted adapter and dictionary state produced by this use case shall supply the runtime inputs consumed by **FR-R10**, **FR-R11**, and **FR-R12**.
- Adapter validation probes shall be non-destructive and shall not mutate project state.
- Model identifiers shall be treated as opaque adapter-defined strings.
- All registry and model-dictionary writes shall be atomic and durable.
- The model list view shall render a readable table containing, at minimum, `model id` and `tier`.

## Technology and Data Variations List

- Adapter registration may arise from `$PATH` auto-detection or manual entry of a binary path.
- Model discovery may be supported or unsupported, depending on the selected adapter.
- A model dictionary may be complete or incomplete; completeness affects later runtime eligibility, not the ability to save configuration.
- The tier vocabulary is fixed to `economy`, `standard`, and `strong`.
- Agent `tier` metadata is resolved against the selected adapter's dictionary by `factory/` at execution time, unless an allowed override or fallback rule applies.

## Frequency of Occurrence

Occasional. The Operator uses this use case when installing a new CLI, revising model assignments, or retiring an adapter.

## Open Issues

- None within this use case. Broader model-selection policy remains governed by the separate model-matrix specification and its validation workflow.

## Business Rules

- **BR-042** — An adapter may be registered only if its binary path resolves to an executable file and a safe validation probe identifies it as a supported adapter implementation.
- **BR-043** — Adapter registrations shall be unique by logical name; the same executable path shall not be registered twice under different names.
- **BR-044** — Each registered adapter owns exactly one model dictionary; creating or removing an adapter creates or removes that dictionary in the same atomic change set.
- **BR-045** — A model dictionary may contain at most one concrete model mapping for each tier `economy`, `standard`, and `strong`.
- **BR-046** — A model dictionary is complete only when all three tiers are mapped. Incomplete coverage may be saved, but later agent-tier resolution for an unmapped tier shall fail unless adapter-default fallback is explicitly enabled.
- **BR-047** — Model auto-detect is an optional adapter capability. If the adapter does not support discovery, the system shall report that fact and shall commit no configuration change.
- **BR-048** — Adapter auto-detect, manual registration, model add/remove, and adapter removal shall be all-or-nothing operations; a failed validation, discovery, or write shall leave the last committed registry state intact.
- **BR-049** — Agent `tier` frontmatter is the abstract input to model resolution; the adapter dictionary is the authoritative mapping from tier to concrete model identifier.

## Activity Diagram (Mermaid flowchart)

```mermaid
flowchart TD
    A[Open configure] --> B{cli-list or cli/{adapter}?}
    B -->|cli-list| C[Show adapters and actions]
    C --> D{Action}
    D -->|auto-detect| E[Scan PATH for known binaries]
    E --> F{Valid supported adapters found?}
    F -->|no| G[Report no changes]
    F -->|yes| H[Atomically register discovered adapters]
    D -->|add adapter| I[Prompt for name and binary path]
    I --> J{Binary valid and unique?}
    J -->|no| K[Reject registration]
    J -->|yes| L[Atomically persist adapter]
    D -->|remove adapter| M[Select adapter]
    M --> N[Atomically remove adapter and dictionary]
    B -->|cli/{adapter}| O[Show model actions]
    O --> P{Action}
    P -->|list models| Q[Display model id and tier table]
    P -->|auto-detect| R{Discovery supported?}
    R -->|no| S[Report unsupported; no change]
    R -->|yes| T[Query adapter and assign tiers]
    T --> U[Atomically persist discovered mappings]
    P -->|add model| V[Prompt for model id and tier]
    V --> W[Atomically persist mapping]
    P -->|remove model| X[Select mapping]
    X --> Y[Atomically remove mapping and refresh coverage]
```

## Acceptance Criteria (Gherkin BDD)

```gherkin
Feature: Manage CLI adapters and their model dictionaries

  Scenario: Auto-detect supported adapters on PATH
    Given known adapter binaries are present on the Operator's PATH
    And those binaries pass adapter validation
    When the Operator selects configure > cli-list > auto-detect
    Then the system registers each newly discovered supported adapter
    And it persists the registry atomically

  Scenario: Reject manual registration with an invalid binary
    Given the Operator is adding an adapter manually
    When the Operator enters a binary path that is missing, not executable, or unsupported
    Then the system rejects the registration
    And the registry remains unchanged

  Scenario: Add or replace a tier mapping for an adapter
    Given a registered adapter named "copilot"
    When the Operator selects configure > cli > copilot > add model
    And enters model id "gpt-5.4-mini" with tier "economy"
    Then the system persists that tier mapping atomically
    And list models shows "gpt-5.4-mini" in tier "economy"

  Scenario: Report unsupported model discovery without side effects
    Given a registered adapter that does not implement model discovery
    When the Operator selects configure > cli > that-adapter > auto-detect
    Then the system reports that model auto-detect is unsupported
    And the adapter's model dictionary remains unchanged

  Scenario: Warn when a dictionary loses tier coverage
    Given a registered adapter with mappings for economy, standard, and strong
    When the Operator removes the only model mapped to tier "strong"
    Then the system persists the removal atomically
    And it marks the dictionary incomplete
    And it warns that later tier-based model resolution may fail

  Scenario: Remove an adapter and its dictionary together
    Given a registered adapter with a persisted model dictionary
    When the Operator selects configure > cli-list > remove adapter for that adapter
    Then the system removes the adapter registration
    And it removes the associated model dictionary in the same atomic change

  Scenario: Use the selected adapter dictionary for later runtime resolution
    Given an agent declares tier "standard" in its frontmatter
    And the selected adapter maps tier "standard" to a concrete model id
    When factory/ later executes that agent through the selected adapter
    Then it resolves the agent's default model through that adapter dictionary
    And it halts on a missing required tier unless configured fallback permits adapter default
```
