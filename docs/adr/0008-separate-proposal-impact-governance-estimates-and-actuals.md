---
id: 0008
status: accepted
evaluation: none
---

# Separate proposal impact, governance, estimates, and actuals

## Context

Agent Factory proposals originally forecast feature size with person-days,
ramifications, agent tokens, and external spend. Most implementation is
performed by AI agents, so person-days misstate the production model. Qualified
human attention, assurance needs, and boundary risk often constrain delivery
more than code generation.

Repository history also shows that implementation volume is a poor proxy for
review effort. The falsification research feature delivered seventeen stories
with no directly traced remediation findings, while token-usage tracking
delivered ten stories and produced seventeen traced reconciliation, quality,
and security findings. Lifecycle, concurrency, security, data integrity, and
compatibility drove the difference.

The current Codex session provides a measured calibration example. Between
cumulative usage records `0049` and `0053`, the estimation-schema discussion
added 15,281 normalized tokens. Provider counters over the same interval added
2,188,234 input tokens, of which 2,161,920 were cache reads, plus 5,028 output
tokens. Normalized tokens measure captured interaction text on a common
yardstick; provider counters measure different processing and billing inputs.
Neither measures human attention. Capture timestamps combine model, tool,
review, thinking, and idle time, so Git or wall-clock intervals cannot be
relabelled as reviewer-hours.

The proposal schema therefore needs to support future calibration without
conflating impact, policy, forecasts, provider cost, and observed actuals. It
must also avoid introducing proposal-level evidence records that duplicate
Completion Criteria, specifications, story acceptance criteria, tests,
findings, and review reports.

ADR-0007 already makes fixed normalized tokens the cross-CLI comparison metric
and preserves provider counts separately for cost reconciliation. This
decision extends that boundary and does not conflict with another ADR. A Pugh
Matrix is not warranted: person-day planning and a parallel first-class
evidence system were rejected through adversarial review and repository
calibration; no unresolved alternative remains.

## Decision

Proposal frontmatter uses schema version 2 and separates three concerns:

```yaml
schema_version: 2
title: <Feature Name>
status: open
owner: <person-or-team>
created: YYYY-MM-DD
updated: YYYY-MM-DD
supersedes: null

impact:
  scope: cross_component
  architecture_change: false
  external_contract_change: true
  boundaries:
    - docs/spec/supplementary_specs/interface-contracts.md

governance:
  assurance: high
  risk_domains:
    - reliability

estimate:
  as_of: YYYY-MM-DD
  basis: analogous_change
  confidence: medium
  human_review_hours:
    min: 0.5
    max: 1.0
  normalized_tokens:
    min: 10000
    max: 25000
```

`impact.scope` is `local`, `cross_component`, or `cross_project`.
Architecture and external-contract changes remain independent Booleans because
either can occur at any scope. Boundaries use tracked paths with optional
Markdown anchors. A separate boundary registry is deferred under YAGNI.

`governance.assurance` is `routine`, `elevated`, `high`, or `critical`.
`risk_domains` selects from `security`, `privacy`, `data_integrity`,
`compatibility`, `reliability`, and `operations`. A versioned governance policy
may later derive required review roles and gates from these values. The schema
does not repeat derived reviewer counts or create evidence-requirement
entities. Completion Criteria and the established delivery artifacts continue
to own feature-specific proof.

`estimate` is a forecast. Its basis is `analogous_change`, `decomposition`, or
`judgment`; confidence is `low`, `medium`, or `high`. Human-review hours measure
active human review, approval, and manual validation. Normalized tokens use the
fixed tokenizer defined by ADR-0007. Each numeric range is non-negative and has
`min <= max`. Either metric may be `unknown` when no defensible estimate exists.
Implemented legacy proposals retain unknown actuals rather than receiving
invented retrospective values.

Low-confidence estimates are revisited after backlog planning. A material
change after acceptance returns the proposal to `open` and requires a new
acceptance. The accepted revision is the full forty-character Git SHA of the
commit that establishes acceptance; it is discovered from Git or recorded by a
separate workflow artifact, never embedded self-referentially in the proposal.

Observed actuals remain append-only and outside proposal frontmatter. Future
calibration records reference `{proposal_path, accepted_sha}`. Usage actuals
derive deltas from cumulative snapshots; rows are never summed. Normalized and
provider-reported counters remain separate. Monetary budgets are deferred until
pricing, reservation, attribution, concurrency, and stop semantics make them
enforceable. Human-attention actuals require explicit capture and are never
inferred from Git timestamps or elapsed session time.

## Consequences

**Positive**

- Proposals classify change impact and assurance independently of production
  volume.
- Estimates have explicit units, basis, confidence, and calibration date.
- Normalized AI effort can be compared across CLIs without pretending to equal
  provider cost.
- Future actuals can preserve the accepted forecast and support calibration
  without rewriting history.
- Existing completion, specification, planning, testing, finding, and review
  artifacts keep one owner each.

**Negative / risks**

- Human-review forecasts remain uncalibrated until active attention is
  explicitly measured.
- Proposal-attributed usage requires lifecycle capture of proposal path and
  accepted SHA or a deterministic mapping from stories to that revision.
- Assurance and risk metadata remain advisory until a versioned validator and
  workflow policy enforce their consequences.
- Open legacy proposals need migration before their next acceptance;
  implemented legacy proposals are grandfathered and may retain unknown
  estimates.
- Path-based boundary references can drift on moves and must be updated like
  other tracked references.
