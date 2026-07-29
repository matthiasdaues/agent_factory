---
title: Feature Proposal Template
version: 1.1.0
---

# Feature Proposal Template

Skeleton for a single `factory/docs/proposals/<name>.md` file.

## Frontmatter

```yaml
---
title: <Feature Name>
status: open                       # draft | open | accepted | implemented | cancelled | superseded
size:
  class: medium                    # small | medium | large | epic
  effort: 5-10 person-days         # range plus an explicit unit, or unknown
  ramifications: cross-cutting     # local | cross-cutting | architectural | ecosystem
  prognosed_spend:
    engineering: 5-10 person-days  # range plus an explicit unit, or unknown
    agent: 1-2 million tokens       # range plus an explicit unit, or unknown
    external: EUR 0-100             # currency and range, none, or unknown
owner: <person-or-team>
created: YYYY-MM-DD
updated: YYYY-MM-DD
supersedes: null                   # proposal path, or null
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

`size` is a forecast, not an accounting record. Update it when material new
information changes the estimate. Use explicit units and ranges; use `unknown`
instead of false precision. `ramifications` describes the expected blast radius,
not implementation difficulty.

# Feature Request: <Feature Name>

<!--
A proposal is the seed brief that opens a feature-addition. It is a DESIGN
ORIGIN consumed by the Planning phase — never a runtime input to a shipped
agent (an agent's `inputs:` must point at tracked, shipped artifacts, not at a
proposal). Keep it decision-complete: a reader should be able to plan a backlog
from it without re-deriving the design.

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
