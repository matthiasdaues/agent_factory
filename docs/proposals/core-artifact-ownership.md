---
schema_version: 2
title: Core Artifact Ownership
status: open
owner: agent-factory
created: 2026-11-02
updated: 2026-11-02
supersedes:

impact:
  scope: cross_component
  architecture_change: true
  external_contract_change: true
  boundaries:
    - packages/factory/agents/requirements-agent.md
    - packages/factory/agents/spec-review-agent.md
    - packages/factory/agents/architecture-agent.md
    - packages/factory/agents/architecture-review-agent.md
    - packages/factory/agents/virgil.md
    - packages/factory/agents/reconciliation-agent.md
    - packages/factory/skills/reconcile-spec/SKILL.md
    - packages/factory/agents/developer-agent.md
    - packages/factory/agents/implementation-agent.md
    - packages/factory/skills/spec-feedback/SKILL.md
    - packages/factory/rulebooks/conventions/dispatch-contract.md
    - packages/factory/scripts/index-lint
    - packages/factory/skills/inspect-spec/SKILL.md
    - packages/factory/skills/maintain-architecture/SKILL.md
    - packages/factory/skills/qa-strategy-from-spec/SKILL.md
    - packages/factory/skills/detect-test-regime/SKILL.md
    - packages/factory/skills/crap-score/SKILL.md
    - packages/factory/skills/mutation-testing/SKILL.md
    - docs/proposals/core-artifact-layout.md

governance:
  assurance: elevated
  risk_domains:
    - compatibility

estimate:
  as_of: 2026-11-02
  basis: decomposition
  confidence: low
  human_review_hours:
    min: 5
    max: 10
  normalized_tokens:
    min: 40000
    max: 80000
  estimated_consumption:
    min: 800000
    max: 1600000
    overhead_multiplier: 20
    playbook: feature-addition
---

# Feature Request: Core Artifact Ownership

## Primer

In the Agent Factory, agents write the files that describe a software project. The most important files form the core. A person edits a core file, other files derive from it, and an automatic check, called a gate, tests it. Each agent declares in its definition which files it reads and writes.

Take the state machine file, which describes how each entity changes its status. Today two agents write it. The requirements agent declares it, and the architecture agent changes it without declaring it. Three other core files have no writer, so nobody creates them. Eight core files have no review, so nobody confirms them.

The proposal sorts the core into three families. Scope and behaviour say what the system must do, and the requirements agent keeps them. Domain structure describes the entities: the glossary, the entity model, the state machines, and the rules written in terms of the entities. A new domain-modeling agent owns it. The architecture agent owns the components and their dependency rules. A file keeps its owner whichever workflow asks for it. Outside the core, a new test-strategy agent records how the project tests and plans the tests for each feature. Virgil, the guide agent for project setup, owns the file that tells agents where project knowledge lives.

Every core file then has one producer, the agent that writes it, and a review in a separate session. The producer names its reviewers in its definition. A test fails when a core file has no producer, several producers, or no reviewer. The spec-review agent reviews behaviour and domain structure, and the architecture-review agent reviews the architecture. The stakeholder, the person who owns the domain, confirms the scope map. The stakeholder also confirms every glossary term, because only that person can settle what a term means.

An agent that reads a file it does not own reports a finding and leaves the file alone. Say the code renames a task status from PENDING to WAITING, but the state machine file still says PENDING. The reconciliation agent compares the core with the code and writes a report row that names the file and its owner. The domain-modeling agent updates the file, and the spec-review agent confirms the change. The finder does not fix the error, because the file would then have several writers and the fix would skip the owner's review.

The same rule holds during implementation. The implementation agent hands out stories in waves to the developer agent, and neither agent edits a specification file. The developer agent writes each drift as a row of the wave's spec-feedback report. A wave closes only when the owners have fixed every row and their reviews have confirmed the fixes. So the specification lags the code by one wave at most.

The test-strategy agent also owns the gates that measure the tests, such as mutation testing. It chooses these gates and sets their thresholds. The implementation agent still runs them after each story, because a gate must block before the merge.

## Summary

Every core artifact gets exactly one producing agent and one review, and both are declared in the agents' frontmatter. The requirements agent keeps scope and behaviour and gives up two artifact families. A new domain-modeling agent takes domain structure: the glossary, the data model, and the rules and contracts written in terms of the entities. A new test-strategy agent takes test practice: the record of how the project tests, the QA strategies, and the quality guardrails that measure the tests. The first release closes every producer and review gap on the [project truth map](project-truth-map.drawio). It builds on the [core artifact layout](core-artifact-layout.md) and starts after that release's agent stories are merged.

## Motivation

The core artifact layout defines the core by three marks: people edit it, other files derive from it, and a gate checks it (core-artifact-layout.md, DEC-02). It does not say who produces each core file or who confirms it. The project truth map in [project-truth-map.drawio](project-truth-map.drawio), page "Current state", shows the gaps. It is drawn from the agents' declared inputs and outputs in `packages/factory/INDEX.yaml`.

- **Three core files have no producer.** No agent or skill writes `dependency-rules.dsl`, `schemas/*`, or `areas/*.md`. `dependency-check` only reads the first.
- **Eight core files have no review.** The spec-review agent declares only the feature files and the scope map as required inputs. `inspect-spec` uses the vocabulary file as a reference, but it reviews neither the glossary nor the four structure files. The structure files are `entity-model.md`, `state-machines.md`, `validation-rules.md`, and `interface-contracts.md`. Nothing reviews the dependency rules, the schemas, or the area specs.
- **State machines have two writers.** The requirements agent declares `state-machines.md` as its output. The architecture agent also writes it, through Step 5 of `maintain-architecture`, without declaring it.
- **The requirements agent does too much.** It declares eight outputs and eight skills, loads about 20,000 tokens, and has three entry modes. It runs interviews, maps scope, writes behaviour, models data, writes the QA strategy, and captures the agent context.

A core file without a producer is never created. A core file without a review is never confirmed.

## Core Principles

- **One producer per core artifact.** Exactly one agent declares each core artifact as an output, and only that agent writes it.
- **One review per core artifact.** Each core artifact has a declared review, run in a separate session from its producer.
- **Readers raise findings.** An agent that reads an artifact it does not own files a finding when the artifact is wrong. It does not edit the artifact.
- **Families, not phases.** Ownership follows the artifact family, not a playbook step. An artifact keeps its owner whichever workflow asks for it.

## Design

### Artifact families and owners

The core splits into three families, each with one owner: scope and behaviour (requirements agent), domain structure (domain-modeling agent), and architecture (architecture agent) (DEC-02). Outside the core, the test practice family, `testing.yaml`, the QA strategies and the test guardrails, has its own owner, the test-strategy agent (DEC-10, DEC-23). The paths are those of the core artifact layout (DEC-05).

Each core artifact has this contract:

| Core artifact            | Producer              | Gate                                     | Review                            |
| ------------------------ | --------------------- | ---------------------------------------- | --------------------------------- |
| `scope-map.md`           | requirements agent    | `scope-lint`, `spec-lint` `SCOPE001`     | stakeholder, per domain batch     |
| `features/*.feature`     | requirements agent    | `scope-lint` (scope header), `spec-lint` | spec-review agent                 |
| `areas/*.md`             | requirements agent    | `spec-lint`                              | spec-review agent                 |
| `glossary.md`            | domain-modeling agent | `spec-lint` `GLOSS001` (info)            | spec-review agent and stakeholder |
| `entity-model.md`        | domain-modeling agent | none yet                                 | spec-review agent                 |
| `state-machines.md`      | domain-modeling agent | `statemachine-lint`                      | spec-review agent                 |
| `validation-rules.md`    | domain-modeling agent | `spec-lint`                              | spec-review agent                 |
| `interface-contracts.md` | domain-modeling agent | `spec-lint`                              | spec-review agent                 |
| `schemas/*`              | domain-modeling agent | none yet                                 | spec-review agent                 |
| `architecture.dsl`       | architecture agent    | `structurizr`, `arch-lint`               | architecture-review agent (ATAM)  |
| `dependency-rules.dsl`   | architecture agent    | `dependency-check`                       | architecture-review agent         |

The missing gates are out of scope (DEC-08).

### Derivations inside the core

The domain-modeling agent derives within its family, and the architecture agent derives from both other families (DEC-06).

- The entity model defines each entity's lifecycle, and `state-machines.md` derives from it.
- `schemas/*` hold the structure inside the entity model's payload columns.
- The glossary's seeded terms derive from the term candidates, as [Glossary terms](#glossary-terms) describes.
- `architecture.dsl` derives from the scope map or the feature files, and its component pass reads the entity model.
- `dependency-rules.dsl` derives from the components in `architecture.dsl`.

### The requirements agent

The requirements agent keeps the interviews and the behaviour: `capture-vision`, `clarify-requirements`, `grill-me`, `grill-with-docs`, `reverse-map`, and `derive-feature`. It writes the scope map, the feature files, the gaps reports, and the area specs. `reverse-map` writes term candidates, not the glossary (DEC-16).

Three jobs belong to other owners:

- **Structure files.** Step 1d of its workflow, "Produce supplementary specs", goes to the domain-modeling agent.
- **QA strategy.** Step 2 and the skill `qa-strategy-from-spec` go to the test-strategy agent (DEC-10).
- **Agent context.** The skill `capture-context` is not in its skill list. Virgil owns it in fitting (DEC-07).

Its handoff names the domain-modeling agent as the next producer.

### The domain-modeling agent

A new agent definition, `packages/factory/agents/domain-modeling-agent.md`, owns the domain structure family. It uses the existing `domain-modeling` skill for the glossary, and it also writes the structure files and `schemas/*`.

- **Tier:** strong, because most other artifacts are written against the domain structure, and its errors cost the most downstream (DEC-12).
- **Inputs required:** `docs/spec/scope-map.md` and at least one feature file.
- **Inputs as context:** `docs/spec/glossary.md`, `docs/spec/work/term-candidates.md`, the source code, `docs/agent-context.md`.
- **Outputs:** the six artifacts of the domain structure family, and the proposed definitions in `docs/spec/work/term-candidates.md`.
- **Handoff:** the spec-review agent, in a new session.

It writes each state machine's pseudocode and derives its Mermaid diagram, as the state machine notation requires. `statemachine-lint` checks that the two agree.

### Glossary terms

Only the domain owner can settle a term, so every glossary term needs the stakeholder's confirmation (DEC-14). A term settled in a `domain-modeling` session is confirmed there.

A term found in the code takes a longer path. During its sweep of the tests and the code, `reverse-map` writes the type, class and module names it finds to `docs/spec/work/term-candidates.md`. So the glossary keeps one producer (DEC-16). The domain-modeling agent then proposes a definition for each candidate, in the same work file.

The glossary holds only confirmed terms (DEC-15). A candidate stays in the work file, with its proposed definition, until the stakeholder confirms it together with its domain area's scope-map batch. The domain-modeling agent then moves the term into the glossary's Term/Definition/Avoid table and removes it from the work file. So no reader takes a proposed definition as settled, and the glossary needs no draft marker. The spec review files a finding for every candidate whose domain area is confirmed but which is still in the work file.

### The architecture agent

The architecture agent declares `dependency-rules.dsl` as an output. It writes no `state-machines.md`. Step 5 of `maintain-architecture` is a read check: the architecture agent compares the components with the state machines and files a finding when they contradict each other.

### The test-strategy agent

A new agent definition, `packages/factory/agents/test-strategy-agent.md`, owns the test practice family (DEC-10). The family has two files: `docs/testing.yaml` records how the project tests, and each `docs/spec/work/<feature>-qa-strategy.md` plans what to test for one feature. The QA strategy is built from the layer bindings in `testing.yaml`, so both files belong to one owner.

- **Tier:** strong, because assigning each contract its owning test layer is judgment. Three agents work from the QA strategy: the QA agent, the code-review agent, and the developer agent (DEC-13).
- **Skills:** `detect-test-regime`, `qa-strategy-from-spec`, `crap-score`, and `mutation-testing`.
- **Inputs required:** the feature file, `interface-contracts.md`, and `entity-model.md` for a QA strategy; the test suites in the code for `testing.yaml`.
- **Outputs:** `docs/testing.yaml` and `docs/spec/work/*-qa-strategy.md`.
- **Handoff:** the planning agent, which assigns the strategy's contracts to stories in its testability probe.

The planning agent and the QA agent do not write the QA strategy. The planning agent already carries the whole backlog sequence, and the QA agent reviews code against the strategy.

### Quality guardrails

The test-strategy agent owns the guardrails that measure the tests: `crap-score`, `mutation-testing`, and `test-design-verify` (DEC-24). A later gate that measures the tests, such as a coverage gate, joins this family.

Owning a guardrail means three jobs. The test-strategy agent chooses the gates and sets their thresholds in the `gates` section of `testing.yaml`. It sets up the project's mutation testing. It also judges the results that a number alone does not settle, such as surviving mutants, against the contract owners in the QA strategy. When a threshold proves wrong, the test-strategy agent adjusts it.

The test-strategy agent does not run the gates (DEC-23), because running a gate needs no judgment and a gate must block before the merge. The implementation agent runs them after each story, as today, and a failing gate blocks the merge. The developer agent may run them before it hands a story back.

Take a case. After ST-0318, `crap-score` reports the function `plan_moves` at 42, above the threshold of 30 in `testing.yaml`. The implementation agent blocks the merge, and the developer agent simplifies the function or adds tests. After the same story, mutation testing leaves three surviving mutants in the path-table planner. The test-strategy agent classifies them by contract owner, and each survivor in an owned contract becomes a missing test.

`dependency-check` stays with the architecture agent. It checks the code against `dependency-rules.dsl`, so its findings go to the architecture agent, which owns those rules.

### The seam files

The seam is the two files in `docs/` that describe how agents work in this project, not the system itself: `agent-context.md` and `testing.yaml`. The two files have different owners.

| Seam file          | Producer                                  | Gate           | Review                  |
| ------------------ | ----------------------------------------- | -------------- | ----------------------- |
| `agent-context.md` | Virgil, with `capture-context`            | `concern-lint` | stakeholder approves    |
| `testing.yaml`     | test-strategy agent, `detect-test-regime` | none yet       | stakeholder, in fitting |

For step 2b of the fitting, the session takes the test-strategy agent's role, because Virgil may not write a file its definition does not declare (DEC-11).

### Reviews

The spec-review agent reviews the feature files, the area specs, the glossary, the structure files, and `schemas/*`. It declares all of them as required inputs. `inspect-spec` has a check for each structure file and reviews the glossary itself: one term per concept, every term defined, and no term from an Avoid column in use.

The architecture-review agent declares `dependency-rules.dsl` as a required input. Its review checks that the rules match the component view.

### Declaring the review

Each output declaration of a core artifact carries a `reviewed_by:` field (DEC-20). Its value is a list of reviewers: agent names, `stakeholder`, or both (DEC-22). The glossary needs both: the stakeholder for each term's meaning, and the spec-review agent for consistency. The producer declares who confirms its work, so producer and review stand in one place, as in the contract table.

```yaml
outputs:
  declarations:
    - path_pattern: docs/spec/features/*.feature
      reviewed_by: [spec-review-agent]
    - path_pattern: docs/spec/scope-map.md
      reviewed_by: [stakeholder]
    - path_pattern: docs/spec/glossary.md
      reviewed_by: [spec-review-agent, stakeholder]
```

`index-lint` carries the field into `INDEX.yaml`. It fails when a named agent does not exist, or when that agent does not declare the artifact as a required input. So the contract test reads `INDEX.yaml` alone. An agent that only reads an artifact, such as the QA agent reading a feature file, never counts as its review.

### Reconciliation

The reconciliation agent compares the core with the code, and it edits no core file (DEC-17). It writes one consolidated report per run, `docs/reviews/reconciliation-<date>.md`. The report holds every finding as a row of one table, and no finding goes into a separate finding file.

Each row names the artifact, the mismatch with its evidence in the code, and the artifact's owner. The owner fixes its rows on its next run, and the fix goes through the owner's review. When the review finds that the code breaks an accepted requirement, the finding becomes a code defect, not a specification change. The next reconciliation run checks each fixed row.

Take a case. The code renames the task status `PENDING` to `WAITING`, and `state-machines.md` still says `PENDING`. The report's row names `state-machines.md` and the domain-modeling agent. The domain-modeling agent updates the pseudocode and the Mermaid diagram, and the spec review confirms both.

### Spec feedback during implementation

The developer agent and the implementation agent edit no specification file (DEC-18). When an implementation reveals drift, the developer agent writes a row into one spec-feedback report per wave, `docs/spec/work/spec-feedback-<feature-branch>-wave-<n>.md` (DEC-19). Each row names the artifact, the drift with its evidence in the code, and the artifact's owner. `spec-feedback` Step 2 writes report rows.

A wave closes only when the owners have fixed every row of its report and their reviews have confirmed the fixes. So the specification lags the code by one wave at most.

Take a case. While implementing ST-0318, the developer agent finds that the migration script must refuse a repository with uncommitted changes. `validation-rules.md` has no such rule. The developer agent writes the row "validation-rules.md: refuse a dirty repository; owner: domain-modeling agent". The domain-modeling agent adds the rule, and the spec review confirms it before the wave closes. A test harness that cannot test a contract at its prescribed layer becomes a row for the test-strategy agent in the same way.

### Order after the core artifact layout

The proposal builds on the core artifact layout. It plans no story that edits a file before that file's layout story is merged (DEC-05). These pending layout stories edit the same files:

| Layout story | Files this proposal also edits                                          |
| ------------ | ----------------------------------------------------------------------- |
| ST-0325      | `scripts/dependency-check`                                              |
| ST-0327      | `scripts/spec-lint` (glossary reader)                                   |
| ST-0328      | `skills/capture-context/SKILL.md`                                       |
| ST-0336      | `skills/domain-modeling/SKILL.md`                                       |
| ST-0337      | `skills/reverse-map/SKILL.md`                                           |
| ST-0338      | `agents/requirements-agent.md`, `skills/qa-strategy-from-spec/SKILL.md` |
| ST-0341      | `agents/architecture-agent.md`, `skills/maintain-architecture/SKILL.md` |

Each story of this proposal names its overlapping layout story as a dependency. ST-0337 makes `reverse-map` write the glossary. After ST-0337 is merged, a story of this proposal redirects that output to the candidates file.

## Scope

**In the first release:**

- The requirements agent declares only the scope-and-behaviour family and loses steps 1d and 2 and `capture-context`.
- The new domain-modeling agent declares the six domain-structure artifacts.
- `reverse-map` writes term candidates to `docs/spec/work/term-candidates.md` instead of the glossary, and the domain-modeling agent moves each term into the glossary once the stakeholder confirms it.
- The architecture agent declares `dependency-rules.dsl` and stops writing `state-machines.md`.
- The spec-review agent and `inspect-spec` review every artifact of two families, the glossary included.
- The architecture-review agent reviews `dependency-rules.dsl`.
- The new test-strategy agent declares `testing.yaml` and the QA strategies, and Virgil stops declaring `testing.yaml`.
- The test-strategy agent owns the test guardrails `crap-score`, `mutation-testing`, and `test-design-verify`; the implementation agent keeps running them, and `dependency-check` stays with the architecture agent.
- The reconciliation agent edits no core file and reports every finding in one consolidated report per run.
- The developer and implementation agents edit no specification file. Drift goes into one spec-feedback report per wave, and the wave closes only when the owners have fixed it.
- Every core output declaration carries `reviewed_by:`, `index-lint` checks it, and a test checks the producer and review contract against `INDEX.yaml`.

**Explicitly deferred (do NOT plan stories for these):**

- **Gates for the entity model, `schemas/*`, and `testing.yaml`.** They are a separate concern and get their own proposal (DEC-08).
- **DBML for the entity model.** The proposal [entity-model-as-dbml.md](entity-model-as-dbml.md) owns it.
- **A blocking glossary gate.** The core artifact layout defers it, and this proposal keeps that deferral.
- **Workflows without playbooks.** The direction is settled (DEC-09), but its design needs its own proposal. This release changes a playbook only where the playbook names a moved responsibility. Artifact states such as draft and confirmed, and eligibility on confirmed inputs, belong to that proposal.

## Design Details

- **Migration of existing projects.** No file moves. Only the agents that write the files change. A project's existing structure files stay as they are, and the domain-modeling agent takes them over on its next run.
- **Eligibility.** `run-step` counts an agent as eligible when the files of its required inputs exist, as today (DEC-21). The order requirements agent, domain-modeling agent, spec-review agent follows from the declared inputs. The test-strategy agent can become eligible while the spec review still runs. The user then chooses the order, and a contract that the review changes needs a revised QA strategy.
- **Findings across owners.** A finding about an artifact names that artifact's owner in its frontmatter, so the fix goes to the owner and not to the reader who found it.

## Open Questions

No question is open.

## Completion Criteria

- `agents/requirements-agent.md` declares exactly these outputs: `scope-map.md`, `features/*.feature`, the gaps reports, and `areas/*.md`. Its skill list contains neither `qa-strategy-from-spec` nor `capture-context`.
- `agents/domain-modeling-agent.md` exists and declares the six domain-structure artifacts as its outputs.
- `agents/architecture-agent.md` declares `docs/spec/dependency-rules.dsl`. `maintain-architecture` contains no step that writes `state-machines.md`.
- The spec-review agent declares every scope-and-behaviour and domain-structure artifact as a required input, and `inspect-spec` has a check for each structure file and for the glossary.
- The architecture-review agent declares `docs/spec/dependency-rules.dsl` as a required input.
- `agents/test-strategy-agent.md` exists, lists `detect-test-regime`, `qa-strategy-from-spec`, `crap-score`, and `mutation-testing` as its skills, and declares `docs/testing.yaml` and `docs/spec/work/*-qa-strategy.md` as its outputs. No other agent declares either.
- The implementation agent still runs `crap-score`, `mutation-testing`, and `test-design-verify` after each story and blocks the merge on a failure. Only the test-strategy agent writes the `gates` section of `testing.yaml`, and `dependency-check` findings name the architecture agent as owner.
- `agents/virgil.md` does not declare `docs/testing.yaml` as an output, and the fitting's step 2b names the test-strategy agent.
- A test reads `INDEX.yaml` and fails when a core artifact is declared as an output by no agent or by more than one agent, or when its declaration has no `reviewed_by:` or an empty list.
- `index-lint` fails when an entry of a `reviewed_by:` list names no existing agent and is not `stakeholder`, or names an agent that does not declare the artifact as a required input.
- `agents/reconciliation-agent.md` declares `docs/reviews/reconciliation-*.md` as its only output. It declares no core file and no `docs/findings/RECON-*.md`, and each row of its report names the owner of the artifact.
- `agents/developer-agent.md` and `agents/implementation-agent.md` do not declare `docs/spec/**/*.md` as an output, and `spec-feedback` Step 2 writes report rows instead of editing a specification file.
- The wave-close rule of the dispatch contract requires every row of the wave's spec-feedback report to be fixed and confirmed by the owner's review.
- `reverse-map` writes no `glossary.md`. It writes its term candidates to `docs/spec/work/term-candidates.md`, and the domain-modeling agent declares that file as an input.
- `index-lint --check` passes.

# Appendix

## Decisions

| ID     | Date       | Kind     | Decided by  | Decision                                                                                                                                                                                                                     | Raised by                              |
| ------ | ---------- | -------- | ----------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------- |
| DEC-01 | 2026-11-02 | decision | stakeholder | A core artifact must have a producer and a review; "none" is a defect, not a valid state.                                                                                                                                    | project truth map                      |
| DEC-02 | 2026-11-02 | decision | stakeholder | The requirements agent splits by artifact family into scope and behaviour, domain structure, and architecture.                                                                                                               | project truth map                      |
| DEC-03 | 2026-11-02 | decision | stakeholder | State machines belong to the domain structure family, beside the entity model; the architecture agent only reads them.                                                                                                       | state machine question                 |
| DEC-04 | 2026-11-02 | decision | stakeholder | Validation rules and interface contracts belong to the domain structure family, because both are written in terms of the entities.                                                                                           | ownership cut                          |
| DEC-05 | 2026-11-02 | decision | stakeholder | The proposal builds on the core artifact layout and runs after it; it does not amend the layout backlog.                                                                                                                     | backlog question                       |
| DEC-06 | 2026-11-02 | decision | stakeholder | Three derivations hold in the target model: entity model to state machines, entity model to schemas, and `architecture.dsl` to `dependency-rules.dsl`.                                                                       | proposed ownership map                 |
| DEC-07 | 2026-11-02 | decision | stakeholder | `capture-context` leaves the requirements agent; Virgil owns it in fitting.                                                                                                                                                  | ownership cut                          |
| DEC-08 | 2026-11-02 | decision | stakeholder | The missing gates for the entity model, `schemas/*`, and `testing.yaml` get a separate proposal.                                                                                                                             | ownership cut                          |
| DEC-09 | 2026-11-02 | decision | stakeholder | Workflows should not depend on playbooks; ownership follows artifact families, and a later proposal designs the workflows.                                                                                                   | playbook discussion                    |
| DEC-10 | 2026-11-02 | decision | stakeholder | A new test-strategy agent owns the test practice family, `testing.yaml` and the QA strategies; the planning agent is already too large to take them.                                                                         | open question: QA strategy owner       |
| DEC-11 | 2026-11-02 | decision | stakeholder | In fitting step 2b, the session takes the test-strategy agent's role, so Virgil writes no file it does not declare.                                                                                                          | DEC-10                                 |
| DEC-12 | 2026-11-02 | decision | stakeholder | The domain-modeling agent runs at the strong tier, like the requirements and architecture agents it sits between.                                                                                                            | open question: agent tier              |
| DEC-13 | 2026-11-02 | decision | stakeholder | The test-strategy agent runs at the strong tier; the layer assignment is judgment, and the agent is not split by skill to save cost on the scan.                                                                             | grilling: agent tier                   |
| DEC-14 | 2026-11-02 | decision | stakeholder | Every glossary term needs the stakeholder; terms seeded from code are drafts, confirmed with their domain area's scope-map batch.                                                                                            | open question: glossary confirmation   |
| DEC-15 | 2026-11-02 | decision | stakeholder | The glossary holds only confirmed terms; a candidate waits with its proposed definition in `docs/spec/work/term-candidates.md` until the stakeholder confirms it, so the glossary needs no draft marker.                     | DEC-14; review of assumptions          |
| DEC-16 | 2026-11-02 | decision | stakeholder | `reverse-map` writes term candidates to `docs/spec/work/term-candidates.md`; the domain-modeling agent proposes their definitions there and moves each confirmed term into the glossary, so the glossary keeps one producer. | grilling: single producer              |
| DEC-17 | 2026-11-02 | decision | stakeholder | The reconciliation agent edits no core file. It reports every finding in one consolidated report per run, not as separate finding files, and the owners fix.                                                                 | grilling: single producer              |
| DEC-18 | 2026-11-02 | decision | stakeholder | The developer and implementation agents edit no specification file. Drift goes into one spec-feedback report per wave, and the wave closes only when the owners have fixed every row.                                        | grilling: single producer              |
| DEC-19 | 2026-11-02 | decision | stakeholder | The spec-feedback report lives at `docs/spec/work/spec-feedback-<feature-branch>-wave-<n>.md`, as working output of the implementation, not as a review.                                                                     | DEC-18; review of assumptions          |
| DEC-20 | 2026-11-02 | decision | stakeholder | The review of a core artifact is declared on the producer's output declaration as `reviewed_by:`, naming an agent or `stakeholder`; `index-lint` checks it.                                                                  | grilling: contract test                |
| DEC-21 | 2026-11-02 | decision | stakeholder | `run-step` eligibility stays existence-based; eligibility on reviewed inputs waits for the workflow proposal (DEC-09).                                                                                                       | grilling: run-step                     |
| DEC-22 | 2026-11-02 | decision | stakeholder | `reviewed_by:` holds a list, so an artifact can have several reviewers; the glossary declares the spec-review agent and the stakeholder.                                                                                     | lector plan C2                         |
| DEC-23 | 2026-11-02 | decision | stakeholder | The test-strategy agent owns the post-implementation test guardrails; the implementation agent or the developer agent runs them.                                                                                             | stakeholder, after the proposal opened |
| DEC-24 | 2026-11-02 | decision | stakeholder | The test guardrail family is `crap-score`, `mutation-testing`, and `test-design-verify`, plus later gates that measure the tests; `dependency-check` stays with the architecture agent.                                      | grilling: guardrail members            |

## Review findings

| ID      | Pass | Severity | Check | Status | Finding                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | Resolution |
| ------- | ---- | -------- | ----- | ------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------- |
| PROP-01 | 1    | major    | 03    | open   | Line 204 makes the spec-review agent declare `schemas/*` and `areas/*.md` as required inputs, and line 223 forces every reviewer to do so. `run-step` counts an agent as eligible only when a file matches each required input (line 283, DEC-21); `intent select` prints "no file matching" otherwise. `schemas/` exists only when a project has payload schemas (core-artifact-layout.md line 418), and many projects have no area spec. So the spec-review agent never becomes eligible in those projects. Define how a reviewer declares an artifact that a project may not have, and how `index-lint` accepts that declaration.                                                                                                                 |            |
| PROP-02 | 1    | major    | 03    | open   | The glossary keeps a second writer through a skill chain. The requirements agent keeps `clarify-requirements` (line 133), which hands brownfield interviews to `grilling` in domain-modeling mode (`clarify-requirements/SKILL.md` line 21). That mode loads `domain-modeling`, which writes settled terms, after ST-0336 into `glossary.md`. Virgil's `grilling` on proposals does the same (`feature-addition.md` line 208), and so does `reconcile-spec` line 41. State what `grilling` and `domain-modeling` write when an agent other than the domain-modeling agent runs them, for example a row in `term-candidates.md`.                                                                                                                      |            |
| PROP-03 | 1    | major    | 03    | open   | Line 161 has the stakeholder confirm a candidate "together with its domain area's scope-map batch". That batch is confirmed inside the `reverse-map` session of the requirements agent. The domain-modeling agent proposes the definition later, because it needs the scope map and a feature file (line 148). So no definition exists when the batch is confirmed. The scope map also records no confirmation per domain area: it carries one `status: draft` or `confirmed` for the whole map (`reverse-map/SKILL.md` lines 124-136). Neither the domain-modeling agent nor the spec review at line 161 can tell which candidate is confirmed. Define when the stakeholder confirms a proposed definition and where that confirmation is recorded. |            |
| PROP-04 | 1    | major    | 03    | open   | Line 235 puts every drift of a wave into one report, `spec-feedback-<feature-branch>-wave-<n>.md`. The developer agents of one wave run in parallel, and `dispatch-contract.md` lines 28-29 forbid two concurrent assignments that can write the same artifact. Line 303 also removes `docs/spec/**/*.md` from the developer agent's outputs, and no criterion declares the report path for it instead. Give each story its own report path, or say which single agent writes the wave report, and declare that path.                                                                                                                                                                                                                                |            |
| PROP-05 | 1    | major    | 03    | open   | The wave-close rule (lines 237, 304) and the reconciliation loop (lines 227-229) leave out their mechanics. No row format defines a status, so nothing records that a row is fixed and confirmed. No text says who starts the owner's run and the owner's review during an open wave, or whether `dispatch close-wave` checks the report. Manual mode has no wave boundaries (`dispatch-contract.md` lines 227-229), so the rule has no anchor there. Line 229 turns a finding into a code defect but does not say where the defect goes. Define the row columns and statuses, the actor that starts each step, the check `close-wave` runs, and the rule for manual mode.                                                                           |            |
| PROP-06 | 1    | major    | 01    | open   | The contract test at line 300 cannot be built from the text. It needs the list of core artifacts it checks and the source of that list. It also needs a matching rule: output patterns differ in form (`docs/spec/{name}.feature` today, `features/*.feature` after the layout), and broad patterns such as `docs/spec/**/*.md` or `docs/*.md` overlap many files. Name where the test reads the core list and when two declarations count as the same artifact.                                                                                                                                                                                                                                                                                     |            |
| PROP-07 | 1    | major    | 03    | open   | Lines 185 and 298 say the implementation agent runs `mutation-testing` after each story "as today". It does not. Its gate execution calls only the `crap-score`, `dependency-check`, and `test-design-verify` scripts (`implementation-agent.md` lines 226-230). `mutation-testing` is a skill with no script and appears only in the hard-coded default at line 221. The case at line 187 also leaves open whether surviving mutants block the merge, and who starts the test-strategy agent to classify them. Define how mutation testing runs per story and when the classification happens relative to the merge.                                                                                                                                |            |
| PROP-08 | 1    | minor    | 01    | open   | Line 298 holds two checks that cannot be tested as written. Output declarations are per file, so "only the test-strategy agent writes the `gates` section of `testing.yaml`" has no mechanical check. `dependency-check` writes a JSON report to `.current-work/`, and the text does not say which field names the architecture agent as owner. The same line also holds only in automated mode, because the gate-check loop does not run in manual mode (`implementation-agent.md` line 207).                                                                                                                                                                                                                                                       |            |
| PROP-09 | 1    | minor    | 03    | open   | The reconciliation agent today has the skill `capture-context` and declares `docs/*.md`, `docs/adr/*.md`, and `docs/CONTEXT.md`. Line 227 removes only core files. Line 302 makes the report its only output, which also removes ADRs and `agent-context.md`. The two disagree. `capture-context` and `docs/*.md` also give `agent-context.md` a second producer beside Virgil (line 197). State which outputs and skills the reconciliation agent keeps.                                                                                                                                                                                                                                                                                            |            |
| PROP-10 | 1    | minor    | 03    | open   | `areas/*.md` and `schemas/*` get a producer but no procedure. The requirements agent's workflow has no step that writes an area spec (`requirements-agent.md` lines 90-121), and line 133 names none. `domain-modeling` covers only the glossary, and step 1d names only the four structure files. Name the step or skill that writes each one.                                                                                                                                                                                                                                                                                                                                                                                                      |            |
| PROP-11 | 1    | minor    | 03    | open   | Line 165 has the architecture agent file a finding, and line 284 puts the owner into a finding's frontmatter. The architecture agent declares no `docs/findings/*` output, and `finding-format.md` and `templates/finding.md` have no owner field. Neither change is in Scope or Completion Criteria. Add both, or say where those findings go.                                                                                                                                                                                                                                                                                                                                                                                                      |            |
| PROP-12 | 1    | minor    | 03    | open   | Line 173 gives the test-strategy agent two sets of required inputs, one for a QA strategy and one for `testing.yaml`. `inputs.required` is a conjunction, so the agent would need a feature file before it may scan the test suites. "The test suites in the code" is also no path pattern. State the declaration, for example an `any_of`.                                                                                                                                                                                                                                                                                                                                                                                                          |            |
| PROP-13 | 1    | minor    | 02    | open   | Line 278 changes a playbook "only where the playbook names a moved responsibility". Four playbooks name one: `feature-addition`, `greenfield-development`, `brownfield-onboarding`, and `documentation-update`. None is in Scope or in `impact.boundaries`. The routing of the two new agents through `INDEX.yaml` preconditions and `intent` is not in Scope either. List the playbooks and the routing change in the In list.                                                                                                                                                                                                                                                                                                                      |            |
| PROP-14 | 1    | minor    | 03    | open   | The overlap table at lines 245-253 misses overlaps. ST-0336 also edits `inspect-spec`, `reconcile-spec`, and `reverse-map`. ST-0338 also edits `spec-review-agent.md` and `spec-feedback`. ST-0340 edits `developer-agent.md`, `implementation-agent.md`, `reconciliation-agent.md`, and `test-design-verify`. ST-0341 also edits `architecture-review-agent.md`. ST-0342 edits `INDEX.yaml` and `test_index_lint.py`. ST-0329 edits `capture-context`. Complete the table, because line 255 derives story dependencies from it.                                                                                                                                                                                                                     |            |
| PROP-15 | 1    | minor    | 04    | open   | `impact.boundaries` (lines 14-33) leaves out files the Design changes: `reverse-map/SKILL.md` (line 263), `domain-modeling/SKILL.md`, `grilling` and `clarify-requirements`, `capture-context/SKILL.md`, `atam-review/SKILL.md` (line 206), the four playbooks of PROP-13, `INDEX.yaml`, and `finding-format.md`. Add them, so the impact matches the Design.                                                                                                                                                                                                                                                                                                                                                                                        |            |
| PROP-16 | 1    | minor    | 03    | open   | The seam table (line 198) reviews `testing.yaml` with the stakeholder "in fitting". The test-strategy agent also changes the file after fitting, when it sets or adjusts gate thresholds (line 183). No review covers those changes. The text also does not say whether seam declarations carry `reviewed_by:`. Define the review of later changes and the declaration.                                                                                                                                                                                                                                                                                                                                                                              |            |

## Review passes

| Pass | Date       | Reviewed commit                          | Disposition | Failed checks  | Summary                                                                                                                                                                                                                                                                                                                                                                                                                       |
| ---- | ---------- | ---------------------------------------- | ----------- | -------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1    | 2026-11-02 | 739f1e9fa600cf1a77fbe622be4b40b3e3f373dd | findings    | 01, 02, 03, 04 | Every boundary exists, no open question is padding, the motivation names real gaps, and the estimate fits the scope. The single-producer rule still breaks through skill chains and parallel wave reports, and required-input reviews block eligibility in projects without schemas or area specs. The term confirmation, the wave close, and the contract test need their mechanics defined before planning can cut stories. |
