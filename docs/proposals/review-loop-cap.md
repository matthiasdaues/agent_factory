---
schema_version: 2
scope: global
title: Review Loop Cap
status: open
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
    - packages/factory/agents/code-review-agent.md
    - packages/factory/agents/qa-agent.md
    - packages/factory/agents/implementation-agent.md
    - packages/factory/rulebooks/conventions/report-format.md
    - packages/factory/rulebooks/templates/review-report.md
    - packages/factory/rulebooks/templates/proposal.md
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

In Agent Factory, agents check each other's work. A reviewer agent reads an artifact and files findings. The author fixes them, and the reviewer runs again. One complete run of the reviewer is a pass. The repeated cycle of passes is a review loop, and it ends when no finding is left open.

The loop may never reach that end, because every repeat pass inspects the whole artifact again. Each fix can produce new findings. Late passes then spend tokens and time on edge cases that an earlier fix created. Only the loop that checks gate results during implementation has a limit today. It stops after three tries. The review loops have no limit.

Not every finding keeps a loop running. A companion proposal on finding classification defines which findings block. A finding on a defect or a risk blocks when it is rated critical or major. A minor finding goes into a project register and never blocks. This proposal uses that rule and adds no second one.

Each loop belongs to a unit. Most loops review the feature branch of a proposal, so their unit is the proposal. A code review that runs on one story branch belongs to the story.

This proposal stops every review loop after three passes, and then the human decides. Take the specification review for the proposal on core artifact ownership. All its passes go into one review document, which starts with a table of passes. Suppose pass 3 still leaves one blocking finding open. The loop does not start pass 4. Instead, it hands the human the open finding and the review document. The finding carries its severity, the pass that filed it, and whether it targets a change that an earlier fix made.

The human then has three choices for each open finding. The human can fix it by hand or tell the author how, and the check pass that follows counts as one granted pass. The human can override the blocking value, so the finding keeps its severity but stops blocking. Or the human can grant more passes. Here the human grants two, which adds a row to the table. The limit is now five, so passes 4 and 5 may run and pass 6 may not.

Only the human overrides or grants. An agent that thinks a finding should not block says so in its report, so the loop never drops a finding on its own. A new check script reads the review document and enforces the limit in two places. The agent that starts the reviewer runs it before each pass, so no tokens go to a pass above the limit. A pre-commit hook runs it again on every staged review document, so a pass that slipped through cannot be recorded.

Each review document keeps the whole loop of its unit in one file. The limit of three matches the loop that checks gate results and can change once pass counts per loop are measured. The proposal has no open questions.

## Summary

Every review loop stops after three passes (DEC-01). If a blocking finding is still open after the third pass, the loop hands the human the open findings and their history. The human then decides how to go on. [finding-classification.md](finding-classification.md) defines which finding blocks, not this proposal.

## Motivation

A review loop runs a reviewer on an artifact, sends the open findings back to the author, and runs the reviewer again. It ends only when no finding is open. Only the gate-check loop in [implementation-agent.md § Gate-Check Loop](../../packages/factory/agents/implementation-agent.md#gate-check-loop) has a cap. It stops after three iterations and escalates. The other loops have no cap, as entry BAD-04 of [review-scrapbook.md](../../poc/workflow/review-scrapbook.md) records.

A repeat pass must run the full inspection again ([review-loop-discipline.md](../../packages/factory/rulebooks/conventions/review-loop-discipline.md)). So each fix can produce new findings, and the loop has no point where it stops by design. Late passes then spend tokens and time on edge cases that an earlier fix created. In manual mode, `story-gates` blocks on open findings for the story ([manual-mode-gates.md](manual-mode-gates.md)), so an uncapped code review keeps a story from closing.

## Core Principles

- **A fixed number of passes, then the human.** The loop never drops a finding on its own.
- **One blocking rule.** Every loop asks [finding-classification.md](finding-classification.md) whether a finding blocks. This proposal adds no second rule (DEC-02).
- **The human overrides, nobody else.** An agent can propose an override, but only the human sets it (DEC-03).

## Design

### The loops

The cap applies to every loop that sends review findings back to an author. Each loop belongs to one unit: the proposal whose feature branch it reviews, or the story it reviews. The unit names the review document.

| Loop                       | Reviewer                    | Author                            | Unit     | Review document                                     |
| -------------------------- | --------------------------- | --------------------------------- | -------- | --------------------------------------------------- |
| Proposal review            | `proposal-review-agent`     | the proposal author               | proposal | the `## Review passes` table of the proposal itself |
| Specification review       | `spec-review-agent`         | `requirements-agent`              | proposal | `docs/reviews/<proposal>/spec-review.md`            |
| Architecture review        | `architecture-review-agent` | `architecture-agent`              | proposal | `docs/reviews/<proposal>/atam-review.md`            |
| Automated-mode code review | `code-review-agent`         | `implementation-agent`            | proposal | `docs/reviews/<proposal>/code-review.md`            |
| Reconciliation alignment   | `reconciliation-agent`      | the owner of the drifted artifact | proposal | `docs/reviews/<proposal>/reconciliation.md`         |
| Reconciliation QA          | `qa-agent`                  | `developer-agent`                 | proposal | `docs/reviews/<proposal>/qa.md`                     |
| Manual-mode code review    | `code-review-agent`         | `developer-agent`                 | story    | `docs/reviews/<story-id>/code-review.md`            |

The automated-mode code review runs once on the feature branch, after the dispatch has merged its stories ([feature-addition.md § Step 4.2](../../packages/factory/playbooks/feature-addition.md#step-42--code-review-separate-session)). Reconciliation also runs once per feature branch ([reconciliation-agent.md](../../packages/factory/agents/reconciliation-agent.md)). So both belong to the proposal. The manual-mode code review runs on each story branch, so it belongs to the story (DEC-06).

The gate-check loop keeps its own cap, because it checks gate results, not review findings.

### Which finding blocks

A finding blocks when the rule in [finding-classification.md § Shared severity scale and blocking rule](finding-classification.md#shared-severity-scale-and-blocking-rule) computes `true` and no human override sets it to `false`. A `minor` finding goes to the register. It never blocks, and no override changes that (DEC-09).

`story-gates` in manual mode uses the same rule. It fails on a finding for the story only when that finding blocks. So a finding with `blocking_override: false` does not stop the story from closing.

### The review document

Each loop has one review document for its unit (DEC-05). Take the specification review of `core-artifact-ownership`. All its passes live in `docs/reviews/core-artifact-ownership/spec-review.md`, so a reader finds the whole loop in one file, in order. A later feature that reviews the same chapters gets its own document and starts at pass 1. The document starts with a passes table.

### Counting passes

Each pass adds one row to the passes table and one section below it. A pass is one complete run of the reviewer, as [review-loop-discipline.md](../../packages/factory/rulebooks/conventions/review-loop-discipline.md) defines a repeat pass. The first review is pass 1. A `grant` row records the extra passes that the human granted at the cap, as [At the cap](#at-the-cap) describes.

| Row | Kind    | Date       | Reviewed commit | Number | By       | Summary                       |
| --- | ------- | ---------- | --------------- | ------ | -------- | ----------------------------- |
| 1   | `pass`  | 2026-11-05 | `<40-char SHA>` |        | reviewer | 2 blocking findings           |
| 2   | `pass`  | 2026-11-05 | `<40-char SHA>` |        | reviewer | 1 blocking finding            |
| 3   | `pass`  | 2026-11-06 | `<40-char SHA>` |        | reviewer | 1 blocking finding            |
| 4   | `grant` | 2026-11-06 |                 | 2      | human    | two more passes for SPEC-0412 |

The `## Review passes` table of the proposal template gains the `Kind` and `Number` columns. So the proposal review keeps its passes in the proposal and follows the same rule (DEC-10). The script `review-pass-check` ([Enforcing the cap](#enforcing-the-cap)) reads both tables by column name.

The limit is 3 plus the numbers of all `grant` rows. The script counts the `pass` rows and computes the limit from the same table (DEC-07). In the example above, the limit is 5, so passes 4 and 5 may run and pass 6 may not.

### At the cap

After the last pass the limit allows, the loop checks whether a blocking finding is still open. If none is open, the loop ends. If one is open, the loop stops and does not start another pass. It hands the human:

- each open blocking finding, with its severity and the `**Why this severity:**` sentence;
- for each finding, the pass that filed it, and whether it targets a change that an earlier fix made;
- the review document, which holds every pass.

The human then picks one of three choices for each finding:

1. **Fix it by hand**, or tell the author how to fix it. A check pass follows, and it counts like any other pass. So this choice writes a `grant` row with the number 1 and the human's name (DEC-11).
2. **Override the blocking value** to `false`, as [finding-classification.md § Human override](finding-classification.md#human-override) defines. The finding stops blocking and keeps its severity.
3. **Grant more passes**, with a number. The grant becomes a `grant` row in the passes table, and the loop stops again at the new limit.

The human can override at any pass, not only at the cap. The loop never sets an override itself. An agent that thinks a finding should not block says so in its report and leaves `blocking_override` empty.

### Enforcing the cap

A new script, `packages/factory/scripts/review-pass-check`, reads one review document. It exits non-zero when the next pass would exceed the limit. Its message lists the open blocking findings and says that the human decides how the loop goes on. Two places run it (DEC-08):

1. **The agent that starts the reviewer** runs it before each pass. If the check fails, the agent does not start the reviewer and escalates to the human. So in the normal case no pass runs above the limit, and no tokens are spent on it.
2. **A pre-commit hook** of the same name runs it on every staged review document under `docs/reviews/` and on every staged proposal under `docs/proposals/` (DEC-10). A commit that adds a `pass` row above the limit fails. So a pass that the starting agent let through by mistake cannot be recorded.

## Scope

**In the first release:**

- The cap of three passes and the escalation in every loop of the table in [The loops](#the-loops), stated in the playbooks and in the agents that run them.
- The three choices of the human at the cap, and the `grant` row.
- One review document per loop and unit, with the passes table, in `report-format.md` and the review-report template. Every reviewer in the table writes it.
- The `Kind` and `Number` columns in the `## Review passes` table of the proposal template.
- The script `review-pass-check`, the check before each pass in every agent that starts a reviewer, and the `review-pass-check` pre-commit hook.
- The `story-gates` open-findings check of [manual-mode-gates.md](manual-mode-gates.md) counts only blocking findings.

**Explicitly deferred (do NOT plan stories for these):**

- **The blocking rule, the register, and the override fields.** [finding-classification.md](finding-classification.md) defines them.
- **A check that only the human wrote an override or a `grant` row.** An agent with a shell can write any field. [gate-evidence.md](gate-evidence.md) covers this class of problem.
- **The gate-check loop.** It already has a cap.

## Design Details

- **Why three.** The gate-check loop already stops after three iterations, and the same number keeps both kinds of loop alike. The number can change once pass counts per loop are measured.

## Open Questions

None.

## Completion Criteria

- Each agent and playbook step that runs a loop of the table in [The loops](#the-loops) states the cap of three passes and the escalation.
- After pass 3 with an open blocking finding, the loop does not start pass 4. It hands the human the open findings, the passes that filed them, and the review document.
- After the human grants two more passes, the loop stops again after pass 5.
- `review-pass-check` exits non-zero on a review document whose `pass` rows exceed 3 plus its `grant` numbers, and exits zero otherwise.
- A commit that adds a fourth `pass` row to a review document without a `grant` row fails in the `review-pass-check` hook.
- Every loop in the table in [The loops](#the-loops) writes its passes into the one review document of its unit.
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
| DEC-05 | 2026-11-04 | decision | stakeholder | Each loop has one review document per unit and review type. Each pass adds a row and a section; no report per pass.             | open question on the pass count                                      |
| DEC-06 | 2026-11-04 | decision | stakeholder | The unit is the proposal for loops on a feature branch and the story for the manual-mode code review.                           | open question on the pass count                                      |
| DEC-07 | 2026-11-04 | decision | stakeholder | A grant of more passes is a `grant` row in the passes table of the same document, so count and limit come from one file.        | open question on the grant record                                    |
| DEC-08 | 2026-11-04 | decision | stakeholder | The agent that starts a reviewer runs `review-pass-check` first, and a pre-commit hook runs it again on the review document.    | open question on who runs the check                                  |
| DEC-09 | 2026-11-04 | decision | stakeholder | A `minor` finding never blocks. The human override only sets a blocking finding to `false`.                                     | lector structural pass, item 13                                      |
| DEC-10 | 2026-11-04 | decision | stakeholder | The proposal template's `## Review passes` table gains `Kind` and `Number`; the hook also watches `docs/proposals/`.            | lector structural pass, item 14                                      |
| DEC-11 | 2026-11-04 | decision | stakeholder | The check pass after a fix counts. Choosing "fix it" at the cap writes a `grant` row of 1.                                      | lector structural pass, item 15                                      |

## Review findings

No review has run yet.

| ID  | Pass | Severity | Check | Status | Finding | Resolution |
| --- | ---- | -------- | ----- | ------ | ------- | ---------- |

## Review passes

No review has run yet.

| Pass | Date | Reviewed commit | Disposition | Failed checks | Summary |
| ---- | ---- | --------------- | ----------- | ------------- | ------- |
