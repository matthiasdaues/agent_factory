# Writing rules, round 1

Motto: "The world is full of bullshit. Let us not add to it."

A text is bullshit when the reader cannot trust it, does not need it, or cannot act on it. The rules below cover these three faults in that order. Each rule has a check that a reader can run on the page alone.

The reader depends on the text. A proposal has two readers: the person who decides to accept it, and the engineer who joined last week and will build it. A chat message or a report has one reader: the person who asked.

## Trust

**T1. Source or mark every statement about what exists.** A statement about existing code, files, tools, people, or numbers names its source: a file, a command, or a document. Without a source, it carries a mark at the same place: "unchecked; run `X` to check". A marked statement does not carry a design decision until someone checks it.
*Check:* every present-tense statement about existing things has a source or a mark next to it. Every number has a source or is labelled as an illustration. *(C00, C15, C18, C35)*

**T2. No two statements contradict each other.** Words such as "every", "only", "never", and "all" make claims about the whole text. Test each such claim against the rest of the text.
*Check:* for each absolute word, search the text for an exception. *(new, U2–U8, U16, U17)*

**T3. An example matches the project or uses made-up IDs.** An example that uses a real ID matches the real item. Otherwise it uses an ID that does not exist. The example agrees with itself.
*Check:* look up each real ID the example uses. *(C16)*

**T4. Every promise has a test.** Each design statement a reader could rely on has a completion criterion. The criterion names its setup, its action, and its expected result.
*Check:* for each "does", "is", or "every" in the design, find the criterion that tests it. *(C14, C32, U5)*

**T5. Open matters are visible.** Every undecided matter appears in Open Questions, with the place its answer goes. This includes conditions such as "if the trial shows…" and limits with no threshold, such as "too slow". Open Questions holds nothing that is already decided.
*Check:* search the text for conditions and unmeasured limits, and find each one in Open Questions. *(C34, U10)*

## Need

**N1. Cut what the reader does not need.** The reader needs what helps them decide or build. Apply the test to clauses as well as sentences.
*Check:* delete the clause; if the reader loses nothing they need, it goes. *(C10)*

**N2. Write about the subject, not about the text, the design's merit, or the reader's worries.** Do not announce the structure ("This section explains…"). Do not use words that rate the design, such as "right", "clean", "robust", or "seamless". Do not write a sentence that only says a worry is settled. Say what the system does. State a limit as a limit, with no benefit attached.
*Check:* each sentence states a fact about the subject, a step, or a decision. *(C07, C11, C12, C13)*

**N3. Weigh an alternative only with its real reason.** Name an alternative only when a reader would expect it, and give the concrete reason against it.
*Check:* each rejected alternative has a reason that refers to this project. *(C12)*

## Clarity

**C1. One word, one meaning; one meaning, one word.** Define each project term where the reader first meets it, in words the reader already knows. A terms table is allowed when it is the only home of the vocabulary.
*Check:* list the terms. No term has two meanings, and no meaning has two terms. *(C05, C06, C22, U1, U9)*

**C2. Use the plainest word that keeps the meaning.** If a plainer word says the same thing, use it. An idiom passes only if a reader who knows each word's first dictionary sense reads it correctly.
*Check:* for each suspect word, try the plainer word and compare the meaning. *(C04, C07, C08, C09)*

**C3. Write complete, active sentences of under 25 words.** Running prose has a subject and a verb in each sentence, and one main clause. Table cells and list items that complete a lead sentence may be fragments.
*Check:* count the words, and look for a missing subject or verb. *(C02, C03)*

**C4. Use "so", "because", and "then" only for a real cause or sequence.** Put independent items in a list.
*Check:* each linking word names a cause or an order that the text states. *(C23, U12)*

## Order

**O1. Put the point first.** A message or a section opens with its point. Its last sentence adds a new fact or names a step.
*Check:* read the first sentence alone, then check the last sentence against the rest. *(C20)*

**O2. Explain from the outside in.** A primer or a motivation starts with who meets the situation and what they see.
*Check:* the first sentence names a person and what that person sees. *(C21)*

**O3. Name the classes before the list.** Give the reason before a rule only when the rule goes against common practice.
*Check:* each long list has its classes stated before it. *(C24)*

**O4. Give each fact one home.** Other sections link to it. The primer and the completion criteria may restate facts. A link says what its target holds and whether the reader needs it now.
*Check:* no fact appears twice outside the primer and the criteria, and each link is clear without being followed. *(C25, C27)*

**O5. Give each topic its own specific heading,** including topics that sit under a heading the template requires.
*Check:* from the heading alone, a reader can say what the section holds. *(C26)*

**O6. Describe the target state in the present tense.** Write no decision stamps and no "who decided". A proposal may say "today the code does X" in its Motivation and where it changes existing code.
*Check:* search for dates, "decided", and "no longer" outside the Motivation and the record. *(C28)*

## Specific texts

**S1. A decision question gives a case.** A question with two or more options whose outcomes differ has four parts: a case with real names, the outcome of each option for that case, a recommendation with its reason, and what the answer changes. Ask only for decisions, and for the meaning of an answer you cannot read.
*Check:* the four parts are present. *(C29, C30)*

**S2. A report lists the required steps.** It gives each step as passed, failed, or not run, with the failures first.
*Check:* the steps the task required all appear. *(C17)*

**S3. A proposal answers fixed questions.** These are: what happens today, what happens afterwards, which files change, what is in scope, what is deferred and what it waits for, how completion is checked, and what stays open. Each "In" item traces to a completion criterion.
*Check:* walk the list, then trace each "In" item. *(C31, C33)*

**S4. A primer is a map.** It runs 400–500 words, uses no identifiers, and carries one running example built only from the proposal's facts. Its order is the situation, the problem, the idea, the main rules with their reasons, and the open questions. It adds the alternative only when a reader would expect one.
*Check:* a reader of the primer alone can explain the core idea to a colleague. *(C36)*

## Process

These rules govern how a text is made. They cannot be checked from the text, so the demon does not attack them as text rules.

- **P1.** A session that read only the document and the files it links to edits the prose. *(C38)*
- **P2.** When you disagree, state the objection and wait for the answer before you act. *(C19)*
- **P3.** Before release, the writer runs every check above and assumes each fault is present. *(C37, C39, C41)*
- **P4.** Code, commands, and output produced by a run keep their exact wording. Output that a proposal specifies is design text. *(C40)*
