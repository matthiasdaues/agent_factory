---
scope: global
schema_version: 2
title: Acceptance-First Implementation
status: draft
owner: Matthias Daues
created: 2026-11-21
updated: 2026-11-21
supersedes:

impact:
  scope: cross_component
  architecture_change: true
  external_contract_change: true
  boundaries:
    - packages/factory/agents/implementation-agent.md
    - packages/factory/agents/developer-agent.md
    - packages/factory/rulebooks/templates/story.md
    - packages/factory/scripts/backlog-lint

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

- **The scenarios reach the developer by one optional link.** The developer follows the story's `traces:` to a scope-map Rule, and from there to the feature file (`developer-agent.md`, Analyse). The story template marks `traces:` as optional, and `backlog-lint` checks only that it is a list. A story without traces reaches the developer without its scenarios.
- **No brief names the feature file.** The dispatch, fix and review-fix briefs of `implementation-agent.md` name the story, the gate reports or the findings. A fix agent reaches the scenarios only if it starts again from Analyse.
- **Each developer writes its own step definitions.** The step definitions turn a scenario's sentences into calls, and they can carry a reading of the spec. When each story's developer writes them, the acceptance run partly tests that developer's glue.
- **One developer, one reading.** A single developer that misreads a rule writes tests that agree with its code. Its tests pass, the gates pass, and the misreading reaches review.

The Karl+Charles experiment supplies the evidence for the parts this proposal adds (repository `karl-charles`, `docs/experiment-log.md` and `docs/phase2-factory-arm.md`). In phase 1 and phase 2, cross-testing a population exposed misreadings that single sessions kept. Paolo's rule v2 showed that a session whose own tests all pass on its own code was right about 97% of the time. A spike ran the spec's Gherkin scenarios directly as the acceptance gate (`docs/gherkin-gate-spike.md`).

## Core Principles

- **The scenarios are the gate.** They run from the `.feature` file the stakeholder owns, on every version, and are never copied into a test file.
- **Correctness first, simplicity second.** Size only breaks ties among versions that pass every test that counts. It never ranks a version above one that is more correct.
- **Size comes from the parse tree.** Layout, formatting and line length never change the measure.
- **A disagreement is a question.** When developers read the spec differently, the stakeholder settles it. No secondary criterion does.

## Design

### 1. Binding traces

Every story that a `.feature` file governs names at least one scope-map Rule in `traces:`. `backlog-lint` reports an error when such a story has no Rule trace, or names a Rule that is missing from `docs/spec/scope-map.md` or from the feature file the map names. Every developer brief names the governing feature file and its Rules, so a fix agent reaches the scenarios without the Analyse step.

### 2. Acceptance step definitions, before the code

The step definitions belong to the feature, not to a story. They are written once per feature, before the first story of the feature starts, and reviewed together with the feature file. They live under `tests/features/steps/`, as today.

A step definition matches the whole sentence of a step and refuses whatever it cannot read. A reworded scenario then fails as `undefined` instead of passing half-checked. A glue choice that reads the spec, such as a default value a scenario leaves out, is written as a comment beside the step and goes to the stakeholder with the review.

### 3. The acceptance gate

A new gate script, `acceptance-check`, runs beside `crap-score` and `mutation-testing`. It runs the governing `.feature` files through the project's Gherkin runner and writes `.current-work/acceptance-check/<story-id>.json`. The report lists each scenario with its status (`passed`, `failed`, `error`, `undefined`, `ambiguous`). A failing scenario is reported as written, with the step that failed and the message. The fix brief hands over that text.

The gate passes only when every scenario of every governing Rule passes.

### 4. One developer or a population

A story runs with one developer, as today, or with a population of developers. The story's frontmatter says which (see Open Questions). With a population:

1. **Starters.** N developers implement the story, each in its own worktree, each test first, each with its own tests. The temperaments rotate across the starters.
2. **Cross-testing.** Every starter's tests run against every starter's code. A test counts only if it cites a rule or scenario, passes on its author's code, and is not quarantined. A test is quarantined when it passes on its author's code alone.
3. **Self-refuted starters are out.** A starter whose own tests fail on its own code cannot be the candidate.
4. **Agreed tests.** The counted tests every remaining starter passes join the story's gates.
5. **Questions.** Counted tests that some remaining starters pass and others fail are questions for the stakeholder. Tests that split the starters the same way count as one question. The questions go to `docs/spec/work/todo.md`. A confirmed test joins the agreed tests; a refuted one drops out.
6. **The candidate** is the remaining starter that passes the acceptance gate and every agreed test. If several do, the least complex wins (section 5).
7. **The candidate enters the gate loop** as any developer's version does, with the agreed tests among its gates. Code review and QA follow as today.

With one developer, steps 1 to 6 reduce to the developer's version passing the acceptance gate and its own tests.

(MD) Question: With one developer why not have sequential fresh sessions? One brief will first start a test-manager agent to write the tests. Then a developer agent writes the code against this test. (2026-11-23T01:24)

### 5. Size from the parse tree

Size is two numbers, in this order:

1. **Total cyclomatic complexity:** the sum over all functions of 1 plus their decisions. A nested function counts on its own.
2. **Statements:** every statement except docstrings.

Both come from the parse tree, so formatting cannot change them. A new script, `code-size`, computes them with tree-sitter, which has grammars for most languages, so one tool serves every project language. `code-size` writes per-function rows in the same shape `crap-score` reads.

## Scope

**In the first release:**

- Binding traces in the story template and `backlog-lint`, and the feature file in every developer brief.
- Acceptance step definitions as a feature-level artifact, written and reviewed before the first story.
- The `acceptance-check` gate script for Python with `behave`, and its place in the gate loop.
- The population start for stories that ask for it, with cross-testing, the self-refuted filter, agreed tests, questions to `todo.md`, and the candidate rule.
- The `code-size` script with tree-sitter's Python grammar.

**Explicitly deferred (do NOT plan stories for these):**

- Gherkin runners other than `behave`. Each language needs its own runner wiring; Python comes first because the evidence comes from Python.
- Grammars other than Python in `code-size`. The design is language-independent; the first release proves it on one language.
- Judges from another model family in code review and QA. The Karl+Charles experiment tests this (hypothesis H2) and has not run yet.
- Moving `crap-score` from radon to tree-sitter. It is a separate change, and `crap-score` works today.
- Choosing N from the story's tier automatically. It waits for the experiment's cost results (hypotheses H1a and H1b).

## Design Details

- **Isolation.** Every acceptance run, cross-test and size measurement runs the code under test in its own process with a timeout, as the existing gates do.
- **Failure of the whole run.** A Gherkin run that crashes or hangs fails the gate with "the acceptance scenarios could not run against the code", not with a list of scenarios.
- **No candidate.** If no starter passes its own tests, or no remaining starter passes every agreed test, the population start runs once more. If that also fails, the story goes back to the stakeholder.
- **Questions block.** A story whose starters disagree waits for the stakeholder's answers. It does not pick a reading by size.
- **The measure on a nested function.** radon leaves nested functions out of its total; `code-size` counts each on its own. On code without nested functions the two agree.

## Open Questions

- **Who writes the step definitions?** The test-strategy agent, which already plans the tests per feature, or a dedicated step in the implementation run before the first wave.
- **How does a story ask for a population?** A field in the story frontmatter, such as `population: 4`, set by the planning agent or by the stakeholder.
- **What does an automated run do while questions are open?** Stop the story and continue the other stories of the wave, or stop the wave.
- **Do the starters see the step definitions?** They see the `.feature` file in any case. Seeing the glue as well makes the acceptance gate easier to meet, and may also narrow the population's readings.

## Completion Criteria

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

| ID     | Date       | Kind       | Decided by     | Decision                                                                                                                                                                                                                                  | Raised by                                           |
| ------ | ---------- | ---------- | -------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------- |
| DEC-01 | 2026-11-20 | decision   | Matthias Daues | A story must name the `.feature` scenarios it implements, through its traces.                                                                                                                                                             | `traces:` is optional and unchecked                 |
| DEC-02 | 2026-11-21 | decision   | Matthias Daues | Tests come from the `.feature` file before any developer writes code; one developer or a population then writes code against them.                                                                                                        | Karl+Charles factory experiment                     |
| DEC-03 | 2026-11-21 | decision   | Matthias Daues | Among the versions that pass, the least complex wins.                                                                                                                                                                                     | Karl+Charles factory experiment                     |
| DEC-04 | 2026-11-21 | decision   | Matthias Daues | Size is not measured in lines: lines depend on a formatter and its settings. Total cyclomatic complexity comes first, statements break ties.                                                                                              | Pilot: `ruff format` moved line counts by up to 16% |
| DEC-05 | 2026-11-21 | decision   | Matthias Daues | tree-sitter is the factory's tool for measuring size.                                                                                                                                                                                     | DEC-04                                              |
| DEC-06 | 2026-11-21 | assumption | Matthias Daues | The candidate is chosen on the acceptance scenarios plus the agreed tests of the population, not on the scenarios alone. Four scenarios caught 4 of 11 planted faults in the spike, and a faulty version can be the simplest passing one. | Gherkin gate spike                                  |
| DEC-07 | 2026-11-21 | assumption | Matthias Daues | Step definitions are written once per feature and reviewed with the feature file, not by each story's developer.                                                                                                                          | Gherkin gate spike, point 3                         |

## Review findings

| ID  | Pass | Severity | Check | Status | Finding | Resolution |
| --- | ---- | -------- | ----- | ------ | ------- | ---------- |

## Review passes

| Pass | Date | Reviewed commit | Disposition | Failed checks | Summary |
| ---- | ---- | --------------- | ----------- | ------------- | ------- |
