# Gaps Report: core-artifact-ownership

Generated: 2026-11-03
Source: [core-artifact-ownership.md](../../proposals/core-artifact-ownership.md)

The first pass ran unattended and put every point that needed a decision as a question in [Questions for the Stakeholder](#questions-for-the-stakeholder). The stakeholder has answered every question. Each entry records the answer, and the specification follows it.

## Actor-Goal Matrix

| ID     | Actor                     | Goal                                                                | Rule                                                                                           | Status    |
| ------ | ------------------------- | ------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- | --------- |
| CAO-01 | Factory maintainer        | Find exactly one producer for every core and seam artifact          | Rule: Factory maintainer finds exactly one producer for every core and seam artifact           | specified |
| CAO-02 | Factory maintainer        | See every declared review checked against the reviewer's inputs     | Rule: Factory maintainer sees every declared review checked against the reviewer's inputs      | specified |
| CAO-03 | Requirements agent        | Keep scope and behaviour only                                       | Rule: Requirements agent keeps scope and behaviour only                                        | specified |
| CAO-04 | Domain-modeling agent     | Produce the domain structure family                                 | Rule: Domain-modeling agent produces the domain structure family                               | specified |
| CAO-05 | Stakeholder               | Confirm every glossary term before it enters the glossary           | Rule: Stakeholder confirms every glossary term before it enters the glossary                   | specified |
| CAO-06 | CLI-Invoked Agent         | Record terms as candidates when it is not the domain-modeling agent | Rule: Agents other than the domain-modeling agent record terms as candidates                   | specified |
| CAO-07 | Architecture agent        | Own the components and their dependency rules                       | Rule: Architecture agent owns the components and their dependency rules                        | specified |
| CAO-08 | Spec-review agent         | Review behaviour and domain structure                               | Rule: Spec-review agent reviews behaviour and domain structure                                 | specified |
| CAO-09 | Architecture-review agent | Review the dependency rules                                         | Rule: Architecture-review agent reviews the dependency rules                                   | specified |
| CAO-10 | Test-strategy agent       | Own the test practice family                                        | Rule: Test-strategy agent owns the test practice family                                        | specified |
| CAO-11 | Implementation agent      | Block a merge on a failing test guardrail                           | Rule: Implementation agent blocks a merge on a failing test guardrail                          | specified |
| CAO-12 | Test-strategy agent       | Resolve the surviving mutants that a developer agent cannot resolve | Rule: Test-strategy agent resolves the surviving mutants that a developer agent cannot resolve | specified |
| CAO-13 | Developer agent           | Report specification drift without editing the specification        | Rule: Developer agent reports specification drift without editing the specification            | specified |
| CAO-14 | Implementation agent      | Close a wave only after the owners have handled every drift row     | Rule: Implementation agent closes a wave only after the owners have handled every drift row    | specified |
| CAO-15 | Reconciliation agent      | Report drift to each artifact's owner                               | Rule: Reconciliation agent reports drift to each artifact's owner                              | specified |
| CAO-16 | Factory maintainer        | Have every finding reach the agent that acts on it next             | Rule: Owner receives every finding it acts on next                                             | specified |
| CAO-17 | Factory maintainer        | See every writer of shared working output declare its path          | Rule: Factory maintainer sees every writer of shared working output declare its path           | specified |
| CAO-18 | Human operator            | Reach the new owners through the playbooks and the routing          | Rule: Human operator reaches the new owners through the playbooks and the routing              | specified |

The factory maintainer works on the factory's own repository. The stakeholder is the person who owns the domain. The other actors are factory agents. Each agent acts for the goal its Rule names, and the factory maintainer checks the agent's declarations.

## Completion Criteria Trace

Each completion criterion of the proposal traces to a Rule or to a question below.

| Completion criterion (short form)                                                                        | Rule or gap                        |
| -------------------------------------------------------------------------------------------------------- | ---------------------------------- |
| The requirements agent declares three core outputs and its working output, without two skills            | CAO-03                             |
| `domain-modeling-agent.md` exists at the strong tier with its inputs, six outputs, and handoff           | CAO-04                             |
| The requirements agent's handoff names the domain-modeling agent                                         | CAO-03                             |
| The architecture agent declares `dependency-rules.dsl`; `maintain-architecture` writes no state machines | CAO-07                             |
| The spec-review agent's required and context inputs; `inspect-spec` checks each structure file           | CAO-08                             |
| The architecture-review agent declares `dependency-rules.dsl` as a context input                         | CAO-09, CAO-G01                    |
| `test-strategy-agent.md` exists with four skills, no required input, and two outputs                     | CAO-10                             |
| The implementation agent runs four gates and blocks the merge; manual mode runs them in the developer    | CAO-11, CAO-G24, CAO-G25           |
| The `dependency-check` JSON report names the architecture agent as owner                                 | CAO-07, question CAO-G07           |
| Virgil declares no `testing.yaml`; fitting step 2b names the test-strategy agent                         | CAO-10                             |
| `core-artifacts.yaml` lists every artifact of the contract and seam tables                               | CAO-01, questions CAO-G05, CAO-G12 |
| A test reads the core list and `INDEX.yaml` and fails on zero or several producers or no review          | CAO-01                             |
| `index-lint` fails on an unknown reviewer or a reviewer without the input                                | CAO-02                             |
| The reconciliation agent declares only its report and has no `capture-context`                           | CAO-15                             |
| The developer and implementation agents declare no `docs/spec/**/*.md`; `spec-feedback` writes rows      | CAO-13                             |
| After a merge, the implementation agent dispatches owner, reviewer, and the test-strategy agent          | CAO-14, CAO-12, question CAO-G02   |
| `reconcile-spec` writes report rows only                                                                 | CAO-15                             |
| `dispatch close-wave` fails on `open`, and on `fixed` for a core artifact; manual mode per story         | CAO-14, questions CAO-G03, CAO-G04 |
| The architecture agent declares `ARCH` findings and two context inputs; `owner:`, tags, and routing      | CAO-07, CAO-16                     |
| Every writer of the Working output table declares its path; the lector agent carries `edits: wording`    | CAO-17, CAO-01                     |
| `grilling` and `domain-modeling`, run by another agent, write candidate rows, not the glossary           | CAO-06                             |
| The term confirmation pause point, the schema step, and the area spec step exist                         | CAO-05, CAO-04, CAO-03             |
| The four playbooks name the new owners                                                                   | CAO-18                             |
| `reverse-map` writes term candidates; the domain-modeling agent reads them                               | CAO-06, CAO-04                     |
| The spec review files a finding for every `proposed` row                                                 | CAO-08                             |
| The planning agent stops on a missing `testing.yaml`, reads `QA` findings, and depends on ST-0340        | CAO-10, CAO-12, CAO-G17            |
| The architecture-review agent reads `dependency-rules.dsl` as context; the core list marks it optional   | CAO-09                             |
| A `rejected` row becomes a `BUG` finding with the developer agent as owner                               | CAO-14, CAO-17, question CAO-G11   |
| `index-lint` carries `reviewed_by:` and `edits:` and matches by sample path                              | CAO-02, questions CAO-G06, CAO-G14 |
| The mutation tool's configuration stays in the project's own files                                       | CAO-10, decided CAO-G08            |
| `index-lint --check` passes                                                                              | CAO-02                             |

## Missing Rules

None. Every actor-goal pair has a Rule.

## Rules Without Scenarios

None. Every Rule has at least one Scenario.

## Questions for the Stakeholder

Each question gives one case, the outcome of each option, the recommendation, and what the answer settles.

The stakeholder decided G08 and G10 on 2026-11-03 and accepted the recommendation of every other question (G01 to G07, G09, G11 to G16) on the same day. These answers are decisions, and the specification follows each of them.

### CAO-G01: Does the architecture-review agent require `dependency-rules.dsl`?

- **Case:** A migrated project has `architecture.dsl` and no `dependency-rules.dsl`, because no agent wrote the file before this feature.
- **Options:** With a required input, the architecture-review agent never becomes eligible in that project. With a context input, the review runs and checks the rules once the file exists.
- **Conflict:** The Reviews section and the completion criterion on line 375 say "required input". The criterion on line 396 and the fix of PROP-31 say "context input".
- **Recommendation:** Context input, as PROP-31 and DEC-25 decide. Accepted on 2026-11-03.
- **Settles:** CAO-09 and the criterion on line 375. The proposal now says "context input" there (2026-11-03).

### CAO-G02: When does the test-strategy agent handle an open `QA` finding?

- **Case:** ST-0318 merges in wave 2 with the open finding QA-0003. ST-0319 of the same wave merges later.
- **Options:** "After the wave" (Quality guardrails) dispatches the test-strategy agent once, after ST-0319. "After a story merges" (the criterion on line 385) dispatches it right after ST-0318.
- **Open part:** The proposal also does not say whether `close-wave` waits for open `QA` findings. Today `close-wave` reads no finding.
- **Recommendation:** After the story merges, with the row owners, because the completion criteria are the acceptance baseline. `close-wave` does not wait for `QA` findings, because the proposal names only report rows as its check. Accepted on 2026-11-03.
- **Settles:** CAO-12, `Scenario: The implementation agent dispatches the test-strategy agent for each open QA finding`.

### CAO-G03: Does manual mode let a `fixed` row on a non-core artifact close the story?

- **Case:** In manual mode, `spec-feedback-ST-0318.md` has one `fixed` row about `docs/spec/work/payments-qa-strategy.md`.
- **Options:** The text of Spec feedback during implementation says that the story closes only without `open` or `fixed` rows, so ST-0318 stays open for good. DEC-35 and the criterion on line 387 say "the same rule per story", so ST-0318 closes.
- **Recommendation:** The same rule as `close-wave`, so ST-0318 closes. A QA strategy has no reviewer who could set `confirmed`. Accepted on 2026-11-03.
- **Settles:** CAO-14 and the manual-mode section of `dispatch-contract.md`.

### CAO-G04: Which columns does a report row have?

- **Case:** `dispatch close-wave` parses `spec-feedback-ST-0318.md` and must find the artifact and the status of each row.
- **Options:** The proposal names the content of a row: the artifact, the drift, its evidence in the code, the owner, and a status. It names no column headers. Without fixed headers, `close-wave` cannot parse the table. For the reconciliation report the proposal says "mismatch" instead of "drift".
- **Recommendation:** One table shape for both reports, with the columns Artifact, Drift, Evidence, Owner, and Status. The [interface contracts](../interface-contracts.md#report-rows-spec-feedback-and-reconciliation) use these headers. Accepted on 2026-11-03.
- **Settles:** The report-row contract, CAO-13, CAO-14, and CAO-15.

### CAO-G05: What does an entry of `core-artifacts.yaml` hold?

- **Case:** The entry for the feature files has the pattern `docs/spec/features/*.feature`. The contract test needs a sample path, such as `docs/spec/features/example.feature`.
- **Options:** The entry stores its sample path in a field, so the test reads it. Or the test derives the sample path from the pattern, so each wildcard needs a fixed replacement rule.
- **Recommendation:** A stored field, because a stored sample needs no rule for `*`, `**`, and `{name}`. The proposal names the content of an entry (path pattern, family, may a project lack it) but no field names. The [interface contracts](../interface-contracts.md#packagesfactoryrulebookscore-artifactsyaml) use `path_pattern`, `sample_path`, `family`, and `optional`. Accepted on 2026-11-03.
- **Settles:** The core list contract, CAO-01, and CAO-14.

### CAO-G06: Where does `index-lint` get the sample path for its reviewer check?

- **Case:** The requirements agent declares `docs/spec/features/{name}.feature` with `reviewed_by: [spec-review-agent]`. The spec-review agent reads `docs/spec/features/*.feature`.
- **Options:** `index-lint` reads `core-artifacts.yaml` and checks only listed artifacts, with their stored sample paths. Or `index-lint` derives a sample path from every declaration that carries `reviewed_by:`, without the core list.
- **Recommendation:** Read the core list, because the contract test uses the same list and the same sample paths. The two checks then cannot disagree. The `index-lint` contract reads the core list. Accepted on 2026-11-03.
- **Settles:** The `index-lint` contract and CAO-02.

### CAO-G07: Which field of the `dependency-check` report names the owner?

- **Case:** `dependency-check` writes `.current-work/dependency-check/ST-0318.json`, a list of rule results with `rule_name`, `pass_fail`, and `violating_import`.
- **Options:** A field `owner: architecture-agent` on each result. Or one top-level `owner` for the whole report, which changes the report from a list to an object and breaks its readers.
- **Recommendation:** The field `owner` on each result entry, the same name as the finding's `owner:` field. The [interface contracts](../interface-contracts.md#agent-factoryfactoryscriptsdependency-check) use it. Accepted on 2026-11-03. On 2026-11-04 the stakeholder narrowed it: only failing entries carry `owner`, because `owner` names the agent that acts next (as for findings, CAO-G26); a passing entry carries none.
- **Settles:** The `dependency-check` contract and CAO-07.

### CAO-G08: How does a fixed agent definition declare project-specific mutation files?

- **Case:** A Python project configures mutmut in `setup.cfg`. A Java project configures PIT in `pom.xml`. The test-strategy agent definition ships with the factory and is the same in both.
- **Decision (stakeholder, 2026-11-03, DEC-36):** Mutation testing is a project capability. The tool's configuration lives in the project's own files, and a story sets it up with the `mutation-testing` skill as guidance. `testing.yaml` holds only `gates.mutation_testing.enabled` and `gates.mutation_testing.command`. The test-strategy agent declares no configuration file of the tool, and the Factory knows no tool format.
- **Settles:** CAO-10, `Scenario: The mutation tool's configuration stays in the project's own files`, the `testing.yaml` contract, and the criterion that replaced PROP-35's.

### CAO-G09: May a rejected term definition be proposed again?

- **Case:** The stakeholder rejects the definition of Slot. The domain-modeling agent learns the right meaning from the note.
- **Options:** The row returns to `proposed` with a new definition, and the stakeholder sees it in the next session. Or the row stays `rejected`, and Slot never enters the glossary.
- **Recommendation:** Return to `proposed`, because the note exists so the next proposal can use it. The proposal does not say so.
- **Answer (stakeholder, 2026-11-03):** Accepted. The [Term Candidate Lifecycle](../state-machines.md#term-candidate-lifecycle) has the transition `rejected → proposed`, the row keeps the stakeholder's note, and BR-065 states the rule. `Scenario: A rejected term returns to proposed with a new definition` covers it.
- **Settles:** The term-candidate lifecycle and CAO-05.

### CAO-G10: Which status does a `QA` finding get when a test is missing?

- **Case:** The test-strategy agent records in QA-0003 that a contract test for `plan_moves` is missing. The planning agent must later add that test to a story.
- **Options:** The status stays `open`, so the orchestrator keeps routing QA-0003 to the test-strategy agent. Or the status becomes `resolved`, so the open-finding loop ends but the planning agent must look for resolved findings with a missing test.
- **Decision (stakeholder, 2026-11-03):** The status stays `open`, and `owner:` moves from the test-strategy agent to the planning agent. The finding becomes `resolved` when the story that adds the test merges. The implementation agent dispatches the test-strategy agent only for open `QA` findings that it owns.
- **Settles:** CAO-12, `Scenario: The test-strategy agent skips an open QA finding whose owner is the planning agent`, and the finding format. The glossary term Owner and `FINDING.owner` define the owner as the agent that acts on the finding next (SPEC-0033).

### CAO-G11: Which agents declare `BUG` findings?

- **Case:** The stakeholder rejects a fixed row about `docs/spec/scope-map.md` in a session of the requirements agent. The requirements agent must file the `BUG` finding.
- **Options:** The criterion on line 397 has only the reviewers declare `docs/findings/BUG-*.md`. Then the requirements agent writes a file it does not declare. Or every agent that runs a stakeholder review declares the path too: the requirements agent, the domain-modeling agent, the test-strategy agent, and Virgil.
- **Recommendation:** Every agent that runs a stakeholder review declares the path, because no agent may write a file it does not declare (DEC-11).
- **Answer (stakeholder, 2026-11-03):** Accepted. The CAO-17 outline has a `docs/findings/BUG-*.md` row for each of the four agents and for the two reviewers. The output Scenarios of CAO-03 and CAO-04 name `BUG-*.md` and say "the outputs include", so they do not close the list.
- **Settles:** CAO-14, CAO-17, and the four agent definitions.

### CAO-G12: Which entries of the core list may a project lack?

- **Case:** A brownfield project has no `docs/testing.yaml` yet. The planning agent stops on that (CAO-10), but the core list must say whether the entry is optional.
- **Options:** The proposal states the value for `schemas/*`, `areas/*.md`, `dependency-rules.dsl`, `state-machines.md`, `validation-rules.md`, and `interface-contracts.md`: a project may lack them. It states nothing for `architecture.dsl`, `agent-context.md`, and `testing.yaml`.
- **Recommendation:** `architecture.dsl` and `agent-context.md` are not optional, because both are anchor files. `testing.yaml` is optional, because the test-strategy agent creates it on demand. The [interface contracts](../interface-contracts.md#packagesfactoryrulebookscore-artifactsyaml) carry these three values. Accepted on 2026-11-03.
- **Settles:** The core list contract and CAO-01.

### CAO-G13: Does a story without a spec-feedback report block the wave?

- **Case:** ST-0319 found no drift, so `spec-feedback-ST-0319.md` does not exist.
- **Options:** A missing report counts as a report without rows, so the wave closes. Or `close-wave` fails, so every developer agent must write an empty report.
- **Recommendation:** A missing report counts as no rows, because the developer agent writes a row only when it finds drift. The [validation rules](../validation-rules.md#ownership-and-drift-reports-core-artifact-ownership-br-056br-066) state this rule in BR-063. Accepted on 2026-11-03.
- **Settles:** CAO-14 and the `close-wave` contract.

### CAO-G14: Does a `{name}` placeholder match like `*`?

- **Case:** The requirements agent declares `docs/spec/features/{name}.feature`. The sample path is `docs/spec/features/example.feature`.
- **Options:** `{name}` matches any text inside one path segment, so the sample path matches. Or `{name}` is a literal, so the requirements agent declares no producer of the feature files, and the contract test fails.
- **Recommendation:** `{name}` matches like `*`, because PROP-33 names exactly this pattern pair as the case the sample path resolves. The [validation rules](../validation-rules.md#ownership-and-drift-reports-core-artifact-ownership-br-056br-066) state this rule in BR-057. Accepted on 2026-11-03.
- **Settles:** The matching rule of the contract test and of `index-lint`.

### CAO-G15: Does the stakeholder confirm the glossary terms this pass added?

- **Case:** This pass added terms such as Producer, Seam File, and Term Candidate to `docs/spec/glossary.md`. Each definition comes from the accepted proposal.
- **Options:** The terms count as confirmed, because the stakeholder accepted the proposal that defines them. Or they wait in `docs/spec/work/term-candidates.md`, as DEC-14 asks for every new term once this feature is built.
- **Recommendation:** Confirm them at the next spec review, because the rule of DEC-14 is not yet in force and the accepted proposal settles their meaning.
- **Answer (stakeholder, 2026-11-03):** The stakeholder confirmed the nine terms Artifact Family, Producer, Reviewer, Seam File, Core List, Stakeholder, Term Candidate, Spec-Feedback Report, and Test Guardrail. The term Owner joined the glossary in the fix pass for SPEC-0033, from the stakeholder's definition of that day.
- **Settles:** The new rows in the glossary's Terms section.

### CAO-G16: Which path does "the source code" stand for?

- **Case:** The domain-modeling agent reads the source code as a context input. In the factory's own repository, the code lives under `packages/`. In other projects it often lives under `src/`.
- **Options:** Declare `src/**/*`, as the reconciliation agent does, and miss the factory's own code. Or declare no path, and keep the input as an instruction in the workflow.
- **Recommendation:** Declare `src/**/*`, the same pattern as the other agents, and let the workflow read further code by instruction. The proposal names no pattern. Accepted on 2026-11-03; `Scenario: The domain-modeling agent definition declares the domain structure family` names `src/**/*`.
- **Settles:** The domain-modeling agent's context inputs, CAO-04.

### CAO-G24: Does the gate list pick `dependency-check`?

- **Case:** ST-0318 has no `quality-gates` field. `docs/testing.yaml` has a `gates` section that enables only `crap_score`. The `gates` schema has no entry for `dependency-check`.
- **Options:** If the gate list picks `dependency-check`, it never runs in a project with a `gates` section. If it always runs, the gate list picks only the test guardrails.
- **Answer (stakeholder, 2026-11-03, SPEC-0030):** `dependency-check` always runs after each story. The story's `quality-gates` field, then the `gates` section of `testing.yaml`, picks only `crap-score`, `test-design-verify`, and mutation testing. Without either, the default runs `crap-score`. No default runs mutation testing, because its command lives in the `gates` section. CAO-G25 later took `test-design-verify` out of the picked list.
- **Settles:** BR-066, CAO-11, the `gates` section schema, and CAO-11-CT-01.

### CAO-G25: Which test guardrails can the story's `quality-gates` field pick?

- **Case:** ST-0318 has `quality-gates: [crap-score]` and a Test Design section. The field's enum lists `crap-score`, `mutation-analysis`, and `dependency-check`, so it cannot name `test-design-verify`. The `gates` schema runs `test-design-verify` whenever the story has test-design output ([SPEC-0036](../../findings/SPEC-0036.md)).
- **Options:** If the field picks `test-design-verify`, ST-0318 skips it, and no story can ever name it. If the gate runs on its sections, ST-0318 runs `crap-score`, `test-design-verify`, and `dependency-check`.
- **Answer (stakeholder, 2026-11-03, SPEC-0036):** The field picks only `crap-score` and `mutation-testing`, then the `gates` section picks them, and the default without either stays `crap-score`. `test-design-verify` is never picked: it runs whenever the story has a Test Design or Prior Tests section. `dependency-check` runs after every story and leaves the enum, and a story that omits it needs no note. The mutation gate has one name, `mutation-testing`, as in `backlog-lint` and the skill. The scope-map rows of other features that name the old skill `mutation-analysis` stay as they are.
- **Settles:** BR-066, the `quality-gates` contract, the term Test Guardrail, CAO-11, and CAO-11-CT-01. The CAO-11 story changes `packages/factory/scripts/backlog-lint`, its enum and its note rule, and `packages/factory/agents/implementation-agent.md`, its default list.

### CAO-G26: Where does a finding without `owner:` go?

- **Case:** SPEC-0041 is open and is about `docs/spec/state-machines.md`. An older review filed it before `owner:` existed, so the field is missing ([ST-0352](../../../backlog/ST-0352.md)).
- **Options:** If the orchestrator skips the finding, nobody acts on it. If it goes to the producer of the artifact it names, the domain-modeling agent gets it.
- **Decision (stakeholder, 2026-11-04):** An open finding without `owner:` goes to the producer of the artifact it names, read from the output declarations.
- **Settles:** The [`owner:` contract](../interface-contracts.md#finding-frontmatter-owner) and CAO-16.

### CAO-G27: How long may the mutation command run?

- **Case:** After ST-0318 the mutation command runs for hours. The implementation agent waits, and the merge neither passes nor fails ([ST-0359](../../../backlog/ST-0359.md)).
- **Options:** If the agent's session sets the limit, each run may stop at a different time. If the gate script enforces a limit from `testing.yaml`, every run stops at the same time and leaves a result.
- **Decision (stakeholder, 2026-11-04):** `gates.mutation_testing.timeout_minutes` is an optional integer with the default 30. The gate script enforces the limit and writes a failing result file on timeout. The merge reads that result.
- **Settles:** BR-066, the [`gates` section schema](../interface-contracts.md#docstestingyaml--gates-section-schema), and CAO-11.

### CAO-G28: What happens to `default_quality_gates` in the house rules?

- **Case:** A project keeps `default_quality_gates` in `docs/charter/house-rules.md` and adds a `gates` section to `docs/testing.yaml`. `premerge-check` reads the house rules today ([ST-0359](../../../backlog/ST-0359.md)).
- **Options:** If both sources count, the two lists can disagree. If the `gates` section replaces the old field, the project needs to learn that the old line no longer counts.
- **Decision (stakeholder, 2026-11-04):** The `gates` section replaces `default_quality_gates`. `premerge-check` warns and names the file when it still finds `default_quality_gates`.
- **Settles:** BR-066 and CAO-11.

### CAO-G29: What does a second reconciliation run on the same day write?

- **Case:** The reconciliation agent runs twice on 2026-11-03. Both runs would write `docs/reviews/reconciliation-2026-11-03.md` ([ST-0363](../../../backlog/ST-0363.md)).
- **Options:** If the second run overwrites the file, the rows of the first run are lost. If it adds a suffix, each run keeps its own report.
- **Decision (stakeholder, 2026-11-04):** A second run on the same day writes `reconciliation-<date>-2.md`, a third `-3`, and so on. The reports sort by date first, then by suffix. The file without a suffix is run 1.
- **Settles:** The [report path](../interface-contracts.md#report-rows-spec-feedback-and-reconciliation) and CAO-15.

### CAO-G30: May `init-factory` write `docs/testing.yaml`?

- **Case:** The test-strategy agent owns `docs/testing.yaml`, and every change waits for the stakeholder (DEC-31). `init-factory` creates the file at install when it is missing and the scan finds exactly one test command ([ST-0357](../../../backlog/ST-0357.md)). With several commands it asks; it never overwrites the file.
- **Options:** Accept the write as a first draft. Or `init-factory` only reports the command and the test-strategy agent writes the file, which needs a story, and `dispatch init` cannot run before the agent has.
- **Decision (stakeholder, 2026-11-04):** Accept it. `init-factory` may create `docs/testing.yaml` once, only when the file is missing and the command is unambiguous. It is the only writer besides the test-strategy agent. The stakeholder confirms the draft in the fitting step "Test regime".
- **Settles:** The [`init-factory` contract](../interface-contracts.md#factoryscriptsinit-factory) and the `docs/testing.yaml` entry of the core list.

## Ambiguous Wording

| ID      | Location                                                       | Text                                                       | Issue                                                                                                         | Disposition                                                                                                |
| ------- | -------------------------------------------------------------- | ---------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| CAO-G18 | Proposal, Scope, `close-wave` bullet                           | "fails while a row of the wave's reports is open or fixed" | The Scope bullet leaves out DEC-35, which lets a `fixed` row on a non-core artifact pass.                     | The specification follows DEC-35 and the criterion on line 387.                                            |
| CAO-G19 | Proposal, The architecture agent, Step 5                       | "When they contradict each other"                          | The proposal does not say what counts as a contradiction between a component and a state machine.             | The Scenario uses one case: a transition that no component performs. `maintain-architecture` defines more. |
| CAO-G20 | Rule: Stakeholder confirms every glossary term …, domain areas | "one domain area at a time"                                | The proposal does not say where the domain areas come from. The Domain area column of the work file holds it. | The domain area of a row is the scope-map area that `reverse-map` or the session assigned to it.           |

## Other Gaps

| ID      | Gap                                                                                                                                                                                                                                                                                                                          |
| ------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| CAO-G17 | Planning order is not a behaviour of the system, so no Rule holds it. Each story names its overlapping layout story as a dependency (DEC-05), and the planning-agent story depends on ST-0340. After ST-0337 merges, a story redirects the output of `reverse-map` from the glossary to `docs/spec/work/term-candidates.md`. |
| CAO-G21 | The proposal defers the gates for `entity-model.md`, `schemas/*`, and `testing.yaml` (DEC-08). The contract test therefore checks producer and review only. No scenario checks a gate for these three artifacts.                                                                                                             |
| CAO-G22 | Eligibility on reviewed inputs waits for the workflow proposal (DEC-09, DEC-21). So `run-step` lets the test-strategy agent run before the spec review confirms a contract. A contract that the review changes then needs a revised QA strategy. No check enforces that revision.                                            |
| CAO-G23 | This pass edited `state-machines.md`, `entity-model.md`, `validation-rules.md`, `interface-contracts.md`, and `glossary.md` as the requirements agent. After this feature, the domain-modeling agent owns these files. The spec review of this pass checks them as usual.                                                    |

## Deferred Scope

The proposal defers gates for the entity model, `schemas/*`, and `testing.yaml`, DBML for the entity model, a blocking glossary gate, and workflows without playbooks. This specification defines no Rule for them.
