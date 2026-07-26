---
title: Research Topic Playbook
category: orchestration
type: runbook
scenario: research-topic
version: 1.0.0
---

# Research Topic Playbook

Operational procedure for **falsification-driven research**, running from an
approved research brief to a validated final report. The playbook admits a
claim to the report only after that claim has survived a serious attempt at
refutation within its stated scope. A surviving claim is never presented as
proved; it has only withstood the defined tests.

The procedure wires thirteen steps in order. Each step names its agent, its
skills, its input artifacts, and its output artifacts. Between every step the
playbook runs a three-stage validation gate, and progression blocks whenever a
stage fails.

## Prerequisites

- [ ] `research-brief.md` exists and is ready for validation.
- [ ] The research templates, schemas, and policies are present under
  `factory/rulebooks/`.
- [ ] The research agents and skills are indexed in `factory/INDEX.yaml`.

## Inputs

The playbook requires a single input artifact:

- `research-brief.md` — defines the research question, intended use, audience,
  scope, exclusions, freshness requirements, source requirements, cost of
  error, and completion criteria.

## Outputs

The playbook produces the full research artifact set:

- `research-plan.md` — questions, conjectures, assignments, and stop conditions.
- `assignments/*.md` — independent research assignments.
- `sources/*.md` — source records with provenance and limitations.
- `conjectures/*.md` — testable claims with scope, assumptions, and refutation
  conditions.
- `tests/*.md` — refutation test records.
- `reviews/*.md` — adversarial reviews.
- `votes/*.md` — disposition votes.
- `claim-register.md` — the frozen register separating surviving, refuted,
  unresolved, and superseded claims.
- `final-report.md` — the validated report built from the frozen register.

## The Validation Gate

Every artifact produced by a step must pass the three-stage validation gate
before the next step begins. The stages run in a fixed order, and progression
blocks on the first failing stage.

1. **Schema validation** — `factory/scripts/schema-validate` checks that the
   artifact has the required form: required fields, field types, allowed
   values, identifier formats, artifact types and states, timestamps,
   references, hashes, vote values, and defect levels.
2. **Policy validation** — `factory/scripts/policy-validate` checks the
   enforceable rules across artifacts and roles: role separation, references,
   quorum, current claim versions, and the remaining policy constraints.
3. **Semantic review** — a qualified agent checks evidence, reasoning, scope,
   refutation attempts, and meaning. This is the judgment that schemas and
   policies deliberately leave open.

An output must PASS schema validation, THEN policy validation, THEN semantic
review before the next step may start. A failing stage blocks progression; the
step's owner must correct the artifact and re-run the gate from the first
stage.

## Procedure

### Step 1 — Validate the Brief

**Agent**: `research-orchestrator`
**Skills**: none
**Input**: `research-brief.md`
**Output**: validated brief, or a blocker

The orchestrator confirms that the brief supplies every required field and
matches its schema. The step fails when a required field is missing or the
brief does not match `research-brief.schema.json`.

**Gate**: schema, then policy, then semantic review of the brief must pass
before Step 2 begins.

### Step 2 — Plan the Research

**Agent**: `researcher`
**Skills**: `research-planning`
**Input**: validated brief
**Output**: `research-plan.md`

Acting as planner, the researcher turns the validated brief into research
questions, competing conjectures where relevant, evidence requirements,
refutation strategies, assignments, review requirements, and stop conditions.

**Gate**: the research plan must pass schema, then policy, then semantic
review before Step 3 begins.

### Step 3 — Assign Independent Research

**Agent**: `research-orchestrator`
**Skills**: none
**Input**: `research-plan.md`
**Output**: `assignments/*.md`

The orchestrator issues assignments. Each conclusion-critical question normally
receives a direct-evidence assignment, a contrary-evidence assignment, and an
alternative-explanation assignment. At least two researchers must work
independently on each conclusion-critical question.

**Gate**: the assignments must pass schema, then policy, then semantic review
before Step 4 begins.

### Step 4 — Collect Evidence

**Agent**: `researcher`
**Skills**: `source-research`
**Input**: `assignments/*.md`
**Output**: `sources/*.md`

Each researcher finds sources for one bounded assignment and records them. Each
source record captures source identity, author or issuing body, publisher,
publication date, relevant event date, source family, precise evidence
location, method, limitations, and provenance.

**Gate**: the source records must pass schema, then policy, then semantic
review before Step 5 begins.

### Step 5 — Form Conjectures

**Agent**: `researcher`
**Skills**: `claim-formulation`, `refutation-design`
**Input**: research question, `sources/*.md`, competing explanations
**Output**: `conjectures/*.md`

The researcher states one claim per conjecture, with its scope, assumptions,
supporting evidence, contrary evidence, possible refuting evidence, planned
tests, qualifications, and content hash. A claim that cannot state what would
count against it is not ready for review.

**Gate**: each conjecture must pass schema, then policy, then semantic review
before Step 6 begins.

### Step 6 — Validate the Conjecture

**Agent**: `research-orchestrator`
**Skills**: none
**Input**: `conjectures/*.md`
**Output**: validation result

The orchestrator rejects missing fields, invalid references, compound claims,
missing source-family data, missing assumptions, missing refutation
conditions, stale content hashes, and invalid artifact states.

As the first, cheapest check the orchestrator runs
`factory/scripts/conjecture-lint <conjecture> --expect-tests <plan tests-per-claim>`,
which flags a **non-atomic (compound) claim** and a **planned-test-count that
does not match the review protocol** — the two defects that, caught later, force
a resolution/re-test pass after the claim's tests, reviews, and votes have
already been spent. A conjecture that lints clean here cannot be sent back to be
split at Step 8 or rejected on test count at admission. The lint is advisory: the
author splits the claim or realigns the test count before the claim proceeds.

**Gate**: the validation result must pass schema, then policy, then semantic
review before Step 7 begins.

### Step 7 — Run Refutation Tests

**Agent**: `researcher` or `claim-reviewer`
**Skills**: `refutation-design`
**Input**: `conjectures/*.md`, planned test
**Output**: `tests/*.md`

The tester records the claim ID and version, the test question, the result
that would refute the claim, the method, the evidence examined, the observed
result, the limitations, and the outcome. Allowed outcomes are `SURVIVED`,
`REFUTED`, `INCONCLUSIVE`, and `INVALID_TEST`. Failed and inconclusive tests
must remain visible.

**Gate**: each test record must pass schema, then policy, then semantic review
before Step 8 begins.

### Step 8 — Review Adversarially

**Agent**: `claim-reviewer`
**Skills**: `adversarial-review`
**Input**: `conjectures/*.md`, `sources/*.md`, `tests/*.md`
**Output**: `reviews/*.md`

At least three reviewers must assess each material claim; high-risk claims may
require five. Reviews remain hidden until all initial reviews are complete.
Each review checks testability, credible alternatives, test severity, whether
the claim survived unchanged, whether the sources support the exact wording,
source independence, explicit assumptions, scope, unexplained contrary
evidence, and what evidence could still overturn the claim. Defects are
classified `BLOCKER`, `MAJOR`, `MINOR`, or `NOTE`; a blocker prevents survival.

**Gate**: each review must pass schema, then policy, then semantic review
before Step 9 begins.

### Step 9 — Vote on Disposition

**Agent**: `claim-reviewer`
**Skills**: none
**Input**: `reviews/*.md`
**Output**: `votes/*.md`

Each vote refers to one completed review, one exact claim hash, and one
eligible reviewer. Allowed votes are `SURVIVE`, `REFUTE`, `UNRESOLVED`, and
`ABSTAIN`. A claim survives only when the required tests were run, evidence
requirements passed, quorum was reached, `SURVIVE` received a strict majority
of decisive votes, no blocker remains, no material refutation remains
unanswered, and all votes refer to the current claim hash.

**Gate**: each vote must pass schema, then policy, then semantic review before
Step 10 begins.

### Step 10 — Resolve Failed Claims

**Agent**: `research-orchestrator`
**Skills**: none
**Input**: refuted or unresolved claim, `reviews/*.md`, `tests/*.md`
**Output**: targeted research assignment, revised conjecture, evidence-gap
claim, or human escalation

Refuted and unresolved claims route back through resolution. A claim may be
withdrawn, narrowed, split, replaced, tested again, or marked unresolved. Any
semantic change creates a new claim version; the old reviews and votes remain
in the audit trail but no longer count. A new version re-enters the procedure
at Step 5 and must earn a fresh set of tests, reviews, and votes.

**Gate**: each resolution output must pass schema, then policy, then semantic
review before the routed step resumes.

### Step 11 — Generate the Claim Register

**Agent**: `research-orchestrator`
**Skills**: none
**Input**: `conjectures/*.md`, `tests/*.md`, `reviews/*.md`, `votes/*.md`
**Output**: `claim-register.md`

The orchestrator generates the register, separating surviving, refuted,
unresolved, and superseded claims. Each surviving claim records its text,
scope, assumptions, evidence, tests, failed tests, reviews, vote result,
qualifications, remaining possible refuters, and applicable date. The claim
register must not be edited by hand.

**Gate**: the claim register must pass schema, then policy, then semantic
review, and is then frozen before Step 12 begins.

### Step 12 — Write the Report

**Agent**: `research-report-writer`
**Skills**: `research-reporting`
**Input**: frozen `claim-register.md`
**Output**: `final-report.md`

The report writer arranges the surviving claims into a report. Every factual
section references one or more surviving claim IDs. The report distinguishes
surviving findings, refuted conjectures, unresolved alternatives,
recommendations, evidence gaps, and limitations, and it adds no new research.

**Gate**: the final report must pass schema, then policy, then semantic review
before Step 13 begins.

### Step 13 — Validate the Report

**Agent**: `research-orchestrator`
**Skills**: none
**Input**: frozen `claim-register.md`, `final-report.md`
**Output**: validation result

The report fails when a factual statement lacks a surviving claim reference,
presents a refuted or unresolved claim as fact, describes a claim as proved,
hides a material failed test, omits a required qualification, changes the scope
of a claim, cites a source that cannot be resolved, treats correlated sources
as independent, or presents stale evidence as current.

**Gate**: the report must pass schema, then policy, then semantic review. Only
then is the research complete.

## Enforced Rules

- **Two independent researchers** — at least two researchers work
  independently on each conclusion-critical question (Step 3).
- **Three reviewers** — at least three reviewers assess each material claim,
  and high-risk claims may require five (Step 8).
- **New version on resolution** — refuted or unresolved claims route back
  through resolution (Step 10), and any semantic change starts a new claim
  version; prior reviews and votes stay in the audit trail but no longer count.
- **Role separation** — the claim author does not review or vote on that
  claim, the reviewer does not edit the claim, the orchestrator does not vote,
  and the report writer does not create findings.

## DONE

The research is complete when:

- [ ] every step declared and produced its input and output artifacts,
- [ ] every output passed schema, then policy, then semantic review before the
  next step began,
- [ ] each conclusion-critical question was researched by at least two
  independent researchers,
- [ ] each material claim was assessed by at least three reviewers,
- [ ] every surviving claim has traceable evidence, tests, reviews, and votes,
- [ ] every factual report statement maps to a surviving claim, and
- [ ] refutations and uncertainty remain visible in the final report.
