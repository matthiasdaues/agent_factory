---
schema_version: 2
title: Evidence-Bound Findings
status: draft
owner: Matthias Daues
created: 2026-11-22
updated: 2026-11-23
supersedes:

impact:
  scope: cross_component
  architecture_change: false
  external_contract_change: true
  boundaries:
    - packages/factory/rulebooks/conventions/finding-classification.md
    - packages/factory/rulebooks/conventions/finding-format.md
    - packages/factory/rulebooks/templates/finding.md
    - packages/factory/rulebooks/schemas/finding-register-runtime.schema.json
    - packages/factory/scripts/finding-lint
    - packages/factory/agents/code-review-agent.md
    - packages/factory/agents/qa-agent.md
    - packages/factory/agents/implementation-agent.md
    - packages/factory/skills/bug-hunt/SKILL.md

governance:
  assurance: elevated
  risk_domains:
    - reliability
    - compatibility

estimate:
  as_of: 2026-11-22
  basis: judgment
  confidence: low
  human_review_hours: unknown
  normalized_tokens: unknown
  estimated_consumption: unknown
---

# Feature Request: Evidence-Bound Findings

## Primer

In the factory, a developer agent writes code and other agents judge it. A code reviewer reads the change, and a hunter in the bug hunt runs it to find bugs. Each judge records a finding. A blocking finding stops the code, and a fix developer changes the code to remove it.

Nothing checks the judgment behind a finding, and nobody knows how often each judge is right. In four of five test conditions of a factory experiment, at least one fix turned correct code into wrong code.

The factory meets the uncertainty of agent work in three ways. A hedge spreads a bet, so one wrong bet costs less. Letting several developers write the same story is a hedge. A fence stops a wrong result before it goes further. The gates, scripts that check the work, are such fences. A gauge measures how often a check is right, so its verdict can be trusted. Code review and the bug hunt are fences that agents run, and no gauge measures them. This proposal adds fences in front of the judges' findings and gauges the judges.

In the experiment's pilot, every bug the hunters reported was false. One rule listed the inputs that raise an error and said nothing of input of the wrong type. The hunters read the list as examples, so they expected the same error for booleans, fractions, missing keys and tuples. All but one of the false bugs came from that reading. Under this proposal, each finding names the rule it rests on, and a script checks that the rule exists. The hunter then quotes the rule and asks whether it states the expected behaviour. The rule is silent on that input, so no bug is filed. Instead the hunter asks the stakeholder, who owns the specification, whether the list is complete. The developer's reading stands until then.

Each finding also says whether a failing test or a measured run shows it, or whether it is only argued. For an argued blocking finding, the fix developer first writes and runs the test that would fail if the finding were true. The fix follows only if the test fails. Otherwise the finding closes as refuted.

The gauge is a calibration set for each kind of review: a correct version of a small artifact and a few planted faults. A judge runs on the set whenever the judge changes, and at least once per release. The run records how many faults the judge catches and how often it raises a false alarm on the correct version. A judge with too many false alarms stops blocking in automated mode until its prompt is fixed.

Judges from a second model family are no substitute, because the experiment found no benefit.

Four questions remain open: the false-alarm rate that stops a judge, who writes the refuting test, whether a second reader should check the quote against the finding, and where a project without planted faults finds its calibration set.

## Summary

A blocking code or runtime finding must name the requirement it rests on and say whether a test has shown it. A finding that rests on a reading the specification does not state becomes a question to the stakeholder, not a defect in the code. A finding that nobody has shown is tested before anyone changes the code for it. The judges themselves are measured on planted faults, so the factory knows how often each one is right. The feature answers a question the factory cannot answer today: when a review blocks code, is the review right?

## Motivation

The factory meets the uncertainty of agent work in three ways:

- A **hedge** spreads a bet, so one wrong bet costs less. [Acceptance-First Implementation](acceptance-first-implementation.md) lets several developers write the same story. A hedge works only when the bets fail independently.
- A **fence** stops a wrong result before it goes further. The factory separates the agents that create work from the scripts that check it, so a gate does not depend on an agent's judgment (`rules.md`, Foundational principles).
- A **gauge** measures how often a check is right, so its verdict can be trusted.

Code review and the QA bug hunt are fences that agents run. Their findings block code like a failing gate, but nothing checks the judgment behind them, and nothing gauges the judges. This proposal puts a deterministic check in front of every blocking finding and gauges each judge on planted faults.

[Finding Classification](finding-classification.md) made severity a fixed rule over recorded facts, so two reviewers who record the same facts agree. It does not ask whether the facts are true. Four gaps follow:

- **The requirement is not named.** In the code class, `fails_purpose` means "behavior that the story or specification requires is missing or wrong" (`finding-classification.md`, Class: code). No field records which requirement. The reviewer's reading of the specification goes unchecked, and a misreading blocks the code like a real defect.
- **A gap in the specification lands on the code.** When the specification leaves a choice open and the reviewer expects one answer, the finding is a code defect. The fix loop then makes the developer adopt the reviewer's reading. The gap in the specification stays.
- **A claim blocks like a proof.** The security class records `confidence: proven | plausible`. The code and runtime classes do not. A finding that nobody has reproduced blocks like one that a failing test shows, and a fix agent changes code that may be right.
- **Nobody measures the judges.** The calibration examples make severities consistent (DEC-08 of Finding Classification). Nothing measures how many real defects a reviewer finds, or how often it raises a false one.

The Karl+Charles factory experiment supplies the evidence (repository `karl-charles`, `docs/phase2-factory-arm.md` and `spike/phase2/runs/round-1/compare.md`). It ran the factory's chain of developer, gates, code review and QA bug hunt on one task, 100 chains in five conditions, and measured the judges on 11 planted faults plus a correct version:

- In the pilot, every bug that a hunter reported was false. All but one came from one reading of one rule. The rule listed the inputs that raise `ValueError` and said nothing of input of the wrong type. The hunters took the list for examples and expected `ValueError` for other bad input too: booleans, fractions, missing keys and tuples.
- After the specification closed that gap and a finding had to name its basis in the specification to block, the false alarms of one reviewer on the correct version fell from 2 of 3 runs to 0 of 3. The two changes came together, so the experiment does not separate their effects.
- The judges were right more often than counted. Two reviews flagged quadratic time on the correct version, and both were counted as false alarms. A measurement showed the claim true: 8,000 jobs took 176 s. The specification set no time bound, so under step 2 neither finding blocks the code. Each becomes a question to the stakeholder: should the specification set one?
- They were also wrong more often than they knew. One hunter family left 29 failing tests on the faulty versions that failed on the correct version too.
- In four of the five conditions, at least one fix made after a finding turned correct code into wrong code.
- The measure of the judges was wrong once too. One planted fault deletes the call `_reject_cycles(jobs)`. All six reviews of it named the fault, for example "`_validate` never calls `_reject_cycles`", and pointed at the first line of `_validate`. The scoring rule wanted a location within three lines of the change, so it counted all six as misses. Counted by the function that lost the line, both reviews catch all 11 faults (`docs/phase2-factory-arm.md`, decision 9).

## Core Principles

- **A finding is a claim.** It earns a change to the code only after a test that could refute it fails to.
- **The specification decides, and the stakeholder owns it.** A judge applies the specification and never extends it. Where the specification is silent, the stakeholder answers.
- **Evidence before opinion.** What a gate measures, a judge cites. A judge does not restate it as an opinion.
- **Judges are measured like code.** Their catch rate and false-alarm rate are known before their findings block anyone.

## Design

### 1. Every blocking finding names what it rests on

The basis of the code and runtime classes gains the field `rests_on`. It names one of:

- a Rule or Scenario of a `.feature` file, as `<feature file>#<Rule or Scenario name>`;
- an acceptance criterion of the story, as `<story ID>#AC-<n>`;
- a project standard with its key in `docs/testing.yaml`, such as the CRAP threshold;
- an interface contract or ADR, by its path.

`fails_purpose` and `harms_downstream` answer "yes" only when `rests_on` is filled. `finding-lint` checks that the reference resolves: the file exists, and the Rule, Scenario, criterion or key exists in it. A finding with an empty or broken `rests_on` is at most `minor`.

### 2. A reading the specification does not state is a specification finding

The reviewer asks one more question before it files a code defect: **does the specification state the behavior the finding expects?** It answers by quoting the text named in `rests_on`.

- **The specification states it:** the code finding stands.
- **The specification leaves it open:** the reviewer files no code finding. It files a document finding of type `ambiguous` or `incomplete` against the specification, and an entry in `docs/spec/work/todo.md`. The developer's choice stands until the stakeholder answers.

The quote goes into the finding file as the line `**Spec says:**`. A reader then checks the reading without opening the specification.

### 3. Confidence, and refutation before the fix

The basis of the code and runtime classes gains the field `confidence`, as the security class has it:

- `proven`: a failing test, a measured run, or a trace from input to wrong output shows the finding. The finding names the test or the measurement.
- `plausible`: the finding is argued, not shown.

A blocking `plausible` finding goes to the fix developer with one more step before any code change: **write the test that would fail if the finding is true, and run it.**

- **The test fails:** the finding becomes `proven`, and the fix follows as today, with the test as its regression test.
- **The test passes:** the finding is refuted. The developer records the test and the result, and the code stays unchanged. The finding closes with status `refuted`, and the review loop does not count it as open.

A runtime finding from the bug hunt is `proven` by its reproduction. The reproduction is itself a claim, so it cites its `rests_on` too, and step 2 applies to it.

### 4. "No test" needs evidence from the gates

The code class's `fails_purpose` includes "an owned contract has no test". It answers "yes" only with evidence from a gate:

- a mutant of `mutation-testing` that survives on the contract's code;
- or lines of the contract that the coverage report shows unexecuted.

The finding cites the gate report. Without that evidence, a missing test is a `suggestion`.

### 5. A calibration set per review class

Each review class keeps a calibration set: a correct version of a small artifact and a few planted faults in it, each one change from the correct version. A judge (an agent definition with its model and prompt) runs on the set:

- when the factory adds or changes a judge's agent definition, model or prompt;
- at least once per release.

The run records each judge's catch rate on the faults and its false-alarm rate on the correct version. A blocking finding catches a fault when it points at the planted change. A deleted line leaves nothing to point at, so for a deletion a finding anywhere in the function that lost the line catches it. A blocking finding counts as a false alarm on the correct version unless step 3 proves it, which reveals a defect in the set itself. A finding on the correct version that step 2 turns into a specification finding is no false alarm either: it reveals a gap in the set's specification. A judge whose false-alarm rate exceeds the threshold (see Open Questions) does not block in automated mode until its prompt is fixed and it runs again.

## Scope

**In the first release:**

- `rests_on` and `confidence` in the basis of the code and runtime classes, in the rulebook, the finding template, the register schema and `finding-lint`.
- The specification check of step 2, with the `**Spec says:**` line, in `code-review-agent`, `fagan-review`, `qa-agent` and `bug-hunt`.
- Refutation before the fix: the step in the fix brief of `implementation-agent`, and the status `refuted` in `finding-format.md` and `finding-lint`.
- The gate-evidence rule for missing tests.
- One calibration set for the code class and one for the runtime class, with a script that runs a judge on a set and writes its rates.

**Explicitly deferred (do NOT plan stories for these):**

- `confidence` in the document and architecture classes. The experiment tested neither class.
- Calibration sets for the document, security and architecture classes. Their planted faults need their own design.
- Choosing judges by model family. The experiment refuted the benefit of judges from another family (its hypothesis H2), so nothing here depends on it.

## Design Details

- **Binding requirements, once.** The proposal [Acceptance-First Implementation](acceptance-first-implementation.md) makes a story's traces to the `.feature` file binding. `rests_on` names the same Rules and Scenarios. Both use one reference format and one resolver in `finding-lint` and `backlog-lint`.
- **Old findings.** Findings filed before this change carry no `rests_on` or `confidence`. `finding-lint` requires both only on a code or runtime finding that is new or whose basis changed, as BR-126 does for the document fields.
- **`refuted` is not `waived`.** A waiver is the stakeholder's choice to leave a true finding unfixed. `refuted` records that a test showed the finding false. An agent sets `refuted` only together with the test and its result; `finding-lint` checks that the named test exists and that the recorded run passed.
- **The quote is short.** `**Spec says:**` quotes at most the sentence or step that decides. A Rule that decides by its silence is quoted in full, with the line `The text says nothing about <case>.`
- **The calibration set is not a gate.** It measures judges, not the project's code. It lives in the factory package, not in a project.

## Open Questions

- **What false-alarm rate stops a judge?** The experiment used "more than one run in three on the correct version". A factory release needs a rate that holds with more runs and more than one artifact.
- **Who writes the refuting test for a review finding?** The fix developer, as designed here, or the reviewer, who knows what it meant. A reviewer that writes the test proves its own claim, which is cheaper, but it marks its own work.
- **Does the specification check need a second reader?** The reviewer that filed the finding also judges whether the specification states it. A misreading can pass both questions. A second, cheap reader could check the quote against the expectation.
- **Where does a calibration set come from in a project with no planted faults?** The factory's own sets measure judges in general, not on the project's language and domain.

## Completion Criteria

- `finding-lint` reports an error for a new code or runtime finding with `fails_purpose: true` or `harms_downstream: true` and an empty `rests_on`, and for a `rests_on` whose file, Rule, Scenario, criterion or key does not exist.
- `finding-lint` computes at most `minor` for such a finding when it recomputes the severity.
- The code and runtime sections of `finding-classification.md` define `rests_on`, `confidence`, the specification check, and the gate-evidence rule for missing tests, each with a calibration example.
- `code-review-agent` and `bug-hunt` file a document finding and a `todo.md` entry, and no code finding, when the quoted specification does not state the expected behavior.
- The fix brief in `implementation-agent.md` tells the developer to write and run the refuting test before changing code for a `plausible` blocking finding, and to set `refuted` when the test passes.
- `finding-lint` accepts `status: refuted` only with a named test and a recorded passing run.
- A script runs a named judge on the code-class and the runtime-class calibration sets and writes its catch rate and false-alarm rate.

## Guiding Rule

A finding blocks code only when it names what the specification says, and a test that could refute it has not.

# Appendix

## Decisions

| ID     | Date       | Kind       | Decided by     | Decision                                                                                                                                                                                                          | Raised by                        |
| ------ | ---------- | ---------- | -------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------- |
| DEC-01 | 2026-11-21 | decision   | Matthias Daues | Judges must stick to what they judge: a finding blocks only when it names its basis in the specification or the stated standard, and where the specification leaves a choice open, the developer's choice stands. | Karl+Charles round-1, decision 7 |
| DEC-02 | 2026-11-22 | decision   | Matthias Daues | The improvements become a proposal of their own, beside Acceptance-First Implementation.                                                                                                                          | Chat                             |
| DEC-03 | 2026-11-22 | assumption | Matthias Daues | A `plausible` finding is tested before it is fixed. The experiment shows judges both right when counted wrong and wrong when trusted; it does not yet show that a refuting test catches the wrong ones.           | Karl+Charles round-1, Study 2    |
| DEC-04 | 2026-11-22 | assumption | Matthias Daues | A judge measured on planted faults in one artifact reflects its behavior on a project. The experiment measured one task; a second artifact per class tests the assumption.                                        | Karl+Charles Study 2             |

## Review findings

| ID  | Pass | Severity | Check | Status | Finding | Resolution |
| --- | ---- | -------- | ----- | ------ | ------- | ---------- |

## Review passes

| Pass | Date | Reviewed commit | Disposition | Failed checks | Summary |
| ---- | ---- | --------------- | ----------- | ------------- | ------- |
