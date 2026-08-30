---
title: Proposal Review — Project Charter (Repeat Pass v2)
date: 2026-08-18
reviewer: proposal-review (independent session, author/reviewer separation; fresh session, did not write the document)
target: "docs/proposals/implemented/capture-project-constraints.md (status open, schema_version 2, untracked in git)"
repeat-pass-of: docs/reviews/proposal-review-2026-08-18.md
---

# Proposal Review — Project Charter (Repeat Pass v2)

Repeat pass over [capture-project-constraints.md](../proposals/implemented/capture-project-constraints.md)
per [review-loop-discipline.md](../../factory/rulebooks/conventions/review-loop-discipline.md):
every prior finding verified individually (Part 1), then the full eight-check
inspection re-run fresh against the current text (Part 2). First pass:
[proposal-review-2026-08-18.md](proposal-review-2026-08-18.md).

## Verdict

**Pass.** All four Major findings ([PROP-0001](../findings/PROP-0001.md) through
[PROP-0004](../findings/PROP-0004.md)) are verified fixed and set to `resolved`;
all seven first-pass Minor findings are verified fixed. The fresh re-inspection
found no regressions, no new Critical or Major findings, and three new Minor
findings (report-only, fixes optional). The proposal is decision-complete, its
"No open questions remain" claim now holds, and it is ready for stakeholder
acceptance at feature-addition Decision Point 0.2.

## Part 1 — Prior-findings verification

| Finding                                                               | Result   | Evidence in current text                                                                                                                                                                                                                                                                                                                                      |
| --------------------------------------------------------------------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [PROP-0001](../findings/PROP-0001.md) — `tests:` timing/ownership     | resolved | New "Timing and ownership" paragraph: humans write the tests before planning begins when house-rules mandate manual test-first; the planning-agent populates `tests:` at story creation; the orchestrating session amends stories after backlog approval, before implementation dispatch. Who, when, and who-populates are all stated.                        |
| [PROP-0002](../findings/PROP-0002.md) — development.md reconciliation | resolved | "Two-phase nature" now derives an explicit Epic 0 story "Update development.md with actual commands and paths", depending on all other Epic 0 stories, last in Epic 0; feature stories carry `deps:` on it (§ Epic 0); Completion Criterion 4 names it.                                                                                                       |
| [PROP-0003](../findings/PROP-0003.md) — impact.boundaries             | resolved | `impact.boundaries` now lists all 13 modified artifacts: three playbooks, five agents (planning, developer, implementation, architecture, requirements), create-backlog, validate, story template, rules.md, backlog-lint. Creation targets were optional per the original fix direction.                                                                     |
| [PROP-0004](../findings/PROP-0004.md) — update-charter vehicle        | resolved | Scope now includes "requirements-agent.md updated: `update-charter` added to `skills:`" and the same for architecture-agent.md; both appear in `impact.boundaries`.                                                                                                                                                                                           |
| Minor 1 — brownfield planning-gate anchor                             | resolved | Body now anchors `--init --scan` "after the Phase 5 ATAM architecture review passes" and the planning gate "before any specification or planning work that follows onboarding". Phase 5 Step 5.1 is the ATAM review in [brownfield-onboarding.md](../../factory/playbooks/brownfield-onboarding.md). (Residual wording mismatch in Scope: new Minor 2 below.) |
| Minor 2 — Epic 0 sequencing enforcement                               | resolved | Feature stories now carry `deps:` on the final Epic 0 story, enforced mechanically by the implementation-agent's existing dependency resolution (verified: `deps:` drives readiness in [implementation-agent.md](../../factory/agents/implementation-agent.md) and referential integrity/acyclicity in `factory/scripts/backlog-lint`).                       |
| Minor 3 — domain-modeling precedent path                              | resolved | Now reads "same pattern as `domain-modeling` maintains `docs/CONTEXT.md`" — correct path.                                                                                                                                                                                                                                                                     |
| Minor 4 — estimated_consumption asymmetric multiplier                 | resolved | `estimated_consumption.min` is now 200000 = 25 × 8000; max 375000 = 25 × 15000. Symmetric at the declared multiplier.                                                                                                                                                                                                                                         |
| Minor 5 — greenfield "vision capture" anchor                          | resolved | Workflow insertion now names the playbook step: "New Step 1.0 (before current Step 1.1)". Current Step 1.1 is "Run Requirements Agent" in [greenfield-development.md](../../factory/playbooks/greenfield-development.md); the playbook starts at Phase 1, so a new Step 1.0 is a well-formed insertion.                                                       |
| Minor 6 — update-charter commit-ID rule                               | resolved | Commit message format now stated: `docs: update charter <document> — <section> (<ID>)` with `<ID>` the triggering story/finding/phase context (SPEC-0003, ATAM-0001), and an explicit no-ID fallback for initial vision capture. Consistent with [commit-conventions.md](../../factory/rulebooks/conventions/commit-conventions.md).                          |
| Minor 7 — ST-NNNN ID ownership                                        | resolved | Rule now stated: capture-charter takes the lowest available ST numbers (from ST-0001); the planning-agent runs after the completeness sweep and allocates subsequent numbers by reading the existing backlog. Ownership is unambiguous.                                                                                                                       |

Resolution summary: 4 of 4 Major verified fixed; 7 of 7 Minor verified fixed.
No prior finding remains open.

## Part 2 — Fresh full re-inspection (all eight checks, current text)

### 1. Template compliance

All required frontmatter fields present and well-formed against the
[proposal template](../../factory/rulebooks/templates/proposal.md):
`schema_version: 2`, `title`, `status: open`, `owner`, `created`/`updated`,
`supersedes: null`, `impact`, `governance`, `estimate`. Estimate satisfies
`0 <= min <= max` on all ranges; consumption now applies the declared 25×
multiplier symmetrically (25 is the top of the template's 15–25×
feature-addition range, admissible). All required body sections present;
"Design Details" remains folded into Design — acceptable, as before.

### 2. Decision-completeness

The "No open questions remain" claim now holds. The four previously unresolved
decisions (tests timing/ownership, development.md reconciliation, boundary
coverage, update-charter vehicle) all carry explicit answers in the body. The
`tests:` timing answer is defensible: in greenfield, planning follows an
approved specification, so manually written tests can exist before planning
against spec scenarios, and the planning-agent maps them to acceptance criteria.
No hidden unresolved decision found.

### 3. Internal consistency

The mitigation edits introduced no new contradictions in the main arc: the
`deps:` mechanism composes correctly (every feature story depends on the final
Epic 0 story; that story depends on all other Epic 0 stories; acyclic).
Two wording-level inconsistencies found — both Minor, in the table below:
the greenfield insertion table attributes wave-1 scheduling to the
planning-agent while the rest of the document assigns it to the
implementation-agent, and the Scope line keeps the pre-fix wording for the
brownfield anchor that the body already corrected.

### 4. Consistency with referenced factory artifacts

Re-verified against current text:

- [greenfield-development.md](../../factory/playbooks/greenfield-development.md)
  Step 3.3 is "Confirm Backlog — manual approval required" — the approval
  analogy holds; Step 1.1 is "Run Requirements Agent", so "New Step 1.0"
  inserts cleanly.
- [feature-addition.md](../../factory/playbooks/feature-addition.md) Step 0.1
  is "Clarify" (proposal intake) — holds.
- [brownfield-onboarding.md](../../factory/playbooks/brownfield-onboarding.md)
  Phase 5 Step 5.1 is the ATAM review — the new anchor holds.
- [planning-agent.md](../../factory/agents/planning-agent.md),
  [developer-agent.md](../../factory/agents/developer-agent.md),
  [implementation-agent.md](../../factory/agents/implementation-agent.md),
  [architecture-agent.md](../../factory/agents/architecture-agent.md),
  [requirements-agent.md](../../factory/agents/requirements-agent.md),
  [create-backlog](../../factory/skills/create-backlog/SKILL.md),
  [story.md](../../factory/rulebooks/templates/story.md), and
  `factory/scripts/backlog-lint` all exist and behave as the proposal assumes:
  the story frontmatter schema is closed (so the paired `backlog-lint` update
  for `tests:` is correctly in Scope), `deps:` is the story template's blocking
  mechanism, and the implementation-agent resolves the dependency graph for
  wave readiness.
- [rules.md](../../factory/rulebooks/rules.md) Coding section is still a
  placeholder; extending it fits.
- No contradiction with [testing-strategy.md](../../factory/rulebooks/conventions/testing-strategy.md),
  [foundational-principles.md](../../factory/rulebooks/conventions/foundational-principles.md),
  [cross-reference-format.md](../../factory/rulebooks/conventions/cross-reference-format.md)
  (bare code-span artifact references match existing proposal house style),
  [commit-conventions.md](../../factory/rulebooks/conventions/commit-conventions.md)
  (the update-charter commit format follows `<type>: <description> (<ID>)`),
  or the rule against proposals in shipped agents' `inputs:` (charter paths
  are shipped artifacts).
- One embellishment, not a defect: the claim that the planning-agent allocates
  the next ST number "same as it does today when stories already exist" is not
  spelled out in [create-backlog](../../factory/skills/create-backlog/SKILL.md),
  though feature-addition planning re-runs over existing backlogs make the
  behavior necessary in practice. The stated allocation rule itself is sound.

### 5. Scope & deferrals coherence

The in-scope list is complete against the Design: every design element (three
documents, three templates, two skills, one script, story-template and
backlog-lint changes, five agent updates, three playbook insertions, rules.md,
validate) has a Scope item. Deferrals are unchanged and still honestly
deferrable under YAGNI. One mismatch: the Design promises pre-commit
integration for `charter-lint` ("Integrated into the `validate` skill and
pre-commit") but neither Scope nor Completion Criteria mention it — new Minor 3.

### 6. Feasibility

`charter-lint` (structural + `--planning-gate`) remains a straightforward
deterministic script. Epic 0 derivation is interactive with the stakeholder;
its exists-vs-missing heuristics are safe in conversation. `update-charter` now
has a delivery vehicle in both phases that need it. The workflow insertions
are concrete (named new step, named gate point, named intake question). The
`deps:`-based Epic 0 enforcement reuses the implementation-agent's existing
readiness resolution rather than adding a new mechanism — no feasibility risk.

### 7. Completion criteria checkability and coverage

All fifteen criteria are checkable. Coverage of the in-scope list is complete,
now including the development.md reconciliation (Criterion 4). The end-to-end
criterion (greenfield reaches implementation with Epic 0 complete before the
first feature story) remains the right integration check. Gap: the pre-commit
integration claimed in Design has no criterion (folded into new Minor 3).

### 8. Estimate plausibility

Normalized 8,000–15,000 tokens for three new templates, two new skills, one new
script, and edits to three playbooks, five agents, one skill, one template, one
linter, rules.md, and validate remains optimistic but defensible at
`confidence: medium`; planning can reforecast at feature-addition Step 3.3.
Consumption is now symmetric at the declared 25×.

## New findings (this pass)

All Minor; per [finding-format.md](../../factory/rulebooks/conventions/finding-format.md)
they stay in this report — no new finding files filed. No Critical or Major.

| Finding                                                                                                                                                                                                                                                                                                                                                                                                    | Artifact                                                                       | Category | Severity |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------ | -------- | -------- |
| Greenfield insertion table row "Planning" says the planning-agent "schedules Epic 0 as wave 1", but Downstream consumers, Scope ("implementation-agent.md updated: … schedule Epic 0 as wave 1"), and Completion Criterion 9 all assign wave scheduling to the implementation-agent. Reword the Planning row to planning's actual lever — e.g. "marks feature stories' `deps:` on the final Epic 0 story". | docs/proposals/implemented/capture-project-constraints.md § Workflow insertion | Defect   | Minor    |
| Scope line says brownfield `--init --scan` runs "after architecture deepening review", while the body anchors it "after the Phase 5 ATAM architecture review passes"; [brownfield-onboarding.md](../../factory/playbooks/brownfield-onboarding.md) lists "Architecture deepening" and "Review" as distinct steps. Align the Scope wording with the body's Phase 5 ATAM anchor.                             | docs/proposals/implemented/capture-project-constraints.md § Scope              | Defect   | Minor    |
| Design says `charter-lint` is "Integrated into the `validate` skill and pre-commit", but Scope lists only the `validate` skill and no Completion Criterion covers pre-commit. Either add pre-commit integration to Scope with a matching criterion, or drop "and pre-commit" from the Design sentence.                                                                                                     | docs/proposals/implemented/capture-project-constraints.md § Deterministic gate | Defect   | Minor    |

## Disposition

Pass. The four Major findings and seven Minor findings from the first pass are
verified fixed; the fresh inspection surfaces three new Minor findings whose
fixes are optional for acceptance. The proposal is ready for stakeholder
acceptance at feature-addition Decision Point 0.2; the author may fold the
three Minor wording fixes in before or at acceptance.
