---
title: Proposal Review — Project Charter
date: 2026-08-18
reviewer: proposal-review (independent session, author/reviewer separation)
target: "docs/proposals/capture-project-constraints.md (status open, schema_version 2, untracked in git)"
---

# Proposal Review — Project Charter

Semantic review of [capture-project-constraints.md](../proposals/capture-project-constraints.md)
against the [proposal template](../../factory/rulebooks/templates/proposal.md),
the factory artifacts it references, and the conventions in
[rules.md](../../factory/rulebooks/rules.md). Not a spec review; spec-lint not run.

## Verdict

The proposal is well-structured, internally coherent in its main arc, and its
factual claims about the factory largely check out. It is **not yet
decision-complete**: the claim "All resolved during grilling. No open questions
remain." does not hold. Two material workflow decisions are unresolved in the
body (the `tests:` field timing, and the post-Epic-0 `development.md`
reconciliation), the declared `impact.boundaries` under-covers the proposal's
own Scope, and the `update-charter` mechanism has no delivery vehicle for the
requirements and architecture phases. Fix the four Major findings before
stakeholder acceptance at feature-addition Decision Point 0.2.

## Finding table

| Finding                                                                                                                                                                                                                                                                                                 | Artifact                                                                          | Category   | Severity |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------- | ---------- | -------- |
| `tests:` field workflow has no timing/ownership decision — who writes the pre-existing tests, when relative to planning and `backlog-lint`, and who populates `tests:` if tests arrive after backlog approval. Decide and state it in the proposal. → [PROP-0001](../findings/PROP-0001.md)             | docs/proposals/capture-project-constraints.md § Story template: `tests:` field    | Defect     | Major    |
| Post-Epic-0 `development.md` reconciliation has no owner or mechanism — "happens naturally" assigns work to "the developer who implements the last Epic 0 story", which no story names and no agent can identify. Derive it as a story or assign it explicitly. → [PROP-0002](../findings/PROP-0002.md) | docs/proposals/capture-project-constraints.md § development.md "Two-phase nature" | Defect     | Major    |
| `impact.boundaries` omits artifacts the Scope itself modifies — `implementation-agent.md`, `architecture-agent.md`, `backlog-lint`, `rules.md`, the `validate` skill. Align boundaries with the in-scope list. → [PROP-0003](../findings/PROP-0003.md)                                                  | docs/proposals/capture-project-constraints.md frontmatter `impact.boundaries`     | Defect     | Major    |
| `update-charter` invocation during requirements and architecture has no delivery vehicle — neither `requirements-agent.md` nor `architecture-agent.md` is updated in Scope, so no agent in those phases knows the skill exists. Add the agent updates to Scope. → [PROP-0004](../findings/PROP-0004.md) | docs/proposals/capture-project-constraints.md § Incremental filling / § Scope     | Defect     | Major    |
| Brownfield planning gate is unanchored — "same planning gate applies" but the brownfield playbook has no planning phase; "after architecture deepening review" is ambiguous between Phase 4 (Component-Resolution) and Phase 5 (ATAM). State the gate's trigger point.                                  | docs/proposals/capture-project-constraints.md § Workflow insertion                | Question   | Minor    |
| Epic 0 sequencing relies on an agent instruction ("schedule as wave 1") with no mechanical enforcement; feature stories carry no `deps:` on Epic 0. Either use `deps` or state why the instruction suffices.                                                                                            | docs/proposals/capture-project-constraints.md § Epic 0                            | Suggestion | Minor    |
| Precedent cited incorrectly: `domain-modeling` maintains `docs/CONTEXT.md`, not `docs/arc42/CONTEXT.md`.                                                                                                                                                                                                | docs/proposals/capture-project-constraints.md § Skill: `update-charter`           | Defect     | Minor    |
| `estimated_consumption.min` 120000 implies a 15× multiplier on `normalized_tokens.min` 8000, not the declared 25× (the max matches 25×). Recompute or note the asymmetric range.                                                                                                                        | docs/proposals/capture-project-constraints.md frontmatter `estimate`              | Defect     | Minor    |
| Greenfield insertion anchors on "vision capture", which is not a step in the current greenfield playbook (it starts at Phase 1 Requirements). Name the playbook step to be added or amended.                                                                                                            | docs/proposals/capture-project-constraints.md § Workflow insertion                | Question   | Minor    |
| `update-charter`'s "one commit per update" has no story/bug ID context per [commit-conventions.md](../../factory/rulebooks/conventions/commit-conventions.md) — charter updates during requirements/architecture carry no ST/BUG/SPEC/ATAM ID. State the commit-ID rule for charter updates.            | docs/proposals/capture-project-constraints.md § Skill: `update-charter`           | Question   | Minor    |
| `capture-charter` and the planning-agent both write `backlog/ST-NNNN.md`; the ID allocation rule between them (who owns the next NNNN at planning time) is unstated.                                                                                                                                    | docs/proposals/capture-project-constraints.md § Epic 0                            | Question   | Minor    |

## 1. Template compliance

All required frontmatter fields present and well-formed: `schema_version: 2`,
`title`, `status: open` (valid per template semantics — ready for review, no
implementation commitment), `owner`, `created`/`updated`, `supersedes: null`,
`impact`, `governance`, `estimate`. Estimate satisfies `0 <= min <= max` on all
ranges; `overhead_multiplier: 25` is the top of the template's stated
feature-addition range (15–25×) and therefore admissible. All required body
sections present (Summary, Motivation, Core Principles, Design, Scope, Open
Questions, Completion Criteria, Guiding Rule). The optional "Design Details"
section is omitted without a stated reason — acceptable, its content is folded
into Design. The Open Questions claim does not survive inspection: see
PROP-0001 and PROP-0002.

## 2. Decision-completeness

A reader can plan most of the backlog from the Design section — the three
documents, two skills, one gate, three templates, and the workflow insertions
are concrete. Two genuinely unresolved decisions remain hidden in the body
(PROP-0001, PROP-0002), and the brownfield gate trigger is unanchored (Minor).
The Epic 0 derivation heuristics (exists-vs-missing per decision) are
acceptable: the completeness sweep runs interactively with the stakeholder
present, so heuristic misses are caught in conversation. The charter-amendment
discipline is explicitly deferred and honestly labelled — no finding.

## 3. Internal consistency

Summary, Motivation, Core Principles, Design, Scope, and Completion Criteria
tell one consistent story: scaffold early, fill incrementally, gate before
planning, Epic 0 first. One inconsistency: the frontmatter `impact.boundaries`
does not cover the proposal's own Scope list (PROP-0003). The Completion
Criteria cover every in-scope item except the `development.md` reconciliation
(PROP-0002).

## 4. Consistency with referenced factory artifacts

Verified claims:

- [greenfield-development.md](../../factory/playbooks/greenfield-development.md)
  Step 3.3 is "Confirm Backlog — manual approval required" — the proposal's
  analogy holds.
- [feature-addition.md](../../factory/playbooks/feature-addition.md) Step 0.1
  is proposal intake ("Clarify") — holds.
- [brownfield-onboarding.md](../../factory/playbooks/brownfield-onboarding.md),
  [planning-agent.md](../../factory/agents/planning-agent.md),
  [developer-agent.md](../../factory/agents/developer-agent.md),
  [implementation-agent.md](../../factory/agents/implementation-agent.md),
  [architecture-agent.md](../../factory/agents/architecture-agent.md),
  [create-backlog](../../factory/skills/create-backlog/SKILL.md),
  [story.md](../../factory/rulebooks/templates/story.md), and
  `factory/scripts/backlog-lint` all exist.
- Adding `tests:` to the story template makes sense; the proposal correctly
  includes updating `backlog-lint`, whose schema is closed ("rejects unknown
  fields" per create-backlog).
- The [rules.md](../../factory/rulebooks/rules.md) "Coding" section is a
  placeholder; extending it fits.
- No contradiction with [testing-strategy.md](../../factory/rulebooks/conventions/testing-strategy.md)
  (the proposal routes the pre-existing-tests workflow through the
  developer-agent rather than duplicating lint rules),
  [foundational-principles.md](../../factory/rulebooks/conventions/foundational-principles.md)
  (charter-lint is a deterministic gate; the skills are bounded), or the rule
  against proposals in shipped agents' `inputs:` (the proposal adds
  `docs/charter/*.md`, a shipped artifact, not the proposal itself).
- One factual error: the `domain-modeling` precedent path (Minor, table above).

## 5. Scope & deferrals

The in-scope list is coherent and padding-resistant; each item traces to a
design element and a completion criterion. The deferrals (drift detection,
amendment gate, standalone derivation script, deeper lint checks) are genuinely
deferrable under YAGNI — none is a capability the first release needs, because
the completeness sweep is interactive and git history covers amendment
tracking. No under-scoping found beyond PROP-0004 (a missing in-scope item
rather than a hidden deferral).

## 6. Feasibility

`charter-lint` (structural + `--planning-gate`) is a straightforward
deterministic script — feasible. Epic 0 derivation is interactive with the
stakeholder, so its heuristics are safe. `update-charter` write-ownership
(skill owns the write target) matches the domain-modeling pattern — feasible
once PROP-0004 gives it a vehicle. The workflow insertions work for greenfield
and feature-addition; the brownfield insertion's anchor and gate trigger are
imprecise (Minor). The `tests:` mechanism works only if its timing question is
answered (PROP-0001).

## 7. Completion criteria

All fifteen criteria are checkable statements and map to must-have stories.
Coverage of the in-scope list is complete except the `development.md`
reconciliation (PROP-0002). The end-to-end criterion ("a project running
greenfield reaches implementation with Epic 0 complete before the first
feature story starts") is the right integration check.

## 8. Estimate plausibility

Normalized 8,000–15,000 tokens for three templates, two new skills, one new
script, and edits to three playbooks, four agents, one skill, one template,
one linter, rules.md, and validate is optimistic but not obviously off at
`confidence: medium`; planning can reforecast per feature-addition Step 3.3.
The asymmetric consumption range (min implies 15×, max implies the declared
25×) is a Minor inconsistency, not a template violation.
