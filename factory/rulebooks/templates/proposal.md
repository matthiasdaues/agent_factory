---
title: Feature Proposal Template
version: 2.0.0
---

# Feature Proposal Template

Skeleton for a single `factory/docs/proposals/<name>.md` file.

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
    - docs/spec/supplementary_specs/interface-contracts.md

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
---
```

Status meanings:

- `draft`: incomplete and not yet ready for review.
- `open`: ready for review; no implementation commitment has been made.
- `accepted`: approved as an input to planning and implementation.
- `implemented`: its accepted scope and completion criteria have been delivered.
- `cancelled`: intentionally closed without implementation.
- `superseded`: replaced by the proposal named in the body; use `supersedes` on
  the replacement to point back to this proposal.

`impact` describes reach and contract risk, not effort. `architecture_change`
and `external_contract_change` are independent of scope. Boundary references
use tracked paths until the project has evidence that a separate boundary
registry is needed.

`governance` classifies the assurance and risk policy that planning and review
must apply. Feature-specific proof remains in Completion Criteria, specifications,
story acceptance criteria, tests, findings, and review reports; proposal
frontmatter does not introduce a parallel evidence entity.

`estimate` is a dated forecast, not an accounting record or enforceable budget.
Ranges use numeric values and satisfy `0 <= min <= max`. Human-review hours
cover active human review, approval, and manual validation—not elapsed waiting
time. Normalized tokens use the fixed cross-CLI tokenizer from ADR-0007 and do
not predict provider billing. Use `unknown` instead of retrospective invention
or false precision.

# Feature Request: <Feature Name>

<!--
A proposal is the seed brief that opens a feature-addition. It is a DESIGN
ORIGIN consumed by the Planning phase — never a runtime input to a shipped
agent (an agent's `inputs:` must point at tracked, shipped artifacts, not at a
proposal). Keep it decision-complete: a reader should be able to plan a backlog
from it without re-deriving the design.

Clarification and grilling amend this file directly. They may move a
decision-complete proposal from `draft` to `open`, but stakeholder acceptance is
the only transition to `accepted`. Material changes after acceptance return it
to `open` for reacceptance.

Fill every section; delete a section only if it genuinely does not apply, and
say why. Delete these comments in the finished proposal.
-->

## Summary

<!-- 2-4 sentences: what the feature adds and the one question it answers that
the system cannot answer today. State the scope boundary of the first release. -->

## Motivation

<!-- Why now. What exists today and why it is insufficient. The concrete need(s)
the feature meets. If a capability is deferred to a later layer, say so and why. -->

## Core Principles

<!-- Optional. The load-bearing design commitments, one bullet each, that every
downstream decision must respect. -->

## Design

<!-- The substance. For a data feature, the record/schema (field tables). For a
tool, its shape and seams. For a workflow, its agents/skills/policies/steps.
Enough that Planning can decompose it into INVEST stories. -->

## Scope

<!-- Two explicit lists. Padding-resistant. -->

**In the first release:**

-

**Explicitly deferred (do NOT plan stories for these):**

-

## Design Details

<!-- Optional. Naming schemes, failure behavior, retention, idempotency — the
decisions an implementer would otherwise guess. -->

## Open Questions

<!-- Genuine unresolved decisions. Each should become a story acceptance
criterion, a recorded assumption, or an explicit deferral — not padding. -->

-

## Completion Criteria

<!-- Checkable statements that make the first release "done". These map directly
to must-have stories in the backlog. -->

-

## Guiding Rule

<!-- Optional. The one sentence a reviewer should hold the whole feature against. -->
