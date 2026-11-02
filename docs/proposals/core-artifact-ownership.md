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

In the Agent Factory, agents write the files that describe a software project. The most important ones form the core. People edit a core file, other files derive from it, and an automatic check, called a gate, tests it. Each agent declares which files it reads and which it writes.

Today three core files have no agent that writes them, so they are never created. Eight have no review, so nobody confirms them. The state machine file, which describes how each entity changes its status, has two writers. The requirements agent does too much: it interviews, maps the scope, writes the behaviour, models the data, and plans the tests.

The proposal sorts the core into three families, and each family gets one owner. The requirements agent keeps scope and behaviour, which say what the system must do. A new domain-modeling agent takes domain structure: the glossary, the data model, and the rules and contracts written in terms of the entities. The architecture agent owns the components and their dependency rules. Outside the core, a new test-strategy agent owns the record of how the project tests and the test plan for each feature. Virgil, the guide agent that runs the project setup called fitting, owns the file that tells agents where project knowledge lives.

Every core file then has exactly one producer, the agent that writes it, and a declared review in a separate session. A test reads the index of all agent definitions and fails when a core file has no producer, more than one producer, or no reviewer. The spec-review agent reviews the behaviour files and the domain structure. The architecture-review agent reviews the architecture. The stakeholder, the person who owns the domain, confirms the scope map and every glossary term, because only that person can settle what a term means. Terms found in the code enter the glossary as drafts until the stakeholder confirms them.

An agent that reads a file it does not own reports a finding and leaves the file alone. Take a case from the proposal. The code renames a task status from PENDING to WAITING, but the state machine file still says PENDING. The reconciliation agent compares the core with the code and writes a report row that names the file and its owner, the domain-modeling agent. The domain-modeling agent updates the file, and the spec review confirms the change.

The obvious shortcut lets the agent that finds an error fix it. The proposal does not take it, because the file would then have several writers, and the fix would skip the owner's review. The same rule holds during implementation. The developer agent and the implementation agent, which hands out stories in waves, edit no specification file. The developer agent writes each drift into one report per wave. A wave closes only when the owners have fixed every row and their reviews have confirmed the fixes. So the specification lags the code by one wave at most.

The proposal leaves no question open.

## Summary

Every core artifact gets exactly one producing agent and one review, and both are declared in the agents' frontmatter. The requirements agent keeps scope and behaviour and gives up two artifact families. A new domain-modeling agent takes domain structure: the glossary, the data model, and the rules and contracts written in terms of the entities. A new test-strategy agent takes test practice: the record of how the project tests, and the QA strategies. The first release closes every producer and review gap on the [project truth map](project-truth-map.drawio). It builds on the [core artifact layout](core-artifact-layout.md) and starts after that release's agent stories are merged.

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

The core splits into three families, each with one owner: scope and behaviour (requirements agent), domain structure (domain-modeling agent), and architecture (architecture agent) (DEC-02). Outside the core, the test practice family, `testing.yaml` and the QA strategies, has its own owner, the test-strategy agent (DEC-10). The paths are those of the core artifact layout (DEC-05).

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
- **Outputs:** the six artifacts of the domain structure family.
- **Handoff:** the spec-review agent, in a new session.

It writes each state machine's pseudocode and derives its Mermaid diagram, as the state machine notation requires. `statemachine-lint` checks that the two agree.

### Glossary terms

Only the domain owner can settle a term, so every glossary term needs the stakeholder's confirmation (DEC-14). A term settled in a `domain-modeling` session is confirmed there.

A term found in the code takes a longer path. During its sweep of the tests and the code, `reverse-map` writes the type, class and module names it finds to `docs/spec/work/term-candidates.md`. So the glossary keeps one producer (DEC-16). The domain-modeling agent then turns each candidate into a draft term of the glossary.

A domain section of `glossary.md` that holds draft terms starts with the line `Status: draft`. The Term/Definition/Avoid tables of the core artifact layout stay unchanged (DEC-15). The line is a marker in the content, like the `status: draft` of the scope map. It is not an artifact state that `run-step` evaluates. Artifact states belong to the workflow proposal, as the deferrals in [Scope](#scope) say.

The stakeholder confirms the draft terms together with their domain area's scope-map batch. Confirming the section's scope-map batch removes the `Status: draft` line. The spec review files a finding for every draft term it still finds.

### The architecture agent

The architecture agent declares `dependency-rules.dsl` as an output. It writes no `state-machines.md`. Step 5 of `maintain-architecture` is a read check: the architecture agent compares the components with the state machines and files a finding when they contradict each other.

### The test-strategy agent

A new agent definition, `packages/factory/agents/test-strategy-agent.md`, owns the test practice family (DEC-10). The family has two files: `docs/testing.yaml` records how the project tests, and each `docs/spec/work/<feature>-qa-strategy.md` plans what to test for one feature. The QA strategy is built from the layer bindings in `testing.yaml`, so both files belong to one owner.

- **Tier:** strong, because assigning each contract its owning test layer is judgment. Three agents work from the QA strategy: the QA agent, the code-review agent, and the developer agent (DEC-13).
- **Skills:** `detect-test-regime` and `qa-strategy-from-spec`.
- **Inputs required:** the feature file, `interface-contracts.md`, and `entity-model.md` for a QA strategy; the test suites in the code for `testing.yaml`.
- **Outputs:** `docs/testing.yaml` and `docs/spec/work/*-qa-strategy.md`.
- **Handoff:** the planning agent, which assigns the strategy's contracts to stories in its testability probe.

The planning agent and the QA agent do not write the QA strategy. The planning agent already carries the whole backlog sequence, and the QA agent reviews code against the strategy.

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

The developer agent and the implementation agent edit no specification file (DEC-18). When an implementation reveals drift, the developer agent writes a row into one spec-feedback report per wave, `docs/reviews/spec-feedback-<feature-branch>-wave-<n>.md` (DEC-19). Each row names the artifact, the drift with its evidence in the code, and the artifact's owner. `spec-feedback` Step 2 writes report rows.

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
- `reverse-map` writes term candidates to `docs/spec/work/term-candidates.md` instead of the glossary, and the domain-modeling agent turns them into draft terms.
- The architecture agent declares `dependency-rules.dsl` and stops writing `state-machines.md`.
- The spec-review agent and `inspect-spec` review every artifact of two families, the glossary included.
- The architecture-review agent reviews `dependency-rules.dsl`.
- The new test-strategy agent declares `testing.yaml` and the QA strategies, and Virgil stops declaring `testing.yaml`.
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
- `agents/test-strategy-agent.md` exists, lists `detect-test-regime` and `qa-strategy-from-spec` as its skills, and declares `docs/testing.yaml` and `docs/spec/work/*-qa-strategy.md` as its outputs. No other agent declares either.
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

| ID     | Date       | Kind       | Decided by  | Decision                                                                                                                                                                              | Raised by                            |
| ------ | ---------- | ---------- | ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------ |
| DEC-01 | 2026-11-02 | decision   | stakeholder | A core artifact must have a producer and a review; "none" is a defect, not a valid state.                                                                                             | project truth map                    |
| DEC-02 | 2026-11-02 | decision   | stakeholder | The requirements agent splits by artifact family into scope and behaviour, domain structure, and architecture.                                                                        | project truth map                    |
| DEC-03 | 2026-11-02 | decision   | stakeholder | State machines belong to the domain structure family, beside the entity model; the architecture agent only reads them.                                                                | state machine question               |
| DEC-04 | 2026-11-02 | decision   | stakeholder | Validation rules and interface contracts belong to the domain structure family, because both are written in terms of the entities.                                                    | ownership cut                        |
| DEC-05 | 2026-11-02 | decision   | stakeholder | The proposal builds on the core artifact layout and runs after it; it does not amend the layout backlog.                                                                              | backlog question                     |
| DEC-06 | 2026-11-02 | decision   | stakeholder | Three derivations hold in the target model: entity model to state machines, entity model to schemas, and `architecture.dsl` to `dependency-rules.dsl`.                                | proposed ownership map               |
| DEC-07 | 2026-11-02 | decision   | stakeholder | `capture-context` leaves the requirements agent; Virgil owns it in fitting.                                                                                                           | ownership cut                        |
| DEC-08 | 2026-11-02 | decision   | stakeholder | The missing gates for the entity model, `schemas/*`, and `testing.yaml` get a separate proposal.                                                                                      | ownership cut                        |
| DEC-09 | 2026-11-02 | decision   | stakeholder | Workflows should not depend on playbooks; ownership follows artifact families, and a later proposal designs the workflows.                                                            | playbook discussion                  |
| DEC-10 | 2026-11-02 | decision   | stakeholder | A new test-strategy agent owns the test practice family, `testing.yaml` and the QA strategies; the planning agent is already too large to take them.                                  | open question: QA strategy owner     |
| DEC-11 | 2026-11-02 | assumption | author      | In fitting step 2b, the session takes the test-strategy agent's role, so Virgil writes no file it does not declare.                                                                   | DEC-10                               |
| DEC-12 | 2026-11-02 | decision   | stakeholder | The domain-modeling agent runs at the strong tier, like the requirements and architecture agents it sits between.                                                                     | open question: agent tier            |
| DEC-13 | 2026-11-02 | decision   | stakeholder | The test-strategy agent runs at the strong tier; the layer assignment is judgment, and the agent is not split by skill to save cost on the scan.                                      | grilling: agent tier                 |
| DEC-14 | 2026-11-02 | decision   | stakeholder | Every glossary term needs the stakeholder; terms seeded from code are drafts, confirmed with their domain area's scope-map batch.                                                     | open question: glossary confirmation |
| DEC-15 | 2026-11-02 | assumption | author      | A draft domain section of the glossary is marked by a `Status: draft` line, so the layout's Term/Definition/Avoid tables stay unchanged.                                              | DEC-14                               |
| DEC-16 | 2026-11-02 | decision   | stakeholder | `reverse-map` writes term candidates to `docs/spec/work/term-candidates.md`; the domain-modeling agent turns them into draft glossary terms, so the glossary keeps one producer.      | grilling: single producer            |
| DEC-17 | 2026-11-02 | decision   | stakeholder | The reconciliation agent edits no core file. It reports every finding in one consolidated report per run, not as separate finding files, and the owners fix.                          | grilling: single producer            |
| DEC-18 | 2026-11-02 | decision   | stakeholder | The developer and implementation agents edit no specification file. Drift goes into one spec-feedback report per wave, and the wave closes only when the owners have fixed every row. | grilling: single producer            |
| DEC-19 | 2026-11-02 | assumption | author      | The spec-feedback report lives at `docs/reviews/spec-feedback-<feature-branch>-wave-<n>.md`, beside the reconciliation reports.                                                       | DEC-18                               |
| DEC-20 | 2026-11-02 | decision   | stakeholder | The review of a core artifact is declared on the producer's output declaration as `reviewed_by:`, naming an agent or `stakeholder`; `index-lint` checks it.                           | grilling: contract test              |
| DEC-21 | 2026-11-02 | decision   | stakeholder | `run-step` eligibility stays existence-based; eligibility on reviewed inputs waits for the workflow proposal (DEC-09).                                                                | grilling: run-step                   |
| DEC-22 | 2026-11-02 | decision   | stakeholder | `reviewed_by:` holds a list, so an artifact can have several reviewers; the glossary declares the spec-review agent and the stakeholder.                                              | lector plan C2                       |

## Review findings

No review has run yet.

| ID  | Pass | Severity | Check | Status | Finding | Resolution |
| --- | ---- | -------- | ----- | ------ | ------- | ---------- |

## Review passes

No review has run yet.

| Pass | Date | Reviewed commit | Disposition | Failed checks | Summary |
| ---- | ---- | --------------- | ----------- | ------------- | ------- |
