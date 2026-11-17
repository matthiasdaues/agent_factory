# Writing rules, round 2

"The world is full of bullshit. Let us not add to it."

A text fails its reader in four ways. The reader cannot tell what it points at. The reader lacks what they need to act. The reader cannot trust it. Or its tone gets in the way. The rules follow that order, because the user's objections fall in that order of frequency.

Each rule names the objections it would have caught (OBJ-nn, in `05-objections.md`). A rule with no objection behind it says why it stays.

## The reader can see what you mean

**1. Every reference shows its target.** "Line 8", "above", "the proposal", "that finding", and "the line" point at something the reader cannot see. Name the thing in full, or quote it where you point at it.
*Check:* for each "this", "that", "the X", "above", or line number, the reader can say which one without scrolling or remembering. *(OBJ-01, 02, 06, 11)*

**2. Use the reader's words; do not coin new ones.** Call a thing by the name the reader already uses. Introduce a new term only when the thing has no name. Then define it in one plain sentence where it first appears, and keep that term.
*Check:* each term that is neither a common term of the trade nor defined earlier in the text has a definition at its first use. *(OBJ-03, 08, 15, 16, 31)*

## The reader can act

**3. Give the case, not only the conclusion.** A note, a table cell, or an observation that the reader must act on is a full sentence, and it names its subject. An argument comes with one concrete case from the project.
*Check:* a reader who saw nothing before this text can say what it is about and why it matters. *(OBJ-04, 18, 20, 30)*

**4. A question carries what the decision needs.** It names the thing to decide, gives one real case, gives each option's outcome for that case, and recommends one option with its reason.
*Check:* the reader can answer without asking back. *(OBJ-10, 17)*

**5. Lead with the point.** The first sentence of a message or a section says what happened or what is needed. When the point is made, stop.
*Check:* the first sentence alone carries the point. *(OBJ-09, 32, 34)*

## The reader can trust it

**6. Claim no more than the evidence shows.** A statement about existing code, files, tools, or numbers names its source, or it says that it is unchecked. A severity, a risk, or an estimate names its concrete consequence and uses the unit the work is measured in. A statement leaves out nothing that would change the reader's conclusion.
*Check:* each claim about what exists has a source or a mark, and each risk names what breaks. *(OBJ-05, 07, 13, 14, 35)*

**7. The text agrees with itself and with the project.** No two statements contradict each other. Test every "every", "only", "never", and "can" against the rest of the text. An example that uses a real ID matches the real item. Otherwise it uses an ID that does not exist.
*Check:* for each absolute word and each "can", find the exception or the command that does it. Look up each real ID. *(Reader test; coverage demon, rounds 1 and 2: proposal lines 188 and 240)*

**8. Every promise has a test, and every open point is visible.** Each design statement a reader may rely on has a completion criterion with a setup, an action, and a result. Each undecided point, including a limit with no threshold, appears in Open Questions.
*Check:* trace each "does" and "can" to a criterion, and each condition to Open Questions. *(Coverage demon, round 1: proposal line 385; reader test, open questions)*

## The tone stays out of the way

**9. People and programs act; ideas do not.** "The severity decides what the run does next" makes an idea act. Write who or what does it: "the implementation agent reads the severity and then …". Write no aphorisms, no drama, and no accusations.
*Check:* the subject of each sentence is a person, a program, a file, or a thing that can act. *(OBJ-21, 26, 27, 29)*

**10. Describe the current state, not its history.** A proposal, a specification, or a changelog entry states what is true now. The decision trail goes to the record.
*Check:* no "no longer", "was", "decided", or date appears outside the record and the Motivation. *(OBJ-12, 33)*

**11. Write short, complete sentences in plain words.** Every sentence has a subject and a verb, with fewer than 25 words. If a plainer word says the same thing, use it.
*Check:* count the words, find the verb, and try the plainer word. *(OBJ-19, 25, 36. This rule stays from the voice file. The objections show that it was not enough on its own.)*

**12. Show one example per rule, and keep it short.** The example serves the explanation. It does not replace it.
*Check:* each example is shorter than the explanation it supports. *(OBJ-22, 23, 24)*

## Left out

The voice file's rules against buzzwords, selling, and announcing have no objection behind them, and they have no counterexample in the controls. Agents already follow them, or the user does not notice the breaches. They are left out until a test shows they are needed.

## How a text is made

These steps cannot be checked from the text.

- A session that read only the document and the files it links to edits the prose.
- When you disagree, state the objection and wait for the answer before you act.
- Before release, run every check above and assume each fault is present.
- Code, commands, and the output of a run keep their exact wording.
