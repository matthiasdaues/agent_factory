# Objections to agent writing

This file lists user turns from the Agent Factory session transcripts that object to text an agent wrote. The user's objections are the ground truth. The fault line restates the user's point; it is not a separate judgment.

## Objections

Counts by category: clarity 20, truth 4, tone 4, wording 3, other 2, structure 2, length 1. High confidence: 21 of 36.

### OBJ-01

- Session: `65936d3d`
- Timestamp: 2026-10-15T22:01:19.991Z
- Category: clarity
- Confidence: high
- Fault: Refers to "line 8" and "as shown above" without showing it.
- Source of the offending text: preceding assistant message.

User's words:

> What do you mean with "line 8 of"...

Offending text:

> It waits for line 8 of `/home/matthiasdaues/Documents/datenschoenheit/agent_factory/.current-work/feature/bug-hunt-fixes/invocation/backlog/ST-0296.md`, as shown above.

### OBJ-02

- Session: `65936d3d`
- Timestamp: 2026-10-16T12:50:10.734Z
- Category: clarity
- Confidence: high
- Fault: "The proposal" is ambiguous; reader cannot tell which.
- Source of the offending text: preceding assistant message.

User's words:

> which proposal?

Offending text:

> Meanwhile I prepare the proposal for the final merge.

### OBJ-03

- Session: `65936d3d`
- Timestamp: 2026-10-27T15:30:19.605Z
- Category: clarity
- Confidence: high
- Fault: Invented label "brief-storage run" used without explanation.
- Source of the offending text: preceding assistant message.

User's words:

> ok. what is the "brief-storage" run?

Offending text:

> - **Next run:** the brief-storage run, then the gate proposal.

### OBJ-04

- Session: `65936d3d`
- Timestamp: 2026-10-27T16:10:09.327Z
- Category: clarity
- Confidence: high
- Fault: Observations too terse; reader lacks context to answer.
- Source of the offending text: preceding assistant message; first of three "weak points".

User's words:

> I need more context for your observations. Grill one by one.

Offending text:

> 1. **Commit check without freshness (part 3):** a story can commit for days on a stale base and only learns about conflicts at the merge. Should `refresh-story` also run when the trial merge is clean but the target is more than N commits ahead?

### OBJ-05

- Session: `b6b07e6b`
- Timestamp: 2026-10-29T12:50:01.199Z
- Category: other
- Confidence: low
- Fault: "Ideal person-days" is a wrong unit for agent work.
- Source of the offending text: preceding assistant message.

User's words:

> Can you stop creating "ideal person days" as an estimation unit? It's not like actual people will be writing anything here...

Offending text:

> For the entity model, LinkML is a medium job: about 8 to 13 ideal person-days.

### OBJ-06

- Session: `b6b07e6b`
- Timestamp: 2026-10-30T12:20:41.829Z
- Category: clarity
- Confidence: low
- Fault: Names a document the user was never told about.
- Source of the offending text: preceding assistant message.

User's words:

> what is the "expected-differences.md" doc?

Offending text:

> - The Gigacron findings from `expected-differences.md` aren't filed yet.

### OBJ-07

- Session: `2339525c`
- Timestamp: 2026-11-02T14:40:34.408Z
- Category: truth
- Confidence: low
- Fault: Risk list reads as inflated paranoia, not real assessment.
- Source of the offending text: preceding assistant message; one sentence from a longer risk list the user questioned as a whole.

User's words:

> perform a reality check. Is this real risk assessment or token use increasing paranoia?

Offending text:

> A project on `v0.12.0` may also have no `install.json`, and then the update stops with "not an init-factory'd project".

### OBJ-08

- Session: `3a7ac5e5`
- Timestamp: 2026-11-04T12:39:13.136Z
- Category: clarity
- Confidence: low
- Fault: Term `dependency-check` not explained; user had to guess its meaning.
- Source of the offending text: preceding assistant message.

User's words:

> 1. dependency-check like when importing pacakges?

Offending text:

> 1. **Where gate result files live.** ST-0359 makes `dependency-check` mandatory for every story.

### OBJ-09

- Session: `3a7ac5e5`
- Timestamp: 2026-11-04T15:33:47.372Z
- Category: clarity
- Confidence: high
- Fault: Sentence meaning unclear.
- Source of the offending text: preceding assistant message. The user's quote matches except that it drops the backticks around `owner:`.

User's words:

> What do you mean with that sentence? owner: names the agent that acts next, and a passing check leaves nobody anything to do.

Offending text:

> `owner:` names the agent that acts next, and a passing check leaves nobody anything to do.

### OBJ-10

- Session: `2796a81d`
- Timestamp: 2026-11-04T20:13:00.849Z
- Category: clarity
- Confidence: high
- Fault: The question was not understandable.
- Source of the offending text: preceding assistant message (closing question after three options built on the term "platform machine").

User's words:

> I don't get your question.

Offending text:

> Which way does the GitHub adapter run `next-id`?

### OBJ-11

- Session: `cf5e2e4c`
- Timestamp: 2026-11-04T20:14:04.392Z
- Category: clarity
- Confidence: high
- Fault: "The line" is a metaphor the reader cannot place.
- Source of the offending text: preceding assistant message.

User's words:

> Which line in which table?

Offending text:

> Should the line stay as drawn, or do you want a different cell?

### OBJ-12

- Session: `54e523f2`
- Timestamp: 2026-11-05T09:09:04.746Z
- Category: tone
- Confidence: low
- Fault: Changelog carries history and flourishes instead of crisp statements.
- Source of the offending text: file the agent wrote: `packages/factory/CHANGELOG.md`, Edit at 2026-11-05T09:08:35Z. The user named no sentence; this is the opening of the entry.

User's words:

> Send the lector over the changelog. It must read crisply and declaratively. No history, no flourishes, no wistful musings.

Offending text:

> This is the layout release. It reorganises the core artifacts of a
> project (ST-0318 to ST-0345). The work ends with the merge of
> `feature/core-artifact-layout` into dev, commit
> `e62ac0b077a6d90635b028bdd0e624e1809cde1a`.

### OBJ-13

- Session: `6ac6ec27`
- Timestamp: 2026-11-05T19:04:20.211Z
- Category: truth
- Confidence: low
- Fault: Statement is incomplete and so misleading.
- Source of the offending text: assistant message before the previous user turn. The user's quote is a paraphrase and does not match verbatim.

User's words:

> - Where the truth lives. BMAD treats the code as truth and keeps documents small. The factory treats the specification and architecture.dsl as truth and reconciles the code against them. => This is incomplete. At the beginning of the IMPLEMENTATION phase, the truth is in the documents. At the onset of RECONCILIATION the truth lies in the code.

Offending text:

> **Where the truth lives.** Agent Factory keeps the specification and the DSL as core truth, with derived views, and reconciles the code against them. BMAD treats the code as truth and keeps documents small.

### OBJ-14

- Session: `6ac6ec27`
- Timestamp: 2026-11-05T19:06:27.304Z
- Category: truth
- Confidence: low
- Fault: Statement is incomplete about what reconciliation does.
- Source of the offending text: preceding assistant message. The user's quote matches.

User's words:

> The reconciliation agent reads the code as built and finds where the documents drifted. => ..and finds where implementation reality created code that differs from its original specification. The learned experience then informs and adapts the specification retroactively. The next feature specification round then starts from the corrected origin state.

Offending text:

> The reconciliation agent reads the code as built and finds where the documents drifted.

### OBJ-15

- Session: `2796a81d`
- Timestamp: 2026-11-05T19:15:46.745Z
- Category: clarity
- Confidence: high
- Fault: Uses an unexplained term, "platform machine".
- Source of the offending text: preceding assistant message.

User's words:

> What is the platform machine you're talking about?

Offending text:

> The GitHub ticket adapter of `project-agent-flows.md` runs on the platform machine. That machine has no clone of the project, so it has no `origin`.

### OBJ-16

- Session: `40d6746a`
- Timestamp: 2026-11-05T20:59:40.896Z
- Category: clarity
- Confidence: low
- Fault: Term appears without saying where it comes from.
- Source of the offending text: preceding assistant message.

User's words:

> where does the payout thingy come from? Must I - to complete a test - do a term confirmation?

Offending text:

> What is a Payout? My proposal is "One amount owed to one recipient, which a payment batch sends to the bank together with other payouts."

### OBJ-17

- Session: `d113754a`
- Timestamp: 2026-11-08T15:07:05.501Z
- Category: clarity
- Confidence: high
- Fault: Asks for a decision without saying what the finding is.
- Source of the offending text: preceding assistant message.

User's words:

> What exactly is the finding?

Offending text:

> IMPL-0014 is still `open` and waits for you. Tell me why it isn't a defect, or write the waiver.

### OBJ-18

- Session: `9f81748e`
- Timestamp: 2026-11-08T21:28:44.054Z
- Category: clarity
- Confidence: high
- Fault: Table cell too terse; meaning of "lowers the level" unclear.
- Source of the offending text: preceding assistant message. The user's quote matches; the sentence appears in four table rows.

User's words:

> What do you mean with " A "yes" lowers the level one step."?

Offending text:

> | `second_breach` | | | | | x | | A "yes" lowers the level one step. |

### OBJ-19

- Session: `9f81748e`
- Timestamp: 2026-11-08T21:40:53.009Z
- Category: wording
- Confidence: high
- Fault: Deck prose reads badly.
- Source of the offending text: file the agent wrote: the slide deck `finding-severity-deck.html` in the session scratchpad, Write at 2026-11-08T21:36:40Z. The user named no sentence; this is the title slide. A turn six seconds earlier ("rewor the prose") is a typo-duplicate of this one.

User's words:

> you better. And also: rework the prose. It reads like shit.

Offending text:

> # How a finding gets its severity
>
> The reviewer records facts. A fixed rule computes the severity.

### OBJ-20

- Session: `9f81748e`
- Timestamp: 2026-11-08T21:54:15.248Z
- Category: clarity
- Confidence: high
- Fault: Statements too terse for a new developer.
- Source of the offending text: file the agent wrote: `fc-talk.html` in the session scratchpad, Write at 2026-11-08T21:51:57Z. The user named no sentence; this is one slide heading of the kind he called terse.

User's words:

> better. Now read this with the eyes of a developer who has recently joined. Will they get any of your tersely worded statements?

Offending text:

> # The AI answers questions. Code sets the severity.

### OBJ-21

- Session: `9f81748e`
- Timestamp: 2026-11-08T22:41:20.060Z
- Category: tone
- Confidence: high
- Fault: Prose is breathless and action-heavy, not sober.
- Source of the offending text: preceding assistant message. The agent later named this sentence as one of its own faults.

User's words:

> You're writing quite breathless and actionistic prose. Explain your state of affairs and your proposed way forward in simple and sober English.

Offending text:

> The project's git guard refused my `uv run pytest` call. I won't work around it.

### OBJ-22

- Session: `9f81748e`
- Timestamp: 2026-11-08T22:45:36.784Z
- Category: clarity
- Confidence: low
- Fault: Presentation makes the rules look more complicated than they are.
- Source of the offending text: slide deck the agent wrote.

User's words:

> Now. The rules seem complicated. But probably this is an issue of presentation, not of the rules themselves.

Offending text:

> No sentence targeted. The objection is to the slide deck `docs/presentations/finding-classification.html` as a whole.

### OBJ-23

- Session: `9f81748e`
- Timestamp: 2026-11-08T23:09:15.521Z
- Category: length
- Confidence: low
- Fault: Deck too long; examples crowd out the explanation.
- Source of the offending text: slide deck the agent wrote.

User's words:

> Ok. This is 25 pages. Explain how it works, which parts are there to scaffold a run-independent and consistent scoring result. Cut everything out that is example. Add in missing information.

Offending text:

> No sentence targeted. The objection is to the 25-slide length of the deck and its worked examples.

### OBJ-24

- Session: `9f81748e`
- Timestamp: 2026-11-08T23:25:05.479Z
- Category: structure
- Confidence: low
- Fault: Slide 7 is cramped and hard to read.
- Source of the offending text: slide deck the agent wrote.

User's words:

> slide 7 is too cramped and not easily legible. Maybe give each approach one slide instead?

Offending text:

> No sentence extracted. The target is slide 7 of the deck.

### OBJ-25

- Session: `9f81748e`
- Timestamp: 2026-11-08T23:37:09.826Z
- Category: wording
- Confidence: high
- Fault: Deck wording still poor despite the lector's clean report.
- Source of the offending text: preceding assistant message (the agent's summary of the lector pass).

User's words:

> I can not believe that the lector is satisfied with the presentation's shape and wording.

Offending text:

> It found no unclear sentences.

### OBJ-26

- Session: `9f81748e`
- Timestamp: 2026-11-08T23:46:05.768Z
- Category: wording
- Confidence: high
- Fault: Heading phrased as a mannered aphorism; abstraction acts.
- Source of the offending text: a slide heading in the deck. The quote is not in the main-session text before the objection; a lector subagent wrote it. The agent's reply at 2026-11-08T23:46:15Z confirms it as a deck heading.

User's words:

> What is this manneristic phrasing? "A severity decides what the run does next"

Offending text:

> A severity decides what the run does next

### OBJ-27

- Session: `9f81748e`
- Timestamp: 2026-11-08T23:47:15.753Z
- Category: tone
- Confidence: high
- Fault: Agent ignores the voice rules: fragments, drama, rhetoric.
- Source of the offending text: preceding assistant message. The agent's next reply names bold label fragments like this one as the fault.

User's words:

> Why the f\*ck do you not apply the factory-voice, the working-agreement rules, the ALWAYS required modicum of rhetoric constraint?

Offending text:

> **Waiting on you, because the guard or ownership stops me**

### OBJ-28

- Session: `8da07c05`
- Timestamp: 2026-11-09T08:31:10.910Z
- Category: clarity
- Confidence: high
- Fault: Intro to context capture is hard to understand.
- Source of the offending text: factory output in another project; the user pasted his own feedback list.

User's words:

> - The language is not easy to understand (the intro to context-capture)

Offending text:

> Not available. The text was factory output in another project's onboarding run; that project's transcripts are out of scope.

### OBJ-29

- Session: `8da07c05`
- Timestamp: 2026-11-09T08:31:10.910Z
- Category: tone
- Confidence: high
- Fault: Sentence sounds accusatory and explains too little.
- Source of the offending text: factory output in another project. The quote could not be verified: it is not in these transcripts, and `packages/factory/` does not contain the phrase.

User's words:

> - the "no factory specific docs folders found" sentence sounds mildly accusatory. It should explain more

Offending text:

> no factory specific docs folders found

### OBJ-30

- Session: `9f81748e`
- Timestamp: 2026-11-09T12:00:36.406Z
- Category: clarity
- Confidence: low
- Fault: Abstract argument; the concrete scenario is missing.
- Source of the offending text: preceding assistant message.

User's words:

> what is the scenario? Why would a commit on dev help?

Offending text:

> A person accepts it with a small commit on `dev`, and the story then passes without a rebase.

### OBJ-31

- Session: `9f81748e`
- Timestamp: 2026-11-09T13:22:55.405Z
- Category: clarity
- Confidence: low
- Fault: New term "ready command" not clearly introduced.
- Source of the offending text: preceding assistant message.

User's words:

> What is the "ready" command?

Offending text:

> If each measuring command gets an optional `ready` command in `docs/testing.yaml`, the setup skill writes it, for example a check that the app container is up.

### OBJ-32

- Session: `9f81748e`
- Timestamp: 2026-11-09T15:36:10.529Z
- Category: clarity
- Confidence: high
- Fault: Messages are foggy; nothing comes through clearly.
- Source of the offending text: preceding assistant message; one sentence from a message the user judged unclear as a whole.

User's words:

> ACtually, all you write makes me feel I'm walking through mist, not seeing anything clearly.

Offending text:

> The two reviews overlap more than they seem to, because several majors come from parts the skeptical review wanted deleted.

### OBJ-33

- Session: `9f81748e`
- Timestamp: 2026-11-09T15:42:52.824Z
- Category: structure
- Confidence: high
- Fault: Proposals keep a decision trail instead of reading fresh.
- Source of the offending text: preceding assistant message.

User's words:

> No. Write the proposals as if they were freshly minted. Get rid of the decision making trail. I think it decreases LLM performance quality.

Offending text:

> `story-gates` and `story-done-gate` now appear only in the decision records and review tables that document their removal.

### OBJ-34

- Session: `9f81748e`
- Timestamp: 2026-11-09T15:55:05.217Z
- Category: clarity
- Confidence: high
- Fault: Message has no clear point for the reader.
- Source of the offending text: preceding assistant message; one passage from a message the user could not follow.

User's words:

> what do you want me to understand?

Offending text:

> Removing the check for open findings leaves one gap. In an orchestrated run, the criterion "the merge waits until no finding for the story is open" is an instruction to the agent, and no script enforces it yet.

### OBJ-35

- Session: `63e25a11`
- Timestamp: 2026-11-16T08:24:01.660Z
- Category: truth
- Confidence: low
- Fault: Severity "critical" overstated for a metadata lint bug.
- Source of the offending text: preceding assistant message.

User's words:

> It is of course not critical because it doesn't actually block anything and it pertains to metadata. It does not actually influence the instruction for the agent.

Offending text:

> **My recommendation.** Keep `critical`, because the rule computes it and I should not lower it myself.

### OBJ-36

- Session: `46e1cd8c`
- Timestamp: 2026-11-17T18:59:23.853Z
- Category: other
- Confidence: low
- Fault: Factory text still contains bullshit; not plain enough.
- Source of the offending text: none; general objection that started this spike.

User's words:

> The factory voice instruction is nice but doesn't cut it. I want more distilled, non-bullshit text a normal human can access and understand. Set up an experiment: Take all instructions pertaining to writing, formulating, communicating that are in the factory. Improve and evolve them. I want each output to be challenged by a "popperian demon" trying to refute their claim. Only hardened statements get through. What will be put in writing afterwards must pass the "no bullshit from my agents" filter. Follow this motto: "The world is full of bullshit. Let us not add to it."

Offending text:

> No sentence targeted. The objection is to the factory's writing instructions and the text they produce in general.

## Accepted controls

Each passage below is the end of an assistant message of at least 40 words. The user's next turn moved on without any objection to the text. Most of these replies accept a decision or a next step. Acceptance of a decision is weak evidence that the prose was acceptable: the user may have disliked the wording and let it pass. Each passage is the final paragraphs of the message, kept whole, between 41 and 149 words.

### CTRL-01

- Session: `03b69245`
- Timestamp: 2026-11-11T17:30:43.013Z
- User reply: `yes.`
- Words in passage: 87

> The gap is in what the repo can confirm. It confirms the end-of-turn event for Claude Code, Copilot, Codex, and OpenCode. It confirms the per-prompt event only for Claude Code. Pi is unconfirmed on both: its usage capture runs only at `session_shutdown`, which is too late for speech. The adapter table marks each unconfirmed cell "to verify".
>
> I suggest a short documentation survey of those cells before the grilling. Otherwise the grilling would argue about events nobody has looked up yet. Should I run that survey now?

### CTRL-02

- Session: `2339525c`
- Timestamp: 2026-11-02T11:35:23.178Z
- User reply: `do both.`
- Words in passage: 77

> The glossary cleanup is a follow-up step the script names in its output, the same way as the fold. It does not write an entry into the project's `work/todo.md`. If you want the script to record both follow-ups there, so they outlast the terminal output, say so and I'll add it.
>
> Next steps:
>
> 1. Commit the fixes as `docs: fix review pass 4 findings on the layout proposal`.
> 2. Start review pass 5 in a fresh session.

### CTRL-03

- Session: `2796a81d`
- Timestamp: 2026-11-05T19:35:50.488Z
- User reply: `yes`
- Words in passage: 69

> **My recommendation:** fail with that message. A project without a remote has one person on one clone, and creating a GitHub repository first takes a minute. Then the counter has one home from the first ID on.
>
> **What the answer settles:** PROP-06, one row in the error table, one completion criterion, and the `init-factory` message for a project without `origin`.
>
> Should `next-id` fail in a project without a remote?

### CTRL-04

- Session: `2796a81d`
- Timestamp: 2026-11-05T20:52:29.644Z
- User reply: `yes`
- Words in passage: 44

> Three of these fixes are small choices of my own: fail fast on any other refusal (PROP-14), a fixed committer (PROP-15), and only a warning from `init-factory` (PROP-16). The other two only correct the text.
>
> Should I write these four fixes into the proposal?

### CTRL-05

- Session: `2796a81d`
- Timestamp: 2026-11-06T16:31:54.003Z
- User reply: `yes`
- Words in passage: 53

> **One more point, from the review loop:** PROP-12 arose from my fix in pass 2. The findings are now moving into cases that earlier fixes created. I'd do these two fixes, have pass 4 check only them, and then end the loop: primer, lector, and your acceptance.
>
> Should I go ahead like that?

### CTRL-06

- Session: `3a7ac5e5`
- Timestamp: 2026-11-03T18:30:46.048Z
- User reply: `Accepted`
- Words in passage: 98

> 1. **G10:** what status does a `QA` finding get when a test is missing? I recommend keeping it `open` and moving its `owner:` from the test-strategy agent to the planning agent. The finding becomes `resolved` when a story adds the test. That way the finding stays visible and goes to the agent that can act on it.
> 2. **The twelve defaults:** G02 to G07, G09, and G11 to G16. The specification already follows my recommendation for each one.
>
> If you accept both, I'll record them, commit step 1 on `dev`, and start the spec-review agent for step 2.

### CTRL-07

- Session: `3a7ac5e5`
- Timestamp: 2026-11-04T15:34:46.284Z
- User reply: `A`
- Words in passage: 80

> **What you decide:**
>
> - **Option A, my recommendation:** only failing rows carry `owner:`. The contract gets corrected to match the story.
> - **Option B:** every row carries `owner:`. Then the field means "who owns this rule" rather than "who must act", and the code has to change.
>
> A is the better fit, because elsewhere in this proposal `owner:` already means the agent that acts next. That is the meaning for findings, CAO-G26. B would give the same field two meanings.

### CTRL-08

- Session: `3a7ac5e5`
- Timestamp: 2026-11-04T21:24:53.245Z
- User reply: `Make it so.`
- Words in passage: 54

> Part B of wave 4 is still running. The implementation agent is waiting on the ST-0358 and ST-0365 developers, so there's no result yet. When it reports, I'll check the merges and `close-wave 4` against git.
>
> Your answer on `--write-glossary` is still open. I recommended keeping the name and adding the argument in ST-0351.

### CTRL-09

- Session: `40d6746a`
- Timestamp: 2026-11-05T20:21:13.658Z
- User reply: `yes`
- Words in passage: 97

> 1. You confirm that the 21:08 run is yours, or a run you started. I won't commit or discard changes whose origin I can't place.
> 2. If it is, I run `statemachine-lint` to close CAO-04-AC-01. Then I commit the two files after `verify-base feature/core-artifact-ownership`, and I move `branch_head` by hand.
> 3. Then we do CAO-05-AC-01. You pick one domain area, which here means "Core artifact ownership". We go through its nine terms, and the domain-modeling agent moves the ones you confirm into the glossary.
>
> Is the 21:08 run yours, and should I go ahead with step 2?

### CTRL-10

- Session: `40d6746a`
- Timestamp: 2026-11-05T20:53:35.108Z
- User reply: `yes.`
- Words in passage: 70

> - The layer key `end_to_end` doesn't match the skill's vocabulary, `e2e_smoke_test`. A test, `test_testing_yaml_declares_end_to_end_layer`, and the value-first onboarding QA strategy both depend on the current key. Renaming it would break both, so a story should change all three together.
> - `layers.deterministic_linter.entry_point` names only `usage-contract-check`. The factory's lint gates actually run through pre-commit.
>
> Do you confirm the proposal as it stands? Or do you have commands for the two orphan suites?

### CTRL-11

- Session: `568b9176`
- Timestamp: 2026-11-09T13:14:17.587Z
- User reply: `Confirmed.`
- Words in passage: 60

> I recommend confirming all seven, because each one matches what we discussed and I have no reason to doubt any of them. After that, three steps remain before `status: open`: a fresh agent writes the primer, the lector agent edits the prose, and I run the readiness check.
>
> Do you confirm all seven, or do you want to change one?

### CTRL-12

- Session: `568b9176`
- Timestamp: 2026-11-09T13:37:58.089Z
- User reply: `yes`
- Words in passage: 49

> I recommend the simple version. A stale function name is cheap to notice, and only 41 references carry one. The change withdraws DEC-02, DEC-04, DEC-07, DEC-10 and DEC-12, and DEC-06 needs rewording. DEC-01, DEC-03, DEC-05, DEC-08, DEC-09 and DEC-11 stay.
>
> Shall I rewrite the proposal to the simple version?

### CTRL-13

- Session: `59af3a3f`
- Timestamp: 2026-11-08T20:30:03.505Z
- User reply: `Yes`
- Words in passage: 41

> The gap report then follows as the detail behind the sentence "I cannot yet check". I recommend making this paragraph the opening of the proposal. Shall I start `draft-proposal` with it, the three-part profile, and the gap report as one feature?

### CTRL-14

- Session: `601a0939`
- Timestamp: 2026-11-02T14:40:05.922Z
- User reply: `continue`
- Words in passage: 102

> **Not done: checking `poc/workflow/workflow.svg`.**
>
> - ImageMagick cannot render the export as it is.
> - I inlined the embedded SVG, but it holds only 797 characters, which is not the shapes. The render came out nearly blank.
> - The shapes must be stored elsewhere in the file. The next step is to find where, or to render the file with a browser or Inkscape.
> - `poc/workflow/` is untracked, and I have not changed it.
>
> When your limit resets, tell me what you want me to check in that export, or a specific problem you saw. I can then pick it up from there.

### CTRL-15

- Session: `601a0939`
- Timestamp: 2026-11-02T17:41:13.230Z
- User reply: `accepted.`
- Words in passage: 69

> One answer is still open: do you approve the lector's plan items, all 27 or only some? You answered my two decision questions, but not that one. As soon as you approve, I write the round-2 brief. It carries the approved items, my ten author fixes for U1 to U6 and C1 to C6, and a note that the proposal has changed since `a19d383b`. Then I start the lector.

### CTRL-16

- Session: `60f0dc5d`
- Timestamp: 2026-11-17T18:51:40.549Z
- User reply: `yes.`
- Words in passage: 56

> I recommend sending the corrections back to the same report writer, because it still holds its reading of the sources and a fix costs one round. Then a fresh validator runs the full check again, as the review-loop rules require. Two concepts may lose their top ranks.
>
> Should I send the corrections to the report writer?

### CTRL-17

- Session: `63e25a11`
- Timestamp: 2026-11-16T08:37:32.239Z
- User reply: `yes.`
- Words in passage: 52

> The other proposals carry `scope: global` on the first line of their frontmatter. Should I add `scope: global` to the two committed proposals in a separate commit, `docs: declare the scope of two proposals`? Then I would retry the fix commit. If either proposal has a narrower scope, tell me the value.

### CTRL-18

- Session: `65936d3d`
- Timestamp: 2026-10-15T12:12:45.893Z
- User reply: `a`
- Words in passage: 73

> How should I go on with BUG-0048?
>
> - **(a)** Correct the finding to a latent defect, with no incident, and finish the fix through the usual cycle.
> - **(b)** Drop it, delete the worktree and the branch, and withdraw the finding. Then I move on to I-1.
>
> I recommend (a). Today showed how hard it is to get out of a wrong install record: three runs, and each one needed a manual cleanup.

### CTRL-19

- Session: `65936d3d`
- Timestamp: 2026-10-16T14:25:40.223Z
- User reply: `yes.`
- Words in passage: 48

> **My proposal:** one small commit on the integration branch, `git update-index --chmod=+x packages/factory/scripts/_docs_assemble.py`, as `fix: make _docs_assemble.py executable`. Then the suite runs again, followed by the final merge into `dev`. The file is yours, from the publish-docs work, which is why I ask first.
>
> Shall I do it?

### CTRL-20

- Session: `65936d3d`
- Timestamp: 2026-10-27T09:03:41.996Z
- User reply: `yes.`
- Words in passage: 149

> 1. **BUG-0111:**
>    - the template lookup with the key check;
>    - `init-factory` sets the key and `remove-factory` unsets it;
>    - tests for both paths (key set → exit 1 with the message; key unset → exit 0, no output).
> 2. **BUG-0110:**
>    - `update-factory` runs the refresh after `init-factory` succeeds;
>    - it shows the diff and asks y/N before it writes, and writes nothing on no;
>    - it skips a project that never merged the factory hooks;
>    - tests for yes, no, unchanged and not merged.
> 3. **This repo's own hooks:**
>    - I move the `stages:` lines into the template, so a refresh here loses nothing;
>    - I leave the `backlog-lint` "$@" difference as the template has it, unless you prefer the repo's variant.
>
> Tests run only through `pre-commit run run-tests --all-files`. When they pass, I show you the diff before anything gets committed.
>
> Shall I build it this way?

### CTRL-21

- Session: `82271b72`
- Timestamp: 2026-11-03T16:05:26.192Z
- User reply: `A`
- Words in passage: 56

> I recommend A for now. It is simple, it gives every project full control, and the update script already moves changes it finds aside. B is worth building once several projects make the same kind of small change. Your answer decides how playbooks are stored in a project and what `update-factory` has to do with them.

### CTRL-22

- Session: `82271b72`
- Timestamp: 2026-11-03T21:40:20.943Z
- User reply: `yes.`
- Words in passage: 80

> 1. The other session fixes the three failures.
> 2. Commit the staged files: the wrapper first, then the proposal.
> 3. Run the grilling round on the eight assumptions: DEC-07 to DEC-11, DEC-13, and DEC-14.
> 4. Run the lector passes, write the primer, and check the gate before the proposal goes to `status: open`.
>
> Should I write this as a handoff in `docs/handoffs/` before you go? Then a fresh session can start tomorrow from the file instead of from this conversation.

### CTRL-23

- Session: `9f81748e`
- Timestamp: 2026-11-15T20:16:19.097Z
- User reply: `A`
- Words in passage: 64

> I recommend option A. A run then has exactly two ends, finished or dropped, and in both cases nothing of the run remains except unmerged branches that the human deletes. Option B leaves stray worktrees behind, which is how this repository came to hold thirteen of them. A story returned to the backlog can start again in a later run from a fresh branch.

### CTRL-24

- Session: `9f81748e`
- Timestamp: 2026-11-16T22:46:59.496Z
- User reply: `yes.`
- Words in passage: 46

> I recommend one guard script that all five tools call, the way `guard-human-fields` already works. pi's TypeScript copy becomes a thin wrapper that hands the command to that script. A completion criterion then checks OpenCode against a real session, not a mock.
>
> Do you accept this?

### CTRL-25

- Session: `b6b07e6b`
- Timestamp: 2026-10-30T14:20:15.428Z
- User reply: `yes.`
- Words in passage: 43

> **Next step:** `draft-proposal` continues with the grilling. It tests the written draft and settles the five assumptions with you. After that come the lector passes, the primer and the readiness gate, and then `status: open` for the review. Should I start the grilling?

### CTRL-26

- Session: `b6b07e6b`
- Timestamp: 2026-10-30T14:58:58.844Z
- User reply: `B`
- Words in passage: 130

> **What it means for the proposal:**
>
> - **Option B from the last question gains weight.** A note travels to the database, and a comment never does.
> - **Generating DDL stays deferred.** Producing the comments is the job of the project's migrations or ORM. The proposal keeps DBML as the model, not as a code generator.
> - **A new question for later in the grilling:** whether `compare` also reports comment drift. Where a project sets comments, a changed note becomes visible. Where it doesn't, every note would show up as a difference. So I'll suggest making it optional.
>
> The pending decision is still: B, with prose in notes, a lint that rejects comments carrying prose, notes free in length and position, and the review rule for behaviour. Do you choose B?

### CTRL-27

- Session: `b6b07e6b`
- Timestamp: 2026-11-01T22:26:49.571Z
- User reply: `A`
- Words in passage: 48

> **What it settles:**
>
> - The format of `glossary.md`.
> - The change to `domain-modeling` and the template.
> - `GLOSS001` reading `glossary.md` in that format. It stays an `info` finding, so the core table names `spec-lint GLOSS001 (info)` as the glossary's check instead of "none yet."
>
> Do you choose A?

### CTRL-28

- Session: `cf5e2e4c`
- Timestamp: 2026-11-04T19:46:38.643Z
- User reply: `C`
- Words in passage: 43

> Your answers decide the Design and the Decisions table of the new proposal, `docs/proposals/finding-threshold.md`. They also decide whether the proposal changes `finding-format.md`, `report-format.md`, and the finding template. After this theme I'll ask whether to go deeper (the actual table cells) or start writing.

### CTRL-29

- Session: `cf5e2e4c`
- Timestamp: 2026-11-04T20:09:48.037Z
- User reply: `yes.`
- Words in passage: 94

> - **`finding-threshold.md` (T-0016)** holds the risk table and the line (Q1, Q6), the cap of 3 passes (Q2), the human-only override (Q4), and the three required fields. It also says that a finding below the line is recorded, not left `open`.
> - **A separate finding-format proposal** settles Q3's register, Q5, Q7, and Q8. The threshold proposal lists it as deferred and links it. I'll also file it as a todo entry, T-0017.
>
> Should I split it this way? If yes, the next step is your answer on Q6, and then I write the draft.

### CTRL-30

- Session: `d113754a`
- Timestamp: 2026-11-04T21:36:22.722Z
- User reply: `Move on.`
- Words in passage: 63

> One open point remains here: the line between the exposures `fails` and `uncertain`. I think the draft defines it well enough, so I recommend moving on to the security factors. The eight factor anchors are my own invention. They decide every security severity, and none of them has met a real finding yet. I would test them against SEC-0003, the unpinned `tiktoken` dependency.

## Method

I read the 34 main-session transcript files in the project folder and ignored the `subagents/` folders. Three files hold no user turn that passes the filter, so 31 sessions contribute. A user turn is a `type=="user"` record with a string `message.content`. I dropped turns that start with "\<" or with "This session is being continued". That left 1,482 user turns. Of these, 500 are relayed subagent hand-backs ("Another Claude session sent a message") and 14 are image placeholders. I read the remaining 968 turns in full or, for turns over 200 characters, by keyword search plus a read of their full text without pasted blocks.

The filter also drops 18 turns that start with a pasted block. I read them separately. They hold logs, prompts, and text from other sessions, with no objection of the user's own. One onboarding feedback list (OBJ-28 and OBJ-29) sits in a turn that starts with the user's own words, so the filter kept it.

I found 65 candidate turns. I kept 35 of them and split one into two objections, which gives 36. I dropped 30:

- 17 objected to a design, a layout, a fact, or the agent's grasp of context, not to the writing. Examples: "Your drawio layout is horribly bad", "Are you stupid or what? ... Get your context-understanding shit together", "The first is not a defect", and "There is no more logical task_id".
- 12 matched keywords only inside text the user pasted: the skeptical-review prompt (six times), the working agreement and replies about it from another session, hook logs, and an onboarding findings list.
- 1 was a typo-duplicate of the turn kept as OBJ-19 ("rewor the prose").

For each kept objection I matched the offending text against the preceding assistant text with a script. All quotes from assistant messages match verbatim. Where the user quoted text, the entry says whether the quote matches. Where the target was a file, the entry names the file and the tool call that wrote it. Three slide-deck objections name no sentence, and the entries say so. The fault line restates the user's point in at most 12 words.

I marked confidence low where the turn is a question that could be about content as well as wording, where it corrects a fact (category `truth`), or where it names no target text.

The controls are 30 assistant passages of at least 40 words, each followed by a short accepting reply such as "yes", "A", or "Move on.". A script drew them at random from 17 sessions between 2026-10-15 and 2026-11-17, at most three per session. I removed five drawn passages: two over 170 words that would have needed cutting, one flattened table, one block of footnote links, and one passage that was mostly a code block.

The scripts and intermediate files are in the session scratchpad, not in the repository.
