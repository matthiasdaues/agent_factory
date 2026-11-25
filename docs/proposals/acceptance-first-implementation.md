---
scope: global
schema_version: 2
title: Acceptance-First Implementation
status: draft
owner: Matthias Daues
created: 2026-11-21
updated: 2026-11-24
supersedes:

impact:
  scope: cross_component
  architecture_change: true
  external_contract_change: true
  boundaries:
    - packages/factory/agents/implementation-agent.md
    - packages/factory/agents/developer-agent.md
    - packages/factory/agents/requirements-agent.md
    - packages/factory/agents/virgil.md
    - packages/factory/agents/test-strategy-agent.md
    - packages/factory/agents/test-review-agent.md
    - packages/factory/skills/detect-test-regime/SKILL.md
    - packages/factory/skills/derive-feature/SKILL.md
    - packages/factory/rulebooks/templates/story.md
    - packages/factory/scripts/backlog-lint
    - packages/factory/scripts/dispatch_lib.py

governance:
  assurance: elevated
  risk_domains:
    - reliability
    - compatibility

estimate:
  as_of: 2026-11-21
  basis: judgment
  confidence: low
  human_review_hours: unknown
  normalized_tokens: unknown
  estimated_consumption: unknown
---

# Feature Request: Acceptance-First Implementation

## Primer

Written by the write-primer skill once the grilling has settled the design.

## Summary

The implementation run turns a story's scenarios into running tests before any developer writes code, and lets one developer or a population of developers write code against them. Among the versions that pass, the least complex wins, measured from the parse tree. The feature answers a question the factory cannot answer today: did the code that goes to review implement the stakeholder's scenarios, and was it the simplest code that did? The first release covers Python stories with a `.feature` file.

## Motivation

The `.feature` file is the factory's acceptance specification, but nothing makes sure a developer runs it:

- **Nobody signs the brief.** The `.feature` file is the stakeholder's brief to the implementation team, but the requirements agent declares it `reviewed_by: [spec-review-agent]` (`requirements-agent.md:44`). The scope map, by contrast, is reviewed by the stakeholder (`:40`).
- **The fitting sets up no acceptance layer.** The fitting's test-regime step records an `acceptance_test` layer only when it finds a `.feature` directory or a Gherkin runner config (`detect-test-regime/SKILL.md:233`). A project without one gets no acceptance layer, and no step sets one up.
- **A blocked story is still planned.** `dispatch plan` reads no story status at all: `load_stories` reads no `status` field (`dispatch_lib.py:2029`), and `compute_wave_plan` (`:2155`) has none to read. `dispatch init` checks only that dependencies outside the run are `done` (`dispatch:903`). A story whose own frontmatter says `status: blocked` is planned and dispatched like any other. The ledger's `blocked` state is a different thing: it is set during a run.
- **The scenarios reach the developer by one optional link.** The developer follows the story's `traces:` to a scope-map Rule, and from there to the feature file (`developer-agent.md`, Analyse). The story template marks `traces:` as optional, and `backlog-lint` checks only that it is a list. A story without traces reaches the developer without its scenarios.
- **No brief names the feature file.** The dispatch, fix and review-fix briefs of `implementation-agent.md` name the story, the gate reports or the findings. A fix agent reaches the scenarios only if it starts again from Analyse.
- **Each developer writes its own step definitions.** The step definitions turn a scenario's sentences into calls, and they can carry a reading of the spec. When each story's developer writes them, the acceptance run partly tests that developer's glue.
- **One developer, one reading.** A single developer that misreads a rule writes tests that agree with its code. Its tests pass, the gates pass, and the misreading reaches review.

The Karl+Charles experiment supplies the evidence for the parts this proposal adds (repository `karl-charles`, `docs/experiment-log.md` and `docs/phase2-factory-arm.md`). In phase 1 and phase 2, cross-testing a population exposed misreadings that single sessions kept. Paolo's rule v2 showed that a session whose own tests all pass on its own code was right about 97% of the time. A spike ran the spec's Gherkin scenarios directly as the acceptance gate (`docs/gherkin-gate-spike.md`).

An outside review, *Vom Intent zum Review* ([factory-improvements.pdf](../reviews/factory-improvements.pdf), 16 November 2026), reached four of these points from a different story, `ST-0014A-Dorthe`, checked against the book *Building the Agentic Software Factory*:

- **Keep the intent traceable up to the review.** Sections 1, 3 and 6.
- **Separate the test author from the implementer.** Sections 4, 5 and 8. The signature of section 1 makes the separation binding, because a developer who changes a Scenario or a step definition voids it.
- **Enforce readiness before dispatch.** Section 7.
- **Check acceptance independently before merge.** Section 6. The review names an acceptance adapter but does not define it; sections 2 and 6 define it.

Its fifth recommendation, a context manifest per agent, belongs to a separate proposal. The review separates two agents but does not ask whose reading of the intent the tests carry. A separate test author still writes one agent's reading of the intent into the tests. The stakeholder's signature on the Scenarios closes that gap.

## Core Principles

- **The scenarios are the gate.** They run from the `.feature` file the stakeholder owns, on every version, and are never copied into a test file.
- **Correctness first, simplicity second.** Size only breaks ties among versions that pass every test that counts. It never ranks a version above one that is more correct.
- **Size comes from the parse tree.** Layout, formatting and line length never change the measure.
- **A disagreement is a question.** When developers read the spec differently, the stakeholder settles it. No secondary criterion does.

## Design

### 1. The signed brief

The `.feature` file is the stakeholder's brief to the implementation team. For every story, the test scenarios come from it. The requirements agent declares the stakeholder as a reviewer of the feature file, beside the spec-review agent.

The brief has two parts, so two people sign it:

- **The stakeholder signs the Scenarios:** the Rules, the sentences and the Examples tables.
- **The test-review agent signs the step definitions** (sections 4 and 5). They are code, and the stakeholder does not read code. Thin glue keeps that review short.

The signatures live in one append-only store, `docs/spec/signoffs.jsonl`. Each line is one signature:

```json
{"feature": "docs/spec/features/scheduling.feature", "part": "scenarios", "signer": "stakeholder", "date": "2026-11-24", "sha256": "…"}
```

`part` is `scenarios` or `step_definitions`. For each feature and part, the newest line counts. A feature file or step definition that changes after signing no longer matches its hash. The signature then lapses, and the governing stories stop until both parts are signed again. Nothing is ever edited or removed from the store, so it also records who signed which revision of the brief.

### 2. Test mechanics in the fitting

If the Scenarios are the acceptance tests of every story, the mechanics that run them must exist before the first story. Setting them up becomes part of the fitting, next to the test-regime step (`virgil.md:254-269`):

1. **Runner.** Choose a Gherkin runner for the project's language and record it, with its command, as the `acceptance_test` layer in `docs/testing.yaml`.
2. **Home.** Fix the home of the step definitions, `tests/features/steps/`, with one module per feature file.
3. **Undefined steps fail.** Configure the runner so that a step with no matching definition fails the run instead of being skipped. Each runner's setting must be checked against its documentation.
4. **Gate.** Wire the acceptance command into the hooks. The hooks step already follows the test-regime step, because hook decisions may depend on the test command (`virgil.md:266`).
5. **Proof.** Run one trivial Scenario with its step definition, and show it green before any story depends on the setup.

The fitting records the result as a seventh fitting key, `acceptance_layer_fitted`.

### 3. Binding traces

Every story that a `.feature` file governs names at least one scope-map Rule in `traces:`. `backlog-lint` reports an error when such a story has no Rule trace, or names a Rule that is missing from `docs/spec/scope-map.md` or from the feature file the map names. Every developer brief names the governing feature file and its Rules, so a fix agent reaches the scenarios without the Analyse step.

### 4. Acceptance step definitions, before the code

The step definitions belong to the feature, not to a story. The test-strategy agent writes them once per feature, after the stakeholder has signed the Scenarios and before the first story of the feature starts. They live under `tests/features/steps/`, as today. They move from the implementation to the brief: `developer-agent.md:101` calls them implementation artifacts and has the developer write them, and the `derive-feature` table (`:262`) assumes the same. Both change.

A step definition calls only what the brief names:

- **Existing behaviour:** the code the `@`-references of the Scenario name (`developer-agent.md:100`).
- **New behaviour:** the operations of `docs/spec/interface-contracts.md`, which the domain-modeling agent writes once the feature file exists (`domain-modeling-agent.md:98`).

The test-strategy agent adds no API of its own. A call that neither source names is a design decision made by the test author, and it goes back to the domain-modeling agent as a gap.

A step definition matches the whole sentence of a step and refuses whatever it cannot read. A reworded scenario then fails as `undefined` instead of passing half-checked. A choice that reads the spec, such as a default value a scenario leaves out, is written as a comment beside the step and goes to the stakeholder with the review.

### 5. The test-review agent

Every authoring agent in the factory has its reviewer, except the test-strategy agent. Its `docs/testing.yaml` is reviewed by the stakeholder alone, and its QA strategy by nobody (`test-strategy-agent.md:24-30`). With the step definitions it now writes part of the signed brief, so it gets a reviewer: a new test-review agent, in its own session.

The reviewer of the step definitions must have no stake in what it checks. That excludes everyone who wrote or approved a source the step definitions are checked against, or is later judged by them:

| Role                  | Stake                                      |
| --------------------- | ------------------------------------------ |
| requirements agent    | wrote the Scenarios                        |
| spec-review agent     | approved the Scenarios                     |
| domain-modeling agent | wrote the interface contracts              |
| test-strategy agent   | wrote the step definitions                 |
| developer agent       | its code is judged by the step definitions |

The test-review agent writes no tests and no specification, so it is free of all five. It runs on a different model family from the test-strategy agent where the matrix offers one: one family tends to fail together.

It reviews two artifacts:

1. **Step definitions.** Each step does what its sentence says and nothing more. It calls only what the `@`-references or the interface contracts name. It refuses a sentence it cannot match in full. Every choice that reads the spec is written as a comment. On a pass, it appends the `step_definitions` signature to the store (section 1).
2. **QA strategies.** Every expected outcome traces to a Rule or Scenario. An edge case whose outcome the specification does not state becomes an entry in `docs/spec/work/todo.md`, not a test. The same rule would close F2 of the [independence review](../reviews/independence-review-2026-11-23.md), which concerns the developer's `test-design` skill; that skill is not in this proposal's scope.

Its findings follow the finding format and go back to the test-strategy agent. `docs/testing.yaml` stays with the stakeholder.

### 6. The acceptance gate

A new gate script, `acceptance-check`, runs beside `crap-score` and `mutation-testing`. It runs the governing `.feature` files through the project's Gherkin runner and writes `.current-work/acceptance-check/<story-id>.json`. The report lists each scenario with its status (`passed`, `failed`, `error`, `undefined`, `ambiguous`). A failing scenario is reported as written, with the step that failed and the message. The fix brief hands over that text.

The gate passes only when every scenario of every governing Rule passes, and the feature file and step definitions still match their signatures (section 1).

The report is also the trace matrix from Scenario to result, which a pull request description can carry as it stands.

### 7. Readiness before dispatch

A readiness check runs before `dispatch plan` places a story in a wave. It refuses the story, with the story ID and the reason, when:

- the story's own `status` is `blocked`;
- a governing feature file has no valid signature (section 1);
- the project has no fitted acceptance layer (section 2);
- a Scenario for new behaviour has no interface contract to call (section 4).

### 8. One developer or a population

A story runs with one developer, as today, or with a population of developers. The story's frontmatter says which (see Open Questions). With a population:

1. **Starters.** N developers implement the story, each in its own worktree, each test first, each with its own tests. The temperaments rotate across the starters.
2. **Cross-testing.** Every starter's tests run against every starter's code. A test counts only if it cites a rule or scenario, passes on its author's code, and is not quarantined. A test is quarantined when it passes on its author's code alone.
3. **Self-refuted starters are out.** A starter whose own tests fail on its own code cannot be the candidate.
4. **Agreed tests.** The counted tests every remaining starter passes join the story's gates.
5. **Questions.** Counted tests that some remaining starters pass and others fail are questions for the stakeholder. Tests that split the starters the same way count as one question. The questions go to `docs/spec/work/todo.md`. A confirmed test joins the agreed tests; a refuted one drops out.
6. **The candidate** is the remaining starter that passes the acceptance gate and every agreed test. If several do, the least complex wins (section 9).
7. **The candidate enters the gate loop** as any developer's version does, with the agreed tests among its gates. Code review and QA follow as today.

With one developer, steps 1 to 6 reduce to the developer's version passing the acceptance gate and its own tests.

(MD) Question: With one developer why not have sequential fresh sessions? One brief will first start a test-manager agent to write the tests. Then a developer agent writes the code against this test. (2026-11-23T01:24)

### 9. Size from the parse tree

Size is two numbers, in this order:

1. **Total cyclomatic complexity:** the sum over all functions of 1 plus their decisions. A nested function counts on its own.
2. **Statements:** every statement except docstrings.

Both come from the parse tree, so formatting cannot change them. A new script, `code-size`, computes them with tree-sitter, which has grammars for most languages, so one tool serves every project language. `code-size` writes per-function rows in the same shape `crap-score` reads.

## Scope

**In the first release:**

- The stakeholder as reviewer of the feature file, the two signatures in `docs/spec/signoffs.jsonl` with their content hashes, and the lapse of a signature on change.
- The test-review agent, reviewing step definitions and QA strategies.
- The fitting step for the test mechanics, for Python with `behave`, and the fitting key `acceptance_layer_fitted`.
- The readiness check before `dispatch plan`, with its four conditions.
- Binding traces in the story template and `backlog-lint`, and the feature file in every developer brief.
- Acceptance step definitions as a feature-level artifact, written by the test-strategy agent against the `@`-references and interface contracts, and reviewed before the first story.
- The `acceptance-check` gate script for Python with `behave`, and its place in the gate loop.
- The population start for stories that ask for it, with cross-testing, the self-refuted filter, agreed tests, questions to `todo.md`, and the candidate rule.
- The `code-size` script with tree-sitter's Python grammar.

**Explicitly deferred (do NOT plan stories for these):**

- Gherkin runners other than `behave`. Each language needs its own runner wiring; Python comes first because the evidence comes from Python.
- Grammars other than Python in `code-size`. The design is language-independent; the first release proves it on one language.
- Judges from another model family in code review and QA. The Karl+Charles experiment tests this (hypothesis H2) and has not run yet.
- Moving `crap-score` from radon to tree-sitter. It is a separate change, and `crap-score` works today.
- Choosing N from the story's tier automatically. It waits for the experiment's cost results (hypotheses H1a and H1b).
- Further readiness conditions: accepted ADRs and closed contract questions. The outside review asks for them; they need their own record of what is open.
- A pull request description written from the whole chain of intent, story and gate reports. The acceptance report of section 6 supplies its trace matrix.
- A context manifest per agent. It belongs to a separate proposal.

## Design Details

- **Isolation.** Every acceptance run, cross-test and size measurement runs the code under test in its own process with a timeout, as the existing gates do.
- **Failure of the whole run.** A Gherkin run that crashes or hangs fails the gate with "the acceptance scenarios could not run against the code", not with a list of scenarios.
- **No candidate.** If no starter passes its own tests, or no remaining starter passes every agreed test, the population start runs once more. If that also fails, the story goes back to the stakeholder.
- **Questions block.** A story whose starters disagree waits for the stakeholder's answers. It does not pick a reading by size.
- **The measure on a nested function.** radon leaves nested functions out of its total; `code-size` counts each on its own. On code without nested functions the two agree.

## Open Questions

- **How does a story ask for a population?** A field in the story frontmatter, such as `population: 4`, set by the planning agent or by the stakeholder.
- **What does an automated run do while questions are open?** Stop the story and continue the other stories of the wave, or stop the wave.
- **Do the starters see the step definitions?** They see the `.feature` file in any case. Seeing the glue as well makes the acceptance gate easier to meet, and may also narrow the population's readings.

## Completion Criteria

- The test-review agent appends a `step_definitions` line to `docs/spec/signoffs.jsonl` only after a passing review, and reports a step definition that calls code neither the `@`-references nor the interface contracts name.
- The test-review agent reports a QA strategy outcome that traces to no Rule or Scenario.
- A feature file changed after signing fails `acceptance-check` with "the signature no longer matches", and so does a changed step definition.
- The fitting of a Python project without a Gherkin runner ends with `behave` recorded as the `acceptance_test` layer, one trivial Scenario green, and an undefined step failing the run.
- `dispatch plan` refuses a story whose `status` is `blocked`, a story under an unsigned feature file, every story of a project without a fitted acceptance layer, and a story with a new-behaviour Scenario that no interface contract covers, naming the story and the reason.
- `backlog-lint` reports an error for a story under a feature file whose `traces:` names no Rule of that file.
- Every developer brief template in `implementation-agent.md` names the governing feature file and its Rules.
- `acceptance-check` runs a feature file through `behave` and writes a JSON report with one row per scenario, its status, and, for a failing scenario, the step and the message.
- A fix brief after a failing `acceptance-check` carries the failing scenarios as written.
- A story with a population runs N starters, cross-tests them, writes the questions to `todo.md`, and hands one candidate to the gate loop with the agreed tests among its gates.
- `code-size` gives the same total cyclomatic complexity as radon on Python code without nested functions, and the same numbers for a file before and after `ruff format`.

## Guiding Rule

Code reaches review only if it passes the stakeholder's scenarios, and among the code that passes, the simplest wins.

# Appendix

## Decisions

| ID     | Date       | Kind       | Decided by     | Decision                                                                                                                                                                                                                                  | Raised by                                                       |
| ------ | ---------- | ---------- | -------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------- |
| DEC-01 | 2026-11-20 | decision   | Matthias Daues | A story must name the `.feature` scenarios it implements, through its traces.                                                                                                                                                             | `traces:` is optional and unchecked                             |
| DEC-02 | 2026-11-21 | decision   | Matthias Daues | Tests come from the `.feature` file before any developer writes code; one developer or a population then writes code against them.                                                                                                        | Karl+Charles factory experiment                                 |
| DEC-03 | 2026-11-21 | decision   | Matthias Daues | Among the versions that pass, the least complex wins.                                                                                                                                                                                     | Karl+Charles factory experiment                                 |
| DEC-04 | 2026-11-21 | decision   | Matthias Daues | Size is not measured in lines: lines depend on a formatter and its settings. Total cyclomatic complexity comes first, statements break ties.                                                                                              | Pilot: `ruff format` moved line counts by up to 16%             |
| DEC-05 | 2026-11-21 | decision   | Matthias Daues | tree-sitter is the factory's tool for measuring size.                                                                                                                                                                                     | DEC-04                                                          |
| DEC-06 | 2026-11-21 | assumption | Matthias Daues | The candidate is chosen on the acceptance scenarios plus the agreed tests of the population, not on the scenarios alone. Four scenarios caught 4 of 11 planted faults in the spike, and a faulty version can be the simplest passing one. | Gherkin gate spike                                              |
| DEC-07 | 2026-11-21 | assumption | Matthias Daues | Step definitions are written once per feature and reviewed with the feature file, not by each story's developer.                                                                                                                          | Gherkin gate spike, point 3                                     |
| DEC-08 | 2026-11-23 | decision   | Matthias Daues | The feature file is the stakeholder's signed brief to the implementation team. For every story, the test scenarios come from it.                                                                                                          | Independence review 2026-11-23                                  |
| DEC-09 | 2026-11-23 | decision   | Matthias Daues | Setting up the test mechanics is part of the factory fitting.                                                                                                                                                                             | DEC-08                                                          |
| DEC-10 | 2026-11-24 | decision   | Matthias Daues | The test-strategy agent writes the step definitions, once per feature, against the `@`-references and the interface contracts.                                                                                                            | DEC-07                                                          |
| DEC-11 | 2026-11-24 | decision   | Matthias Daues | Signatures live in an append-only JSONL store, one line per signature with a content hash.                                                                                                                                                | DEC-08                                                          |
| DEC-12 | 2026-11-24 | decision   | Matthias Daues | Every author has its reviewer. A new test-review agent reviews the test-strategy agent's step definitions and QA strategies. No role that wrote or approved a source of the step definitions, or is judged by them, may review them.      | Spec-review agent approved the Scenarios and is not independent |

## Review findings

| ID  | Pass | Severity | Check | Status | Finding | Resolution |
| --- | ---- | -------- | ----- | ------ | ------- | ---------- |

## Review passes

| Pass | Date | Reviewed commit | Disposition | Failed checks | Summary |
| ---- | ---- | --------------- | ----------- | ------------- | ------- |
