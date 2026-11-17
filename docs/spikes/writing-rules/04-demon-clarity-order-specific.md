# Demon, round 2: Clarity, Order, Specific texts

Register under attack: `03-rules-round1.md`, rules C1–C4, O1–O6 and S1–S4. Each rule is read as the claim that a writer who follows it produces text the reader can trust, needs, and can act on, and that its check tells a reader whether a text obeys it.

Line numbers marked "proposal L" refer to `input/proposal-working-copy.md`. Line numbers marked "conversation L" refer to `input/conversation-run-lifecycle.md`.

### C1 — damaged

- Attack 1: succeeded. The rule asks for one meaning per term, not for a meaning with edges. Proposal L111 defines a run as "Everything the Factory does for one feature branch, from `dispatch init` to `dispatch close`." Reconciliation works on that feature's code, yet proposal L148 puts it "outside the run". The term has one meaning and passes the check, and the reader still cannot tell whether a given step belongs to the run.
- Attack 2: succeeded. Proposal L123 lists the old words for the same meanings: "automated mode, manual mode, mechanized dispatch, invocation branch, gate-check loop, drift report, main checkout." That breaks "one meaning, one word". Without the list, an engineer who meets "manual mode" in an old ADR cannot map it, and the criterion at L435 cannot be written.
- Attack 3: failed. No other rule in the file asks for one term per meaning.
- Attack 4: succeeded. Proposal L84 says "the commands that need a person", L179 says "every point where a person decides", and the rest of the text says "the human". Reader A: "a person" and "the human" are two words for one meaning, so the text breaks the rule. Reader B: "a person" is ordinary English, not a project term, so the check does not list it. The rule does not say which words count as terms. The same gap decides whether "CRAP score" (L90, never defined) is a trade term or a project term.
- Attack 5: succeeded. "One word, one meaning" claims every word, and no English text can obey that. The proposal uses "run" as a defined noun and "runs" as a plain verb in the same sentence: "The implementation agent runs the gate-check step" (L197) inside a section about a run. The check narrows the rule to "terms", but the rule text does not.
- Attack 6: succeeded. Conflict with C2. C2 says to use the plainest word that keeps the meaning. Proposal L118 defines "spawn" as "Starting one agent", so C2 tells the writer to write "start". Then "start" means two things: to start a story (L154) and to start an agent. Proposal L72 shows the writer caught between both rules: "it spawns, or starts, a fresh developer agent." The text cannot keep one word per meaning and also use the plainest word.
- Weakest point: the rule never says which words are project terms, so its check has no fixed list to run on.
- Smallest repair, if damaged or refuted: limit the rule to project terms, say that each definition must decide membership in borderline cases, and allow a list of the old names a term replaces.

### C2 — damaged

- Attack 1: succeeded. Plain words can still say nothing. Proposal L84: "The two ways differ only in who starts a story, whether stories run in parallel, and who runs the commands that need a person." No plainer word exists for "the commands that need a person", so the clause passes. It names no command, so the reader cannot act on it. The exact names, `dispatch return-story`, `dispatch close` and `dispatch close --drop`, only appear 100 lines later.
- Attack 2: succeeded. Proposal L242: "`dispatch merge-story` moves the feature branch back to the commit before the merge." The plain verb hides a git reset, and the guardrail refuses agents `reset --hard` (L320). An engineer cannot tell whether the step will be refused. The technical version breaks C2 and answers the question: "`dispatch merge-story` resets the feature branch to the commit before the merge. The script runs the reset itself, so the guardrail never sees the command." The second sentence is from conversation L433 and did not reach the proposal.
- Attack 3: failed. N2 catches rating words only; C2 also catches inflated words that rate nothing, such as "utilize".
- Attack 4: succeeded. Proposal L118 defines "spawn" as "Starting one agent." Reader A: "start" keeps the meaning, so "spawn" must go. Reader B: "spawn" says that the agent is a new process with no memory, which "fresh developer agent" (L72, L196) depends on, so "start" loses meaning. "Keeps the meaning" is exactly what the two readers disagree on.
- Attack 5: succeeded. "A reader who knows each word's first dictionary sense" sounds like a test and is not one. Dictionaries order senses differently: some by history, some by frequency. The idiom "on the human's go" (L70, L72, L154) passes or fails depending on which dictionary the checker opens.
- Attack 6: succeeded. Conflict with C1, shown under C1 with "spawn" and "start".
- Weakest point: plainness and precision pull apart, and the rule names no way to choose when the plain word hides the mechanism.
- Smallest repair, if damaged or refuted: keep the technical word when the plain word hides which command, file, or state is meant, and replace the dictionary test with "a reader who knows the trade but not the project".

### C3 — damaged

- Attack 1: succeeded. Short, complete, active sentences in a row can lose the order of events. Proposal L72: "The implementation agent then runs the gates, automatic checks such as the dependency check. For each failure, it spawns, or starts, a fresh developer agent. The test-strategy agent sets the gates and the number of attempts." Every sentence obeys C3. The third sentence reads as the next step, but the test-strategy agent acts before the run, not after a failure.
- Attack 2: succeeded. Proposal L242: "The feature branch is not shared yet, so nobody has built on the failed merge." It has two main clauses, so it breaks "one main clause". The obeying version is "The feature branch is not shared yet. Nobody has built on the failed merge." The split drops the cause, and the reader must rebuild it.
- Attack 3: failed. No other rule sets sentence length or completeness.
- Attack 4: succeeded. Proposal L195: "It writes its report to `docs/reviews/code-review-<story-id>-YYYY-MM-DD.md`, so two stories reviewed on the same day do not collide at the merge." Reader A reads "so" as "so that", a subordinate clause, and the sentence has one main clause. Reader B reads "so" as "therefore", a second main clause, and the sentence breaks the rule. The list exemption splits readers too. Proposal L296 is one list item that holds a fragment and then two full sentences: "Before it removes a worktree, it stashes ... Git keeps stashes in the repository, not in the folder, so they survive the removal". One reader exempts the whole item, the other exempts only the fragment.
- Attack 5: succeeded. The rule makes four demands: complete, active, under 25 words, one main clause. The check tests two: word count and a missing subject or verb. A passive sentence such as "Every file a run creates is removed at its close" (L102) passes the check and breaks the rule.
- Attack 6: succeeded. Conflict with C4. C4 allows "so" for a real cause. Joining two clauses with "so" makes two main clauses, which C3 forbids. Proposal L242 cannot obey both: C4 accepts it, C3 rejects it.
- Weakest point: "one main clause" bans the very "X, so Y" sentence that C4 permits.
- Smallest repair, if damaged or refuted: drop "one main clause", keep the word limit and the subject-and-verb test, and add "active voice where the actor is known" to the check.

### C4 — damaged

- Attack 1: failed. Every "so", "because" and "then" in the proposal I tested names a cause or an order. The reassuring "So nothing in the middle of a run reads the backlog" (L240) is N2's fault, and C4 neither causes it nor claims to cure it.
- Attack 2: succeeded. Two breaks read better than the obeying version. First, "so" for a purpose: "so two stories reviewed on the same day do not collide" (L195) names neither a cause nor an order. It is clear. Second, independent items in prose: "This repository holds six old ledgers, thirteen worktrees besides the primary checkout, and 36,109 files under `.current-work/`." (L88). A three-line bullet list of those counts would be longer and no clearer.
- Attack 3: failed. No other rule checks linking words.
- Attack 4: succeeded. The rule says "real cause", and the check says "a cause that the text states". Proposal L213: "The OWASP review ... stays in QA, at the feature level, because the flaws it finds usually lie in how stories fit together." Reader A runs the check: the text states a cause, so it passes. Reader B runs the rule: "usually" has no source, so nobody knows if the cause is real. The same split applies to L242, which only a reader who knows how git treats a reverted merge can judge.
- Attack 5: succeeded. The rule names three words and leaves the act unfenced. "Since" (L156), "therefore" (L240) and "so" all claim a cause, but only "so" falls under the rule. A writer can keep a false cause by switching to "therefore".
- Attack 6: succeeded. Conflict with C3, shown under C3 with L242.
- Weakest point: the rule names words instead of the act of claiming a cause, and its check accepts any stated cause.
- Smallest repair, if damaged or refuted: apply the rule to any word that claims a cause or a purpose, require that the cause is sourced or follows from the text, and drop "put independent items in a list".

### O1 — damaged

- Attack 1: succeeded. The demand that the last sentence add a new fact leads writers to put a limit at the end. Proposal L225 closes the section on fast gates with "`dependency-check` reads Python imports only." The section obeys O1. Yet the limit decides whether the hook does anything in a TypeScript project, and the reader meets it last.
- Attack 2: succeeded. Proposal L72 opens a primer paragraph with an example: "Take a run by hand on a feature branch named feature/login." It breaks "opens with its point". It is clearer than a point-first version, "A run by hand uses the same steps and checks as an orchestrated run", because the newcomer does not yet know what those steps are.
- Attack 3: failed. O2 and S4 govern only primers and motivations, and O1 covers every section.
- Attack 4: succeeded. Proposal L240 opens with "The run checks the dependency tree against the backlog once, at its start." Reader A: that is the point, so the paragraph obeys. Reader B: the point is the sixth sentence, "A returned story therefore holds back the stories that depend on it, and through them the whole chain behind it", because that is what the human must act on. The rule also does not say if "a section" includes a paragraph.
- Attack 5: failed. The wording is concrete; its vagueness is the "point" problem of attack 4.
- Attack 6: succeeded. Conflict with S4 and O2. S4 orders a primer as situation, problem, idea. O2 makes the first sentence name a person. O1 makes the first sentence the point. Proposal L66 obeys S4: "The Agent Factory is a set of AI agents and scripts that build software from a backlog of stories." The point of the primer, that a run gets one lifecycle with an end, comes in L70 and L80. A primer cannot open with the situation and with the point at once.
- Weakest point: primers and motivations follow a different order by the file's own rules, and O1 does not exempt them.
- Smallest repair, if damaged or refuted: exempt primers and motivations, and say that a limit on scope belongs in the first paragraph, not the last sentence.

### O2 — damaged

- Attack 1: failed. A first sentence that names a person and what the person sees adds no needless or false content by itself; an invented scene is T1's and T3's to catch.
- Attack 2: succeeded. Proposal L66 breaks O2: "The Agent Factory is a set of AI agents and scripts that build software from a backlog of stories." The obeying version would be "A developer who lists the worktrees sees thirteen of them besides the primary checkout." A newcomer does not know what the Factory, a worktree, or a run is, so the obeying version is less clear.
- Attack 3: succeeded for primers. S4 already puts the situation first in a primer. For a motivation, O2 adds a demand that no other rule makes, so that half stands.
- Attack 4: succeeded. "The implementation agent finds six old ledgers and treats them as active runs." Reader A: an agent is the one who meets the situation in this project, so the sentence passes. Reader B: an agent is not a person, and the rule says "a person". Proposal L88, "The Factory defines how a run starts, but not how it ends", fails for both readers, though it is the clearest opening the Motivation could have.
- Attack 5: failed. "Outside in" is a metaphor, but the rule's body says what it means.
- Attack 6: succeeded. Conflict with O1, shown under O1.
- Weakest point: a reader who does not yet know the system cannot use a scene inside it.
- Smallest repair, if damaged or refuted: apply the rule to the motivation only, and allow the first sentence of a primer to say what the system is.

### O3 — refuted

- Attack 1: succeeded. The check tests that classes are named, not that they sort the list. "The guardrail checks fall into two classes: safety and process." Placed before the eight items at proposal L320–L327, this sentence passes the check. It tells the reader nothing about which item is which.
- Attack 2: succeeded. Proposal L76 gives the reason after a rule that goes against common practice: "When tests fail after a merge, the usual fix is a revert commit. The proposal moves the feature branch back instead, because a revert makes git treat the story as merged, and a second attempt would bring in nothing." The reason-first version is "A revert makes git treat the story as merged, so a second attempt brings in nothing. The proposal therefore moves the feature branch back." The original is at least as clear and names the decision earlier.
- Attack 3: failed. No other rule asks for classes before a list.
- Attack 4: succeeded. "Long list" and "common practice" have no measure. Proposal L295–L300 lists six things that `dispatch close` removes, with no classes. Reader A: six items is long, so it breaks the rule. Reader B: six items is short, so it passes. On a local branch, resetting is also common practice among git users, so the readers can disagree on whether L76 even needs a reason.
- Attack 5: succeeded. The rule joins two unrelated rules under one ID, and its check tests only the first. Nothing checks the order of reason and rule.
- Attack 6: succeeded. Conflict with O1. When a rule goes against common practice, O3 wants the reason first, and O1 wants the point first. In proposal L76 the point is "The proposal moves the feature branch back instead." A paragraph cannot open with both the reason and the point.
- Weakest point: the second sentence fights O1 and has no check, and the first sentence's check accepts empty class names.
- Smallest repair, if damaged or refuted: cut the sentence on reasons, and rewrite the rest as "A list of more than seven items is preceded by a sentence that names the groups, and every item belongs to exactly one group."

### O4 — damaged

- Attack 1: succeeded. The demand that every link say "whether the reader needs it now" adds a clause to every link. Proposal L144 has "as [Wave close](#wave-close) describes", which says what the target holds. The obeying version adds padding: "as [Wave close](#wave-close) describes; you need it before the next step." That clause is a fault that N1 then has to cut.
- Attack 2: succeeded. Proposal L200 restates a fact whose home is L175 and L198: "It never runs a gate script and never sets `status: done`." This breaks O4. The sentence sits in the story workflow, where a reader writing the developer agent's instructions looks. Replacing it with a link sends that reader to the ledger section for a rule about the developer agent.
- Attack 3: failed. No other rule limits repetition.
- Attack 4: succeeded. Proposal L188 and L327–L329 both say that the guardrail refuses only `dispatch return-story` and `dispatch close --drop`. Reader A: one fact twice, so the text breaks the rule. Reader B: L188 states a different fact, that a run by hand depends on the human watching, and only cites the refusal. "Needs it now" also has two answers, because the file's own preamble gives a proposal two readers: the person who decides and the engineer who builds.
- Attack 5: failed. The wording is concrete. Its weakness is the size of "a fact", covered in attack 4.
- Attack 6: failed. T5 puts each undecided matter in Open Questions, which could make it appear twice. The writer can resolve this by linking from the design to Open Questions.
- Weakest point: "a fact" has no size, so the check cannot count how often one appears.
- Smallest repair, if damaged or refuted: allow a restatement in the section where a named reader acts on the fact, and drop "whether the reader needs it now".

### O5 — damaged

- Attack 1: failed. Splitting proposal L382–L386 into five headings adds noise but no false or needless content. That cost is covered in attack 2.
- Attack 2: succeeded. Proposal L382–L386 puts five topics under the template heading "Design Details" with bold labels: "Cost.", "Bypass.", "Review coverage.", "Interrupted runs.", "The leftovers in this repository." Each topic has one to four sentences. Five `###` headings over one-sentence sections would break the flow without helping the reader find anything.
- Attack 3: failed. No other rule covers headings.
- Attack 4: succeeded. Proposal L284 has the heading "### Close". Reader A: the heading says the section holds how a run is closed, which is correct. Reader B: the section also holds `dispatch close --orphans` (L306), which cleans up runs from before this release, so the heading does not predict it. The rule also does not say whether a bold label such as "**Cost.**" counts as a heading.
- Attack 5: failed. The wording is concrete.
- Attack 6: failed. No other rule in the file sets the number or form of headings.
- Weakest point: "topic" has no size, so nobody can say when a topic needs its own heading.
- Smallest repair, if damaged or refuted: allow bold run-in labels for topics shorter than one paragraph, and require a heading of its own for content that a link elsewhere points to.

### O6 — damaged

- Attack 1: succeeded. Present tense makes design statements look like statements about what exists, which T1 then requires to be sourced. Proposal L331: "It relies on refusing a command, which every tool's guard supports." Proposal L225: "`dependency-check` reads Python imports only." Both obey O6. The reader cannot tell if they describe today's tools, which need a source, or the target, which needs a completion criterion.
- Attack 2: failed. Each change sentence I tried that helps the reader, such as "`mark-done` is removed" (L175), is covered by the exemption for text that changes existing code.
- Attack 3: failed. No other rule covers tense or decision stamps.
- Attack 4: succeeded. The exemption "where it changes existing code" covers almost every sentence of a proposal that rebuilds `dispatch`. Proposal L329: "The last check is new." Reader A: the check is new code, so the sentence is allowed. Reader B: "new" describes history, not the target state, so the sentence is a record.
- Attack 5: succeeded. The check searches for dates, "decided" and "no longer". It misses "is renamed" and "becomes" (L325) and "The last check is new" (L329). It also flags example dates that are not stamps: "`premerge ST-0350 2026-11-20`" (L262) and "`run feature/login ST-0350 2026-11-24`" (L296).
- Attack 6: failed. Present tense in O6 and the present-tense trigger in T1 overlap, but a writer can obey both by sourcing each statement about existing things.
- Weakest point: the exemption for changes to existing code swallows the rule in any proposal that changes code.
- Smallest repair, if damaged or refuted: require "today" or a source on every sentence about existing behavior outside the Motivation, and replace the word search with "each sentence describes either the target or a marked present fact".

### S1 — damaged

- Attack 1: succeeded. Conversation L407–L413 has all four parts. The case: "Take ST-0350, a story at the Sonnet tier. `crap-score` fails". The outcomes: three rounds, or three more with Opus. The recommendation and the change: "ADR-0012 then changes to match the instructions." The reason is a selling claim with no source: "A stronger model often fixes what a weaker one could not, and three more agent runs cost less than your time to look at the story." S1 asks for a reason and does not ask that the reason be true.
- Attack 2: succeeded. Conversation L430 has the user's question: "Can we make the count configurable and use these 3+3 as default?" It has two options with different outcomes and none of the four parts. Anyone can answer it at once. A four-part version would bury the question.
- Attack 3: failed. No other rule covers decision questions.
- Attack 4: succeeded. Conversation L281–L284 gives the case "a feature with five stories. All five have merged into `feature/login`". Option A then describes a command and its checks, and option B describes who merges. Reader A: each option states its outcome for the case, so the part is present. Reader B: both options run the same checks on the same five stories, so the case shows no difference in outcome, only who runs the command. The rule does not say what counts as an outcome.
- Attack 5: failed. The wording is concrete.
- Attack 6: succeeded. Conflict with T3. S1 asks for "a case with real names". T3 says that an example with a real ID matches the real item, or else it uses an ID that does not exist. Conversation L407 uses ST-0350 as a Sonnet-tier story whose gate fails. The real `backlog/ST-0350.md` has `tier: standard` and `status: done`. A decision case is about a future that has not happened, so a real name cannot match the real item. The case must break S1 by using a made-up ID, or break T3 by using a real one.
- Weakest point: "real names" and "outcome" carry the rule, and neither is defined.
- Smallest repair, if damaged or refuted: ask for "a case built from the project's real kinds of items, with made-up IDs where the case is hypothetical", require the reason to meet T1, and exempt yes-or-no questions whose outcome the question itself states.

### S2 — damaged

- Attack 1: succeeded. The three states hide a skip. Proposal L225: without a rules file, the hook prints "`dependency-check: no docs/spec/dependency-rules.dsl, skipped`" and passes. A report that says "`dependency-check`: passed" obeys S2 and misleads the reader.
- Attack 2: succeeded. Proposal L207 runs `test-design-verify` only "when the story has a Test Design or Prior Tests section". The obeying report says "`test-design-verify`: not run", which suggests a missed step. A report that breaks S2 is clearer: "`test-design-verify`: does not apply, because the story has no Test Design section."
- Attack 3: failed. No other rule covers reports.
- Attack 4: succeeded. The check needs the task, which is not on the page. The file's preamble says each check "a reader can run on the page alone". A reader who holds the brief and a reader who does not will disagree on whether all required steps appear. The rule also does not say if a review report, which has findings and no steps, is a report in its sense.
- Attack 5: failed. The wording is concrete; its scope problem is part of attack 4.
- Attack 6: failed. N1 could cut a long list of passed steps, but a reader needs that list to see that nothing was skipped, so N1 keeps it.
- Weakest point: the check cannot run on the page alone, which the file's own preamble requires.
- Smallest repair, if damaged or refuted: add the states "skipped" and "does not apply", each with its reason, and require the report to name the task that set the steps.

### S3 — damaged

- Attack 1: succeeded. Proposal L388–L390 answers "what stays open" with "None." That obeys S3. Yet L215 holds an open condition: "If the trial in mutation-gate.md shows that it is too slow per story, it moves to the feature checks". The In item "The guidance by hand in the implementation agent" (L366) traces to criterion L400. That criterion names no setup, action or expected output that a test can run, so the trace passes and tests nothing.
- Attack 2: failed. S3 forbids no section, and every fixed question has an honest answer even when it is "none".
- Attack 3: succeeded for the trace. "Each In item traces to a completion criterion" is a case of T4, "Every promise has a test", because each In item is a promise. The question "what stays open" restates T5. The other fixed questions stand.
- Attack 4: succeeded. The In item "The document changes listed in Documents that change" (L370) covers twelve changes. Reader A: criteria L434 and L435 test the dispatch contract and the vocabulary, so the item traces. Reader B: the changes to ADR-0012, ADR-0029 and arc42 chapters 5 and 6 (L345–L351) trace to no criterion, so the item does not trace.
- Attack 5: failed. The list of questions is concrete, apart from "what happens afterwards".
- Attack 6: succeeded. Conflict with O4. O4 allows only the primer and the criteria to restate a fact. S3 requires an In list, and the In list restates the design. Proposal L361, "The configurable attempts with escalation, without the limit of one escalation per wave", restates L229, "`dispatch escalate` today lets only one story per wave escalate, and that limit is dropped." O4's check fails on the Scope section of every proposal that obeys S3.
- Weakest point: the trace half repeats T4 and accepts a criterion that cannot be run.
- Smallest repair, if damaged or refuted: cut the trace sentence in favor of T4, and add the Scope list to O4's exemptions or require In items to be links.

### S4 — damaged

- Attack 1: succeeded. The word band invites padding or cutting to fit. The proposal's primer (L66–L80) has 499 words, one below the ceiling. Proposal L74 restates the guardrail and L78 restates the order after the last wave, each from later in the text. A writer with 380 words of content must add 20 words to pass, and the check rewards that.
- Attack 2: succeeded. Proposal L72 uses the identifier `feature/login`: "Take a run by hand on a feature branch named feature/login." That breaks "no identifiers". It is clearer than the obeying version, "a feature branch for the login feature", because the reader sees the branch name that the rest of the proposal uses in L246, L395 and L427.
- Attack 3: failed. O2 overlaps with S4's first part, but S4's length, example and order demands appear nowhere else.
- Attack 4: succeeded. The check is an experiment with a reader, not a reading of the page, so two checkers with two test readers get two results. "Identifier" is also open. Reader A: `dev`, "dispatch" (L68) and "QA agent" are names of things, so they are identifiers. Reader B: only IDs such as ST-0350 are identifiers, so the primer passes.
- Attack 5: succeeded. "A primer is a map" is a metaphor in the place of a rule. "400–500 words" is false precision: the rule gives no reason for the band, and a small proposal cannot fill it without padding.
- Attack 6: succeeded. Conflict with C1. A primer that obeys S4 must define the terms it uses, because its reader knows nothing. Proposal L70 defines waves as "sets of stories that run in parallel". C1 allows a terms table only when it is the only home of the vocabulary, so the table at L109–L121 becomes illegal. The two homes have already drifted. L116 defines a wave as "A set of stories that start together. By hand, each story is a wave of its own", and a wave of one story does not run in parallel. The conflict with O1 is shown under O1.
- Weakest point: the check needs a test reader, so it cannot be run on the page, and the word band has no reason behind it.
- Smallest repair, if damaged or refuted: replace the band with "under 500 words", allow identifiers that the rest of the proposal uses, and replace the check with "every term in the primer is defined in the primer or is a trade term".

## Patterns

Most checks test that a part is present, such as a stated cause, named classes, a reason or a trace, and not that it does its job, so empty or false parts pass. Several rules are word lists, either the words to find (O6) or the words to police (C4), and writers pass by changing words. The file sets three rules for the first sentence: point first (O1), a person first (O2) and situation first (S4). It also sets two rules for the "X, so Y" sentence, banned by C3 and allowed by C4, so the rules collide where a writer meets them most often. Two checks cannot run on the page alone (S2, S4), which breaks the file's own preamble.
