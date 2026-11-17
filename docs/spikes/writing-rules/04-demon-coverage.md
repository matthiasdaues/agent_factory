# Coverage attack on the round-1 rule set

Target: [03-rules-round1.md](03-rules-round1.md), as a whole.
Hunting ground: [input/proposal-working-copy.md](input/proposal-working-copy.md). Line numbers refer to that file.

The demon found 19 passages that are bullshit in the sense of the motto and pass every rule. They are ranked by harm to the reader: first the passages that would make the engineer build the wrong thing, then the ones that mislead the person who decides, then the ones that only slow the reader down.

Each entry was checked against the repository where the fault depends on a fact. The demon skipped passages that a rule already catches. Example: the unsourced counts in line 88 fail T1, and the "only" in line 84 fails T2.

## Uncaught passages

### 1. Line 188: an undo that the state machine forbids

- Quote: "If an agent takes one too early, the human sees it and undoes it: a story branch can be returned, and a merge undone by moving the feature branch back."
- Fault: line 238 adds return transitions only from `failed` and `blocked`, and line 419 tests exactly those two. A story that an agent started too early is `dispatching` or `dispatched`, so it cannot be returned. Line 291 has the same hole: a run cannot be dropped while a story is running. The whole case for leaving by-hand steps unguarded rests on this undo.
- Why no rule catches it: T2 scans only for "every", "only", "never" and "all", and neither sentence uses one. T4's check looks for "does", "is" and "every", not "can".
- Smallest new rule: Each "can" names the command that does it, and that command's stated preconditions allow it from the state in question.

### 2. Line 229: existing escalation conditions dropped without a word

- Quote: "Every story that uses up its attempts escalates. `dispatch escalate` today lets only one story per wave escalate, and that limit is dropped."
- Fault: `cmd_escalate` in `packages/factory/scripts/dispatch` (lines 1480–1560) has seven more refusals: already at `strong` tier, not exactly one prior implementation attempt, a failure class outside `QUALIFYING_ESCALATION_FAILURE_CLASSES`, already escalated, missing branch metadata, failed verify-base, and a scope violation. The proposal names only the per-wave limit. A builder cannot tell whether the other seven stay. The text also never says what "a stronger model" means for a story that is already `strong`.
- Why no rule catches it: T1 checks statements and has nothing to say about a missing one. T2 looks for exceptions only inside the text. S3 asks "what happens today" once for the whole proposal, not for each replaced behaviour.
- Smallest new rule: Where the design replaces existing behaviour, list each existing condition of that behaviour and say whether it stays or goes.

### 3. Line 384: unreviewed code merges because fixes are "usually small"

- Quote: "Code that changes after the last review, such as a gate fix, is not reviewed again. A gate fix is usually small, and another review would cost a full spawn."
- Fault: the claim has no source, and the design contradicts it. Line 229 allows six fix attempts, three of them on a stronger model, all after the last review. Line 213 uses the same move: "the flaws it finds usually lie in how stories fit together."
- Why no rule catches it: T1 covers statements about existing code, files, tools, people and numbers, not frequency claims about the world. T5 covers undecided matters, and this matter is decided. C4 checks that a cause is stated, not that it holds.
- Smallest new rule: A reason that rests on frequency ("usually", "often", "rarely", "most") names its source or carries the T1 mark.

### 4. Line 141: two runs allowed at once, with no home for `dev`

- Quote: "One run may be active per feature branch, and several runs may be active at once."
- Fault: a run by hand holds the primary checkout on a story branch. An orchestrated run that finishes at the same time needs `dev` checked out for the human's merge (line 146) and for reconciliation (line 148). The text never says where `dev` is checked out then. It also never says which checkout's installed copy `dispatch merge-story` overwrites (line 339) while the run by hand is using it.
- Why no rule catches it: T5 finds only open matters that the text phrases as conditions or limits. An interaction that the text never mentions leaves nothing to search for. "Open Questions: None" (line 390) then passes.
- Smallest new rule: For each pair of things the design allows at once, name each resource they share and who holds it.

### 5. Line 278: rejected drift rows disappear

- Quote: "`close-wave` then refuses while a report has an `open` row, or a `fixed` row about an artifact on the core list"
- Fault: under ADR-0029 (`docs/adr/0029-per-story-drift-reports-block-the-wave-close.md`, Decision), a `rejected` row becomes a `BUG` finding against the code. The proposal moves the drift sessions to the wave close and never says what happens to that finding: which wave fixes it, and whether the next wave waits for it.
- Why no rule catches it: this is the same hole as entry 2. No rule asks for the old behaviour that a change drops.
- Smallest new rule: the rule from entry 2.

### 6. Line 175: `mark-done` goes, and its second job goes with it

- Quote: "`mark-done` is removed. It set `done` without a merge, and only `merge-story` sets `done`."
- Fault: `cmd_mark_done` also removes the story's step manifest and switches off its guards (`dispatch` line 1304: "Mark a story done and remove its step manifest (guards deactivate)"). The proposal never uses the word "manifest". Nobody knows which command now switches off a merged story's guards.
- Why no rule catches it: the same hole as entry 2. The stated reason is true, so C4 passes.
- Smallest new rule: the rule from entry 2, applied to removed commands as well: list every effect of the removed command and name its new owner.

### 7. Line 246: present tense for both today and the target state

- Quote: "A finding file has a `story` field with the story ID, such as `story: ST-0350`. [finding-format.md] and the finding template define it."
- Fault: the finding template has no `story` field today (`packages/factory/rulebooks/templates/finding.md`, lines 30–33). In the same paragraph, "which already has a required `story` field" is true today (`finding-register-*.schema.json`). Line 258, "Both fields are defined in report-format.md", is also true today. A builder reads three sentences in the same tense and form, and one of them is work still to do.
- Why no rule catches it: O6 requires the target state in the present tense. T1 is satisfied because a source is named. Together the two rules produce this ambiguity. T1 cannot even be applied until the reader knows which present-tense sentences describe today.
- Smallest new rule: A present-tense sentence about a named file that the proposal changes says "gains", "today", or an equal marker, so the reader can tell the change from the fact.

### 8. Lines 164–173: a table that looks complete and is not

- Quote: "The `dispatch` subcommands fall to these actors:"
- Fault: `dispatch` also has `status`, `plan`, `prepare-wave`, `clear-manifest`, `close-wave` and `suggest-merge-args` (`dispatch` lines 2116–2206). The text never says who runs `close-wave` or `clear-manifest` in a run by hand, or whether `suggest-merge-args` survives the new feature merge check.
- Why no rule catches it: T2 needs an absolute word. "The subcommands" claims the whole set through the definite article alone.
- Smallest new rule: A list or table introduced as the whole set ("the subcommands", "the gates") holds the whole set; check it against the source.

### 9. Line 362: existing behaviour listed as new scope

- Quote: "The wave close with the drift sessions, and the refusal of the next wave until the close succeeds."
- Fault: `dispatch close-wave` and the wave record already exist (`dispatch` line 2064, `dispatch_lib.py` line 367), and ADR-0029 already makes `prepare-wave` refuse until the previous wave is closed. Only the timing of the drift sessions is new. A planner who reads Scope will cut stories for code that is already built.
- Why no rule catches it: S3 asks what happens today, but not for each "In" item. Each item traces to a criterion (lines 416–417), so S3 passes.
- Smallest new rule: Each "In" item says whether it is new, a change, or already built.

### 10. Lines 70 and 98: "the same checks" for both ways, which is false

- Quote: "Both ways share the same branches, ledger, steps, checks, and end."
- Fault: line 325 requires `verify-base-ok` only for "a commit in a worktree". By hand the story runs in the primary checkout, which the terms table (line 121) treats as something other than a worktree. So commits by hand skip the base check. `refresh-story` is not used by hand either (line 171).
- Why no rule catches it: "same" is not on T2's list of absolute words.
- Smallest new rule: Add "same", "both", "the two", "once" and every number to T2's list of words that make claims about the whole text.

### 11. Line 74: "the two commands that destroy work"

- Quote: "It refuses agents the two commands that destroy work: returning a story and dropping a run."
- Fault: the guardrail also refuses `push`, `reset --hard`, `clean -f`, `branch -D`, `checkout .` and `restore .` (line 320). Most of those destroy work too. The primer teaches the newcomer that these two commands are the only dangerous ones.
- Why no rule catches it: "the two" is a count, not one of T2's words. S4 checks the primer's length, identifiers and order, not its truth against the design.
- Smallest new rule: the T2 extension from entry 10.

### 12. Lines 188 and 329: "because both destroy work", never shown

- Quote: "Both commands destroy work, and both are always the human's decision"
- Fault: the only description of `dispatch return-story` (line 238) says it sets the story to `pending` in the ledger and in the backlog. Nothing there is destroyed. The text never says what happens to the returned story's branch. Line 173 also gives `dispatch close` to the human, although `close` deletes the ledger, and the guardrail does not refuse it. The text gives no reason for that split.
- Why no rule catches it: C4 checks that the linking word names a cause the text states. The cause is stated. Nothing checks that the text shows the cause to be true.
- Smallest new rule: A stated cause appears in the description of the thing it explains; if the text never shows the effect, the reason goes or the description grows.

### 13. Line 280: a reason that the rejected design also meets

- Quote: "These drift sessions run at the wave close and not after each merge, so a story merge and a drift session never commit on the feature branch at the same time."
- Fault: ADR-0029 runs the sessions after each merge and makes the next `dispatch merge-story` wait for them. That design already rules out simultaneous commits. The decider cannot see what the change buys.
- Why no rule catches it: N3 asks for a reason that refers to this project, and this one does. It does not ask that the reason tell the options apart. The alternative is also never named in this section, so N3 may not apply at all.
- Smallest new rule: A reason for a choice must be false for the option it replaces.

### 14. Lines 78 and 148: reconciliation on `dev` "so parallel runs do not conflict"

- Quote: "After the merge into dev, the reconciliation agent updates the shared documents there, so parallel runs do not conflict."
- Fault: two runs that both finish still produce two reconciliation sessions that edit the same scope map and glossary on `dev`. The conflict moves from the feature merge to `dev`. It goes away only if the sessions run one at a time, and the text does not say that they do.
- Why no rule catches it: C4 passes, because the cause is stated in line 148. Nothing checks that the effect holds in every case the design allows.
- Smallest new rule: the rule from entry 12, read as "the effect holds in every case the design allows".

### 15. Line 103: "once per story" next to "twice per story"

- Quote: "**Fast on every commit, slow once per story.** A gate that takes minutes runs in the gate-check step and again at the merge"
- Fault: the heading says once, and the next sentence says twice. Line 382 says twice too.
- Why no rule catches it: "once" is not on T2's list. O4 lets a principle restate a fact only if the principle matches it, and nobody checks the match.
- Smallest new rule: the T2 extension from entry 10.

### 16. Line 278: a script that commands agents

- Quote: "it has the implementation agent spawn the owner of each row, and then that owner's reviewer. … it writes a wave record into the ledger and sends each open `QA` finding of the wave to the test-strategy agent."
- Fault: a script cannot spawn an agent or send it anything. The builder cannot tell which parts belong in `dispatch` and which belong in the implementation agent's instructions.
- Why no rule catches it: C3 checks that each sentence has a subject and a verb. It does not check that the subject can do what the verb says.
- Smallest new rule: The subject of each sentence can do its verb: a script runs, writes and refuses; an agent spawns, sends and decides.

### 17. Line 432: a criterion that can be run only once

- Quote: "After `dispatch close --orphans` in this repository, the only ledger without a branch left is the one it listed, of `core-artifact-layout`."
- Fault: the criterion depends on today's leftovers. Line 386 tells the human to remove that ledger, and after that the criterion can never run again. It also fails on any other clone.
- Why no rule catches it: T4 asks for a setup, an action and a result, and all three are present. It does not ask that the setup be reproducible.
- Smallest new rule: A completion criterion builds its own setup and does not depend on the current contents of this repository.

### 18. Line 68: the primer denies the step it then uses

- Quote: "When the human drives it, there is no merge step, so failing code can merge."
- Fault: a newcomer reads "no merge step" and then "can merge". The meaning is "no merge check". Line 90 says so, but the primer comes first.
- Why no rule catches it: C1 lists project terms, and "merge step" reads as plain English. C4 passes, because the "so" names a cause.
- Smallest new rule: Read each negation against the clause that follows it; if the clause uses what the negation denied, rename the thing.

### 19. Lines 141, 146, 192, 229, 254, 345 and 359: "on both ways"

- Quote: "`--stories` names the stories of the run on both ways."
- Fault: the phrase is not English that a native speaker would write. A reader whose first language is not English stops at it every time. The proposal fell into it after it banned "mode" in prose, even though the ledger field is still `mode` (line 310).
- Why no rule catches it: C2 tests plain words and idioms, and each word here is plain. C1 may catch the "way"/`mode` pair, but not the preposition.
- Smallest new rule: Use the preposition and article a native reader expects; when unsure, write the phrase a grammar checker accepts.

## Rules that never fire on this proposal

The demon checked each text rule against the proposal. Twelve rules fire at least once, for example T3 on line 240, where `backlog/ST-0352.md` has `deps: []`, and on line 425, where `BUG-0090` has `status: resolved`. Four rules never fire.

| Rule | Why it does not fire here                                                                                                                                                                            | Would it fire on other text?                                                                                                           |
| ---- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| N3   | Every rejected alternative (revert commit at line 76, a second review at line 384, a per-story OWASP review at line 213) has a reason that refers to this project.                                   | Yes, on proposals that set up a weak alternative only to knock it down. Entry 13 shows that its check is too weak where it does apply. |
| O6   | No decision stamps, no "who decided", no "no longer". Each "today" sits where the text changes existing code, which O6 allows. "The last check is new" (line 329) is the same kind of change marker. | Yes, on proposals rewritten from a handoff or a decision log, where dates and "we decided" leak in.                                    |
| S1   | The proposal asks no question: Open Questions says "None".                                                                                                                                           | Yes, on chat messages and on proposals with open questions. It is a rule for a different kind of text.                                 |
| S2   | The proposal is not a report.                                                                                                                                                                        | Yes, on status reports and handoffs. It is a rule for a different kind of text.                                                        |

Cutting these four loses nothing on this text. Only N3 is a real candidate for cutting. S1 and S2 apply to other kinds of text, and O6 guards against a known way that rewritten proposals fail.

## Patterns

The rules test the sentences that are on the page, so the worst faults escape: missing cases, old behaviour dropped without a word, and interactions between features the design allows. T2 catches contradictions only through four absolute words, and the text makes the same sweeping claims with "same", "the two", "once", and definite-article lists. C4 and N3 check that a reason is stated, not that it is true, shown, or false for the rejected option. T1 and O6 together make the present tense mean both "exists today" and "exists after the change", so a sourced sentence can still mislead the builder. Most of the needed repairs ask the writer to compare the text with the repository, which no rule in the set requires.
