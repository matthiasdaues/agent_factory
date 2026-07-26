---
name: research-planning
description: Turn a validated brief into research questions, assignments, competing conjectures, and stop conditions.
category: research
disable-model-invocation: false
---

# Research Planning

This skill provides a capability for turning a validated research brief into the
structured plan appropriate to its mode. It does not control the workflow
sequence — the playbook controls when planning occurs and how the plan is used.

## Capability

Read the brief's `mode` before choosing the output contract. An omitted mode
means `survey`.

- For `survey` (including an omitted mode), produce the source-grounded survey
  plan validated against
  [`research-survey-plan.schema.json`](../../rulebooks/schemas/research-survey-plan.schema.json)
  and structured by
  [`research-survey-plan.md`](../../rulebooks/templates/research-survey-plan.md).
- For `falsification`, produce the existing research plan validated against
  [`research-plan.schema.json`](../../rulebooks/schemas/research-plan.schema.json)
  and structured by
  [`research-plan.md`](../../rulebooks/templates/research-plan.md).

## Falsification Plan Output

For a `falsification` brief, transform the validated brief into a research plan
that defines:

- research questions,
- competing conjectures where relevant,
- evidence requirements,
- refutation strategies,
- assignments,
- review requirements,
- stop conditions.

## Output

The skill produces a research plan artifact validated against [`factory/rulebooks/schemas/research-plan.schema.json`](../../rulebooks/schemas/research-plan.schema.json).

Each plan must contain:

| Field                   | Purpose                                             |
| ----------------------- | --------------------------------------------------- |
| `research_questions`    | Bounded questions this plan sets out to answer      |
| `competing_conjectures` | Rival candidate answers under consideration         |
| `evidence_requirements` | What evidence each conjecture needs to be evaluated |
| `refutation_strategies` | Approaches for trying to disprove each conjecture   |
| `assignments`           | Bounded assignments this plan hands out             |
| `review_requirements`   | What a review of this plan's output must check      |
| `stop_conditions`       | Conditions under which this research effort stops   |

Refer to [`factory/rulebooks/templates/research-plan.md`](../../rulebooks/templates/research-plan.md) for the template structure.

## Survey Plan Output

For a `survey` brief, create a bounded source-search plan containing research
questions, search angles, source targets, assignments, and stop conditions.
Assignments identify the source search to perform and its output path. Do not
add conjectures or a review protocol to this artifact.

## Review Protocol

For falsification plans, the plan fixes the review protocol as explicit
numbers, recorded in `review_requirements`, so downstream steps stay consistent
and conjectures are admittable by construction:

- State **reviewers-per-claim** and **tests-per-claim** for each tier the plan uses (standard, and high-risk if any). At least three reviewers assess each material claim; high-risk claims may take five.
- Set **tests-per-claim equal to the number of tests actually executed** under the protocol (typically one severe test per reviewer). Admission requires one executed test record per planned test, so this number is the count conjecture authors must plan to.
- Conjecture authors read these numbers and plan exactly that many severe tests (see [`claim-formulation`](../claim-formulation/SKILL.md) and [`refutation-design`](../refutation-design/SKILL.md)); planning more tests than the protocol runs makes a claim unadmittable regardless of merit.

## Responsibility

This skill is **responsible for** planning research work: framing questions, identifying assumptions, specifying what evidence counts, and defining review criteria.

This skill is **not responsible for** controlling workflow: that is the playbook's role. It is not responsible for executing the research, collecting sources, running tests, reviewing claims, or generating the report.
