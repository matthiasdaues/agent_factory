---
title: Feature Proposal Template
version: 2.1.0
---

# Feature Proposal Template

Skeleton for a single `docs/proposals/<name>.md` file.

## Frontmatter

```yaml
---
schema_version: 2
title: <Feature Name>
status: open                       # draft | open | accepted | implemented | cancelled | superseded
owner: <person-or-team>
created: YYYY-MM-DD
updated: YYYY-MM-DD
supersedes: null                   # proposal path, or null

impact:
  scope: cross_component           # local | cross_component | cross_project
  architecture_change: false
  external_contract_change: true
  boundaries:                      # tracked path with optional Markdown anchor
    - docs/spec/interface-contracts.md

governance:
  assurance: high                  # routine | elevated | high | critical
  risk_domains:                    # security | privacy | data_integrity |
    - reliability                  # compatibility | reliability | operations

estimate:
  as_of: YYYY-MM-DD
  basis: analogous_change          # analogous_change | decomposition | judgment
  confidence: medium               # low | medium | high
  human_review_hours:              # or: unknown
    min: 0.5
    max: 1.0
  normalized_tokens:               # or: unknown; fixed tokenizer from ADR-0007
    min: 10000
    max: 25000
  estimated_consumption:           # or: unknown; total tokens consumed by the
    min: 150000                    # agentic workflow (overhead multiplier applied)
    max: 375000
    overhead_multiplier: 15        # typical range: 8-25x normalized_tokens
    playbook: feature-addition     # playbook path determines multiplier
---
```

What each status means:

- `draft`: not finished and not ready for review.
- `open`: ready for review; nobody has committed to building it yet.
- `accepted`: approved as an input to planning and implementation.
- `implemented`: its accepted scope and completion criteria have been delivered.
- `cancelled`: closed on purpose without being built.
- `superseded`: replaced by the proposal named in the body; on the
  replacement, set `supersedes` to point back to this proposal.

`impact` describes how far the change reaches and how much it risks breaking
contracts, not how much work it is. `architecture_change` and
`external_contract_change` do not depend on scope. Boundary references use
tracked paths until the project shows that it needs a separate list of
boundaries.

`governance` sets the level of assurance and the risk policy that planning and
review must apply. The evidence for a feature stays in the Completion Criteria,
specifications, story acceptance criteria, tests, findings, and review reports;
the proposal frontmatter does not add a second place to keep evidence.

`estimate` is a dated forecast, not a record of what was spent and not a budget
anyone enforces. Ranges use numbers and meet `0 <= min <= max`. Human-review
hours count the time a human spends reviewing, approving, and checking by hand,
not time spent waiting. Normalized tokens use the fixed tokenizer from ADR-0007,
the same for every CLI, and measure the **edit volume**: how many tokens of
text change across the affected files. They do not predict what the provider
bills or the extra work of the agents.

`estimated_consumption` predicts the **total tokens consumed** by the agent
workflow: reading context, grilling, reviews, fix rounds, and coordination. It
multiplies `normalized_tokens` by an `overhead_multiplier` that is set from
past runs of the playbook path. Typical multipliers:

- Feature-addition with review loops: 15–25×
- Bug fix or refactoring: 8–12×
- Documentation update: 5–10×

Write `unknown` instead of making up numbers afterwards or giving more
precision than you have. After the work is done, record the actual numbers in
the external calibration store (not in the proposal), so later multiplier
estimates get better.

# Feature Request: <Feature Name>

<!--
A proposal is the first document of a feature-addition. It is where the DESIGN
COMES FROM, and the Planning phase reads it. It is never an input that a shipped
agent reads at run time (an agent's `inputs:` must point at tracked, shipped
files, not at a proposal). Settle every decision in it: a reader should be able
to plan a backlog from it without working out the design again.

Clarification and grilling edit this file directly. They may move a proposal
with every decision settled from `draft` to `open`, but only the stakeholder's
acceptance moves it to `accepted`. A real change after acceptance sets it back
to `open`, and the stakeholder must accept it again.

The file has two parts. The proposal describes the design in the present
tense, as if it were already built. The Appendix records how the design got its
shape: decisions and review findings. The proposal cites an appendix row by its
ID, for example "(DEC-07)", where a reader might ask why the design has its
shape. A reader never needs the Appendix to understand the design. So the
proposal contains no dates, no "Decision:" stamps and no answers to reviewers;
see "Target state and history" in factory-voice.md.

Fill every section. Delete a section only if it really does not apply, and say
why. Delete these comments in the finished proposal.
-->

## Primer

<!-- 400-500 words for a newcomer, written by the write-primer skill once the
design is settled. It gives an overview, not every detail. -->

## Summary

<!-- 2-4 sentences: what the feature adds, and the one question it answers that
the system cannot answer today. State where the first release stops. Do not
repeat the Primer: the Primer introduces the topic to a newcomer, the Summary
tells a planner what the feature contains. -->

## Motivation

<!-- Why now. What exists today and why it is not enough. The concrete needs the
feature meets. If a capability is left for a later layer, say so and why. -->

## Core Principles

<!-- Optional. The design decisions that the rest depends on, one bullet each.
Every later decision must respect them. -->

## Design

<!-- The main part. For a data feature, the record or schema (field tables). For
a tool, its shape and the points where its parts connect. For a workflow, its
agents, skills, policies, and steps. Enough that Planning can split it into
INVEST stories. -->

## Scope

<!-- Two explicit lists. No filler items. -->

**In the first release:**

-

**Explicitly deferred (do NOT plan stories for these):**

-

## Design Details

<!-- Optional. Naming schemes, behavior on failure, retention, idempotency: the
decisions an implementer would otherwise have to guess. -->

## Open Questions

<!-- Only decisions that are really still open. Each should become a story
acceptance criterion, a recorded assumption, or an explicit deferral, not
filler. When a question is decided, remove it here, write the result into the
section where it belongs, and add a row to Decisions. -->

-

## Completion Criteria

<!-- Statements someone can check that make the first release "done". Each one
maps directly to a must-have story in the backlog. -->

-

## Guiding Rule

<!-- Optional. The one sentence a reviewer should measure the whole feature
against. -->

# Appendix

<!-- The history of how the proposal got its shape. Tables only. Add rows and
update them where they are; never delete a row. -->

## Decisions

<!-- One row for each decision or assumption that shaped the proposal, written
when it is made. Kind is `decision` or `assumption`; an assumption becomes a
decision when the person named in "Decided by" confirms it. "Raised by" names
the finding, open question or grilling round that led to it. -->

| ID     | Date       | Kind     | Decided by    | Decision                              | Raised by |
| ------ | ---------- | -------- | ------------- | ------------------------------------- | --------- |
| DEC-01 | YYYY-MM-DD | decision | product owner | \<the decision, one or two sentences> | PROP-01   |

## Review findings

<!-- One table that collects all review passes. The reviewer adds new rows
with status `open`. Whoever fixes a finding sets `fixed` and writes the
resolution with its evidence. The next review pass checks each `fixed` row and
sets `resolved`, or sets `open` again with the reason. Severity is `major`,
`minor`, or `note`, never `critical`. The Finding cell ends with a sentence
that starts with `Severity:`. Only the stakeholder sets `waived`, only on a
`major` row, and with the reason in Resolution. The review agent never sets
`waived`. -->

| ID      | Pass | Severity | Check | Status | Finding                                                                                            | Resolution |
| ------- | ---- | -------- | ----- | ------ | -------------------------------------------------------------------------------------------------- | ---------- |
| PROP-01 | 1    | major    | 02    | open   | \<what is wrong, with line references> Severity: \<level>, because \<reason> (\<deciding answer>). |            |

## Review passes

<!-- One row for each review pass. Line references in findings refer to the
commit that was reviewed in their pass. -->

| Pass | Date       | Reviewed commit | Disposition | Failed checks | Summary                  |
| ---- | ---------- | --------------- | ----------- | ------------- | ------------------------ |
| 1    | YYYY-MM-DD | \<40-char SHA>  | findings    | 02, 03        | <one to three sentences> |
