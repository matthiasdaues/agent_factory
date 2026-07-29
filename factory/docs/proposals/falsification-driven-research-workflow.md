---
title: "Falsification-Driven Research Playbook"
status: implemented
size:
  class: large
  effort: 10-30 person-days
  ramifications: cross-cutting
  prognosed_spend:
    engineering: 10-30 person-days
    agent: unknown
    external: none
owner: agent-factory
created: 2026-07-21
updated: 2026-07-29
supersedes:
---

# Feature Request: Falsification-Driven Research Playbook

## Summary

Add a research playbook that:

1. plans a research topic,
2. assigns independent research,
3. forms testable claims,
4. tries to refute those claims,
5. reviews them adversarially,
6. admits only surviving claims to the final report.

The workflow must use common templates, schemas, and policies so that artifacts can be checked before they pass from one step to the next.

A surviving claim is not proved true. It has only survived the defined tests within its stated scope.

## Existing Structure

```text
agents/
skills/
playbooks/
rulebooks/
├── policies/
└── templates/
```

Add:

```text
rulebooks/
└── schemas/
```

The resulting structure is:

```text
agents/
skills/
playbooks/
rulebooks/
├── policies/
├── templates/
└── schemas/
```

## Responsibility of Each Folder

| Folder                 | Purpose                                               |
| ---------------------- | ----------------------------------------------------- |
| `agents/`              | Defines who performs a role and what that role may do |
| `skills/`              | Defines reusable capabilities                         |
| `playbooks/`           | Defines ordered procedures and artifact handoffs      |
| `rulebooks/policies/`  | Defines rules that agents and playbooks must obey     |
| `rulebooks/templates/` | Defines the initial form of artifacts                 |
| `rulebooks/schemas/`   | Defines the valid structure of completed artifacts    |

Templates guide creation.

Schemas validate structure.

Policies enforce rules across artifacts and roles.

Playbooks control sequence.

Agents perform the work.

Skills provide the required capabilities.

## Proposed Files

```text
agents/
├── research-orchestrator.md
├── researcher.md
├── claim-reviewer.md
└── research-report-writer.md

skills/
├── research-planning/
│   └── SKILL.md
├── source-research/
│   └── SKILL.md
├── claim-formulation/
│   └── SKILL.md
├── refutation-design/
│   └── SKILL.md
├── adversarial-review/
│   └── SKILL.md
└── research-reporting/
    └── SKILL.md

playbooks/
└── research-topic/
    └── PLAYBOOK.md

rulebooks/
├── policies/
│   └── research/
│       ├── role-separation.md
│       ├── evidence-policy.md
│       ├── claim-admission-policy.md
│       └── report-policy.md
├── templates/
│   └── research/
│       ├── research-brief.md
│       ├── research-plan.md
│       ├── research-assignment.md
│       ├── source-record.md
│       ├── conjecture.md
│       ├── test-record.md
│       ├── review.md
│       ├── vote.md
│       ├── claim-register.md
│       └── final-report.md
└── schemas/
    └── research/
        ├── research-brief.schema.json
        ├── research-plan.schema.json
        ├── research-assignment.schema.json
        ├── source-record.schema.json
        ├── conjecture.schema.json
        ├── test-record.schema.json
        ├── review.schema.json
        ├── vote.schema.json
        ├── claim-register.schema.json
        └── final-report.schema.json
```

## Agents

### Research Orchestrator

Runs the playbook.

It may:

- start playbook steps,
- assign agents,
- run validation,
- request another research round,
- tally eligible votes,
- freeze the claim register,
- start report generation.

It must not:

- write substantive claims,
- review claims,
- vote,
- add findings to the report.

### Researcher

Researches a bounded question.

It may:

- find sources,
- assess source provenance,
- record evidence,
- propose testable claims,
- design or execute refutation tests.

It must record:

- supporting evidence,
- contrary evidence,
- source limitations,
- alternative explanations,
- failed searches,
- unresolved gaps.

It may not review or vote on its own claim.

### Claim Reviewer

Attempts to refute a claim.

It checks:

- whether the claim can be falsified,
- whether the sources support its exact wording,
- whether the sources are independent,
- whether credible alternatives were considered,
- whether the tests were severe,
- whether assumptions were added after a failed test,
- whether the claim exceeds the tested scope.

It may not edit the claim.

### Research Report Writer

Writes the final report from the frozen claim register.

It may:

- arrange surviving claims,
- summarize them,
- preserve refutations and limitations.

It must not:

- conduct new research,
- create claims,
- remove qualifications,
- present a surviving claim as proved,
- use rejected or unresolved claims as facts.

## Skills

### Research Planning

Turns an approved brief into research questions, assignments, competing conjectures, and stop conditions.

### Source Research

Finds sources for one bounded assignment.

### Claim Formulation

Turns recorded evidence into one precise and testable claim.

### Refutation Design

Defines evidence or observations that would count against a claim.

### Adversarial Review

Tests a claim, its evidence, and its refutation attempts.

### Research Reporting

Builds a report from the frozen claim register without adding new findings.

Skills do not control the workflow. The playbook does.

## Policies

### Role-Separation Policy

The policy must enforce that:

- a claim author cannot review or vote on that claim,
- a reviewer cannot edit the claim,
- the orchestrator cannot vote,
- the report writer cannot create findings,
- one agent cannot fill conflicting roles for the same claim.

### Evidence Policy

The policy must require:

- precise source references,
- source dates,
- source provenance,
- source-family identification,
- source limitations,
- contrary-evidence searches,
- clear separation between evidence and interpretation.

Several copies of one source count as one source family.

Repetition is not independent corroboration.

### Claim-Admission Policy

A claim may enter the final report only when:

- it states one assertion,
- its scope is clear,
- its assumptions are explicit,
- it states what would count against it,
- required tests were run,
- evidence checks passed,
- required reviews were completed,
- a strict majority voted for survival,
- no blocking defect remains,
- no material refutation remains unanswered,
- all votes refer to the current claim version.

A vote decides whether a claim met the process standard. It does not decide truth.

### Report Policy

The final report must:

- use surviving claims as its factual basis,
- cite claim IDs,
- preserve material qualifications,
- show important failed or inconclusive tests,
- distinguish findings from recommendations,
- identify unresolved questions,
- avoid language that presents claims as proved.

Preferred wording includes:

- “survived the defined tests,”
- “not refuted within the tested scope,”
- “provisionally retained,”
- “remains open to refutation.”

## Playbook

### Inputs

The playbook requires:

```text
research-brief.md
```

The brief must define:

- research question,
- intended use,
- audience,
- scope,
- exclusions,
- freshness requirements,
- source requirements,
- cost of error,
- completion criteria.

### Outputs

The playbook produces:

```text
research-plan.md
assignments/*.md
sources/*.md
conjectures/*.md
tests/*.md
reviews/*.md
votes/*.md
claim-register.md
final-report.md
```

## Procedure

### Step 1: Validate the Brief

**Agent:** Research orchestrator
**Input:** Research brief
**Output:** Validated brief or blocker

The step fails when required fields are missing or the brief does not match its schema.

### Step 2: Plan the Research

**Agent:** Researcher acting as planner
**Skill:** Research planning
**Input:** Validated brief
**Output:** Research plan

The plan defines:

- research questions,
- competing conjectures where relevant,
- evidence requirements,
- refutation strategies,
- assignments,
- review requirements,
- stop conditions.

### Step 3: Assign Independent Research

**Agent:** Research orchestrator
**Input:** Research plan
**Output:** Research assignments

Each conclusion-critical question should normally receive:

- a direct-evidence assignment,
- a contrary-evidence assignment,
- an alternative-explanation assignment.

At least two researchers must work independently on each conclusion-critical question.

### Step 4: Collect Evidence

**Agent:** Researcher
**Skill:** Source research
**Input:** Research assignment
**Output:** Source records

Each source record must contain:

- source identity,
- author or issuing body,
- publisher,
- publication date,
- relevant event date,
- source family,
- precise evidence location,
- method,
- limitations,
- provenance.

### Step 5: Form Conjectures

**Agent:** Researcher
**Skills:**

- Claim formulation
- Refutation design

**Input:**

- research question,
- source records,
- competing explanations.

**Output:** Conjecture

Each conjecture must contain:

- one claim,
- its scope,
- its assumptions,
- supporting evidence,
- contrary evidence,
- possible refuting evidence,
- planned tests,
- qualifications,
- content hash.

A claim that cannot state what would count against it is not ready for review.

### Step 6: Validate the Conjecture

**Agent:** Research orchestrator
**Input:** Conjecture
**Output:** Validation result

Validation must reject:

- missing fields,
- invalid references,
- compound claims,
- missing source-family data,
- missing assumptions,
- missing refutation conditions,
- stale content hashes,
- invalid artifact states.

### Step 7: Run Refutation Tests

**Agent:** Researcher or claim reviewer
**Input:**

- conjecture,
- planned test.

**Output:** Test record

Each test record must state:

- claim ID and version,
- test question,
- result that would refute the claim,
- method,
- evidence examined,
- observed result,
- limitations,
- outcome.

Allowed outcomes are:

- `SURVIVED`
- `REFUTED`
- `INCONCLUSIVE`
- `INVALID_TEST`

Failed and inconclusive tests must remain visible.

### Step 8: Review Adversarially

**Agent:** Claim reviewer
**Skill:** Adversarial review
**Input:**

- conjecture,
- source records,
- test records.

**Output:** Review

At least three reviewers must assess each material claim.

High-risk claims may require five.

Reviews should remain hidden until all initial reviews are complete.

Each review must check:

01. Is the claim testable?
02. Were credible alternatives considered?
03. Were the tests severe?
04. Did the claim survive without being changed?
05. Do the sources support the exact wording?
06. Are the sources independent?
07. Are assumptions explicit?
08. Does the claim exceed the tested scope?
09. Is contrary evidence still unexplained?
10. What evidence could still overturn the claim?

Defects are classified as:

- `BLOCKER`
- `MAJOR`
- `MINOR`
- `NOTE`

A blocker prevents survival.

### Step 9: Vote on Disposition

**Agent:** Claim reviewer
**Input:** Completed review
**Output:** Vote

Allowed votes are:

- `SURVIVE`
- `REFUTE`
- `UNRESOLVED`
- `ABSTAIN`

Each vote must refer to:

- one completed review,
- one exact claim hash,
- one eligible reviewer.

A claim survives only when:

- required tests were run,
- evidence requirements passed,
- quorum was reached,
- `SURVIVE` received a strict majority of decisive votes,
- no blocker remains,
- no material refutation remains unanswered,
- all votes refer to the current claim hash.

### Step 10: Resolve Failed Claims

**Agent:** Research orchestrator
**Input:**

- refuted or unresolved claim,
- reviews,
- test records.

**Output:**

- targeted research assignment,
- revised conjecture,
- evidence-gap claim,
- or human escalation.

A claim may be:

- withdrawn,
- narrowed,
- split,
- replaced,
- tested again,
- marked unresolved.

Any semantic change creates a new claim version.

Old reviews and votes remain in the audit trail but no longer count.

### Step 11: Generate the Claim Register

**Agent:** Research orchestrator
**Input:**

- conjectures,
- tests,
- reviews,
- votes.

**Output:** Generated claim register

The register separates:

- surviving claims,
- refuted claims,
- unresolved claims,
- superseded claims.

Each surviving claim records:

- claim text,
- scope,
- assumptions,
- evidence,
- tests,
- failed tests,
- reviews,
- vote result,
- qualifications,
- remaining possible refuters,
- applicable date.

The claim register must not be edited by hand.

### Step 12: Write the Report

**Agent:** Research report writer
**Skill:** Research reporting
**Input:** Frozen claim register
**Output:** Final report

Every factual report section must reference one or more surviving claim IDs.

The report must distinguish:

- surviving findings,
- refuted conjectures,
- unresolved alternatives,
- recommendations,
- evidence gaps,
- limitations.

### Step 13: Validate the Report

**Agent:** Research orchestrator
**Input:**

- frozen claim register,
- final report.

**Output:** Validation result

The report fails when:

- a factual statement lacks a surviving claim reference,
- it presents a refuted or unresolved claim as fact,
- it describes a claim as proved,
- it hides a material failed test,
- it omits a required qualification,
- it changes the scope of a claim,
- a source cannot be resolved,
- it treats correlated sources as independent,
- it presents stale evidence as current.

## Templates

Templates must provide a common starting form for each research artifact.

They should:

- include required headings,
- include short field instructions,
- avoid optional sections that have no current use,
- use the same field names as the matching schema.

Templates must not contain workflow rules. Those belong in policies and playbooks.

## Schemas

Schemas validate artifacts exchanged between playbook steps.

The first implementation should cover only research artifacts.

Schemas should validate:

- required fields,
- field types,
- allowed values,
- identifier formats,
- artifact types,
- artifact states,
- timestamps,
- references,
- hashes,
- vote values,
- defect levels.

Schemas should not try to decide:

- whether evidence supports a claim,
- whether a source is truly independent,
- whether a test was severe,
- whether a claim is atomic,
- whether an assumption is ad hoc.

Those checks belong to policies, semantic validators, and reviewers.

## Validation Order

Each artifact passes through three checks:

```text
Schema validation
    ↓
Policy validation
    ↓
Semantic review
```

### Schema Validation

Checks whether the artifact has the required form.

### Policy Validation

Checks role separation, references, quorum, current versions, and other enforceable rules.

### Semantic Review

Checks evidence, reasoning, scope, refutation attempts, and meaning.

## Required Tests

The implementation must prove that:

- an artifact with missing required fields fails schema validation,
- an unfalsifiable claim cannot enter review,
- an author cannot review its own claim,
- copied sources do not count as independent evidence,
- a failed severe test blocks survival,
- an invalid test does not support a claim,
- a changed claim invalidates prior reviews and votes,
- a new assumption starts a new review cycle,
- a tie does not produce survival,
- abstentions do not create a majority,
- a blocker prevents survival,
- a refuted claim cannot enter the report as fact,
- an unsupported report statement fails validation,
- failed tests remain visible,
- required qualifications remain in the report.

## Completion Criteria

The feature is complete when:

- `rulebooks/schemas/` exists,
- the research artifacts have templates and schemas,
- the playbook runs from brief to validated report,
- every step declares its input and output artifacts,
- outputs pass schema validation before the next step begins,
- role separation is enforced,
- each material claim states what would refute it,
- every surviving claim has traceable evidence, tests, reviews, and votes,
- every factual report statement maps to a surviving claim,
- refutations and uncertainty remain visible,
- all required tests pass.

## Guiding Rule

The workflow must not ask only:

> How many agents agree?

It must ask:

> What would refute this claim, and was it exposed to a serious attempt at refutation?
