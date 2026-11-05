---
scope: global
---

# EPICs — Core Artifact Ownership

Proposal trace: [core-artifact-ownership.md](../docs/proposals/core-artifact-ownership.md)
Specification trace: [core-artifact-ownership.feature](../docs/spec/features/core-artifact-ownership.feature), [gaps report](../docs/spec/work/core-artifact-ownership-gaps.md), [interface-contracts.md § Core Artifact Ownership Contracts](../docs/spec/interface-contracts.md#core-artifact-ownership-contracts), [validation-rules.md § Ownership and drift reports](../docs/spec/validation-rules.md#ownership-and-drift-reports-core-artifact-ownership-br-056br-066)
Architecture trace: [ADR-0027](../docs/adr/0027-split-the-requirements-agent-by-artifact-family.md), [ADR-0028](../docs/adr/0028-declared-review-and-core-list-check-ownership.md), [ADR-0029](../docs/adr/0029-per-story-drift-reports-block-the-wave-close.md), [arc42 § 8.17](../docs/arc42/08_crosscutting_concepts.md#817-artifact-ownership-one-producer-one-declared-review), [arc42 § 5.10](../docs/arc42/05_building_block_view.md#510-level-2-component-view----factory-agents), [arc42 § 6.11](../docs/arc42/06_runtime_view.md#611-specification-handoff-between-producers), [arc42 § 6.12](../docs/arc42/06_runtime_view.md#612-spec-feedback-and-wave-close), [ADR-0030](../docs/adr/0030-reconciliation-rows-return-through-the-documentation-update-playbook.md), [arc42 § 6.13](../docs/arc42/06_runtime_view.md#613-reconciliation-backfeed)
QA strategy trace: [core-artifact-ownership-qa-strategy.md](../docs/spec/work/core-artifact-ownership-qa-strategy.md)

Dependency order: E1 and E4 start in parallel. E1 → E2 → E3 → E6. {E1, E4} → E5. {E1, E4} → E7 → E8. {E3, E4, E7} → E9 → E10. {E2, E7, E10} → E11. {E9, E10, E11} → E12 comes last. E2 and E7 both edit `agents/requirements-agent.md`, so their stories merge one after the other. Two stories leave their EPIC's order: ST-0359 (E8) has no dependency and runs in wave 1, and ST-0366 (E4) waits for ST-0363 (E10).

## Story waves

Every story regenerates `INDEX.yaml`, so the stories of one wave are developed in parallel and merged one at a time.

| Wave | Stories                                     | Merge order inside the wave                                                       |
| ---- | ------------------------------------------- | --------------------------------------------------------------------------------- |
| W1   | ST-0346, ST-0352, ST-0355, ST-0359          | any                                                                               |
| W2   | ST-0347                                     | —                                                                                 |
| W3   | ST-0348, ST-0353, ST-0357                   | any                                                                               |
| W4   | ST-0349, ST-0350, ST-0354, ST-0358, ST-0365 | ST-0358 and ST-0365 share `implementation-agent.md`; ST-0349 merges after ST-0357 |
| W5   | ST-0351, ST-0360                            | ST-0360 merges after ST-0365, because both edit `developer-agent.md`              |
| W6   | ST-0356, ST-0362                            | both edit `spec-review-agent.md`, so they merge one after the other               |
| W7   | ST-0361, ST-0363                            | any                                                                               |
| W8   | ST-0364, ST-0366                            | any                                                                               |
| W9   | ST-0367                                     | —                                                                                 |

Every story carries `quality-gates: []` until ST-0359 ships and the factory is reinstalled with `update-factory`. The installed `premerge-check` ignores `testing.yaml`, and without the field it requires a mutation result that no script writes before ST-0365.

The layout stories ST-0325 to ST-0345 are all `done`, so the order of [DEC-05](../docs/proposals/core-artifact-ownership.md#order-after-the-core-artifact-layout) no longer constrains this backlog. The first story ID is `ST-0346`. Phase 4 rescans `backlog/` before it writes the first story, because parallel sessions may take IDs in the meantime.

## Terms used in every EPIC

- **Core artifact and seam file.** A core artifact is a file in `docs/spec/` that people edit and other files derive from, such as `entity-model.md`. A seam file describes how agents work in the project: `docs/agent-context.md` and `docs/testing.yaml`.
- **Producer.** The one agent whose output declaration matches a core artifact or seam file. Each file has exactly one.
- **Declared review.** The `reviewed_by:` list on the producer's output declaration. It names agents, `stakeholder`, or both.
- **Core list.** The new file `packages/factory/rulebooks/core-artifacts.yaml`. It lists the thirteen core and seam entries with their path pattern, sample path, family, and whether a project may lack the file.
- **Sample path.** One concrete path that an entry's pattern matches, such as `docs/spec/features/example.feature`. The contract test and `index-lint` match patterns through it.
- **Contract test.** The pytest test that reads the core list and `INDEX.yaml` and checks one producer with a declared review per entry.
- **Expected-failure list.** The strict list of core list entries that have no valid producer yet. The contract test expects each listed entry to fail. A listed entry that passes fails the test.
- **Working output.** Files in `docs/spec/work/`, `docs/reviews/`, and `docs/findings/`. They may have several writers, as long as each writer declares the path.
- **Drift row.** One row of a spec-feedback report (`docs/spec/work/spec-feedback-<story-id>.md`) or a reconciliation report (`docs/reviews/reconciliation-<date>.md`). Its columns are Artifact, Drift, Evidence, Owner, and Status. Status is `open`, `fixed`, `confirmed`, or `rejected`.
- **Owner of a finding.** The agent that acts on the finding next, recorded in the finding's `owner:` field.

## Rules that hold for every EPIC

- Source edits go to `packages/factory/`, never to `.agent-factory/factory/`.
- `index-lint --check` passes after every story (CC-31). A story that changes an agent definition regenerates `INDEX.yaml` in the same commit.
- A story that adds `reviewed_by:` with an agent name also makes that agent declare the artifact as a required or context input. Otherwise the reviewer check of E1 fails the story.
- The expected-failure list only shrinks. A story deletes an entry in the same commit that makes the entry pass. No story adds an entry.
- No story plans the gates for `entity-model.md`, `schemas/*`, or `testing.yaml`, DBML, a blocking glossary gate, or eligibility on confirmed inputs. The proposal defers all four.
- No Factory agent declares or writes a mutation tool's configuration file. It lives in the project's own files.
- Tests carry `@pytest.mark.spec("CAO-NN")` and their layer marker. The first story with a test adds `CAO-*` to the `spec` marker description in `pyproject.toml`.
- Completion criteria are numbered CC-01 to CC-31 in the order of the proposal's [Completion Criteria](../docs/proposals/core-artifact-ownership.md#completion-criteria).

## Before the merge into dev

Decided by the stakeholder on 2026-11-04. These run after the last wave, before `feature/core-artifact-ownership` merges into `dev`:

1. **Cleanup pass:** each open spec-feedback row in the stories of this backlog goes to its owner, who fixes it; the reviewer sets `confirmed` or `rejected` (BR-061). This includes the stale anchor in `state-machine-notation.md` (ST-0353 row 3) the wording of `implement-issue` Step 5, which still says the developer updates the specification, and the manual-mode sentence of the proposal (§ Spec feedback during implementation), which must follow DEC-35 as ST-0362 does. First move the rows that waves 1 to 5 wrote into story files into `docs/spec/work/spec-feedback-<story-id>.md`, where `close-wave` reads them after ST-0361.
2. **Acceptance runs with the stakeholder present:** CAO-04-AC-01, the domain-modeling agent's first run on the factory, CAO-10-AC-01, the test-strategy agent's first run, and CAO-05-AC-01, the confirmation of one area's terms (ST-0351). One session for all three, together with the skipped demos of ST-0349, ST-0350 and ST-0354.

## E1: Check every core artifact's producer and review

### Why this EPIC exists

Today nothing shows who produces a core file or who confirms it. Five agents match `docs/spec/entity-model.md` with their output patterns, and no agent declares `dependency-rules.dsl`. Without a list of the core and a check against it, every later EPIC changes ownership blind. This EPIC gives the factory maintainer that list and two checks, and it records today's gaps as expected failures that the later EPICs remove.

### Actor Goals

- Factory maintainer finds exactly one producer for every core and seam artifact.
- Factory maintainer sees every declared review checked against the reviewer's inputs.

### Demo

1. Run `index-lint`. `INDEX.yaml` shows `reviewed_by: [spec-review-agent]` on the requirements agent's `docs/spec/features/{name}.feature` and `edits: wording` on the lector agent's `docs/**/*.md`.
2. Change the requirements agent's `reviewed_by:` on the feature files to `[qa-reviewer]` and run `index-lint --check`. It exits 1 and names `qa-reviewer` as no agent.
3. Change it to `[developer-agent]`. `index-lint --check` exits 1, because the developer agent does not declare the feature files as an input. Revert the change.
4. Run `uv run pytest tests/factory/test_core_artifact_ownership.py`. It passes. The output lists `docs/spec/architecture.dsl` as passing and `docs/spec/entity-model.md` as an expected failure with four matching producers.
5. Add `reviewed_by: [architecture-review-agent]` to a copy of an agent that declares `docs/spec/dependency-rules.dsl`, so the entry passes. The test fails and names `docs/spec/dependency-rules.dsl` as an expected failure that now passes. Remove the copy.

### Scope

**In:**

- `index-lint` reads `reviewed_by:` and `edits:` on every output declaration and writes both into `INDEX.yaml` beside `path_pattern`, `validator`, and `required`.
- The reviewer check in `index-lint`. It fails on a `reviewed_by:` entry that is neither `stakeholder` nor an existing agent. It also fails on an agent that declares the artifact neither as a required nor as a context input. The check matches the producer's pattern and the reviewer's pattern through the sample path of the core list entry, and a `{name}` placeholder matches like `*` (CAO-G06, CAO-G14).
- The new core list `packages/factory/rulebooks/core-artifacts.yaml` with the thirteen entries of [interface-contracts.md § core-artifacts.yaml](../docs/spec/interface-contracts.md#packagesfactoryrulebookscore-artifactsyaml).
- `reviewed_by:` on the four declarations whose producer does not change: `scope-map.md` and the feature files (requirements agent), `architecture.dsl` (architecture agent), and `agent-context.md` (Virgil). `edits: wording` on the lector agent's `docs/**/*.md` (the lector half of CC-20).
- The contract test. For each entry it counts the output declarations whose pattern matches the sample path, skips `edits: wording`, and fails on zero matches, on more than one, and on a missing or empty `reviewed_by:`. Working output never counts.
- The expected-failure list, as Option A of the phase-1 approval (2026-11-03) decided. It holds one entry per core list entry that fails today, with the EPIC that removes it:

| Entry                                                                                                                                                                               | Fails today because                                                                    | Removed by |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- | ---------- |
| `docs/spec/schemas/*`                                                                                                                                                               | no producer                                                                            | E2         |
| `docs/spec/dependency-rules.dsl`                                                                                                                                                    | no producer                                                                            | E5         |
| `docs/testing.yaml`                                                                                                                                                                 | Virgil declares it without a review                                                    | E7         |
| `scope-map.md`, `features/*.feature`, `areas/*.md`, `glossary.md`, `entity-model.md`, `state-machines.md`, `validation-rules.md`, `interface-contracts.md`, `docs/agent-context.md` | the developer, implementation, and reconciliation agents match them with wide patterns | E10        |

**Out:**

- Every other `reviewed_by:` declaration. Each producer EPIC adds its own.
- The working-output declarations of the writers (E9). E1 only makes the contract test skip working output.
- A gate for any core artifact (DEC-08).

### Dependencies

None. E1 is the base of every other EPIC except E4.

### Boundaries

- Script: `packages/factory/scripts/index-lint` (`build_agents_data`, `_render_structured_field`)
- New file: `packages/factory/rulebooks/core-artifacts.yaml`
- Agent definitions: `requirements-agent.md`, `architecture-agent.md`, `virgil.md`, `lector-agent.md` in `packages/factory/agents/`
- Catalog: `packages/factory/INDEX.yaml`
- Contracts: [interface-contracts.md § Output declaration fields](../docs/spec/interface-contracts.md#output-declaration-fields), [§ index-lint reviewer check](../docs/spec/interface-contracts.md#index-lint-reviewer-check)
- Tests: `tests/factory/test_index_lint.py` (extend), `tests/factory/` (new contract test file)

### Domain Rules

- An agent that only reads an artifact never counts as its review.
- `stakeholder` needs no input declaration.
- A declaration with `edits: wording` is never a producer.
- A wide pattern that matches a sample path counts as a producer.
- The contract test passes only while the expected-failure list is exact: every listed entry fails, and every unlisted entry passes.

### Size

2 stories.

### Building-Block Inventory

| Story   | Capability                                                    | Tier     | Size | Goal                                                                                                                                                                         | Basis                                                                                                                                                      |
| ------- | ------------------------------------------------------------- | -------- | ---- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| ST-0346 | Declare a review and see `index-lint` check the reviewer      | standard | M    | The factory maintainer finds `reviewed_by:` and `edits:` in `INDEX.yaml`, and `index-lint --check` fails on a reviewer that is no agent or does not read the artifact.       | `index-lint` renders `path_pattern`, `validator`, and `required` only. Adds the two fields, the core list, the reviewer check, and five declaration edits. |
| ST-0347 | Find each core artifact without exactly one reviewed producer | standard | M    | The factory maintainer runs the contract test and sees each core list entry pass, or fail with its matching producers, while the expected-failure list records today's gaps. | No contract test exists. Reads ST-0346's core list and fields. Adds the test with fixture catalogs and the expected-failure list.                          |

### Testability Assessment

Both goals produce observable results: the content of `INDEX.yaml`, the exit code and message of `index-lint --check`, and the pass or failure of the contract test with the names of the matching producers. Tests instrument `index-lint` as a subprocess on fixture agent directories, and the contract test's counting rule on fixture catalogs. The real-catalog check uses the factory's own `INDEX.yaml`. No red flag remains: Option A turns "every artifact has one producer" into an exact, bounded list that each EPIC shrinks.

### Ownership Resolution

| Contract                                                                                           | .feature Rule                                                                                                       | Owner   | Rationale                                                        |
| -------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- | ------- | ---------------------------------------------------------------- |
| CAO-02-IT-01: `index-lint` writes `reviewed_by:` and `edits:` into `INDEX.yaml`                    | core-artifact-ownership.feature#Factory maintainer sees every declared review checked against the reviewer's inputs | ST-0346 | introduces both fields in `index-lint`                           |
| CAO-02-CT-01: unknown reviewer and reviewer without the input fail; `stakeholder` and context pass | core-artifact-ownership.feature#Factory maintainer sees every declared review checked against the reviewer's inputs | ST-0346 | introduces the reviewer check                                    |
| CAO-02-CT-02: the reviewer check matches `{name}` and `*` patterns by sample path                  | core-artifact-ownership.feature#Factory maintainer sees every declared review checked against the reviewer's inputs | ST-0346 | introduces sample-path matching with the core list               |
| CAO-02-LN-01: `index-lint --check` exits 0 on the factory's agent definitions                      | core-artifact-ownership.feature#Factory maintainer sees every declared review checked against the reviewer's inputs | ST-0346 | first story whose catalog carries the new fields                 |
| CAO-02-CT-03: `reviewed_by: []` fails, also when another agent reads the artifact                  | core-artifact-ownership.feature#Factory maintainer sees every declared review checked against the reviewer's inputs | ST-0347 | introduces the contract test that counts reviews                 |
| CAO-01-CT-01: one reviewed producer passes; none, two, or a wide pattern fails                     | core-artifact-ownership.feature#Factory maintainer finds exactly one producer for every core and seam artifact      | ST-0347 | introduces the producer count                                    |
| CAO-01-CT-02: a producer declaration without `reviewed_by:` or with an empty list fails            | core-artifact-ownership.feature#Factory maintainer finds exactly one producer for every core and seam artifact      | ST-0347 | introduces the review check of the contract test                 |
| CAO-01-CT-03: `edits: wording` is skipped; `{name}` matches the sample path                        | core-artifact-ownership.feature#Factory maintainer finds exactly one producer for every core and seam artifact      | ST-0347 | introduces the skip rule                                         |
| CAO-01-LN-01: the real catalog gives each of the thirteen entries its producer and review          | core-artifact-ownership.feature#Factory maintainer finds exactly one producer for every core and seam artifact      | ST-0347 | introduces the real-catalog check with the expected-failure list |
| CAO-17-CT-01: several declarations of `term-candidates.md` produce no producer finding             | core-artifact-ownership.feature#Factory maintainer sees every writer of shared working output declare its path      | ST-0347 | the contract test's working-output rule lands here               |

## E2: Hand domain structure to the domain-modeling agent

### Why this EPIC exists

Today the requirements agent writes the scope map, the feature files, and every structure file. The structure files carry the most downstream cost, and no one reviews them as a family. This EPIC creates the domain-modeling agent (a new strong-tier agent that owns the glossary, the entity model, and the structure files) and narrows the requirements agent to scope and behaviour. After it, `intent select` routes the operator to the domain-modeling agent once a feature file exists.

### Actor Goals

- Requirements agent keeps scope and behaviour only.
- Domain-modeling agent produces the domain structure family.

### Demo

1. In a fixture project with `docs/spec/scope-map.md` and no feature file, run `intent select`. The domain-modeling agent is not eligible, and the output names `docs/spec/features/*.feature`.
2. Add `docs/spec/features/payments.feature` and run `intent select` again. The domain-modeling agent is eligible.
3. Read the requirements agent's handoff. It names the domain-modeling agent as the next producer.
4. Run `uv run pytest tests/factory/test_core_artifact_ownership.py`. It passes, and `docs/spec/schemas/*` is no longer on the expected-failure list.
5. Run the domain-modeling agent on the factory with the stakeholder present. It writes `docs/spec/glossary.md` and changes `docs/spec/entity-model.md` at its existing path, and `statemachine-lint` passes.

### Scope

**In:**

- New `packages/factory/agents/domain-modeling-agent.md` at the strong tier. It requires `scope-map.md` and a feature file. Its context inputs are `glossary.md`, `docs/spec/work/term-candidates.md`, `src/**/*`, and `docs/agent-context.md`.
- Its six outputs with `reviewed_by:`. `glossary.md` (`[spec-review-agent, stakeholder]`) and `entity-model.md` are `required: true`. `state-machines.md`, `validation-rules.md`, `interface-contracts.md`, and `schemas/*` are written only when the domain has state machines, rules, contracts, or structured payloads.
- Its workflow: a step that writes `schemas/*` for payload columns with inner structure, and a step that writes each state machine as pseudocode and derives its Mermaid diagram. The handoff names the spec-review agent, and also the architecture agent after a change to `entity-model.md` or `state-machines.md`.
- The spec-review agent's input declarations for the six files: `glossary.md` and `entity-model.md` as required inputs, the other four as context inputs. The reviewer check of E1 needs them in the same story. The `inspect-spec` checks stay with E6.
- The requirements agent drops its structure-file outputs, step 1d "Produce supplementary specs", and `capture-context`. It gains `reviewed_by: [spec-review-agent]` on `areas/*.md`, a step that writes an area spec where the stakeholder asks for more depth, and a handoff that names the domain-modeling agent.
- The `schemas/*` entry leaves the expected-failure list.

**Out:**

- The QA strategy step and `qa-strategy-from-spec` (E7). The requirements agent keeps them until the test-strategy agent exists.
- Term candidates and the confirmation of terms (E3).
- The working-output declarations of the two report paths (E9).
- The playbook steps that name the new owner (E11).

### Dependencies

E1, for `reviewed_by:`, the reviewer check, and the contract test.

### Boundaries

- Agents: `packages/factory/agents/domain-modeling-agent.md` (new), `requirements-agent.md`, `spec-review-agent.md`
- Skill: `packages/factory/skills/domain-modeling/SKILL.md`
- Routing: `packages/factory/INDEX.yaml`, `packages/factory/scripts/intent`
- Gate used in the demo: `statemachine-lint`
- Runtime view: [arc42 § 6.11](../docs/arc42/06_runtime_view.md#611-specification-handoff-between-producers)

### Domain Rules

- Only the domain-modeling agent declares a domain-structure file as an output.
- The domain-modeling agent always writes `glossary.md` and `entity-model.md`, even when the glossary holds no term yet.
- A structure file that already exists keeps its path. The domain-modeling agent takes it over without a move.
- The handoff names the architecture agent only after a change to `entity-model.md` or `state-machines.md`.

### Size

2 stories.

### Building-Block Inventory

| Story   | Capability                                                      | Tier     | Size | Goal                                                                                                                                                                                 | Basis                                                                                                                                                   |
| ------- | --------------------------------------------------------------- | -------- | ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| ST-0348 | Start the domain-modeling agent once a feature file exists      | strong   | L    | The human operator sees the domain-modeling agent in `intent select` after a feature file exists, and the agent writes the glossary and the entity model with their declared review. | No agent exists; the `domain-modeling` skill does. Adds the agent, its six outputs, its workflow steps, and the spec-review agent's input declarations. |
| ST-0349 | Keep the requirements agent to scope, behaviour, and area specs | standard | M    | The requirements agent declares only scope-and-behaviour core outputs, writes an area spec where the stakeholder asks for depth, and hands off to the domain-modeling agent.         | The requirements agent declares all structure files and lists `capture-context`. Removes both, adds the area spec step and the handoff.                 |

### Testability Assessment

The declarations and the eligibility are observable: the agent definitions, `INDEX.yaml`, the contract test's expected-failure list, and the output of `intent select` on fixture projects. The workflow steps are checked as text, so a test sees that the definition states the schema step and the handoff rule, not that a session follows them. That red flag is accepted: the first run of the agent on the factory, CAO-04-AC-01, is a manual check recorded in ST-0348 with the stakeholder present.

### Ownership Resolution

| Contract                                                                                                       | .feature Rule                                                                              | Owner   | Rationale                                  |
| -------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------ | ------- | ------------------------------------------ |
| CAO-04-LN-01: the domain-modeling agent's tier, inputs, outputs, optional-file condition, schema step, handoff | core-artifact-ownership.feature#Domain-modeling agent produces the domain structure family | ST-0348 | introduces the agent                       |
| CAO-04-IT-01: `intent select` reports the agent as not eligible without a feature file                         | core-artifact-ownership.feature#Domain-modeling agent produces the domain structure family | ST-0348 | introduces the agent's required inputs     |
| CAO-04-AC-01: the first run writes the glossary and the entity model; `statemachine-lint` passes               | core-artifact-ownership.feature#Domain-modeling agent produces the domain structure family | ST-0348 | introduces the agent's workflow            |
| CAO-03-LN-01: the requirements agent's core outputs, `capture-context` removal, area spec step, and handoff    | core-artifact-ownership.feature#Requirements agent keeps scope and behaviour only          | ST-0349 | introduces the narrowed requirements agent |

## E3: Confirm glossary terms before they enter the glossary

### Why this EPIC exists

Only the domain owner can settle what a term means. Today `reverse-map` writes the type and class names it finds straight into the glossary, so unconfirmed definitions reach every agent that reads it. This EPIC makes every agent except the domain-modeling agent record terms as candidates, and lets the stakeholder confirm each definition before the domain-modeling agent moves it into the glossary.

### Actor Goals

- Stakeholder confirms every glossary term before it enters the glossary.
- Agents other than the domain-modeling agent record terms as candidates.

### Demo

1. Run `reverse-map` on a fixture project whose code holds the class `PaymentBatch`. `docs/spec/work/term-candidates.md` gains a row `PaymentBatch` with status `candidate`. `docs/spec/glossary.md` is unchanged.
2. Run the domain-modeling agent. The row gets a proposed definition and status `proposed`.
3. The agent asks the stakeholder to confirm the proposed terms of the domain area `payments`. The stakeholder confirms `PaymentBatch` and rejects `LedgerLine` with a note.
4. `PaymentBatch` appears in the glossary's Term/Definition/Avoid table and leaves the work file. `LedgerLine` stays with status `rejected` and the stakeholder's note.

### Scope

**In:**

- The work file `docs/spec/work/term-candidates.md` with the columns Term, Domain area, Source, Proposed definition, Status, and Note, and the statuses `candidate`, `proposed`, `confirmed`, and `rejected`.
- `reverse-map` writes term candidates instead of glossary rows.
- `grilling` and `domain-modeling`, run by any agent except the domain-modeling agent, write a settled term as a `confirmed` row of the work file, never into `glossary.md`.
- `reconcile-spec` writes terminology drift as a drift row with the domain-modeling agent as owner, in the columns of [interface-contracts.md § Report rows](../docs/spec/interface-contracts.md#report-rows-spec-feedback-and-reconciliation). E10 brings the rest of `reconcile-spec` to rows.
- The domain-modeling agent's pause point: it proposes definitions and asks for confirmation one domain area at a time. It moves `confirmed` rows into the glossary without a second question, keeps `rejected` rows with the note, and returns a reconsidered row to `proposed` with its note kept (CAO-G09). An unattended run leaves its proposals in the work file.
- Terms the layout migration moved count as confirmed.
- The requirements agent, Virgil, and the domain-modeling agent declare `term-candidates.md` as working output.

**Out:**

- The spec-review finding for `proposed` rows (E6).
- The other rows of the reconciliation report (E10).

### Dependencies

E2, for the domain-modeling agent and its workflow.

### Boundaries

- Skills: `packages/factory/skills/reverse-map/SKILL.md`, `grilling/SKILL.md`, `domain-modeling/SKILL.md`, `reconcile-spec/SKILL.md`
- Agents: `domain-modeling-agent.md`, `requirements-agent.md`, `virgil.md`
- Working output: `docs/spec/work/term-candidates.md`
- Core artifact: `docs/spec/glossary.md`

### Domain Rules

- The glossary holds only confirmed terms.
- Only the domain-modeling agent writes `glossary.md`.
- A term confirmed in another agent's session moves without a second question to the stakeholder.
- A rejected term can return to `proposed` with a new definition, and its note stays.

### Size

2 stories.

### Building-Block Inventory

| Story   | Capability                                             | Tier     | Size | Goal                                                                                                                                                              | Basis                                                                                                  |
| ------- | ------------------------------------------------------ | -------- | ---- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| ST-0350 | Record found and settled terms as candidates           | standard | M    | After `reverse-map`, `grilling`, or `reconcile-spec` meets a term, the work file or the reconciliation report holds a row for it, and `glossary.md` is unchanged. | ST-0337 made `reverse-map` write the glossary. Redirects four skills to the work file or a report row. |
| ST-0351 | Confirm proposed definitions one domain area at a time | strong   | M    | The stakeholder confirms or rejects each proposed definition of one domain area, and only confirmed terms reach the glossary.                                     | ST-0348's agent has no pause point. Adds the confirmation step, the move, and the rejected-row rule.   |

### Testability Assessment

The candidate rows and the glossary content are observable files, so the redirection of the four skills is checkable on their text and on the work file's table shape. The confirmation is a stakeholder session, which a pytest test cannot run. That red flag is accepted with CAO-05-AC-01: one recorded session in ST-0351 confirms one domain area and moves its terms. The rule "only the domain-modeling agent writes `glossary.md`" is bounded by the factory's own skill and agent files.

### Ownership Resolution

| Contract                                                                                                     | .feature Rule                                                                                          | Owner   | Rationale                             |
| ------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------ | ------- | ------------------------------------- |
| CAO-06-LN-01: four skills name `term-candidates.md` or a report row; no other agent writes `glossary.md`     | core-artifact-ownership.feature#Agents other than the domain-modeling agent record terms as candidates | ST-0350 | introduces the redirection            |
| CAO-05-LN-01: the pause point, the per-area order, the move, the rejected-row rule, the return to `proposed` | core-artifact-ownership.feature#Stakeholder confirms every glossary term before it enters the glossary | ST-0351 | introduces the confirmation step      |
| CAO-05-AC-01: one stakeholder session confirms one domain area and moves its terms                           | core-artifact-ownership.feature#Stakeholder confirms every glossary term before it enters the glossary | ST-0351 | first story where the session can run |

## E4: Route each finding to its owner

### Why this EPIC exists

Today the review loop sends every open finding back to the author of the reviewed phase. After this feature, a finding about `state-machines.md` must reach the domain-modeling agent, even when the requirements agent wrote the reviewed feature file. This EPIC adds the `owner:` field to the finding format and makes the orchestrator route by it. E5, E7, and E9 file the first `ARCH`, `QA`, and `BUG` findings with an owner.

### Actor Goals

- Factory maintainer has every finding reach the agent that acts on it next.

### Demo

1. Read `finding-format.md`. The frontmatter has an `owner:` field, defined as the agent that acts on the finding next. The tag table lists `ARCH` and `QA` and no `RECON`.
2. File `SPEC-0040` about `docs/spec/state-machines.md` with `owner: domain-modeling-agent`.
3. Run the review loop of the feature-addition playbook. It sends `SPEC-0040` to the domain-modeling agent and not to the requirements agent.

### Scope

**In:**

- `owner:` in `packages/factory/rulebooks/conventions/finding-format.md` and `packages/factory/rulebooks/templates/finding.md`.
- The tag table adds `ARCH` (architecture read check) and `QA` (test practice) and drops `RECON`.
- [§ How the orchestrator reads findings](../packages/factory/rulebooks/conventions/finding-format.md#how-the-orchestrator-reads-findings) routes each open finding to the agent in `owner:`.

**Out:**

- The agents that file `ARCH`, `QA`, and `BUG` findings (E5, E7, E9).
- The removal of the reconciliation agent's `RECON-*.md` output (E10).

### Dependencies

None for ST-0352. ST-0366 depends on ST-0363 (E10).

### Boundaries

- Convention: `packages/factory/rulebooks/conventions/finding-format.md`
- Template: `packages/factory/rulebooks/templates/finding.md`
- Entity: `FINDING.owner` in [entity-model.md](../docs/spec/entity-model.md)

### Domain Rules

- The owner is the agent that acts on the finding next, not the agent that filed it.
- An open finding goes to its owner only.

### Size

2 stories.

### Building-Block Inventory

| Story   | Capability                                    | Tier     | Size | Goal                                                                                                                                          | Basis                                                                                                      |
| ------- | --------------------------------------------- | -------- | ---- | --------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| ST-0352 | Send an open finding to the agent in `owner:` | standard | S    | The orchestrator sends each open finding to the agent its `owner:` field names, or to the producer of its artifact when the field is missing. | The format has no `owner:` and lists `RECON`. Adds the field, the two tags, the routing, and the fallback. |
| ST-0366 | Give every open finding an owner              | standard | S    | Every open finding in `docs/findings/` carries `owner:`.                                                                                      | The 39 open findings have no `owner:`. Adds it after ST-0363, when each core artifact has one producer.    |

### Testability Assessment

The field, the tag table, and the routing rule are observable in two rulebook files. The routing itself runs in an agent session, so the test checks that the rule is stated, not that a loop follows it. That red flag is accepted, because the routing is a prose instruction to the orchestrating agent and no script reads findings for routing today.

### Ownership Resolution

| Contract                                                                                      | .feature Rule                                                                | Owner   | Rationale                  |
| --------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------- | ------- | -------------------------- |
| CAO-16-LN-01: `owner:` defined, `ARCH` and `QA` listed, `RECON` dropped, routing to the owner | core-artifact-ownership.feature#Owner receives every finding it acts on next | ST-0352 | introduces the owner field |
| CAO-16-LN-02: a finding without `owner:` goes to the producer of its artifact                 | core-artifact-ownership.feature#Owner receives every finding it acts on next | ST-0352 | introduces the fallback    |

## E5: Own and review the dependency rules

### Why this EPIC exists

`dependency-check` checks the code against `docs/spec/dependency-rules.dsl`, but no agent declares that file. Nobody owns its violations, and nobody reviews the rules. Today the architecture agent also writes `state-machines.md`, which E2 gives to the domain-modeling agent. This EPIC makes the architecture agent the producer of the dependency rules and the owner of their violations, and makes the architecture-review agent check them.

### Actor Goals

- Architecture agent owns the components and their dependency rules.
- Architecture-review agent reviews the dependency rules.

### Demo

1. In a fixture project with a feature file and no `entity-model.md`, run `intent select`. The architecture agent is eligible.
2. Run `dependency-check` on a fixture with one forbidden import. Every violation in the JSON report carries `owner: architecture-agent`.
3. Read Step 5 of `maintain-architecture`. It compares components with `state-machines.md` and files an `ARCH` finding with `owner: domain-modeling-agent` on a contradiction. It writes no `state-machines.md`.
4. Run the contract test. It passes, and `docs/spec/dependency-rules.dsl` is no longer on the expected-failure list.
5. Run the architecture-review agent in a project without `dependency-rules.dsl`. It runs, because it declares the file as a context input.

### Scope

**In:**

- The architecture agent declares `docs/spec/dependency-rules.dsl` with `reviewed_by: [architecture-review-agent]` and `docs/findings/ARCH-*.md`. It lists `entity-model.md` and `state-machines.md` as context inputs.
- Step 5 of `maintain-architecture` becomes a read check that files an `ARCH` finding. It runs only when `state-machines.md` exists.
- `run-step` counts the architecture agent's step as done once its outputs exist.
- The architecture-review agent declares `dependency-rules.dsl` as a context input (CAO-G01), and `atam-review` checks the rules against the component view.
- The core list marks `dependency-rules.dsl` as optional.
- The `dependency-check` JSON report names the architecture agent in an `owner` field of every violation (CAO-G07).
- `docs/spec/dependency-rules.dsl` leaves the expected-failure list.

**Out:**

- The gate list of the implementation agent (E8).
- The domain-modeling agent's handoff that starts the component pass (E2).

### Dependencies

E1, for `reviewed_by:` and the contract test. E4, for the `ARCH` tag and the `owner:` field.

### Boundaries

- Agents: `architecture-agent.md`, `architecture-review-agent.md`
- Skills: `maintain-architecture/SKILL.md`, `atam-review/SKILL.md`, `run-step/SKILL.md`
- Script: `packages/factory/scripts/dependency-check` (`write_report`)
- Core artifacts: `docs/spec/architecture.dsl`, `docs/spec/dependency-rules.dsl`
- Contract: [interface-contracts.md](../docs/spec/interface-contracts.md), section `dependency-check`

### Domain Rules

- The architecture agent never writes a domain-structure file. It reports a contradiction as an `ARCH` finding for the domain-modeling agent.
- The architecture agent builds the baseline before the domain structure exists.
- Nothing restarts the architecture agent by itself. The domain-modeling agent's handoff starts the component pass.

### Size

3 stories.

### Building-Block Inventory

| Story   | Capability                                                         | Tier     | Size | Goal                                                                                                                                                   | Basis                                                                                                    |
| ------- | ------------------------------------------------------------------ | -------- | ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------- |
| ST-0353 | Own the dependency rules and report state-machine contradictions   | strong   | M    | The architecture agent declares `dependency-rules.dsl` with its review, writes no `state-machines.md`, and files an `ARCH` finding on a contradiction. | `maintain-architecture` writes state machines; no agent declares the rules. Adds the outputs and Step 5. |
| ST-0354 | Review the dependency rules against the component view             | standard | S    | The architecture-review agent checks `dependency-rules.dsl` against the component view and runs in a project that lacks the file.                      | `atam-review` reads no dependency rules. Adds the check.                                                 |
| ST-0355 | Name the architecture agent as owner of every dependency violation | economy  | S    | Every violation in the `dependency-check` JSON report carries `owner: architecture-agent`.                                                             | `write_report` writes no owner. Adds the field.                                                          |

### Testability Assessment

The outputs, the eligibility, and the report field are observable: agent definitions, `intent select` on fixture projects, the contract test, and the JSON report of `dependency-check` on a fixture. The read check of Step 5 and the `atam-review` check are prose steps, checked as text. No other red flag.

### Ownership Resolution

| Contract                                                                                                            | .feature Rule                                                                                     | Owner   | Rationale                                  |
| ------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- | ------- | ------------------------------------------ |
| CAO-07-LN-01: the architecture agent's outputs and context inputs, the skip without an entity model, Step 5         | core-artifact-ownership.feature#Architecture agent owns the components and their dependency rules | ST-0353 | introduces the new declarations and Step 5 |
| CAO-07-IT-02: the architecture agent is eligible without `entity-model.md` and its step counts as done              | core-artifact-ownership.feature#Architecture agent owns the components and their dependency rules | ST-0353 | introduces the context inputs              |
| CAO-09-LN-01: the reviewer reads the rules as context, `atam-review` checks them, the core list marks them optional | core-artifact-ownership.feature#Architecture-review agent reviews the dependency rules            | ST-0354 | completes the review of the rules          |
| CAO-07-IT-01: every violation in the `dependency-check` report carries `owner: architecture-agent`                  | core-artifact-ownership.feature#Architecture agent owns the components and their dependency rules | ST-0355 | introduces the owner field                 |

## E6: Review behaviour and domain structure

### Why this EPIC exists

Today the spec-review agent requires only the feature files and the scope map, and `inspect-spec` has no check for the structure files or the glossary. So the domain-modeling agent's work from E2 has a declared review that checks nothing. This EPIC gives `inspect-spec` a check for each structure file and for the glossary, and makes every unconfirmed term visible as a finding.

### Actor Goals

- Spec-review agent reviews behaviour and domain structure.

### Demo

1. Run the spec-review agent in a fixture project with feature files, the scope map, the glossary, and `entity-model.md`, and without `schemas/` or `areas/`. The review runs.
2. Read the review report. It holds a section for each present structure file and one for the glossary.
3. The glossary holds `Batch` and `PaymentBatch` for one concept. The report records a finding for the duplicate.
4. `term-candidates.md` holds one row with status `proposed`. The review files a `SPEC` finding for it with `owner: domain-modeling-agent`.
5. The review reads the scope map and files no finding on its content. The stakeholder reviews it.

### Scope

**In:**

- The spec-review agent declares `term-candidates.md` as a context input. The input declarations of the six structure files come from ST-0348.
- `inspect-spec` checks each structure file, and the glossary for three term defects: one term per concept, every term defined, and no term from an Avoid column in use.
- A `SPEC` finding for every row of `term-candidates.md` with status `proposed`.
- The spec review reads the scope map and leaves its review to the stakeholder.

**Out:**

- A blocking glossary gate (deferred).
- The architecture review (E5).

### Dependencies

E3, for the work file and its statuses. E2 comes through E3.

### Boundaries

- Agent: `packages/factory/agents/spec-review-agent.md`
- Skill: `packages/factory/skills/inspect-spec/SKILL.md`
- Outputs: `docs/reviews/spec-review-*.md`, `docs/findings/SPEC-*.md`

### Domain Rules

- A missing optional structure file never stops the review.
- The spec review never reviews the scope map. The stakeholder does.

### Size

1 story.

### Building-Block Inventory

| Story   | Capability                                   | Tier     | Size | Goal                                                                                                                           | Basis                                                                                       |
| ------- | -------------------------------------------- | -------- | ---- | ------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------- |
| ST-0356 | Review every structure file and the glossary | standard | M    | The spec-review agent reports on each present structure file and the glossary, and files a finding for every unconfirmed term. | `inspect-spec` checks feature files only. Adds the structure checks and the glossary check. |

### Testability Assessment

The required and context inputs are observable in `INDEX.yaml`, and the checks are observable as steps of `inspect-spec`. Whether the review finds a real duplicate term depends on a session, so the test checks the stated checks and the finding rule. That red flag is accepted; the next spec review of this feature reads the first outputs, as the QA strategy's gap findings recommend.

### Ownership Resolution

| Contract                                                                                     | .feature Rule                                                                            | Owner   | Rationale                                      |
| -------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- | ------- | ---------------------------------------------- |
| CAO-08-LN-01: required and context inputs, the `inspect-spec` checks, the `proposed` finding | core-artifact-ownership.feature#Spec-review agent reviews behaviour and domain structure | ST-0356 | introduces the checks and completes the inputs |

## E7: Hand test practice to the test-strategy agent

### Why this EPIC exists

Today Virgil writes `testing.yaml` during the fitting, the requirements agent writes the QA strategy, and the planning agent runs `detect-test-regime` when the file is missing. No one owns the surviving mutants that a developer agent cannot resolve. This EPIC creates the test-strategy agent (a new strong-tier agent that owns `testing.yaml`, the QA strategies, and the test guardrails) and gives it the open `QA` findings.

### Actor Goals

- Test-strategy agent owns the test practice family.
- Test-strategy agent resolves the surviving mutants that a developer agent cannot resolve.

### Demo

1. In a fixture project with a test suite and no feature file, run `intent select`. The test-strategy agent is eligible.
2. Run the agent. It proposes `docs/testing.yaml` and writes nothing until the stakeholder confirms.
3. Read the fitting in `virgil.md`. Step 2b names the test-strategy agent, and Virgil no longer declares `docs/testing.yaml`.
4. Remove `docs/testing.yaml` and start the planning agent. Its pre-flight stops and names the test-strategy agent.
5. Run the contract test. It passes, and `docs/testing.yaml` is no longer on the expected-failure list.
6. File `QA-0003` with `owner: test-strategy-agent` for a surviving mutant. The test-strategy agent records the missing test in the finding and moves `owner:` to the planning agent. On its next run it skips `QA-0003`.

### Scope

**In:**

- New `packages/factory/agents/test-strategy-agent.md` at the strong tier with the skills `detect-test-regime`, `qa-strategy-from-spec`, `crap-score`, and `mutation-testing`. It declares no required input.
- Its outputs: `docs/testing.yaml` with `reviewed_by: [stakeholder]`, `docs/spec/work/*-qa-strategy.md`, and `docs/findings/QA-*.md`.
- Its workflow: `testing.yaml` also without a feature file, a QA strategy only when a feature file, `interface-contracts.md`, and `entity-model.md` exist, a pause point before every change to `testing.yaml`, and a handoff to the planning agent.
- `testing.yaml` records only `gates.mutation_testing.enabled` and `gates.mutation_testing.command`. The mutation tool's configuration stays in the project's files.
- The requirements agent drops step 2 and `qa-strategy-from-spec` (its half of CC-01). Virgil drops `docs/testing.yaml`, and fitting step 2b names the test-strategy agent.
- The planning agent no longer runs `detect-test-regime`. A missing `testing.yaml` stops its pre-flight and names the test-strategy agent. It declares `docs/findings/QA-*.md` as a context input.
- `mutation-testing` files an unresolved mutant as a `QA` finding with the test-strategy agent as owner. The implementation agent dispatches the test-strategy agent after the wave for each open `QA` finding it owns. The test-strategy agent changes the QA strategy's contract-owner table, or records the missing test and moves `owner:` to the planning agent (CAO-G10). The finding resolves when the story that adds the test merges.
- `docs/testing.yaml` leaves the expected-failure list.

**Out:**

- Running the gates and blocking the merge (E8).
- The gates for `testing.yaml` (DEC-08).

### Dependencies

E1, for `reviewed_by:` and the contract test. E4, for the `QA` tag and the `owner:` field. E7 and E2 both edit `requirements-agent.md`, so their stories merge one after the other.

### Boundaries

- Agents: `test-strategy-agent.md` (new), `virgil.md`, `planning-agent.md`, `requirements-agent.md`, `implementation-agent.md`
- Skills: `detect-test-regime/SKILL.md`, `qa-strategy-from-spec/SKILL.md`, `mutation-testing/SKILL.md`
- Seam file: `docs/testing.yaml`
- Routing: `packages/factory/INDEX.yaml`, `packages/factory/scripts/intent`

### Domain Rules

- Only the test-strategy agent declares `docs/testing.yaml` and the QA strategies.
- Every change to `testing.yaml` waits for the stakeholder.
- The test-strategy agent never runs a gate.
- The test-strategy agent works only on `QA` findings it owns.

### Size

2 stories.

### Building-Block Inventory

| Story   | Capability                                                           | Tier     | Size | Goal                                                                                                                                                       | Basis                                                                                                                         |
| ------- | -------------------------------------------------------------------- | -------- | ---- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| ST-0357 | Hand `testing.yaml` and the QA strategies to the test-strategy agent | strong   | L    | The human operator sees the test-strategy agent in `intent select` and in fitting step 2b, and no other agent declares `testing.yaml` or a QA strategy.    | Virgil, the requirements agent, and the planning agent share the files. Adds the agent and moves the declarations and steps.  |
| ST-0358 | Resolve the surviving mutants a developer agent cannot resolve       | standard | M    | Each open `QA` finding owned by the test-strategy agent ends with a changed contract-owner table or with the missing test recorded for the planning agent. | `mutation-testing` files no `QA` finding. Adds the filing, the dispatch, the two resolutions, and the planning agent's input. |

### Testability Assessment

The declarations, the eligibility, and the planning agent's stop are observable in agent definitions, `INDEX.yaml`, the contract test, and `intent select` on fixtures. The stakeholder pause before a `testing.yaml` change is a session behaviour, checked once by CAO-10-AC-01 in ST-0357. The resolution of a `QA` finding is a prose rule, checked as text. The red flag of the QA strategy's gap findings applies: text tests show that the rules are stated, not that the agent follows them.

### Ownership Resolution

| Contract                                                                                                         | .feature Rule                                                                                                            | Owner   | Rationale                                    |
| ---------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------ | ------- | -------------------------------------------- |
| CAO-10-LN-01: the agent's definition and workflow, Virgil's outputs and step 2b, the planning agent's pre-flight | core-artifact-ownership.feature#Test-strategy agent owns the test practice family                                        | ST-0357 | introduces the agent                         |
| CAO-10-LN-02: only the test-strategy agent declares `testing.yaml` and the QA strategies                         | core-artifact-ownership.feature#Test-strategy agent owns the test practice family                                        | ST-0357 | removes the other declarations               |
| CAO-10-IT-01: `intent select` reports the agent as eligible without a feature file                               | core-artifact-ownership.feature#Test-strategy agent owns the test practice family                                        | ST-0357 | introduces the agent without required inputs |
| CAO-10-AC-01: the first run proposes `testing.yaml` and writes nothing before the stakeholder confirms           | core-artifact-ownership.feature#Test-strategy agent owns the test practice family                                        | ST-0357 | introduces the pause point                   |
| CAO-12-LN-01: `QA` filing, owned-only work, the planning agent reads `QA` findings                               | core-artifact-ownership.feature#Test-strategy agent resolves the surviving mutants that a developer agent cannot resolve | ST-0358 | introduces the `QA` loop                     |

## E8: Block a merge on a failing test guardrail

### Why this EPIC exists

The implementation agent runs gates after each story, but the mutation gate has no command to run, and the gate list has no defined order of sources. An enabled mutation gate without a command passes silently today. This EPIC makes the implementation agent run the project's mutation command from `testing.yaml`, pick the gates in a fixed order, and fail closed. The developer agent runs the same gates in manual mode.

### Actor Goals

- Implementation agent blocks a merge on a failing test guardrail.

### Demo

1. In a fixture project, `crap-score` reports a function at 42 against a threshold of 30. The implementation agent blocks the merge.
2. Set `gates.mutation_testing.enabled: true` without a `command`. The gate fails and names the test-strategy agent.
3. Set `command` to a script that exits 1. The merge is blocked.
4. Remove the story's `quality-gates` field and the `gates` section. The default runs `crap-score` and `dependency-check` and no mutation testing.
5. Read the developer agent's manual-mode workflow. It runs the same gates before it hands the story back.

### Scope

**In:**

- `dependency-check` runs after every story. `test-design-verify` runs whenever the story has a Test Design or Prior Tests section.
- The story's `quality-gates` field, then the `gates` section of `testing.yaml`, picks `crap-score` and mutation testing (CAO-G24, CAO-G25). Without either, the default runs `crap-score` and no mutation testing.
- The implementation agent runs the command in `gates.mutation_testing.command`. A non-zero exit blocks the merge. An enabled gate without a command fails and names the test-strategy agent.
- The developer agent's manual-mode step runs the same gates. The developer agent resolves each surviving mutant before the merge, as `mutation-testing` requires.

**Out:**

- Enabling the gates for the factory's own `testing.yaml`. That change waits for the stakeholder (DEC-31).
- The `QA` findings loop (E7).

### Dependencies

ST-0359 has none. ST-0365 depends on ST-0359 and on E7 (ST-0357), for the test-strategy agent as the owner the gate names.

### Boundaries

- Agents: `implementation-agent.md`, `developer-agent.md`
- Scripts: `packages/factory/scripts/premerge-check`, `crap-score`, `test-design-verify`, `dependency-check`
- Seam file: the `gates` section of `docs/testing.yaml`, [interface-contracts.md](../docs/spec/interface-contracts.md), section `docs/testing.yaml` — `gates` section schema

### Domain Rules

- A gate that cannot run fails.
- No default runs mutation testing, because its command lives in the `gates` section.
- `dependency-check` never depends on the gate list.

### Size

2 stories.

### Building-Block Inventory

| Story   | Capability                                                | Tier     | Size | Goal                                                                                                                                                       | Basis                                                                                                       |
| ------- | --------------------------------------------------------- | -------- | ---- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| ST-0359 | Take the gate list from the story, then from testing.yaml | standard | S    | `premerge-check` picks the gates from the story, then from the `gates` section, then from a `crap-score` default, and warns about `default_quality_gates`. | `premerge-check` reads the house rules and defaults to all three gates. Replaces both.                      |
| ST-0365 | Block a merge on a failing or slow mutation command       | strong   | M    | The implementation agent runs the mutation command through a gate script, and a missing, failing, or slow command blocks the merge.                        | No mutation gate script exists. Adds the script, the time limit, the result file, and the manual-mode step. |

### Testability Assessment

The gate choice and the blocked merge are observable as exit codes and messages of the gate runner on fixture projects with different `quality-gates` fields and `gates` sections. Tests instrument the runner as a subprocess with a stub mutation command. The manual-mode step is prose, checked as text. No other red flag.

### Ownership Resolution

| Contract                                                                                                   | .feature Rule                                                                                   | Owner   | Rationale                       |
| ---------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------- | ------- | ------------------------------- |
| CAO-11-CT-01: the order of gate sources and the default                                                    | core-artifact-ownership.feature#Implementation agent blocks a merge on a failing test guardrail | ST-0359 | introduces the gate order       |
| CAO-11-IT-01: an enabled gate without a command fails and names its owner; a failing command blocks        | core-artifact-ownership.feature#Implementation agent blocks a merge on a failing test guardrail | ST-0365 | introduces the mutation command |
| CAO-11-LN-01: the implementation agent's gate section and the developer agent's manual-mode step           | core-artifact-ownership.feature#Implementation agent blocks a merge on a failing test guardrail | ST-0365 | introduces both instructions    |
| CAO-11-IT-02: the gate script stops the command at `timeout_minutes` and writes a failing result           | core-artifact-ownership.feature#Implementation agent blocks a merge on a failing test guardrail | ST-0365 | introduces the time limit       |
| CAO-11-IT-03: `premerge-check` warns about `default_quality_gates` and takes the gates from `testing.yaml` | core-artifact-ownership.feature#Implementation agent blocks a merge on a failing test guardrail | ST-0359 | introduces the new gate source  |

## E9: Gate the wave close on handled drift rows

### Why this EPIC exists

Today the developer agent edits any file under `docs/spec/` when the code reveals drift. So a core file changes without its producer and without its review, and five agents match `entity-model.md`. This EPIC makes the developer agent report drift as rows, makes the implementation agent send each row to its owner and reviewer, and makes `dispatch close-wave` refuse a wave while a row is not handled. The specification then lags the code by one wave at most.

### Actor Goals

- Developer agent reports specification drift without editing the specification.
- Implementation agent closes a wave only after the owners have handled every drift row.
- Factory maintainer sees every writer of shared working output declare its path.

### Demo

1. While implementing ST-0318, the developer agent finds a rule that `validation-rules.md` lacks. It writes the row `validation-rules.md | refuse a dirty repository | … | domain-modeling-agent | open` into `docs/spec/work/spec-feedback-ST-0318.md`. `validation-rules.md` is unchanged.
2. Run `dispatch close-wave` for the wave. It fails and names the report, the artifact, and the status `open`.
3. The implementation agent dispatches the domain-modeling agent, which sets the row to `fixed`. `close-wave` still fails, because `validation-rules.md` is on the core list.
4. The spec review sets the row to `confirmed`. `close-wave` passes.
5. A row about a QA strategy at `fixed` and a `rejected` row both pass. The rejected row has a `BUG` finding with `owner: developer-agent`.

### Scope

**In:**

- The developer and implementation agents stop declaring `docs/spec/**/*.md`. The developer agent declares `docs/spec/work/spec-feedback-*.md`.
- Step 2 of `spec-feedback` writes a row into the story's own report instead of editing a specification file. A test harness that cannot test a contract becomes a row for the test-strategy agent.
- `dispatch close-wave` reads the reports of the wave's stories and the installed core list. It fails on `open` rows and on `fixed` rows about core list entries. It passes on `confirmed`, `rejected`, other `fixed` rows, and a story without a report (CAO-G13).
- After a merge, the implementation agent dispatches each row's owner and then the reviewer. A rejected row becomes a `BUG` finding filed by the reviewer, with the developer agent as owner. When the stakeholder rejects, the agent that ran the session files it (CAO-G11).
- The dispatch contract states the rule, and its manual-mode section states it per story.
- Every writer of the Working output table declares its paths: the two report paths for the five owners and the two reviewers, and `docs/findings/BUG-*.md` for the reviewers and owners (the writer half of CC-20).

**Out:**

- The reconciliation report (E10).
- The expected-failure entries. They pass only once the reconciliation agent also gives up its wide patterns (E10).

### Dependencies

E3, for the domain-modeling agent and the `term-candidates.md` declarations that the writer check reads. E4, for `owner:` and the `BUG` routing. E7, for the test-strategy agent as a row owner. E1 and E2 come through E3.

### Boundaries

- Agents: `developer-agent.md`, `implementation-agent.md`, and the seven owner and reviewer definitions
- Skill: `packages/factory/skills/spec-feedback/SKILL.md`
- Scripts: `packages/factory/scripts/dispatch` (`cmd_close_wave`), `dispatch_lib.py` (`Ledger.close_wave`)
- Convention: `packages/factory/rulebooks/conventions/dispatch-contract.md`
- Contract: [interface-contracts.md § dispatch close-wave](../docs/spec/interface-contracts.md#dispatch-close-wave)
- Runtime view: [arc42 § 6.12](../docs/arc42/06_runtime_view.md#612-spec-feedback-and-wave-close)

### Domain Rules

- The developer and implementation agents never edit a specification file.
- Each story has its own report, because the developer agents of a wave run in parallel.
- A `fixed` row about a core list entry blocks the wave until its review. A `fixed` row about any other artifact does not.
- A `rejected` row never blocks the wave.

### Size

3 stories.

### Building-Block Inventory

| Story   | Capability                                                  | Tier     | Size | Goal                                                                                                                                                          | Basis                                                                                                                        |
| ------- | ----------------------------------------------------------- | -------- | ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| ST-0360 | Report drift as a row of the story's spec-feedback report   | standard | M    | The developer agent records each drift as a row in `spec-feedback-<story-id>.md` and changes no specification file.                                           | The developer agent declares `docs/spec/**/*.md` and `spec-feedback` edits the specification. Replaces both.                 |
| ST-0361 | Refuse to close a wave while a drift row is unhandled       | strong   | M    | `dispatch close-wave` fails while a row of the wave's reports is `open`, or `fixed` on a core list entry, and names each such row.                            | `close_wave` reads no report. Adds the report reader and the core list lookup.                                               |
| ST-0362 | Send each drift row to its owner and reviewer after a merge | standard | M    | After a merge, the implementation agent dispatches each row's owner and reviewer, a rejected row becomes a `BUG` finding, and every writer declares its path. | The implementation agent dispatches no owner. Adds the dispatch, the `BUG` rule, the manual-mode rule, and the declarations. |

### Testability Assessment

`close-wave` has the clearest boundary of this feature: its exit code and error message on fixture ledgers with report files of every status. The declarations and the writer check are observable in `INDEX.yaml`. The post-merge dispatch and the `BUG` rule are prose, checked as text. No other red flag.

### Ownership Resolution

| Contract                                                                                 | .feature Rule                                                                                                         | Owner   | Rationale                         |
| ---------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- | ------- | --------------------------------- |
| CAO-13-LN-01: no `docs/spec/**/*.md` output; `spec-feedback` Step 2 writes a row         | core-artifact-ownership.feature#Developer agent reports specification drift without editing the specification         | ST-0360 | introduces the report rows        |
| CAO-14-IT-01: `close-wave` fails on `open` and core `fixed` rows and passes on the rest  | core-artifact-ownership.feature#Implementation agent closes a wave only after the owners have handled every drift row | ST-0361 | introduces the report reader      |
| CAO-14-IT-02: `close-wave` reads the installed core list to classify a row               | core-artifact-ownership.feature#Implementation agent closes a wave only after the owners have handled every drift row | ST-0361 | introduces the core list lookup   |
| CAO-14-LN-01: the post-merge dispatch, the `BUG` rule, the manual-mode section           | core-artifact-ownership.feature#Implementation agent closes a wave only after the owners have handled every drift row | ST-0362 | introduces the dispatch rule      |
| CAO-17-LN-01: every writer of the Working output table declares its path in `INDEX.yaml` | core-artifact-ownership.feature#Factory maintainer sees every writer of shared working output declare its path        | ST-0362 | adds the last writer declarations |

## E10: Report reconciliation drift to owners

### Why this EPIC exists

Today the reconciliation agent edits core files, ADRs, and `docs/*.md` directly and files `RECON` findings. So a core file changes without its producer, and the agent's wide patterns keep nine core list entries on the expected-failure list. This EPIC makes the reconciliation agent write one report per run, with each row naming the artifact's owner.

### Actor Goals

- Reconciliation agent reports drift to each artifact's owner.

### Demo

1. The code renames the task status `PENDING` to `WAITING`, and `state-machines.md` still says `PENDING`. Run the reconciliation agent.
2. `docs/reviews/reconciliation-2026-11-10.md` holds a row for `state-machines.md` with `owner: domain-modeling-agent` and status `open`. `state-machines.md` is unchanged.
3. A stale ADR and a stale `agent-context.md` give rows for the architecture agent and Virgil.
4. Run the contract test. It passes, and the expected-failure list is empty.
5. After the domain-modeling agent fixes the row, the next reconciliation run checks it.

### Scope

**In:**

- The reconciliation agent declares `docs/reviews/reconciliation-*.md` as its only output and drops `capture-context`. It declares no core file, no `docs/*.md`, no `docs/adr/*.md`, and no `docs/findings/RECON-*.md`.
- `reconcile-spec` writes every finding as a drift row with the artifact's owner and edits no file outside the report.
- The next run checks each `fixed` row.
- The nine remaining entries leave the expected-failure list, which is then empty.

**Out:**

- The terminology row (ST-0350).
- The `close-wave` check, which reads spec-feedback reports only (E9).

### Dependencies

E9, for the row statuses, the owners' report declarations, and the removal of the developer and implementation agents' wide patterns.

### Boundaries

- Agent: `packages/factory/agents/reconciliation-agent.md`
- Skill: `packages/factory/skills/reconcile-spec/SKILL.md`
- Output: `docs/reviews/reconciliation-<date>.md`

### Domain Rules

- The reconciliation agent edits no file outside its report.
- Each row names the owner of the artifact, not the reconciliation agent.

### Size

1 story.

### Building-Block Inventory

| Story   | Capability                                          | Tier     | Size | Goal                                                                                                                  | Basis                                                                                                                           |
| ------- | --------------------------------------------------- | -------- | ---- | --------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| ST-0363 | Report each drift as a row for the artifact's owner | standard | M    | The reconciliation agent writes one report per run with a row per drift, names each owner, and changes no other file. | The agent declares nine wide outputs and `RECON` findings. Replaces them with the report and empties the expected-failure list. |

### Testability Assessment

The single output and the empty expected-failure list are observable in `INDEX.yaml` and the contract test. The rows themselves come from an agent session, so the test checks the instruction in `reconcile-spec`. That red flag is the same as in E7 and is accepted.

### Ownership Resolution

| Contract                                                                                                | .feature Rule                                                                               | Owner   | Rationale                  |
| ------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- | ------- | -------------------------- |
| CAO-15-LN-01: one report output; `reconcile-spec` writes rows with owner and status, edits nothing else | core-artifact-ownership.feature#Reconciliation agent reports drift to each artifact's owner | ST-0363 | introduces the report rows |

## E11: Reach the new owners through the playbooks

### Why this EPIC exists

A human operator follows a playbook step by step. Four playbooks still name the requirements agent for the structure files and the QA strategy, and the reconciliation agent for stale core files. After E2, E7, and E10, those steps point at the wrong agent. This EPIC makes the playbooks and `run-step` name the new owners.

### Actor Goals

- Human operator reaches the new owners through the playbooks and the routing.

### Demo

1. Read the step of `feature-addition` that produces the structure files. It names the domain-modeling agent. The QA strategy step names the test-strategy agent.
2. Read `brownfield-onboarding`. The glossary, the entity model, and the state machines name the domain-modeling agent.
3. Read `documentation-update`. A stale core file is fixed by the owner in each report row.
4. In a project with an accepted proposal and no specification, follow `run-step`. The requirements agent is eligible first, then the domain-modeling agent, then the spec-review agent.
5. With the spec review of payments still running, `run-step` shows the test-strategy agent beside the spec-review agent, and the operator chooses.

### Scope

**In:**

- `feature-addition`, `greenfield-development`, `brownfield-onboarding`, and `documentation-update` name the new owner where they named a moved responsibility.
- `run-step` states that the declared inputs set the order of the producers, and that the operator chooses when two agents are eligible.

**Out:**

- Workflows without playbooks and eligibility on confirmed inputs (DEC-09).
- The `intent` routing of the two agents, which ST-0348 and ST-0357 deliver.

### Dependencies

E2, E7, and E10, for the owners the playbooks name.

### Boundaries

- Playbooks: `packages/factory/playbooks/feature-addition.md`, `greenfield-development.md`, `brownfield-onboarding.md`, `documentation-update.md`
- Skill: `packages/factory/skills/run-step/SKILL.md`
- Routing: `packages/factory/INDEX.yaml`, `packages/factory/scripts/intent`

### Domain Rules

- A playbook changes only where it names a moved responsibility.

### Size

1 story.

### Building-Block Inventory

| Story   | Capability                            | Tier    | Size | Goal                                                                                          | Basis                                                               |
| ------- | ------------------------------------- | ------- | ---- | --------------------------------------------------------------------------------------------- | ------------------------------------------------------------------- |
| ST-0364 | Follow each playbook to the new owner | economy | S    | The human operator reads the new owner in every playbook step that produces a moved artifact. | Four playbooks name the old owners. Edits the steps and `run-step`. |

### Testability Assessment

The playbook steps and the `run-step` order are observable text, and `intent select` shows the eligible agents on fixture projects. No red flag: each row of the playbook outline names one file, one step, and one owner.

### Ownership Resolution

| Contract                                                                                              | .feature Rule                                                                                               | Owner   | Rationale                     |
| ----------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------- | ------- | ----------------------------- |
| CAO-18-LN-01: the four playbooks name the new owners; `intent select` lists the domain-modeling agent | core-artifact-ownership.feature#Human operator reaches the new owners through the playbooks and the routing | ST-0364 | introduces the playbook edits |

## E12: Bring each reconciliation row back to its owner

### Why this EPIC exists

After E10, a reconciliation run writes an `open` row for each drift, with the artifact's owner. A reconciliation run belongs to no wave, so no implementation agent dispatches that owner, and `close-wave` never reads the report. The row stays `open`, and nobody notices. This EPIC makes the `documentation-update` playbook carry each row to its owner and its reviewer, and keep the playbook open until every row is handled.

### Actor Goals

- Orchestrator brings every reconciliation row back to its owner and the owner's reviewer.

### Demo

1. A fixture project has `docs/reviews/reconciliation-2026-11-03.md` with `open` rows on `state-machines.md`, `architecture.dsl`, and an ADR. Run the backfeed step of `documentation-update`.
2. The DONE list names each `open` row, so the playbook stays open.
3. The orchestrator (the session that runs the playbook) dispatches each owner, one session at a time. Each owner fixes its artifact and sets the row to `fixed` in the same commit.
4. The orchestrator dispatches the spec-review agent and the architecture-review agent for the two core rows. They set `confirmed`. The ADR row closes at `fixed`.
5. The DONE list names no row, and the playbook is done.

### Scope

**In:**

- A backfeed step in `documentation-update` after the reconciliation run. It reads every reconciliation report, dispatches the owner of each `open` row, then the reviewer of each `fixed` row on the core list. A `stakeholder` reviewer sees the fix in the orchestrator's session, after any agent reviewer. A `rejected` row becomes a `BUG` finding.
- The DONE list waits for every row of every reconciliation report.
- `reconcile-spec` keeps each row in the report that first wrote it. A later run writes a new row only when the drift of a `confirmed` row appears again.
- The architecture agent names the skill for a row on each artifact it owns.

**Out:**

- A script gate on reconciliation rows. No script reads them, so a row blocks no merge (CAO-G32).
- A skill field on the core list.

### Dependencies

E9, for the spec-feedback dispatch that this step follows and the core list lookup of `close-wave`. E10, for the report and its rows. E11, for the owner names of `documentation-update`.

### Boundaries

- Playbook: `packages/factory/playbooks/documentation-update.md`
- Agents: `reconciliation-agent.md`, `architecture-agent.md`
- Skill: `packages/factory/skills/reconcile-spec/SKILL.md`
- Decision: [ADR-0030](../docs/adr/0030-reconciliation-rows-return-through-the-documentation-update-playbook.md)
- Runtime view: [arc42 § 6.13](../docs/arc42/06_runtime_view.md#613-reconciliation-backfeed)

### Domain Rules

- A row stays in the report that first wrote it, and only its status changes.
- Only the playbook's DONE list waits for a row.
- A `fixed` row outside the core list closes at `fixed` (DEC-35).

### Size

1 story.

### Building-Block Inventory

| Story   | Capability                                                   | Tier     | Size | Goal                                                                                                                                  | Basis                                                                                                                           |
| ------- | ------------------------------------------------------------ | -------- | ---- | ------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| ST-0367 | Bring each reconciliation row back to its owner and reviewer | standard | M    | The operator of `documentation-update` sees every row reach its owner and reviewer, and the playbook names each row that still waits. | The playbook has no backfeed step, and `reconcile-spec` repeats checked rows in the new report. Adds the step and the row rule. |

### Testability Assessment

The backfeed step, the DONE list, and the row rule are text in a playbook, a skill, and an agent definition, so the tests check the instruction, as in E10. The absence of a script gate is observable: `premerge-check` and `dispatch` name no reconciliation path. The core list's missing skill field is observable in `core-artifacts.yaml`. That red flag is the same as in E7 and E10 and is accepted.

### Ownership Resolution

| Contract                                                                                                     | .feature Rule                                                                                                           | Owner   | Rationale                         |
| ------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------- | ------- | --------------------------------- |
| CAO-19-LN-01: the backfeed step, its order, the stakeholder case, the `BUG` rule; no repeated row            | core-artifact-ownership.feature#Orchestrator brings every reconciliation row back to its owner and the owner's reviewer | ST-0367 | introduces the backfeed step      |
| CAO-19-LN-02: the DONE list waits for every row; `premerge-check` and `dispatch` name no reconciliation path | core-artifact-ownership.feature#Orchestrator brings every reconciliation row back to its owner and the owner's reviewer | ST-0367 | introduces the DONE list rule     |
| CAO-19-LN-03: the architecture agent lists both skills; no skill field on the core list                      | core-artifact-ownership.feature#Orchestrator brings every reconciliation row back to its owner and the owner's reviewer | ST-0367 | introduces the skill-per-row step |
