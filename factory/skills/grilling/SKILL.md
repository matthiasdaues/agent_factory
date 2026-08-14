---
name: grilling
description: Relentless interview to sharpen a plan or design until reaching shared understanding. Use when the user wants to stress-test a plan, get grilled on their design, or mentions "grill me".
category: utility
source: https://github.com/mattpocock/skills/
---

Interview me relentlessly about every aspect of this plan until we reach shared understanding. Walk down each branch of the design tree, resolving dependencies one-by-one. For each question, give your recommended answer — ask one question at a time, waiting for feedback before continuing.

Use caveman style; the auto-clarity exception covers ambiguity risk in questions and options.

If a question is a *fact* answerable by exploring the codebase, look it up instead of asking. The *decisions* are the user's — put each one to them and wait for their answer.

Do not enact the plan until shared understanding is reached.

## Proposal target

When the target is a feature proposal:

1. Read the proposal, the proposal template, and every referenced boundary.
2. Treat the proposal as the sole interview record. Amend it in place as
   decisions settle; do not create parallel notes or a second design brief.
3. Test Summary, Motivation, Design, Scope, Open Questions, and Completion
   Criteria for enough precision to plan without re-deriving the design.
4. Update `impact`, `governance`, and the dated estimate when answers invalidate
   them. Use `unknown` rather than invented precision.
5. Resolve each Open Question as a decision, explicit assumption, or explicit
   deferral. Leave genuinely unresolved items visible.
6. When decision-complete, set `draft` to `open` and update `updated`.

Never set a proposal to `accepted` or `implemented`; those are stakeholder and
delivery gates outside the interview.
