# Demon, round 2: Trust and Need

Register under attack: `03-rules-round1.md`, rules R0 (the preamble), T1–T5 and N1–N3.
Hunting ground: `input/proposal-working-copy.md`. A citation such as "PWC:240" names a line of that file.

### R0 — damaged

- Attack 1: succeeded. The definition says a text is bullshit when the reader "cannot trust it". A fabricated text written with confidence is one the reader can trust, in the sense of "is able to believe". Example: "Six old ledgers sit under `.current-work/` (`find .current-work -name dispatch-ledger.yaml`)." If the count is invented, the reader still trusts it, so by R0's wording the text is not bullshit. The motto's bullshit is about the writer's disregard for truth, and R0 measures only what the reader is able to do.
- Attack 2: failed. Every text I tried that the reader cannot trust, does not need, or cannot act on was worse for it.
- Attack 3: failed. No rule in the file defines the three faults or the reader.
- Attack 4: succeeded. "Cannot act on it" splits readers on a report of a negative result. Text: "All five gates passed on `story/ST-0350`. Nothing is open." Reader A: the reader cannot act on it, so the text is suspect. Reader B: deciding to merge is the act. R0 gives no way to choose.
- Attack 5: succeeded. "A chat message or a report has one reader: the person who asked" is a false statement about what exists, and it has no source, so R0 breaks T1. The input folder holds `subagent-proposal-review.md`, a third reader of the proposal, and a handoff file whose reader is the next session, not the person who asked. "The rules below cover these three faults in that order" names three faults, but five sections of text rules follow. Clarity, Order and Specific texts are not mapped to any fault.
- Attack 6: succeeded. R0 says "Each rule has a check that a reader can run on the page alone." T3's check is "look up each real ID the example uses", which needs the backlog. PWC:240 uses ST-0350, ST-0351 and ST-0352. Only `backlog/ST-0352.md` shows that ST-0352 has `deps: []` and does not depend on ST-0351. No reader can find this from the page. N1's check also needs knowledge of the reader's need, which the page does not hold.
- Weakest point: the definition measures what the reader is able to believe, not whether the reader should believe it.
- Smallest repair: write "should not trust", list the actual readers per text type (including the review agent and the next session), and drop "on the page alone" or move T3 out of the page-checkable rules.

### T1 — damaged

- Attack 1: succeeded. The check asks only that a source stands next to the statement, not that the source says it. PWC:94: "At the cap on attempts, ADR-0012 marks the story `blocked`." The statement names its source and passes the check whether or not ADR-0012 says this. A writer can also mark every statement "unchecked; run `X` to check", obey T1 in full, and hand all the checking to the reader.
- Attack 2: succeeded. T1 names "tools" and grants no exemption for knowledge of the trade. PWC:296: "Git keeps stashes in the repository, not in the folder, so they survive the removal." T1 requires "(source: git-stash(1))" or "unchecked; run `git stash list` after removing a worktree". The bare sentence is clearer, and the journeyman knows git. The same holds for PWC:76 on revert commits.
- Attack 3: failed. No other rule asks for a source.
- Attack 4: succeeded. The check keys on "present-tense statement about existing things", and O6 makes the present tense the tense of the design. PWC:225: "`dependency-check` reads Python imports only." Reader A: a design statement about the target state, no source needed. Reader B: a fact about the existing script, needs a source. Numbers split readers too. PWC:90: "A function with a CRAP score of 42 against a threshold of 30 can merge by hand." Reader A: an illustration, the modal "can" already says so. Reader B: an unlabelled number, so it breaks T1.
- Attack 5: succeeded. "A marked statement does not carry a design decision until someone checks it" is a process rule inside a text rule. No check on the page can tell whether a decision rests on a marked statement. The rule also lists "people" as a subject, but its sources are only a file, a command, or a document.
- Attack 6: succeeded. T1 conflicts with S4 ("uses no identifiers"). PWC:68 in the primer: "A script named dispatch writes a ledger, a file that tracks the stories, and no command ever removes it." This is a present-tense statement about existing code. T1 requires a file, a command or a mark with a command next to it. S4 forbids all three in the primer.
- Weakest point: the check counts sources and does not test them.
- Smallest repair: exempt statements of the trade and the primer, and change the check to "open one source per section and confirm it says what the text claims".

### T2 — damaged

- Attack 1: succeeded. The rule forbids every contradiction, but the check only searches absolute words. Invented text: "`premerge-check` reads the finding files from the branch head." Later: "`premerge-check` reads the finding files in the folder it runs in." Neither sentence has an absolute word, so the check passes them. The rule also invites hedging. A writer who writes "usually" in place of "always" escapes the check. PWC:384 "A gate fix is usually small" can be contradicted by nothing.
- Attack 2: failed. PWC:88 says "no command ever removes it", and PWC:293 says `dispatch close` removes the ledger. The check flags this. Adding "today" costs one word and makes the time scope clear, so the obeying version is better.
- Attack 3: failed. C1 covers words with two meanings, not statements that disagree.
- Attack 4: succeeded. PWC:100: "The git guardrail refuses agents only the commands that destroy work." PWC:322–323: the guardrail refuses "test commands outside `testing.yaml`" and a merge without `premerge-check-ok`. Reader A: PWC:100 speaks about `dispatch` commands in a run by hand, as PWC:329 shows, so there is no exception. Reader B: "only" is contradicted twice. A second case: PWC:200 says the developer agent "never runs a gate script", and PWC:223 adds `dependency-check` as a hook on every commit the developer agent makes. Reader A: the hook runs the script, not the agent. Reader B: the agent runs it through the commit.
- Attack 5: succeeded. "Words such as 'every', 'only', 'never', and 'all' make claims about the whole text" is wrong. "Every story goes through these steps" (PWC:192) is a claim about stories, not about the text. The heading promises "no two statements contradict"; the check delivers one kind of contradiction.
- Attack 6: failed. O6 allows "today" where the proposal changes existing code, so a scoped absolute claim can obey both T2 and O6. C3 can be obeyed by splitting a long qualified claim into a list.
- Weakest point: the check covers absolute words only, so a contradiction between two plain statements passes.
- Smallest repair: change the check to "for each subject, list what the text says it does and reads, and compare the entries", and keep the absolute-word search as one part of it.

### T3 — damaged

- Attack 1: succeeded. A made-up ID in a counter format becomes real later. "Uses an ID that does not exist" holds on the day of writing and fails silently when the counter reaches it. PWC:240 shows the end state: ST-0350, ST-0351 and ST-0352 all exist, and all are `done`. A done story cannot be "returned", as the example says.
- Attack 2: failed. The real mismatch matters. Completion criterion PWC:422 says "After ST-0350 is returned...". An engineer who builds that test against the real backlog finds that ST-0352 has `deps: []` (`backlog/ST-0352.md`) and that the chain does not exist. The obeying version with made-up IDs would spare that engineer the confusion.
- Attack 3: succeeded in part. A real ID in an example is a statement about what exists, so T1 already covers "matches the real item". "The example agrees with itself" is T2. The only new demand is that a made-up ID must not exist.
- Attack 4: succeeded. The text does not say which IDs are meant as real. PWC:386 uses ST-0344 as a real item, and PWC:240 uses ST-0350 in the same document. Reader A takes ST-0350 as real, looks it up, and finds a violation, because ST-0352 does not depend on ST-0351. Reader B takes it as made up and finds a violation of a different kind, because the ID exists. `feature/login` (PWC:72) is the same. The check "look up each real ID" assumes the reader knows which ones are real.
- Attack 5: succeeded. The rule promises a lasting property, "an ID that does not exist", that a counter-based project cannot give.
- Attack 6: succeeded. T3 conflicts with R0's "a check that a reader can run on the page alone", as shown under R0.
- Weakest point: the reader cannot tell a real ID from a made-up one, and a made-up one does not stay made up.
- Smallest repair: made-up IDs use a reserved form that the counter never issues, such as `ST-EXAMPLE-1` or `feature/example-login`, and every other ID counts as real.

### T4 — damaged

- Attack 1: succeeded. A criterion can name setup, action and expected result and still test nothing reliable. PWC:400: "In a run driven by hand, the implementation agent stops before each step listed in Guidance by hand and waits for the human's go before it runs the command." This is the behavior of a language model under a prompt. One passing run does not show that the next run stops. The criterion obeys T4 and gives a false sense of safety.
- Attack 2: succeeded. The check flags every "does" and "is". PWC:238: "The names tell the human why the story stopped." No criterion can test this, and none should. The sentence is an honest reason for the two state names. PWC:213: "The security scanner is a deterministic gate." A criterion for it would test a deferred item and contradict Scope.
- Attack 3: failed. S3's tracing of "In" items is narrower, and T4 includes it.
- Attack 4: succeeded. "Names its setup" splits readers. PWC:403: "`dispatch merge-story` sets `status: done` in the merge commit, and the developer agent's commits never set it." Reader A: the setup is a story ready to merge, which is implied. Reader B: no setup is named, so it fails. PWC:395 names its setup ("With an orchestrated run active on `feature/login`"), so the document itself holds both standards. "A design statement a reader could rely on" also splits readers. PWC:384 "A gate fix is usually small": Reader A: a reason, no test. Reader B: the design skips a second review because of it, so a reader relies on it.
- Attack 5: succeeded. The heading says "promise"; the body says "each design statement a reader could rely on"; the check says every "does", "is" or "every". These are three different sets, and the last one is nearly every sentence of the Design section. The rule also does not say which text types it applies to. A chat reply has no completion criteria.
- Attack 6: failed. I looked for a conflict with T5 at PWC:215 ("If the trial ... shows that it is too slow per story, it moves to the feature checks"). An open statement is not one a reader can rely on, so T4 does not demand a test for it. A long criterion can be split, so C3 does not conflict either.
- Weakest point: the keyword check makes every sentence a promise.
- Smallest repair: limit T4 to proposals and to behaviors that the Scope lists as "In", and require the setup to be named only where the action has a precondition.

### T5 — damaged

- Attack 1: succeeded. The check searches for conditions and unmeasured limits. An unmeasured assumption is neither, and it passes. PWC:384: "A gate fix is usually small, and another review would cost a full spawn." The design skips a second review on this ground. PWC:213: "the flaws it finds usually lie in how stories fit together." Both are open matters, and PWC:390 says "None."
- Attack 2: succeeded. PWC:215 and PWC:260 leave the speed of mutation testing to `mutation-gate.md`, and Scope at PWC:378 lists it as deferred, with its owner. This is clear: the reader learns who settles it and what the run does until then. T5 demands a third entry in Open Questions for a question this proposal cannot answer. The obeying version adds a repeat and suggests this proposal owns the question.
- Attack 3: failed. T1's mark covers unchecked facts, not undecided matters.
- Attack 4: succeeded. Every "when" in the design is a condition. PWC:229: "When a gate fails, the implementation agent spawns a fresh developer agent." Reader A: a decided rule, not open. Reader B: the check says find each condition in Open Questions. The limits split readers too. PWC:103: "A gate that takes minutes runs in the gate-check step." Reader A: decided, the slow gates are named elsewhere. Reader B: "takes minutes" is a limit with no threshold.
- Attack 5: failed. The wording is plain. "The place its answer goes" is loose, but any concrete place satisfies it.
- Attack 6: succeeded. T5 conflicts with O4 and S3. S3 gives deferred items their own home in Scope, "what is deferred and what it waits for". O4 gives each fact one home. T5 says every undecided matter appears in Open Questions. For mutation testing at the merge (PWC:378), a writer cannot obey all three: either the fact appears twice, or the Scope deferral breaks S3, or Open Questions misses it and breaks T5.
- Weakest point: T5 has no place for a matter that is open here but owned by another document.
- Smallest repair: count a Scope deferral that names its owner as visible, and replace "conditions" with "conditions whose outcome the text does not decide".

### N1 — refuted

- Attack 1: succeeded. The test runs on whole clauses, so padding inside a needed clause survives. Invented text: "In order to be able to proceed with the merge, the agent must first ensure that `premerge-check` has passed." Delete the clause and the reader loses a needed fact. The padding is "in order to be able to" and "first ensure that", and the clause test cannot reach it.
- Attack 2: succeeded. N1 defines need as what helps the reader "decide or build". PWC:76 in the primer: "The proposal moves the feature branch back instead, because a revert makes git treat the story as merged, and a second attempt would bring in nothing." Delete the "because" clause and the builder loses nothing: the design says to move the branch back. The version that keeps the reason is more honest. It stops a later engineer from replacing the move with a revert.
- Attack 3: failed. N1 is the general rule; N2 and N3 are cases of it.
- Attack 4: succeeded, at the core. R0 gives a proposal two readers, and N1 does not say whose need counts. PWC:88: "36,109 files under `.current-work/`." The person who decides needs the number to see the scale of the problem. The engineer who builds the close command needs only "files pile up". The check "if the reader loses nothing they need, it goes" is the rule itself again. The writer who runs it is the person least able to judge what a newcomer lacks.
- Attack 5: succeeded. "Decide or build" fits a proposal. For a status report or a chat reply, the reader neither decides on a design nor builds one, so the definition of need does not apply to the texts R0 lists.
- Attack 6: succeeded. N1 conflicts with O4, which lets the primer and the completion criteria restate facts. PWC:76 restates PWC:242. Run N1's check on PWC:76: the reader of the Design section loses nothing, so the sentence goes. O4 keeps it. N1 has no exception for the primer.
- Weakest point: the check repeats the rule and gives the writer no test that does not depend on the writer's own judgment.
- Smallest repair: replace N1 with a list of named cuts that a reader can find on the page, such as restatement outside the primer and the criteria, history the target state does not need, and options no reader proposed. Keep "need" only as the reason behind them.

### N2 — damaged

- Attack 1: succeeded. The check does not catch the words the rule bans. "The guardrail design is clean and robust." The sentence states something about the subject, so it passes "each sentence states a fact about the subject". The rule also bans a sentence that "only" settles a worry, so a worry-settler with a fact attached passes. PWC:213: "This proposal needs nothing special for it: `premerge-check` reruns every gate that `docs/testing.yaml` enables." The first half is about the proposal and settles a worry, and the second half carries it through the check.
- Attack 2: succeeded. PWC:343: "These changes follow the decisions above:" This sentence is about the text. Cut it, and the two lists at PWC:337–341 and PWC:345–351 merge. The reader then loses the difference between "the document changes to match the code" and "the document changes because of a decision". The version that breaks N2 is clearer.
- Attack 3: succeeded in part. Every sentence N2 bans also fails N1: a reader does not need an announcement, a rating, or a settled worry. N2 adds a word list, and the list is its only part that a reader can check.
- Attack 4: succeeded. Link sentences split readers. PWC:196: "finding-classification.md § Shared severity scale and blocking rule defines which findings block." Reader A: a fact about another document, not about "the text", so it passes. Reader B: a sentence about a text, so it fails. O4 requires exactly such sentences ("A link says what its target holds").
- Attack 5: failed. The banned words and structures are concrete. The rule does not claim an effect it cannot have.
- Attack 6: succeeded. N2 conflicts with N3. PWC:384: "Code that changes after the last review, such as a gate fix, is not reviewed again. A gate fix is usually small, and another review would cost a full spawn." N3 says to give the concrete reason against an alternative the reader expects, here a second review. N2 says to state a limit as a limit, "with no benefit attached", and the saved spawn is a benefit. The writer cannot obey both in this paragraph.
- Weakest point: the check accepts any sentence with the subject as its grammatical subject, including a rating.
- Smallest repair: make the check "no banned word, no sentence whose subject is this text, no clause that says a worry is settled", and let a limit carry the reason against the alternative that N3 asks for.

### N3 — damaged

- Attack 1: succeeded. A project-specific reason can still be incomplete. PWC:242: "A revert commit would make git treat the story's commits as merged, and a second attempt would bring in nothing." Git's documented answer to that problem is to revert the revert before the second attempt. The reason holds only if nobody does that, and the text does not say so. The rule's check passes it. The rule also lets the writer leave out the strongest alternative, because "a reader would expect it" is the writer's own call.
- Attack 2: succeeded. The check demands a reason "that refers to this project". The best reason against the revert is a general fact of git, not of this project. Writing it as "a revert commit on `feature/login` would make git treat `story/ST-0350` as merged" adds project names to pass the check and makes the sentence harder to read.
- Attack 3: failed. No other rule asks for the reason against an alternative.
- Attack 4: succeeded. "A reader would expect it" depends on the reader. PWC:148 explains why reconciliation runs on `dev`, not on the feature branch. Reader A, the person who decides: the alternative is expected, keep it. Reader B, the engineer who knows the playbook: nobody proposed it, cut it under N1. The revert reason at PWC:242 also splits readers on "refers to this project", as shown under Attack 2.
- Attack 5: succeeded. The heading promises the "real reason", meaning the reason that actually decided the matter. The check tests only that the reason names the project. A made-up reason that mentions the project passes.
- Attack 6: succeeded. N3 conflicts with N2, as shown under N2 at PWC:384.
- Weakest point: the check tests where the reason points, not whether it is the reason that decided.
- Smallest repair: change the check to "each rejected alternative has a reason a reader can test: a fact with a source, or a cost in named units", and drop "refers to this project".

## Patterns

Most checks test a surface form, such as the presence of a source, an absolute word, a keyword, or a grammatical subject, while the rule promises a property of the content. Every rule that turns on the reader's need or expectation breaks down because R0 names two or more readers and no rule says whose judgment counts. The present tense carries both existing facts and the target state, so T1 and T4 flag the same sentences for different reasons. Several conflicts come from one missing rule: where a fact that this text does not own belongs, whether it is a deferred matter, a primer restatement, or a link. The proposal itself breaks T3 with real IDs that look made up, which shows the rule cannot be checked by its own writer.
