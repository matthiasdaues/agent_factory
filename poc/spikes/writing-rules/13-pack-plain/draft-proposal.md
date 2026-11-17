---
name: draft-proposal
description: >-
  Crystallize an explored idea into a decision-complete feature proposal.
  Called by VIRGIL (or directly) once the shape of a feature is clear.
  Runs in the current session with the stakeholder present.
category: requirements
version: 0.4.0
---

# Draft Proposal

This skill writes `docs/proposals/<name>.md`. It takes an idea that already
has a clear shape, from a VIRGIL conversation, a grilling session, or the
stakeholder's own notes, and writes it into the proposal template.

This skill does not explore ideas. If the idea is still taking shape, stay in
the conversation where it is taking shape. Come here when you are ready to
write it down.

**Runs in the session that coordinates the work, never as a spawned
subagent.** The stakeholder must be present to confirm what is written.

Read [factory-voice.md](../../rulebooks/conventions/factory-voice.md) now and follow every rule in it while you write. No text goes to the terminal or into a file until it passes all four checks before sending and the last read-through.

## Procedure

1. **Create** `docs/proposals/<name>.md` from the
   [proposal template](../../rulebooks/templates/proposal.md). Pick a name
   that a teammate would recognize without context: the slug, not a ticket
   number.

2. **Fill it from the conversation.** Go through the template as a writer of
   minutes, not as an interviewer. Most sections already have answers from
   the conversation so far. Write them down. Where the conversation covered
   something the template does not ask for, put it in Design Details. Where
   the template asks for something the conversation did not cover, ask about
   it now.

3. **Frontmatter.** Fill `impact`, `governance`, and `estimate` from what
   the conversation showed. Write `unknown` instead of making up precise
   numbers. Set `status: draft`.

   Keep the two parts of the template apart. The proposal states the design
   in the present tense. Each decision made in the conversation gets a row
   in the Appendix Decisions table, not a date or stamp in the text.

4. **Sharpen.** Run `grilling` on the proposal to test the written version
   with hard questions. The grilling skill edits the proposal directly as
   decisions are settled.

5. **Primer.** Start a fresh subagent with the
   [write-primer](../write-primer/SKILL.md) skill and the proposal path. It
   returns the primer; write it into the `## Primer` section below the
   title, and replace any earlier one. The design is settled after the
   grilling, and the lector-agent changes wording, not meaning, so the
   primer comes before the edit of the text.

6. **Text edit.** Start the `lector-agent` in a fresh session for the whole
   proposal, primer included: first the structural pass, whose plan the
   stakeholder approves, then the sentence pass. The structural pass reads
   the primer next to the Summary, so it can catch a Summary that repeats
   the primer. Authors do not see the faults in their own text, and the
   review agents do not check the writing. Run it again after each round of
   review fixes, before the proposal is accepted.

7. **Check.** Before you set `status: open`:

   - Every section is filled or has an explicit "does not apply because
     …" note. No blank sections, no `TODO`.
   - A reviewer could check each Completion Criterion without asking the
     author what it means.
   - The Scope lists have no filler: each "In" item traces to a Completion
     Criterion, and each "Deferred" item says why it is deferred.
   - Each Open Question is real: it must become a story acceptance
     criterion, a recorded assumption, or an explicit deferral. Remove
     filler questions; do not answer them.
   - Open Questions contains only open items. Every decision and assumption
     has a row in the Appendix Decisions table, and the proposal part
     contains no dates or "Decision:" stamps.
   - The Primer section describes the proposal as it is now. If this check
     changed the design, run steps 5 and 6 again. Write the primer after
     the last change to the design.

8. **Open.** Set `status: open`, update `updated:`, and commit.

## Validation

Run `.agent-factory/factory/scripts/mdformat --number docs/proposals/<name>.md` before
you commit.

No lint script for proposals exists yet. You do the check in Step 7 by
hand.

## Writing quality

Write every section by the rules in factory-voice.md while you judge whether the proposal is ready. This check judges readiness only. The proposal lifecycle decides who may change its status.

## Completion

One file at `docs/proposals/<name>.md` with `status: open`, every section
filled or marked as not applicable, and no `mdformat` changes left. It is
ready for the proposal review agent.
