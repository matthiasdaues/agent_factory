# Handoff: Test-Design Layer Redistribution

**Date:** 2026-09-08
**Branch:** dev (uncommitted)
**Session focus:** Proposal authoring and adversarial review for redistributing test-design responsibilities across factory agents.

## Context

A colleague challenged the value of writing detailed test scenarios at epic level before code exists. The session explored the argument, grilled the design space, and produced an open proposal with two rounds of adversarial review.

## Key Decisions Made

1. **Detailed test design moves from planning to implementation.** The developer agent authors tests with code in hand, not the planning agent speculatively.
2. **Testability probes stay at planning level.** Lightweight assessment (observable outcomes, instrumentation boundaries, red flags) plus contract ownership resolution — the one concern that needs the full backlog view.
3. **Fork into two skills**, not a mode parameter: `testability-probe` (planning) and narrowed `test-design` (implementation). Almost no shared procedure.
4. **`.feature`-governed stories skip the post-TDD test-design pass.** The `.feature` file is the test design.
5. **No handwritten coverage assessment artifact.** Tests are the evidence; QA cross-references mechanically.
6. **`test-design-pass` field** (`done` | `skipped-feature-governed`) gives QA an observable signal.
7. **Traceability lifecycle:** developer records `tests:` at commit time; reconciliation agent audits and backfills — mirrors existing `@`-reference pattern.
8. **`test-design-verify` gate adapts** (not deprecated): verifies `tests:` + `test-design-pass` for new-model stories, keeps old validation for old-model stories.

## Artifacts

| Artifact                            | Path                                                 | Status                                                                                            |
| ----------------------------------- | ---------------------------------------------------- | ------------------------------------------------------------------------------------------------- |
| Main proposal                       | `docs/proposals/test-design-layer-redistribution.md` | open, uncommitted                                                                                 |
| Subsession phases proposal (parked) | `docs/proposals/planning-agent-subsession-phases.md` | draft, uncommitted, parked — separate cost-optimization idea explored and shelved in this session |

## What Was Done

- Grilled the problem space: test-last vs TDD layers, QA split vs widen, developer-agent as test author.
- Drafted initial proposal, ran consultative review (proposal-review-agent). Key finding: ownership resolution breaks at story level — resolved by keeping it in the planning-level probe.
- Sent three open questions back to reviewer: skill fork approach, `.feature` interaction, coverage enforcement. All resolved.
- Investigated traceability lifecycle (Explore agent): `@`-references in `.feature` files are implementation-code only (derive-feature → developer reads → reconciliation backfills). Test references live in story files only. No test refs in `.feature` files.
- Ran adversarial review. 5/8 checks failed (structural completeness). All 7 findings fixed: scope section, completion criteria (17 testable), story-level procedure (8-step), missing boundaries (6 added), gate adaptation, observable QA signal, scope enum.

## What Remains

1. **Two open questions in the proposal:**

   - Probe ownership vs story slicing: does the probe re-run after phase 3 slicing, or is epic-level ownership stable enough?
   - Probe sequencing: part of `create-backlog` sequence (replacing phase 2.5) or standalone?

2. **Commit the proposals to dev.** Both proposals are uncommitted.

3. **If accepted → planning and implementation** via feature-addition playbook. The proposal has 17 completion criteria and 13 boundary artifacts.

## Suggested Skills

- `grilling` — if the open questions need further stress-testing before acceptance.
- `draft-proposal` — if the open questions resolve into design decisions that need a proposal amendment.
- `adversarial-review` or `proposal-review-agent` — for a final pass before setting status to `accepted`.
- `create-backlog` sequence — once accepted, to plan implementation stories.
- `spec-feedback` — if the proposal's design changes conflict with existing spec artifacts.
