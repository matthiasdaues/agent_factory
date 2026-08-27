---
name: draft-proposal
description: >-
  Crystallize an explored idea into a decision-complete feature proposal.
  Called by chat-agent (or directly) once the shape of a feature is clear.
  Runs in the current session with the stakeholder present.
category: requirements
version: 0.2.0
disable-model-invocation: false
---

# Draft Proposal

Crystallization skill for `docs/proposals/<name>.md`. Takes an idea that
already has shape — from a chat-agent conversation, a grilling session, or
the stakeholder's own notes — and pours it into the proposal template.

This skill does not explore. If the idea is still forming, stay in the
conversation that is forming it. Come here when you are ready to write
things down.

**Runs in the orchestrating session, never as a spawned subagent.** The
stakeholder must be present to confirm what gets written.

Write for a colleague who is not yet deeply involved in the project. Use
plain, clear, accessible language, even when making a sharp observation.

## Procedure

1. **Create** `docs/proposals/<name>.md` from the
   [proposal template](../../rulebooks/templates/proposal.md). Pick a name
   that a teammate would recognize without context — the slug, not a ticket
   number.

2. **Fill from conversation.** Walk the template not as an interview but as
   a transcription — most sections already have answers from the preceding
   conversation. Write them down. Where the conversation covered something
   the template does not ask for, put it in Design Details. Where the
   template asks for something the conversation did not cover, surface it
   now as a question.

3. **Frontmatter.** Fill `impact`, `governance`, and `estimate` from what
   the conversation revealed. Use `unknown` rather than inventing
   precision. Set `status: draft`.

4. **Sharpen.** Invoke `grilling` with the proposal as target to
   pressure-test the written version. The grilling skill amends the
   proposal in place as decisions settle.

5. **Gate.** Before setting `status: open`:

   - Every section is filled or carries an explicit "does not apply because
     …" note. No blank sections, no `TODO`.
   - Completion Criteria are statements a reviewer could check without
     asking the author what they meant.
   - Scope lists are padding-resistant: "In" items trace to Completion
     Criteria, "Deferred" items say why they are deferred.
   - Open Questions are genuine — each must become a story acceptance
     criterion, a recorded assumption, or an explicit deferral. Padding
     gets removed, not resolved.

6. **Transition.** Set `status: open`, update `updated:`, commit.

## Validation

Run `factory/scripts/mdformat --number docs/proposals/<name>.md` before
committing.

No dedicated lint script exists for proposals yet. The gate in Step 5 is
manual.

## Completion

A single file at `docs/proposals/<name>.md` with `status: open`, every
section filled or explicitly inapplicable, and `mdformat` clean. Ready for
the proposal review agent.
