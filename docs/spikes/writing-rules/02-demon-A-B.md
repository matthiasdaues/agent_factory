# Demon round 1: claims C00 to C09

Line numbers refer to `input/proposal-working-copy.md` unless a claim source is named.

### C00 — damaged

- Attack 1: succeeded. The check tests only the first half of the rule ("true"), not the second ("what the reader needs"), and it passes statements that are true but chosen to mislead. Invented, built on line 262: "`premerge-check` passed on every story merged this month." Each word can be checked in the session. The sentence still hides that `premerge-check` skips the semantic gates on every branch not named `story/ST-NNNN`, so "passed" says little. Every statement has a source, and the text is still written without regard for the truth the reader needs.
- Attack 2: failed. The real unmarked claim at line 384, "A gate fix is usually small", reads more honestly with the mark ("unchecked; the diff sizes of past gate-fix commits would settle it"), so breaking the rule does not help here.
- Attack 3: failed. C15 covers tools and services only. Statements about repository state, such as "This repository holds six old ledgers" (line 88) or "Three sources name three different owners" (line 94), fall under C00 alone.
- Attack 4: succeeded. The check asks for a source for "each statement", but a proposal is mostly design. Line 141: "One run may be active per feature branch." Reader A says this is a decision, true because the proposal says so, and needs no source. Reader B says it is a statement, has no source, no check, and no mark, so it fails. The rule does not say which statements are claims of fact.
- Attack 5: failed. "Write only what you know to be true" is plain, and the check turns "know" into something a reader can test.
- Weakest point: the check counts sources per statement, so true statements arranged to mislead pass, and design statements have no defined status.
- Smallest repair, if damaged or refuted: limit the check to statements about the present world (code, repository, tools, people) and add "no statement leaves out a fact that would change the reader's conclusion".

### C01 — damaged

- Attack 1: succeeded. The persona has five traits, but the check tests only one: whether needed facts are present. A text full of idioms, or one that only makes sense on a second reading, passes. Line 278 also shows that "behind a link" lets insider knowledge through: "a `fixed` row about an artifact on the core list in `rulebooks/core-artifacts.yaml`" names a path. The reason a fixed row blocks the wave is never given. The reader has a pointer and no reason, and the check passes it.
- Attack 2: succeeded, at an edge. The rule applies to every text, including commit messages (user instructions say so). Obeying version: "fix: make premerge-check, the script that checks a branch before a merge, read findings from the branch head". Breaking version: "fix: premerge-check reads findings from the branch head". The real reader of `git log` in this repository knows `premerge-check`. The second version is clearer, and the first pads.
- Attack 3: failed. C06 and C27 catch undefined terms and opaque references, but not a missing step or a missing reason, such as the one at line 278.
- Attack 4: succeeded. Line 72: "The test-strategy agent sets the gates and the number of attempts." Reader A says a newcomer must know what the test-strategy agent is before acting, so the fact is missing. Reader B says the name explains its job, so nothing is missing. "Every fact the reader needs to act" depends on which act the reader takes, and the rule does not name it.
- Attack 5: failed. The persona is concrete and each trait is a real reading condition.
- Weakest point: one fixed reader for every kind of text, checked by a test that covers one of the five traits.
- Smallest repair, if damaged or refuted: name the reader per artifact type, keep the newcomer for proposals and specifications, and let the check name the action the reader must take.

### C02 — damaged

- Attack 1: succeeded. Line 145: "The finding's `artifact` serves the overlap planning in place of a story's file list." It has 14 words, one main clause, and the active voice. The reader still reads it twice, because "serves the overlap planning" hides the act: `dispatch plan` reads the field to decide which units of work may run in parallel. The rule also invites a second fault. Line 72 is a run of short, compliant sentences that introduce six agents in a row, and the reader must hold all of them. C23 names that fault, and C02 pushes toward it.
- Attack 2: failed. The long sentences in the text split cleanly. For example, line 141 ("`init` refuses only when ... since both would need the primary checkout", 33 words, passive "is started") reads better as three sentences.
- Attack 3: failed. No other claim counts length or clauses.
- Attack 4: succeeded. The rule says "one idea", and the check counts main clauses. Line 99: "After `dispatch close`, nothing of the run remains except unmerged branches and named stashes, which the human handles." It has one main clause. Reader A counts one idea, what remains. Reader B counts three: the close removes the state, two kinds of things stay, and the human handles them.
- Attack 5: failed. "Under 25 words" is an arbitrary limit, but the rule states it as a limit and claims nothing more.
- Weakest point: "one idea" is not countable, and the clause count that replaces it lets dense, opaque sentences through.
- Smallest repair, if damaged or refuted: drop "one idea" and keep the measurable parts: one main clause, active voice, under 25 words.

### C03 — damaged

- Attack 1: succeeded. Line 145 again: "The finding's `artifact` serves the overlap planning in place of a story's file list." The sentence has a subject and a verb and parses as English. It is still compressed, and the reader must decode "serves the overlap planning".
- Attack 2: succeeded. The table cell at line 154 is a fragment: "The implementation agent, wave by wave." The complete version is "The implementation agent starts a story, wave by wave." That version repeats the row header in every cell and makes the table harder to scan. The list at lines 181–184 ("- before a story starts;") is a run of fragments with semicolons. It reads more clearly than four complete sentences would.
- Attack 3: failed. C02 targets tangled sentences, and C03 targets compressed ones. These are different faults.
- Attack 4: succeeded. Lines 179–184. Reader A says each item completes the lead sentence "It stops at every point where a person decides", so the whole thing is one sentence and complies. Reader B says each item is a fragment and the semicolons form a chain, so it fails.
- Attack 5: failed. The wording is concrete: fragments, articles, arrows, semicolons.
- Weakest point: the rule is written for running prose and gives no status to table cells or list items.
- Smallest repair, if damaged or refuted: exempt table cells and list items that complete a lead sentence, and add "names the act, not a stand-in for it" to the check.

### C04 — damaged

- Attack 1: failed. I found no text that uses plain nouns and verbs and still makes a simple act sound grand. The principle slogans at lines 98–103 are plain in their words, and their fault is a different one.
- Attack 2: succeeded. Line 211: "The test-strategy agent owns the gates, their thresholds and their commands." "Owns" names no act, so it fails the check. A version that names acts is "The test-strategy agent writes and changes the gate entries in `docs/testing.yaml`." It is longer and loses the point that no other agent changes them. "Owns", "belongs" (line 264), and "depends" (line 240) name relations, and the plain relation word is the clearest choice.
- Attack 3: failed. C07 covers adjectives such as "robust", and C09 covers drama. Neither covers register swaps such as "preserve" for "keep", which only C04 catches. The example "fix, not lock" is shared with C09.
- Attack 4: succeeded. Line 238: "the story carries on in the same run." Reader A says "carries on" is plain. Reader B says nothing physical happens, so it fails. Almost every verb in software ("refuses", "files", "reads") fails a literal reading of "physically happens". Readers will split on each one.
- Attack 5: succeeded. In software, the check word "physically" points at something that does not exist. The check claims a test that no reader can apply as written.
- Weakest point: the check demands physical events from a domain made of relations and state.
- Smallest repair, if damaged or refuted: change the check to "no plainer word has the same meaning".

### C05 — damaged

- Attack 1: succeeded. The check tests one direction only: that no concept has two names. It passes one name for two concepts. In the text, "close" names the end of a run (heading "Close", line 284, `dispatch close`) and the end of a wave (heading "Wave close", line 276, `dispatch close-wave`). A reader who follows the link "as [Close](#close) describes" from step 7 lands correctly, but "the close" in later prose can point to either. The rule's own fault, the reader confusing two things, happens here, and the check passes it.
- Attack 2: succeeded, at an edge. Line 72: "it spawns, or starts, a fresh developer agent" gives one concept two names on purpose, and the second-language reader gains from it. Plain term and identifier pairs work the same way: "returning a story" (line 74) and `dispatch return-story`. Naming both is clearer than forcing one.
- Attack 3: failed. No other claim covers term consistency.
- Attack 4: succeeded. Line 146 says "the feature merge check", line 266 says "`premerge-check dev <feature-branch>`", and line 360 says "the feature merge check in `premerge-check`". Reader A says these are one concept with two names, so the text fails. Reader B says the first is the concept and the second is the command that runs it, so the text passes. The rule does not say whether a command and the concept it implements count as one concept.
- Attack 5: failed. The wording is plain and states its reason.
- Weakest point: the check misses one name for two concepts and does not decide how a term relates to its identifier.
- Smallest repair, if damaged or refuted: add "and no term names two concepts", and allow a term to be paired with its identifier or a gloss.

### C06 — damaged

- Attack 1: succeeded. Line 120 defines a term at first use and still leaves the reader with jargon: "drift session | The spawn of an owner, or of that owner's reviewer, to settle one row of a spec-feedback report." "Owner" (owner of what?) and "row" are not defined. The rule is obeyed, and the term stays unknown.
- Attack 2: succeeded, at an edge. "Spawn" is a trade term in process and agent tooling. Line 72 still glosses it: "it spawns, or starts, a fresh developer agent". For the second-language reader, the glossed version is clearer than "it spawns a fresh developer agent", which is the version the rule wants.
- Attack 3: failed. C22 overlaps on placement, but it does not cover "do not define trade terms" or abbreviations.
- Attack 4: succeeded. Line 90: "A function with a CRAP score of 42 against a threshold of 30". Reader A says CRAP is a published trade metric, so a definition would pad. Reader B says most engineers do not know it and cannot judge the numbers without a definition. "Fagan" (line 270), "arc42" (line 351), and "TDD" (line 194) split readers the same way.
- Attack 5: failed. The rule states its reason ("helps the speaker, not the receiver" at FV 64–65).
- Weakest point: the line between trade term and project term is left to the writer's own knowledge.
- Smallest repair, if damaged or refuted: define a trade term as one a capable engineer finds in a standard reference, and require every definition to use only words the reader already has.

### C07 — damaged

- Attack 1: succeeded. Line 377: "YAML and prose gates are a separate concern." None of the listed words appear, and the search passes. "A separate concern" sounds settled and says nothing about where the work goes, unlike the other deferred items, which each name a proposal.
- Attack 2: failed. In this domain, each listed word has a plainer equivalent. The one technical sense, "ensures" meaning "creates if missing", reads better as written out (line 162 does this).
- Attack 3: failed. C04 covers nouns and verbs. C07 also covers adjectives ("robust", "seamless", "comprehensive"), which C04 leaves open.
- Attack 4: succeeded. The list is checkable, but "their kin" is not. Line 84: "This proposal defines one lifecycle for a run". Reader A says "lifecycle" is a trade term, as in object lifecycle. Reader B says it is a kin of the listed words and stands in for "the steps from start to end".
- Attack 5: failed. The fault label "buzzword bingo" is an idiom, but the working wording, "words that sound important and say little", is plain.
- Weakest point: a word search finds the listed words, and the fault lives in unlisted words that the search cannot reach.
- Smallest repair, if damaged or refuted: keep the search for the list, and test every other suspect word with C04's test: does a plainer word keep the meaning?

### C08 — damaged

- Attack 1: succeeded. Line 72: "On the human's go, the implementation agent starts a story." "The human's go" appears on ten lines, also as "after the human's go" (lines 72, 74, 154, 158, 168, 169, 172, 186, 400, 420). General dictionaries list "go" as a noun meaning a turn, so the phrase passes the check. A second-language reader can read "on the human's go" as "while the human goes" or "on the human's turn". The text means "after the human approves".
- Attack 2: succeeded. The rule calls "smoke test" a fake technical term for "check". Breaking version: "Run a smoke test after the deploy." Obeying version: "Run a check after the deploy." "Check" loses the meaning: a shallow, broad test that runs before deeper testing. Unchecked: I believe the ISTQB glossary defines "smoke test", and reading that glossary would settle it.
- Attack 3: failed. No other claim covers idioms, or "actually", "even", and "just".
- Attack 4: succeeded. Line 70: "In a run by hand, stories run one at a time". Reader A says "by hand" is in the dictionary as "manually", so it passes. Reader B says "by hand" is an idiom for manual work, so it fails. Dictionaries list most idioms, so the check cannot tell readers which reading is right.
- Attack 5: failed. The operative wording is plain. Its defects, the wrong example and the dictionary check, are counted above.
- Weakest point: a dictionary check passes the idioms that the rule exists to catch.
- Smallest repair, if damaged or refuted: change the check to "a reader who knows only each word's first dictionary sense reads the phrase correctly", and replace the smoke-test example.

### C09 — damaged

- Attack 1: failed. I found no text that uses neutral words and still tells a simple thing as an event. The drama in the text sits in words such as "destroy", which the check reaches.
- Attack 2: failed. Where a strong word carries meaning, the check keeps it: "destroy" in line 74 carries "cannot be undone", which a neutral swap would lose, so the rule allows it.
- Attack 3: failed. C04 shares the "lock" example but covers only nouns and verbs. C09 also covers adverb phrases such as "never changes again".
- Attack 4: succeeded. Line 329: "Both commands destroy work". Reader A says to replace "destroy" with "delete", because the meaning is kept and the drama is gone. Reader B says the meaning is lost, so "destroy" stays. The text cannot settle it, because it never says what `dispatch return-story` deletes. Line 419 says only that it sets the story to `pending`, and line 188 lists returning a story as a way to undo a step. Whether the strong word keeps its meaning depends on a fact the reader does not have.
- Attack 5: succeeded. The rule's own examples change meaning. "Is read-only" (a permission) does not mean "never changes again" (immutability). A git commit, for example, is immutable, not read-only. "Locked" in a query context can mean a database lock, a real technical state, and "fixed" does not mean that. So the rule claims a swap that keeps meaning and shows two swaps that do not.
- Weakest point: the examples model swaps that change the meaning, and the check needs a fact that a dramatic sentence usually leaves out.
- Smallest repair, if damaged or refuted: replace the examples with true equivalents, and change the check to "state the fact first, then use the plainest word that states it".

## Patterns

Most successful attacks hit the check, not the rule. The checks test something nearby (a word list, a dictionary, a clause count, "physically happens") that the fault slips past. Three rules (C04, C08, C09) carry examples that are wrong or change meaning, so the examples teach the opposite of the rule. Tables, lists, commit messages, and identifiers fall outside rules written for running prose to one newcomer. The proposal also breaks several of these rules where it was meant to follow them: "semantic gates" is never defined (lines 262, 426), "on the human's go" is an idiom, and "destroy work" (line 329) contradicts line 188.
