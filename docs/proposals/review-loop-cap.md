---
schema_version: 2
scope: global
title: Review Loop Cap
status: draft
owner: agent-factory
created: 2026-11-04
updated: 2026-11-04
supersedes:

impact:
  scope: cross_component
  architecture_change: false
  external_contract_change: true
  boundaries:
    - packages/factory/playbooks/feature-addition.md
    - packages/factory/playbooks/greenfield-development.md
    - packages/factory/agents/proposal-review-agent.md
    - packages/factory/agents/spec-review-agent.md
    - packages/factory/agents/architecture-review-agent.md
    - packages/factory/agents/reconciliation-agent.md
    - packages/factory/agents/developer-agent.md
    - packages/factory/rulebooks/conventions/review-loop-discipline.md
    - docs/proposals/finding-classification.md
    - docs/proposals/manual-mode-gates.md

governance:
  assurance: elevated
  risk_domains:
    - reliability

estimate:
  as_of: 2026-11-04
  basis: judgment
  confidence: low
  human_review_hours: unknown
  normalized_tokens: unknown
  estimated_consumption: unknown
---

# Feature Request: Review Loop Cap

## Primer

The primer is written last, by the `write-primer` skill, once the design is settled.

## Summary

Every review loop stops after three passes. If a blocking finding is still open after the third pass, the loop hands the human the open findings and their history, and the human decides how to go on. Which finding blocks is defined in [finding-classification.md](finding-classification.md), not here. Only the human can override that blocking value.

## Motivation

A review loop runs a reviewer on an artifact, sends the open findings back to the author, and runs the reviewer again. It ends only when no finding is open. Only the gate-check loop in [implementation-agent.md § Gate-Check Loop](../../packages/factory/agents/implementation-agent.md#gate-check-loop) has a cap: three iterations, then escalation. The other loops have none, as [review-scrapbook.md](../../poc/workflow/review-scrapbook.md) BAD-04 records.

So late passes spend tokens and time on edge cases that an earlier fix created. A repeat pass must run the full inspection again ([review-loop-discipline.md](../../packages/factory/rulebooks/conventions/review-loop-discipline.md)), so each fix can produce new findings, and the loop has no point where it stops by design. In manual mode, `story-gates` blocks on open findings for the story ([manual-mode-gates.md](manual-mode-gates.md)), so an uncapped code review keeps a story from closing.

## Core Principles

- **A fixed number of passes, then the human.** The loop does not decide on its own that a finding no longer matters.
- **One blocking rule.** Every loop asks [finding-classification.md](finding-classification.md) whether a finding blocks. This proposal adds no second rule.
- **The human overrides, nobody else.** An agent can propose an override. Only the human sets it.

## Design

### The loops

The cap applies to every loop that sends review findings back to an author:

| Loop                     | Reviewer                    | Author                            |
| ------------------------ | --------------------------- | --------------------------------- |
| Proposal review          | `proposal-review-agent`     | the proposal author               |
| Specification review     | `spec-review-agent`         | `requirements-agent`              |
| Architecture review      | `architecture-review-agent` | `architecture-agent`              |
| Reconciliation alignment | `reconciliation-agent`      | the owner of the drifted artifact |
| Reconciliation QA        | `qa-agent`                  | `developer-agent`                 |
| Manual-mode code review  | `code-review-agent`         | `developer-agent`                 |

The gate-check loop keeps its own cap. It checks gate results, not review findings.

### Counting passes

A pass is one complete run of the reviewer on the artifact, as [review-loop-discipline.md](../../packages/factory/rulebooks/conventions/review-loop-discipline.md) defines a repeat pass. The first review is pass 1. The count belongs to one loop on one artifact. So the specification review of `core-artifact-ownership` and its architecture review count separately.

### At the cap

After pass 3, the loop checks whether a blocking finding is still open. If none is open, the loop ends as it does today. If one is open, the loop stops and does not start pass 4. It hands the human:

- each open blocking finding, with its severity and the `**Why this severity:**` sentence;
- for each finding, the pass that filed it, and whether it targets a change that an earlier fix made;
- the review report of every pass.

The human then picks one of three ways for each finding:

1. **Fix it by hand**, or tell the author how to fix it. The loop runs one more pass to check the fix.
2. **Override the blocking value** to `false`, as [finding-classification.md § Human override](finding-classification.md#human-override) defines. The finding stops blocking and keeps its severity.
3. **Grant more passes**, with a number. The loop records the grant and stops again at the new limit.

### Blocking and the override

A finding blocks the loop when the rule in [finding-classification.md § Shared severity scale and blocking rule](finding-classification.md#shared-severity-scale-and-blocking-rule) computes `true` and no human override sets it to `false`. A finding the human sets to `true` blocks, whatever its severity. A `minor` finding goes to the register and never blocks.

The same rule holds for `story-gates` in manual mode. `story-gates` fails on a finding for the story only when that finding blocks. A finding with `blocking_override: false` does not stop the story from closing.

The human can override at any pass, not only at the cap. An agent that thinks a finding should not block says so in its report and leaves the field empty.

## Scope

**In the first release:**

- The cap of three passes and the escalation in every loop of the table above, stated in the playbooks and the agents that run them.
- The three choices of the human at the cap, and the record of a grant of more passes.
- The `story-gates` open-findings check of [manual-mode-gates.md](manual-mode-gates.md) counts only blocking findings.

**Explicitly deferred (do NOT plan stories for these):**

- **The blocking rule, the register, and the override fields.** [finding-classification.md](finding-classification.md) defines them.
- **A check that only the human wrote an override.** An agent with a shell can write any field. [gate-evidence.md](gate-evidence.md) covers this class of problem.
- **The gate-check loop.** It already has a cap.

## Design Details

- **Why three.** The gate-check loop already stops after three iterations. The same number keeps both kinds of loop alike. The number can change once pass counts per loop are measured.
- **No automatic drop.** The loop never sets an override itself at the cap. A finding that an agent would like to drop still goes to the human.

## Open Questions

- **Where does a script read the pass count?** The cap should be enforced by a check, not by the agent's own count. Candidates are the Review passes table of the reviewed artifact or the review reports under `docs/reviews/`. Neither exists for every loop today.
- **Where is a grant of more passes recorded?** It needs one home that the pass-count check reads.

## Completion Criteria

- Each agent and playbook step that runs a loop of the table above states the cap of three passes and the escalation.
- After pass 3 with an open blocking finding, the loop does not start pass 4 and hands the human the open findings, their passes, and the review reports.
- After the human grants two more passes, the loop stops again after pass 5.
- A finding with `blocking_override: false` neither keeps a loop running nor makes `story-gates` fail.
- A `minor` finding neither keeps a loop running nor makes `story-gates` fail.
- `index-lint --check` passes.

# Appendix

## Decisions

| ID     | Date       | Kind     | Decided by  | Decision                                                                                                                        | Raised by                                                            |
| ------ | ---------- | -------- | ----------- | ------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------- |
| DEC-01 | 2026-11-04 | decision | stakeholder | Every review loop stops after three passes, and then the human decides.                                                         | [review-scrapbook.md](../../poc/workflow/review-scrapbook.md) BAD-04 |
| DEC-02 | 2026-11-04 | decision | stakeholder | The loops use the blocking rule of finding-classification.md, so both proposals treat findings the same. No second rule exists. | T-0016 grilling                                                      |
| DEC-03 | 2026-11-04 | decision | stakeholder | Only the human overrides the blocking value of a finding.                                                                       | T-0016 grilling                                                      |
| DEC-04 | 2026-11-04 | decision | stakeholder | A `minor` finding goes into one project register and never blocks. finding-classification.md defines the register.              | T-0016 grilling                                                      |

## Review findings

No review has run yet.

| ID  | Pass | Severity | Check | Status | Finding | Resolution |
| --- | ---- | -------- | ----- | ------ | ------- | ---------- |

## Review passes

No review has run yet.

| Pass | Date | Reviewed commit | Disposition | Failed checks | Summary |
| ---- | ---- | --------------- | ----------- | ------------- | ------- |
