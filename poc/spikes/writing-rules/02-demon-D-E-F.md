# Demon attacks on C20 to C41

Line numbers without a file name refer to `input/proposal-working-copy.md`. "Opened" means `input/proposal-opened-bb717678.md`, the version that passed the release check and went to `status: open`. "Conversation" means `input/conversation-run-lifecycle.md`.

## D. Order

### C20 — damaged

- Attack 1: succeeded. Line 304 ends the Close section with "The ledger holds nothing a later step reads." The check passes, because the last sentence is a fact. The sentence still only reassures the reader, which C12 forbids, and it repeats the principle at line 102. "Is a fact" lets almost any closing sentence through.
- Attack 2: succeeded. Line 76 opens with the situation, as C21 demands, and puts the point second: "When tests fail after a merge, the usual fix is a revert commit. The proposal moves the feature branch back instead, because…". The C20 version reads: "The proposal moves the feature branch back after a failed merge instead of making a revert commit, because…". The original is easier to follow, because the reader first learns what the usual fix is. C20 and C21 give opposite orders for the same paragraph.
- Attack 3: failed. C10 catches a closing flourish, but no other claim catches a buried point.
- Attack 4: succeeded. Step 1 at line 141 opens with "`dispatch init --mode orchestrated|by-hand` cuts the feature branch from `dev` and writes the ledger". Reader A says this sentence is the point. Reader B says the point is the concurrency rule in sentences 5 and 6 ("One run may be active per feature branch…"). The rule does not say how to find the point of a design paragraph.
- Attack 5: failed. The wording is plain and names an order a reader can see.
- Weakest point: the check of the last sentence accepts any fact, including a repeated or reassuring one.
- Smallest repair, if damaged or refuted: Apply the rule to messages and section openings only, and require that the last sentence adds a fact not stated before or names a step.

### C21 — damaged

- Attack 1: succeeded. Line 316 opens with "The git guardrail runs before every shell command an agent issues." The check passes, because "an agent issues a shell command" is a situation. Yet the paragraph is mechanism from its first word. "Situation" is broad enough that nearly every sentence names one.
- Attack 2: succeeded. Line 310 opens with the mechanism: "The ledger holds only fields that a command reads." The outside-in version would read: "When an implementer opens the ledger, they need to know which fields to keep. The ledger holds only fields that a command reads." The added sentence is padding. In a reference section, the mechanism-first sentence is clearer.
- Attack 3: failed. No other claim covers the order inside a paragraph, although C20 conflicts with it.
- Attack 4: succeeded. The same line 316 passes for Reader A, who sees an agent and a command, and fails for Reader B, who sees a component described from the inside.
- Attack 5: failed. The wording is concrete.
- Weakest point: the check accepts any sentence that mentions an actor, so it cannot tell outside-in from inside-out.
- Smallest repair, if damaged or refuted: Limit the rule to explanatory prose such as primers and motivation, and check that the first sentence names who meets the situation and what they see.

### C22 — refuted

- Attack 1: failed. I found no paragraph that obeys and still makes the reader hold a glossary in memory.
- Attack 2: succeeded. The Terms table at lines 107–121 defines eleven terms up front and breaks the rule. It is clearer than spreading the terms out. Line 123 maps old terms to new ones, and completion criterion 435 checks the vocabulary against that table. Broken up, the definitions would have no single place to check against.
- Attack 3: succeeded. C06 already requires each project term to be defined where the reader first meets it. A definition block placed before first use fails C06's check, because the first use carries no definition. C22 adds no case that C06 misses.
- Attack 4: succeeded. Primer line 70 defines "run", "orchestrated run", "waves", and "run by hand" in one paragraph. Reader A says the reader needs all four for the example in the next paragraph. Reader B says "waves" is not needed until line 78. The phrase "a term the reader does not yet need" decides the check.
- Attack 5: failed. The wording is plain.
- Weakest point: the rule repeats C06 and fails for a design document that must fix a vocabulary in one table.
- Smallest repair, if damaged or refuted: cut, and add to C06 that a terms table is allowed when it is the single home of the vocabulary.

### C23 — damaged

- Attack 1: succeeded. Line 240 says: "So nothing in the middle of a run reads the backlog… A returned story therefore holds back the stories that depend on it." The "therefore" links to the sentence about the backlog. The real cause is the sentence before: a story starts only when every dependency inside the run is `done`. The rule asks for links, and a link here asserts a cause that is wrong.
- Attack 2: succeeded. Line 229 states independent rules: "Both values live in `docs/testing.yaml`… A value of 0 for `gates.attempts_escalated` turns escalation off. The same counts apply on both ways. Every story that uses up its attempts escalates." These are separate rules, and the paragraph is clear as it is. A linked version ("So the same counts apply…") would invent a sequence that does not exist.
- Attack 3: failed. No other claim covers links between sentences.
- Attack 4: succeeded. Line 229 reads as a list for Reader A and as an argument for Reader B, who follows attempts to configuration to behavior. "Reads as an argument" is a judgment.
- Attack 5: succeeded. The fault says a paragraph of unlinked claims "says nothing". Line 229 says a great deal without links. The rule claims an effect that linking words cannot have.
- Weakest point: the rule rewards linking words even where no cause or sequence exists.
- Smallest repair, if damaged or refuted: Use "so", "because", or "then" only where the cause or the sequence is real, and present independent rules as a list.

### C24 — damaged

- Attack 1: failed. I found no list that obeys the map rule and still cannot be placed.
- Attack 2: succeeded. Line 242 states the rule first and the reason after it: "When the test suite fails after a story merges, `dispatch merge-story` moves the feature branch back…, and the story is `blocked`. The feature branch is not shared yet… A revert commit would make git treat the story's commits as merged…". Moving a branch back looks arbitrary to anyone who avoids rewriting history, so C24 demands the reason first. The reason-first version reads: "A revert commit would make git treat the story's commits as merged, and a second attempt would bring in nothing. The feature branch is not shared yet. So when the test suite fails, `dispatch merge-story` moves the branch back." The original is clearer, because the reader knows what the reasons are for.
- Attack 3: failed. C20 conflicts with the "reason before rule" part, but it does not cover the same ground.
- Attack 4: succeeded. Line 141 says: "By hand it creates none, because the run works in the primary checkout". Reader A says the rule looks arbitrary and the reason must come first. Reader B says the rule is plain and the order is fine. The qualifier "where the rule would otherwise read as arbitrary" decides the check.
- Attack 5: succeeded. The claim bundles three rules under one ID with one check. A text can pass the map rule and fail the reason rule, and the claim then has no verdict.
- Weakest point: "reason before rule" contradicts "point first, reason second" in C20, and the qualifier that decides between them is a matter of taste.
- Smallest repair, if damaged or refuted: Split the claim into three, and put the reason first only when the rule contradicts common practice.

### C25 — damaged

- Attack 1: failed. The working copy shows the fault the rule names. Line 318 merges the guardrail checks into "one set of checks in every session", while criterion 396 still says the guardrail "allows the commands that it refuses inside a run". The copy drifted, as the rule predicts.
- Attack 2: succeeded. Criterion 413 restates line 229: "a story whose gate still fails gets three attempts on its tier and three on the stronger tier, the first attempt included". A criterion that only links ("the attempts behave as Attempts and stops defines") cannot be checked without asking the author, and C32 forbids that. Breaking C25 here is clearer.
- Attack 3: failed. No other claim covers duplicates.
- Attack 4: succeeded. For line 413, Reader A says completion criteria are tests, not copies. Reader B says the criterion states the same fact as line 229. The check "no fact appears twice" does not say whether criteria count.
- Attack 5: failed. The wording is plain.
- Weakest point: every completion criterion restates a design fact, so the check fails every proposal unless criteria are exempt.
- Smallest repair, if damaged or refuted: Let the primer and the completion criteria restate a fact, and replace every other copy with a link.

### C26 — damaged

- Attack 1: failed. The specific headings ("Checks at the merge", "Close", "The ledger") predict what their sections hold.
- Attack 2: failed. "Design Details" at line 380 does not predict its content (cost, bypass, review coverage, interrupted runs, leftovers). A heading such as "Costs, limits and leftovers" would be clearer, so breaking the rule does not help here.
- Attack 3: failed. No other claim covers headings.
- Attack 4: succeeded. Reader A says "Design Details" passes, because the proposal template defines it as the place for anything the template does not ask for. Reader B says it fails, because nobody can say from the heading what it holds. `draft-proposal` step 2 makes this heading a catch-all, and the lector's sentence pass may not rename headings.
- Attack 5: failed. The wording is short and checkable.
- Weakest point: a template that prescribes a catch-all heading makes the rule fail by design.
- Smallest repair, if damaged or refuted: Exempt template headings from the check, and require a specific subheading for each topic under a catch-all heading.

### C27 — damaged

- Attack 1: succeeded. Line 196 says: "[finding-classification.md § Shared severity scale and blocking rule](%E2%80%A6) defines which findings block." The reference says what it holds, so the check passes. The reader still cannot act without opening the file, because the proposal never says which findings block. The named fault, "references that force the reader to open another file", stays. C25 tells the writer to link instead of restating, so the two rules pull in opposite directions.
- Attack 2: failed. Line 94 ("At the cap on attempts, ADR-0012 marks the story `blocked`") gives the content with the ID, and a bare ID would be worse.
- Attack 3: failed. No other claim covers references.
- Attack 4: failed. "As Scope states" at line 213 points to a section of the same file, and both readers would accept it.
- Attack 5: failed. The wording names a concrete fault and a concrete fix.
- Weakest point: the fault is stated wrongly, since a single home for a fact means the reader must sometimes open another file.
- Smallest repair, if damaged or refuted: Restate the fault as "a reference the reader cannot place", and check that the reader knows what the target holds and whether they need it now.

### C28 — damaged

- Attack 1: failed. I found no text that obeys and still makes the reader rebuild the design from its history.
- Attack 2: succeeded. Line 229 ends with "`dispatch escalate` today lets only one story per wave escalate, and that limit is dropped." The obeying version keeps only "Every story that uses up its attempts escalates." That sentence is already in the paragraph, and it does not tell the implementer that the code must change. Line 141 ("Today `init` refuses while any ledger anywhere is active") and line 262 ("Today it accepts only `story/ST-NNNN`…") work the same way. A proposal describes a change, and the change is part of what the reader must act on.
- Attack 3: failed. No other claim covers history in target-state text.
- Attack 4: succeeded. Line 310 says "The old value `automated` becomes `orchestrated`, and `invocation_branch` is renamed to `feature_branch`." Reader A says this sentence is target state, because it describes the migration the feature performs. Reader B says it is history. The search check also fails both ways: "becomes" and "renamed" are not on the list, and the dates in `premerge ST-0350 2026-11-20` (line 262) are example names, not history.
- Attack 5: failed. The wording is precise about stamps and history words.
- Weakest point: for a proposal, the current code is part of what the reader needs, and the rule treats it as history.
- Smallest repair, if damaged or refuted: Keep the ban on decision stamps and "who decided", and allow plain "today the code does X" statements in a proposal's Motivation and where the design changes existing code.

## E. Questions and structured artifacts

### C29 — damaged

- Attack 1: failed. The question at Conversation 1710–1724 has all four parts (case ST-0350, an outcome for options A, B, and C, a recommendation, and "This settles the ledger states"). The user rejected its premise at line 1729 ("Why do we need a new state?"). The four parts did their job, because the case let the user see that the premise was wrong.
- Attack 2: succeeded. Conversation 858 asks "Shall I commit the draft first as a checkpoint?" It has no case, no outcomes, and no statement of what the answer changes. It is clear as it is. Adding a case ("Take the draft at its current state…") would be padding. The rule covers every question that asks for a decision, including small procedural ones.
- Attack 3: failed. C27 covers bare option labels in references, but not the structure of a question.
- Attack 4: succeeded. Conversation 1757 uses the case "ST-0350, blocked because its merge hit a conflict in one file." ST-0350 is a real ID, but the conflict is invented. Reader A says the case comes from the project's own material, because the names are real. Reader B says it does not, because the event never happened. The voice's own example ("Task `nightly-billing`… is still `PENDING`") is invented too, so the rule does not settle the question.
- Attack 5: failed. The four parts are concrete and countable.
- Weakest point: the rule applies to every decision question, so a yes-or-no question about procedure needs four parts it does not need.
- Smallest repair, if damaged or refuted: Apply the four parts only to questions with two or more options whose outcomes differ, and say that the case may be invented if it uses real names.

### C30 — damaged

- Attack 1: failed. I found no question that obeys and still has an answer in the repository or floods the reader.
- Attack 2: succeeded. Conversation 1794–1800 asks "I am not sure what your 'no' rejects… Which one did you mean?" This question asks for the meaning of an answer, not for a decision. "Ask only for decisions" forbids it. The obeying version guesses a reading and writes it down, which is less honest. C19 demands exactly this question, so C30 and C19 conflict.
- Attack 3: failed. C00 and C15 cover facts stated in text, not questions asked.
- Attack 4: succeeded. Conversation 1923–1924 asks "Do you take A or B for the merge?" and "Do you accept my correction for dependencies outside the ledger?" Reader A sees one theme, the story merge rules. Reader B sees two themes, merge and dependencies. "Theme" is undefined, so the limit of one theme at a time cannot be checked.
- Attack 5: failed. The limit of five is arbitrary but checkable.
- Weakest point: the rule forbids the question that asks what the other person meant.
- Smallest repair, if damaged or refuted: Ask only for decisions and for the meaning of an answer you cannot read, and define a theme as the questions that change one section or one rule.

### C31 — damaged

- Attack 1: succeeded. The frontmatter answers "Which files change?" with a list at lines 15–45, and one entry is `docs/adr/`. The question is answered in form, but the entry names a folder, not files. The ADRs appear only at lines 345–346, in prose. An implementer who walks the table finds an answer and still has to search.
- Attack 2: failed. I found no artifact that skips an applicable question and is clearer for it.
- Attack 3: failed. C32 and C33 cover two rows of the table, not all nine.
- Attack 4: succeeded. The proposal has no section for "What commands verify completion?" or "When should the agent stop and ask?". Reader A says it fails both questions: only line 437 names a command, and no stop conditions exist. Reader B says the rule's own phrase "Apply the questions that fit its structure" exempts the proposal, because the template has no such sections.
- Attack 5: succeeded. "Each applicable question" lets the writer decide which questions apply. So a missing answer can always be called "not applicable", and the rule cannot fail.
- Weakest point: the writer decides which questions are applicable, so the check can always pass.
- Smallest repair, if damaged or refuted: Fix the required questions per artifact type in the rule, so "applicable" is no longer the writer's call.

### C32 — damaged

- Attack 1: succeeded. Criterion 396 says: "With `dev` checked out and a ledger of another branch under `.current-work/`, the guardrail allows the commands that it refuses inside a run." It names an observable state, so the check passes. Line 318 says the guardrail applies "one set of checks in every session", and line 402 says a merge without a marker is refused "in every session". A reviewer cannot tell which commands the criterion means without asking the author. Criterion 400 ("the implementation agent stops before each step… and waits for the human's go") also passes the check. It describes the behavior of a language model, so one passing run proves little. The session itself said so at Conversation 687: "An instruction to ask leaves no trace."
- Attack 2: failed. I found no criterion that is unchecked and still clearer.
- Attack 3: failed. C14 applies the same test to goals, not to criteria.
- Attack 4: succeeded. For criterion 396, Reader A takes "the commands that it refuses inside a run" as the list at lines 320–327. Reader B reads lines 318 and 323 and concludes the set is empty, because every check applies in every session.
- Attack 5: failed. The wording is plain.
- Weakest point: "names an observable state" passes a criterion whose state is ambiguous or whose behavior varies between runs.
- Smallest repair, if damaged or refuted: Require each criterion to name its setup, its action, and its expected result, and require a criterion on agent behavior to say how many runs count as a pass.

### C33 — damaged

- Attack 1: succeeded. Deferred item 377 says: "**Gates for documents.** YAML and prose gates are a separate concern." The check passes, because the item says something after "why". "A separate concern" gives no reason. The same text stands in Opened line 355, which passed the release check.
- Attack 2: failed. I found no scope item that breaks the rule and is clearer for it.
- Attack 3: failed. No other claim traces scope items.
- Attack 4: succeeded. Reader A accepts "a separate concern" as a reason. Reader B does not. The check "says why" does not say what counts as a reason.
- Attack 5: failed. The title says the scope "resists padding", but the rule body is a plain trace check.
- Weakest point: any phrase after the item name passes as a reason.
- Smallest repair, if damaged or refuted: Require each Deferred item to name what it waits for or which document owns it.

Note: In item 370 ("The document changes listed in Documents that change") traces to no criterion for ADR-0029, the branching policy, or arc42 chapters 5 and 6. The check would catch it. The proposal was opened without it, so the rule was not applied. That is not an attack on the rule.

### C34 — damaged

- Attack 1: succeeded. Line 390 says "None." under Open Questions, so the section holds only open items. Line 215 says "If the trial in mutation-gate.md shows that it is too slow per story, it moves to the feature checks". Line 260 says `mutation-testing` "keeps its stored result until mutation-gate.md settles how it runs". Both are undecided matters written as conditional design. The rule checks only the Open Questions section, and it pushes the writer to reach "None" by moving open items into the design text.
- Attack 2: failed. An undecided matter written as a deferral ("mutation-gate.md settles it") is allowed by the rule.
- Attack 3: failed. C33 covers deferrals in the scope, not undecided matters in the design.
- Attack 4: failed. Both readers would agree whether a listed question is decided.
- Attack 5: failed. "Genuine" is defined by the check.
- Weakest point: the check reads one section, and an open item outside that section is invisible to it.
- Smallest repair, if damaged or refuted: Require every undecided matter in the text, including a conditional such as "if the trial shows…", to appear in Open Questions with where its answer goes.

### C35 — damaged

- Attack 1: succeeded. Line 90 says: "A function with a CRAP score of 42 against a threshold of 30 can merge by hand". The 42 is made up for the example. The 30 matches the threshold commonly quoted for the original CRAP metric, a fact I did not check in this session. So Reader A finds a source for every number, and the check passes. `docs/proposals/crap-gate-setup.md` line 59 says the Factory has no built-in threshold. The number looks exact and is a guess for this project.
- Attack 2: failed. The obeying version, "A function above the CRAP threshold can merge by hand", is just as clear and does not invent a threshold.
- Attack 3: failed. C15 covers claims about tools, not numbers in general.
- Attack 4: succeeded. Reader A accepts general literature as the source of the 30. Reader B demands a source in this project and finds none. "Has a source" does not say which sources count.
- Attack 5: failed. "Use `unknown`" is plain, and the frontmatter at lines 53–59 follows it honestly.
- Weakest point: a number from general knowledge passes the check even when the project has a different value or no value.
- Smallest repair, if damaged or refuted: Require each number to come from this project's files or a run in the session, or to be marked as an illustration.

### C36 — damaged

- Attack 1: succeeded. The required order has a slot for "the alternative". Primer line 76 fills it with the revert commit, which is a detail of one step. The obvious alternative to the core idea, one lifecycle with an end, would be to keep two processes or to clean up by hand. The fixed order invites the writer to promote a detail into the slot.
- Attack 2: succeeded. Primer line 72 says "Take a run by hand on a feature branch named feature/login." "feature/login" is an identifier, and the rule forbids identifiers. The obeying version, "a feature branch for a login feature", loses the link to lines 246 and 427, where the proposal uses `feature/login` again. The identifier lets the reader recognize the example later.
- Attack 3: failed. C36 uses C21, C22, C23, C07, and C16, but its length, order, and running example are its own.
- Attack 4: succeeded. Reader A counts "feature/login" and the script name "dispatch" (line 68) as identifiers. Reader B counts them as plain names. The check, "a reader of the primer alone can explain the core idea", cannot be run from the text. It needs a test reader.
- Attack 5: failed. The limit of 400–500 words is a choice, not a claim about the world.
- Weakest point: the fixed order makes the writer fill every slot, even when the proposal has no real alternative.
- Smallest repair, if damaged or refuted: Make the alternative slot optional, and allow names the proposal uses again later.

## F. Process

### C37 — refuted

- Attack 1: failed. No text shows whether its writer applied the rules while writing.
- Attack 2: failed. No pair of texts shows that a cleanup pass beats writing-time application.
- Attack 3: succeeded. C37's source, FV 211–212, is part of C41's source, FV 209–228. C41 already contains the instruction.
- Attack 4: succeeded. The register says the claim is "not checkable from the text". Two readers cannot even disagree, because neither has anything to read.
- Attack 5: succeeded. The rule rejects a cleanup pass. The same paragraph of the voice then requires four gates and a final pass "before a text leaves the speaker", which is a cleanup pass. C38 and C39 are cleanup passes too. The rule contradicts the process it belongs to.
- Weakest point: the rule claims an effect on the text that no reader can observe, and the surrounding process contradicts it.
- Smallest repair, if damaged or refuted: cut from the register, and keep it as a process instruction if wanted.

### C38 — damaged

- Attack 1: succeeded. Opened line 72, written by a fresh primer agent and passed by a fresh lector, says: "The implementation agent then runs the gates, automatic checks such as the dependency check." In the trade, a dependency check usually means scanning third-party packages for known flaws. In this project it means checking imports against `dependency-rules.dsl`. A journeyman misreads it. Two fresh sessions let it pass, because a fresh language model shares the author's knowledge and blind spots. A fresh session is not a newcomer.
- Attack 2: failed. The working copy's primer was edited by the author after the lector pass. It is not released yet, and Conversation 1840 lists the lector pass as still to do. So the rule is not yet due.
- Attack 3: failed. No other claim covers who edits.
- Attack 4: succeeded. The repository holds `docs/handoffs/handoff-run-lifecycle-decisions-2026-11-16.md`, which records the conversation's decisions. Reader A says a lector that read this file had access to the conversation. Reader B says it had only files. "No access to the conversation" depends on what counts as the conversation.
- Attack 5: failed. The wording is plain.
- Weakest point: freshness removes the conversation but not the knowledge the newcomer lacks.
- Smallest repair, if damaged or refuted: Say that a fresh session reads only the document and the files it links to, and check trade terms that have a different meaning in the project.

### C39 — refuted

- Attack 1: failed. I found no text that obeys and still keeps a buzzword, because obeying cannot be seen in the text.
- Attack 2: failed. No pair of texts shows the effect.
- Attack 3: succeeded. C07 names the same fault, buzzword bingo, and its check searches the text for the same words. C39 is only the way to apply C07. Every fault C39 finds, C07 finds.
- Attack 4: succeeded. The register says the claim is "not checkable from the text".
- Attack 5: succeeded. The rule tells the writer to assume a fault before looking. FV 241 then has to add "A text with no such word leaves unchanged" to stop the rule from causing rewrites of sound text. The rule claims an effect on the text that only C07's search can deliver.
- Weakest point: the rule is a mindset, not a rule about text, and C07 covers its effect.
- Smallest repair, if damaged or refuted: cut, and keep the prompt as the procedure for applying C07.

### C40 — damaged

- Attack 1: failed. Code spans and commands in the proposal are kept exactly, and I found no fault the exemption invites.
- Attack 2: failed. I found no exempt span that is clearer when rewritten.
- Attack 3: failed. No other claim covers exempt text.
- Attack 4: succeeded. Line 225 says the hook "prints `dependency-check: no docs/spec/dependency-rules.dsl, skipped` and passes". Reader A says this is tool output and must stay byte-identical. Reader B says it is proposed design text, the message the tool does not print yet, and an editor may improve it. The rule does not say whether specified output counts as quoted output.
- Attack 5: failed. The list of exemptions is concrete.
- Weakest point: the rule does not separate quoted evidence from specified wording that only looks like code.
- Smallest repair, if damaged or refuted: Exempt quoted output only when it was produced by a run, and treat output a proposal specifies as design text that the author may change.

### C41 — refuted

- Attack 1: succeeded. Opened passed the four gates and the final pass before it went to `status: open`. It still holds "a separate concern" as a reason (Opened line 355) and an open question written as design (Opened line 202). The bundle let through faults that C33 and C34 name.
- Attack 2: failed. No text breaks the bundle as a whole.
- Attack 3: succeeded. The register itself says the claim has no fault of its own and bundles C01 to C36. Every claim it covers is already in the register.
- Attack 4: succeeded. Gate 1 adds a judgment that no other claim holds: "A peer master would… accept it as a pull request". For criterion 396, Reader A says a journeyman can start work. Reader B says the journeyman must ask which commands are meant.
- Attack 5: succeeded. The claim form says the text loses fault K, and C41 names no fault. The gate names "Junior Clarity / Senior Acceptance" and "Agent-Answerability" are invented labels that a reader must learn before they mean anything.
- Weakest point: the claim has no fault of its own, and its one addition, the senior's acceptance, is a judgment no one can check.
- Smallest repair, if damaged or refuted: cut from the register, and keep the gates as the procedure that runs the other claims.

## Patterns

Most checks accept any text that has the right shape, such as a fact at the end, an actor at the start, or a phrase after "why", so the shape passes while the fault stays. Several rules conflict with each other: C20 with C21 and C24 on order, C25 with C27 on links, and C30 with C19 on questions. Rules written for messages or primers fail when they are applied to reference sections, terms tables, and completion criteria. The process rules C37, C39 and C41 cannot be checked from the text, and they repeat claims that can. The released proposal still holds faults that C32, C33 and C34 name, which shows that following the rules does not make their checks pass.
