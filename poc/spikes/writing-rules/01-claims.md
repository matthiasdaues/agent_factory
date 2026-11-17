# Claims register, round 0

Sources: `factory-voice.md` (FV), `lector-agent.md` (LA), `draft-proposal/SKILL.md` (DP), `write-primer/SKILL.md` (WP), `working-discipline.md` (WD). Line numbers refer to `packages/factory/` at commit `49d4640e`.

Each claim has the same form: **if a writer follows the rule, the text loses the named fault and keeps its meaning.** "Check" says how a reader tells whether a text obeys the rule.

Rules that only govern tooling or procedure are left out, because they do not shape the text. Examples are `mdformat`, the lector's report format, and inbound anchors. The style models (Hemingway, King, Wolf Schneider, FV 50–52) are left out too, because no reader can check a text against them.

## A. Reader

**C00 Truth first.** Write only what you know to be true and what the reader needs. Mark what you do not know. *Fault:* text written without regard for whether it is true. *Check:* each statement is supported by a source, a check run in the session, or an explicit "unchecked" mark. *Source:* new; the motto. FV 87–88 and WD "Claims about tools" cover parts of it.

**C01 One reader.** Write for one reader: a capable engineer who joined last week. That reader knows the trade but not the project, reads English as a second language, reads once in order, and cannot ask back. *Fault:* text that assumes insider knowledge. *Check:* every fact the reader needs to act is in the text or behind a link. *Source:* FV 12–22, LA 76–82.

## B. Sentences and words

**C02 Short sentences.** Write one idea per sentence, in the active voice, in under 25 words. *Fault:* tangled sentences the reader must read twice. *Check:* count the words and the main clauses. *Source:* FV 40–42, LA 138.

**C03 Complete sentences.** Write no fragments, dropped articles, arrows, or semicolon chains. *Fault:* compressed text the reader must decode. *Check:* each sentence has a subject and a verb and parses as English. *Source:* FV 42–44, LA 137, WP 43–44.

**C04 Plain words.** Use concrete nouns and plain verbs: "check", not "prove"; "fix", not "lock". *Fault:* inflated words that make a simple act sound grand. *Check:* each verb names what physically happens. *Source:* FV 54–56.

**C05 One term per concept.** Use one term for one concept and never swap in a synonym. Repeat the noun where a pronoun could point to two things. *Fault:* the reader takes two words for two things. *Check:* list the terms; no concept has two names. *Source:* FV 56–58, LA 139.

**C06 Define once, at first use.** Define a project term or abbreviation once, where the reader first meets it. Do not define terms of the trade or terms the reader already read upstream. *Fault:* unknown jargon, or definitions that pad. *Check:* the first use of each project term carries its definition; no trade term is defined. *Source:* FV 60–65, FV 129–131, WP 39.

**C07 No buzzwords.** Do not use words that sound important and say little, such as "robust", "seamless", "leverage", "comprehensive", "crucial", "ensures", "powerful". Rewrite each the way one colleague says it to another. *Fault:* buzzword bingo. *Check:* search for the listed words and their kin. *Source:* FV 230–241, WP 53–54, LA 150.

**C08 No idioms or fake technical terms.** Avoid idioms, slang, and words that only sound technical, such as "smoke test" for "check". Use "actually", "even", and "just" only when they change the meaning. *Fault:* words a second-language reader misreads. *Check:* each word means what a dictionary says it means. *Source:* FV 67–69.

**C09 No drama.** Describe an operation by its plain effect: "is read-only", not "never changes again"; "fixed", not "locked for the rest of the query". *Fault:* a simple thing told as an event. *Check:* the sentence keeps its meaning when the strong words are replaced by neutral ones. *Source:* FV 97–98, LA 136.

## C. Content

**C10 Every sentence earns its place.** Each sentence helps the reader act. Cut a sentence that only makes the writer look good or thorough. *Fault:* padding and vanity. *Check:* delete the sentence; if the reader loses nothing needed to act, it goes. *Source:* FV 87–88, LA 84–87.

**C11 No announcing or selling.** Do not announce what comes next ("This document explains…") and do not praise the design ("That is the right default"). *Fault:* sentences about the text instead of the subject. *Check:* the sentence states a fact about the subject. *Source:* LA 141–142.

**C12 No defending.** Do not answer a doubt nobody raised, and do not write a sentence that only reassures a reviewer. Weigh an alternative only when someone proposed it or a reader would expect it, and then give the real reason against it. *Fault:* argument against a straw man; comfort instead of fact. *Check:* each rejected alternative names who proposed it or why a reader would expect it. *Source:* FV 99–108, LA 143–145.

**C13 A constraint stays a constraint.** State a constraint in the constraints section, not as an achievement. *Fault:* a limitation sold as a feature. *Check:* no constraint appears as a benefit. *Source:* FV 95–96.

**C14 A goal names an observable result.** A goal says what the reader can do or see afterwards, from outside: "the gate exits non-zero". The mechanism belongs in the scope. *Fault:* a goal that describes work instead of an outcome. *Check:* someone outside the code can observe the goal. *Source:* FV 90–94.

**C15 Check or mark claims about tools.** A statement about how a tool or service behaves is checked in the session or marked as unchecked, with what would check it. An unchecked claim never enters a document as fact. *Fault:* stale or invented tool behavior stated as fact. *Check:* each tool claim cites a run or a doc, or carries the mark. *Source:* FV 109–111, WD "Claims about tools".

**C16 Examples agree with themselves.** An invented example agrees with itself and with the project: names fit, dates agree, no fact contradicts another. *Fault:* examples that undermine trust. *Check:* the three checks in WD. *Source:* FV 112–114, WD "Invented examples", WP 49–52.

**C17 Name failures.** A report states what failed and what was skipped, in the same plain words as what succeeded. *Fault:* reports that hide failure. *Check:* every skipped or failed step appears. *Source:* FV 115–117.

**C18 Say uncertainty once.** When unsure, say so once, in plain words, and name what would settle the question. *Fault:* hedging spread over every sentence, or false certainty. *Check:* each uncertain statement carries one mark and a way to settle it. *Source:* FV 31–32.

**C19 Object openly.** When a premise, claim, or request does not make sense, say so and ask. Never agree only to keep the conversation smooth. *Fault:* agreement that hides a disagreement. *Check:* no reply accepts a premise the writer believes wrong. *Source:* FV 34–38.

## D. Order

**C20 Point, reason, next step, stop.** Put the point first, the reason second, the next step third. Stop when the message is complete. The last sentence adds a fact or a next step. *Fault:* buried point; closing flourish. *Check:* the first sentence states the point; the last sentence is a fact or a step. *Source:* FV 41–48, LA 80–82.

**C21 Outside in.** A paragraph starts with the situation a person meets and leads to the mechanism behind it. *Fault:* mechanism without a reason to care. *Check:* the first sentence names a person, a situation, or a need. *Source:* FV 126–128, WP 45.

**C22 Terms on arrival.** A term arrives where the reader meets the thing it names. A block of definitions up front is broken up. *Fault:* a glossary the reader must hold in memory. *Check:* no paragraph defines more than one term the reader does not yet need. *Source:* FV 129–131.

**C23 Linked sentences.** Connect sentences with "so", "because", or "then" where one idea leads to the next. *Fault:* a paragraph of unlinked claims that passes every sentence rule and says nothing. *Check:* the paragraph reads as an argument, not a list. *Source:* FV 121–124, FV 134–135, WP 45–48.

**C24 Map before list, reason before rule, example before abstraction.** *Fault:* items the reader cannot place; rules that read as arbitrary. *Check:* each list has its classes stated before it; each rule that could look arbitrary has its reason before it. *Source:* FV 139–144.

**C25 One home per fact.** State each fact once. Other sections link to it. A primer that orients is not a copy. *Fault:* repetition, and copies that drift apart. *Check:* no fact appears twice in the target-state text. *Source:* FV 145–147, LA 171–175.

**C26 A heading predicts its content.** *Fault:* the reader looks in the wrong place. *Check:* from the heading alone, a reader can say what the section holds. *Source:* FV 150–151.

**C27 Usable references.** A reference says in a few words what it holds, then links: not "D-20 option C". *Fault:* references that force the reader to open another file. *Check:* each reference makes sense without following it. *Source:* FV 152–154, LA 146–147.

**C28 Target state, present tense.** A specification, proposal, or architecture text describes the target state in the present tense. It holds no history words ("no longer", "was called"), no decision stamps, and no "who decided". The record lives apart and is cited by ID. *Fault:* the reader must reconstruct the current design from its history. *Check:* search for history words and dates in the target-state text. *Source:* FV 156–167, LA 99–102, DP 44–46.

## E. Questions and structured artifacts

**C29 Decision questions carry a case.** A question that asks the reader to decide has four parts: one concrete case from the project with real names; the outcome of each option for that case; the recommendation with its reason; and what the answer changes. If two options lead to the same outcome, pick another case. *Fault:* option labels the reader must decode. *Check:* the four parts are present. *Source:* FV 171–184.

**C30 Ask only for decisions.** Look facts up before asking. With the reader present, ask about one theme at a time, at most five questions. *Fault:* questions the writer could have answered; question floods. *Check:* no question has an answer in the repository. *Source:* FV 186–189.

**C31 A structured artifact answers its questions.** A story, proposal, or specification answers, from its own text, each applicable question: what behavior exists after, which files change, which rule owns the behavior, what state matters, what tests check, which commands verify, what is out of scope, when to stop and ask, what stays open. *Fault:* an artifact the implementer must complete by guessing. *Check:* walk the table. *Source:* FV 191–207.

**C32 Checkable completion criteria.** A reviewer can check each completion criterion without asking the author. *Fault:* criteria that sound done and decide nothing. *Check:* each criterion names an observable state or a command. *Source:* DP 71–72.

**C33 Scope that resists padding.** Each "In" item traces to a completion criterion. Each "Deferred" item says why. *Fault:* scope lists that grow to look complete. *Check:* trace each item. *Source:* DP 73–74.

**C34 Genuine open questions.** Open Questions holds only open items, and each becomes an acceptance criterion, a recorded assumption, or a deferral. Padding is removed. *Fault:* questions listed to look careful. *Check:* each question is undecided and names where its answer goes. *Source:* DP 75–80.

**C35 No invented precision.** Use `unknown` rather than an invented number. *Fault:* estimates that look exact and are guesses. *Check:* each number has a source. *Source:* DP 40–42, WP 50.

**C36 The primer is a map.** A primer of 400–500 words lets a newcomer follow the proposal. It uses plain words and no identifiers, carries one running example built only from the proposal's facts, and follows the order: situation, problem, framing, idea, alternative, rules with reasons, what lasts, open questions. *Fault:* a primer that is a summary, or one that needs the proposal to be understood. *Check:* a reader of the primer alone can explain the core idea to a colleague. *Source:* WP 13–130.

## F. Process

**C37 Write it right the first time.** Apply the rules while writing each sentence, not in a cleanup pass. *Fault:* a cleanup pass that misses what the writer no longer sees. *Check:* not checkable from the text. *Source:* FV 211–212.

**C38 A fresh reader edits.** The prose is edited by a session that did not see the conversation behind the text. *Fault:* the author cannot see what a newcomer lacks. *Check:* the editing session had no access to the conversation. *Source:* LA 35–38, WP 27–30, DP 59–64.

**C39 Assume the fault.** In the final pass, assume the text reads like buzzword bingo and look for it. *Fault:* a reviewer who finds nothing because they expect nothing. *Check:* not checkable from the text. *Source:* FV 230–241, WP 121–123.

**C40 Exemptions.** Code, commands, quoted tool output, verbatim transcripts, user notes, and policy-required status words keep their exact wording. *Fault:* an editor who rewrites evidence. *Check:* exempt spans are byte-identical. *Source:* FV 243–251, LA 112–113.

**C41 Four gates and a final pass.** Before a text leaves the writer, it passes Junior Clarity / Senior Acceptance, International Readability, No Pretense, and Agent-Answerability, then the final pass. *Fault:* none of its own; it bundles C01–C36. *Check:* the bundled rules. *Source:* FV 209–228.
