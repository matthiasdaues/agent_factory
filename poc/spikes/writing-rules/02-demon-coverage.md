# Demon: coverage of the register

Target: `docs/spikes/writing-rules/input/proposal-working-copy.md`, read in full. Line numbers refer to that file.

The test for "passes" is strict. A passage passes a claim when the claim's own check, applied to the text alone, does not flag it. Several rules have prose wide enough to cover almost anything, for example C00, C01 and C10. A rule that catches a fault only through its prose, while its check stays silent, does not count as a catch here. Where that happens, the row says so.

Facts checked in this session on 2026-11-17: the six ledgers and their branches (`find .current-work -name dispatch-ledger.yaml`, `git rev-parse`), the worktree and file counts, the CRAP threshold in `docs/testing.yaml`, and the behavior of `git stash push --include-untracked` followed by `git stash pop` on a clean tree, in a scratch repository.

## Uncaught passages

19 passages. Ranked by harm to the reader, worst first.

### U1. "stops" names two things, and the gap hides an undecided design

- **Line:** 144, 231, 278 (with 179, 238).
- **Quote:** "After the last story of a wave stops, `dispatch close-wave` handles the spec-feedback reports of the wave" (144). "A story stops in one of two states" (231). "It stops at every point where a person decides" (179).
- **Fault:** "Stops" means "ends in `failed` or `blocked`" in one place and "pauses for the human" in another. So the reader cannot tell whether a wave closes while a story is `blocked` and can still be re-dispatched in the same run (238). If it does close, the re-dispatched story merges after the wave record, and its spec-feedback report is never handled. If it does not close, one blocked story holds the whole run. The text decides neither case, and Open Questions says "None" (390).
- **Why no claim catches it:** C05 checks that a concept has only one name. It does not check that a name has only one concept. C34 checks the questions that are listed, and "None" lists nothing.
- **Smallest new rule:** A term or state verb keeps one sense through the whole text. Where the design uses the word for a condition, the condition is defined once.

### U2. The guardrail does more than the principle says it does

- **Line:** 100, against 318–327.
- **Quote:** "The git guardrail refuses agents only the commands that destroy work."
- **Fault:** The list at 320–326 also refuses test commands outside `testing.yaml`, a merge without a marker, a commit without `verify-base-ok`, and a branch without a worktree. None of these destroys work. A reader who trusts the principle builds or debugs the wrong guardrail.
- **Why no claim catches it:** No claim compares one statement with another. C16 checks consistency only for invented examples. C25 checks for a fact stated twice, not for two statements that disagree.
- **Smallest new rule:** Each "only", "every", "all", "never", and "nothing" holds against every other statement in the text.

### U3. The relied-on condition "not shared yet" is false in an orchestrated run

- **Line:** 242, against 175.
- **Quote:** "The feature branch is not shared yet, so nobody has built on the failed merge."
- **Fault:** In an orchestrated run, `refresh-story` brings a running story branch up to a feature branch that moved (175). A story refreshed after the failed merge is built on it. Moving the feature branch back then leaves that story on a commit the feature branch no longer holds. Nothing in the design stops the human from pushing the feature branch either.
- **Why no claim catches it:** The sentence is a design premise, not a tool claim (C15) and not an example (C16). C00's check asks for a source, and the design itself is the source.
- **Smallest new rule:** A condition the design relies on names the mechanism that enforces it, or is listed as an assumption together with what breaks when it fails.

### U4. "Returning" destroys work in one place and only changes a status in another

- **Line:** 74, 188, against 238.
- **Quote:** "It refuses agents the two commands that destroy work: returning a story and dropping a run" (74). "If an agent takes one too early, the human sees it and undoes it: a story branch can be returned" (188). "Returning sets the story back to `pending`, in the ledger and in the backlog" (238).
- **Fault:** By 238, returning only sets a status, so it destroys nothing. Yet the guardrail refuses it because it destroys work, and 188 uses it as the undo for an early start. The text never says what `return-story` does to the story branch, its worktree, or its commits. An implementer cannot build it from this text.
- **Why no claim catches it:** As for U2, no claim checks statements against each other. C31's table asks which behavior exists afterwards, and the text answers it, wrongly in one of two places.
- **Smallest new rule:** The U2 rule, plus this one: a command the text calls destructive states what it destroys.

### U5. Design promises without a completion criterion

- **Line:** 385, 141, 262, 278, 341.
- **Quote:** "Every `dispatch` command reads the ledger and the branch state before it acts, so a new session continues an interrupted run from where it stopped" (385).
- **Fault:** This is the widest promise in the proposal, and no completion criterion tests it. The same holds for these: `init` refuses when the feature branch already has a ledger (141), `premerge-check` names a stash it cannot pop (262), `close-wave` sends open `QA` findings to the test-strategy agent (278), and reconciliation runs after QA (341). A planner who cuts stories from the criteria drops these behaviors silently.
- **Why no claim catches it:** C33 traces Scope items to criteria, not Design statements. C32 checks that each criterion is checkable, not that each promise has a criterion.
- **Smallest new rule:** Each behavior the Design promises maps to a completion criterion, or is marked as untested.

### U6. The Summary's list of differences is wrong

- **Line:** 84, against 152–160 and 141, 171.
- **Quote:** "The two ways differ only in who starts a story, whether stories run in parallel, and who runs the commands that need a person."
- **Fault:** The table shows that the human runs the same commands on both ways, so the third difference does not exist. Differences that do exist are missing: where a story runs, whether `init` creates a worktree, `refresh-story`, and the guidance stops. This is the first account of the design the reader gets.
- **Why no claim catches it:** As for U2.
- **Smallest new rule:** The U2 rule. A summary claims no more and no less than the Design states.

### U7. The account of the leftovers does not add up

- **Line:** 386.
- **Quote:** "This repository holds six ledgers [...] Three of them [...] have no feature branch left, and one is nested inside the `counter-ids-fitting` worktree. [...] A ledger whose branch still exists closes with `dispatch close`."
- **Fault:** Three ledgers have living branches: `finding-classification`, `counter-ids`, and the nested `counter-ids-fitting` one. `dispatch close` needs a merge into `dev` and no `failed` or `blocked` story (290, 293), and the text does not say whether those hold. The nested ledger sits at `.current-work/feature/counter-ids-fitting/.current-work/feature/counter-ids-fitting/dispatch-ledger.yaml`, not at the path `init` writes, so `dispatch close` may not find it. The person who cleans up has no full plan.
- **Why no claim catches it:** C16 covers invented examples, and these are real. C35 checks that numbers have a source, and the six is correct.
- **Smallest new rule:** An account of real items says what happens to each item it counts.

### U8. "Every file a run creates is removed"

- **Line:** 102, 99, against 195, 250, 296.
- **Quote:** "Every file a run creates is removed at its close. Untracked files go into named stashes for the human." (102) "After `dispatch close`, nothing of the run remains except unmerged branches and named stashes" (99).
- **Fault:** The run creates review reports and finding files, and they stay in `dev`. The second sentence of 102 contradicts the first, because stashed files are kept, not removed. The intended statement is narrower: every untracked state file is removed.
- **Why no claim catches it:** As for U2. Each sentence on its own passes C02 to C09.
- **Smallest new rule:** The U2 rule.

### U9. "fresh", "closed", and "run" each carry two meanings

- **Line:** 196, 260, 259, 70.
- **Quote:** "A fresh developer agent fixes each open blocking finding" (196). "so `crap-score` reads fresh coverage" (260). "Findings are closed" (259). "In a run by hand, stories run one at a time" (70).
- **Fault:** In "fresh agent", the word means a new spawn without the earlier context, and the text never says so. In "fresh coverage", it means recomputed. Finding statuses are `open` and `resolved` (145), so "closed" is not a status. "Closed" also names the removed ledger field and the wave close. "Run" is the central noun, and it is also the most common verb in the text.
- **Why no claim catches it:** As for U1, C05 checks only in one direction.
- **Smallest new rule:** The U1 rule. A status word in prose uses the status value the files hold.

### U10. "too slow" has no threshold and no decider

- **Line:** 215.
- **Quote:** "If the trial in mutation-gate.md shows that it is too slow per story, it moves to the feature checks without changing the rest of the run."
- **Fault:** The condition that changes where a gate runs names neither a limit nor who decides. "without changing the rest of the run" is a reassurance, and the exception at 260 already contradicts it.
- **Why no claim catches it:** C32 covers completion criteria only. C35 covers numbers that are stated, not numbers that are missing.
- **Smallest new rule:** A condition that changes the design names its threshold or the person who decides.

### U11. A completion criterion depends on the live repository

- **Line:** 432.
- **Quote:** "After `dispatch close --orphans` in this repository, the only ledger without a branch left is the one it listed, of `core-artifact-layout`."
- **Fault:** The criterion holds only while the repository stays as it was on 2026-11-15. Anyone who cleans one ledger by hand makes it untestable, and it can never be run a second time.
- **Why no claim catches it:** C32 is satisfied: the criterion names an observable state and a command.
- **Smallest new rule:** A completion criterion runs against a fixture it sets up, not against the state of the live repository.

### U12. A "so" that asserts a cause that does not exist

- **Line:** 164.
- **Quote:** "Both ways use the same ledger states, so a story reaches `dispatched` before it merges on either way."
- **Fault:** Sharing a set of states does not force a story through one of them. The real reason comes at 175: the agent runs `mark-dispatched` on both ways. C23 rewards the connective, so it invites this fault.
- **Why no claim catches it:** C23 checks that the paragraph reads as an argument. A false "so" makes it read as one.
- **Smallest new rule:** A "so" or "because" joins only a cause to its effect. Test it by asking whether the effect could happen without the cause.

### U13. A snapshot count, precise and already stale

- **Line:** 88.
- **Quote:** "This repository holds six old ledgers, thirteen worktrees besides the primary checkout, and 36,109 files under `.current-work/`."
- **Fault:** On 2026-11-17 the repository held 14 worktrees besides the primary checkout and 39,858 files. The argument needs "tens of thousands", not five digits.
- **Why no claim catches it:** C35 is satisfied, because the number came from a count. C28 forbids dates in target-state text, so the writer cannot add "as of". The two rules together push the writer toward an undated precise number.
- **Smallest new rule:** A measured value of changing state is rounded to the precision the argument needs, or carries the command and date that produced it. Measurement dates are exempt from C28.

### U14. "Three sources" with no names

- **Line:** 94.
- **Quote:** "Three sources name three different owners for setting a story to `done`." "The dispatch contract lists ledger fields the code never writes."
- **Fault:** The precise count makes the claim look checked, but the reader cannot find the three sources or the fields. Documents that change (333–351) does not list the three sources either, so nobody knows which documents to fix.
- **Why no claim catches it:** C27 checks references that exist, and this sentence holds none. C35 is satisfied by a count.
- **Smallest new rule:** A claim about other documents names them.

### U15. A definition vaguer than its term

- **Line:** 121.
- **Quote:** "primary checkout | The repository's main folder."
- **Fault:** "Main folder" is less precise than "primary checkout". It also revives the word "main" that 123 bans in "main checkout". The precise meaning is the folder that `git clone` made, as opposed to a linked worktree.
- **Why no claim catches it:** C06 checks that a definition exists at first use, not that it explains anything.
- **Smallest new rule:** A definition uses words more concrete than the term it defines.

### U16. "Every story escalates" against "0 turns escalation off"

- **Line:** 229.
- **Quote:** "A value of 0 for `gates.attempts_escalated` turns escalation off. [...] Every story that uses up its attempts escalates."
- **Fault:** The two statements stand three sentences apart and contradict each other. The intended statement is that the limit of one escalation per wave goes away.
- **Why no claim catches it:** As for U2.
- **Smallest new rule:** The U2 rule.

### U17. Reconciliation is a step of the run and outside the run

- **Line:** 148, 136–138.
- **Quote:** "8. **Reconciliation.** The reconciliation agent then brings the documents in line with the code, on `dev` and outside the run."
- **Fault:** The numbered list headed "The run" and the diagram both include a step that the sentence places outside the run. So the reader cannot tell whether `dispatch close` waits for reconciliation, or who starts it.
- **Why no claim catches it:** As for U2. C26 is satisfied, because the heading predicts the steps.
- **Smallest new rule:** The U2 rule.

### U18. "one more" with no baseline

- **Line:** 382.
- **Quote:** "Each story needs one more review spawn, and sometimes a retry."
- **Fault:** The sentence does not say what the story needs one more than: an orchestrated run today, or a run by hand today. A cost the reader cannot compare tells them nothing.
- **Why no claim catches it:** C35 is about invented numbers. "one more" is a comparison, not a count.
- **Smallest new rule:** A comparison names what it compares against.

### U19. Estimate fields that report a judgment nobody made

- **Line:** 55–59.
- **Quote:** "basis: judgment / confidence: low / human_review_hours: unknown / normalized_tokens: unknown / estimated_consumption: unknown"
- **Fault:** Every value is `unknown`, so no judgment exists, and no confidence can attach to it. The fields look filled in and say nothing.
- **Why no claim catches it:** C35 is satisfied, because `unknown` is the value the rule asks for. No claim covers metadata.
- **Smallest new rule:** When every estimate value is `unknown`, the basis and confidence are `unknown` too.

## Worst passages the claims do catch

Five, ranked by harm. The rewrite should remove each of them.

| Rank | Line          | Quote                                                                                                                                                                           | Fault                                                                                                                                                                                                                                                                                                                  | Claim                                                                                                                            |
| ---- | ------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| 1    | 262           | "It then stashes the untracked files of the checkout with `git stash push --include-untracked` [...] After the gates run, it puts the files back with `git stash pop`."         | Checked in a scratch repository: with no untracked files, `push` prints "No local changes to save" and exits 0. Then `pop` drops the newest older stash into the checkout, for example a `run feature/login ST-0350` stash from an earlier close, and also exits 0. Files from another run enter the story's checkout. | C15, but only if the reviewer reads a design sentence as a claim about git.                                                      |
| 2    | 384           | "Code that changes after the last review, such as a gate fix, is not reviewed again. A gate fix is usually small, and another review would cost a full spawn."                  | Unreviewed code reaches the merge, and an unsupported "usually" plays it down.                                                                                                                                                                                                                                         | C12 by its prose (reassurance) and C00 ("usually" has no source). C12's check looks only at rejected alternatives and misses it. |
| 3    | 278           | "it has the implementation agent spawn the owner of each row, and then that owner's reviewer [...] sends each open `QA` finding of the wave to the test-strategy agent"         | A script cannot make an agent spawn, and "sends" names no channel. The reader cannot tell whether `close-wave` blocks, prints instructions, or writes files.                                                                                                                                                           | C04: the verb does not name what physically happens.                                                                             |
| 4    | 145, 170, 278 | "The finding's `artifact` serves the overlap planning in place of a story's file list. [...] so it runs on the default tier." Also `verify-story`, and "the owner of each row". | Project terms the reader needs to build the feature are never defined.                                                                                                                                                                                                                                                 | C06, C01.                                                                                                                        |
| 5    | 331           | "It relies on refusing a command, which every tool's guard supports."                                                                                                           | The claim about five tools is unchecked, and the criterion at 397 and the principle at 100 rest on it.                                                                                                                                                                                                                 | C15.                                                                                                                             |

The register also catches these, with lower harm: the CRAP example at 90 uses a threshold of 30, while this project's `docs/testing.yaml` sets 8 (C16). "Design Details" (380) holds the risks, so the heading does not predict them (C26, C31).

## Patterns

Most uncaught faults are contradictions between two statements that each pass every sentence rule. The register checks sentences, paragraphs, and examples, and it never checks one statement against another. The second group is undefined scope: words with two senses, conditions with no threshold, premises with no enforcement, and promises with no criterion. In each case the text looks decided and is not. Two claims invite faults: C23 rewards a false "so", and C28 together with C35 pushes the writer toward precise undated numbers.
