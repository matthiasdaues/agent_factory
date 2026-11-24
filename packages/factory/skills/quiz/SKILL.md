---
name: quiz
description: Quiz me about the current codebase, one open question at a time, graded against the actual code.
argument-hint: "[area...] [N] [with code]"
disable-model-invocation: true
---

Quiz the user about the codebase in the working directory: its code, tests and in-repo docs (ADRs, glossary, specs). The point is to find where the user's mental model and the code part ways.

Read [factory-voice.md](../../rulebooks/conventions/factory-voice.md) now and hold every rule as a writing constraint. No prose reaches terminal output or a file until it passes all four gates and clears the final pass.

## Settings

Read them from the free-text arguments: $ARGUMENTS

Defaults for anything left out: areas across the whole repo, 5 questions, **closed book** (the user answers from memory). Start right away, without asking about settings.

Interpret the arguments as follows:

- One positive integer token sets the number of questions `N`; if it is absent, use 5. If it is below 3, use 3 so the round can include the required question types.
- Any expression equivalent to `with code` in the language of the conversation, such as `mit Code` in German, selects **open book**.
- All remaining text names the area or areas; if it is absent, use the whole repo.
- Treat the repository as source files, tests, and in-repo documentation. Exclude dependencies, generated artifacts, build outputs, and external fixtures unless the selected area requires them.
- Ignore unrecognized tokens only when they are part of an area name; do not invent another setting from them.

If the current client exposes prompt suggestions in `/config`, the first message holds only one line, in the user's language: the prompt suggestions in the input box can give answers away, so turn them off and reply when done. Do not ask a question or give a hint about the questions to come. Wait for the reply, then ask question 1. Otherwise, ask question 1 in the first message.

- **Closed book**: lean on scenario questions; exact-value questions are guesswork here, keep them rare.
- **Open book** (any expression equivalent to "with code" in the language of the conversation): the user may read the code before answering; lean on why-is-it-built-this-way questions.

Quiz questions test the user's understanding of the codebase. They do not ask the user to make a project decision, so the decision-question format does not apply.

## Each question

1. **Pick** an area this session has not quizzed yet, where possible. An area is a cohesive module, component or subsystem, not a single file. Before question 1, survey the repo structure once and plan N questions across distinct areas within the selected scope, keeping them to yourself; if the arguments name areas, stay within those. Keep a running list of the areas already used and take the next planned one, even if another area is bigger or harder to read. A question belongs to the area it was picked for, even if resolving it leads into a neighbouring one. Use each available area once before repeating one. If the selected scope has fewer than N distinct areas, go deeper into the same areas with different questions after exhausting them; do not stop early or fail. Read the code for that area now, just enough to ask and resolve this one question.
2. **Write** the question. Across a round, mostly scenarios ("What happens when …?"), plus one exact value ("What does `f` return for …?") and one flow or design question ("How does X come about, why is it built so?"). The question is **spoiler-free**: open wording, no answer options, no hint at which case is special. Check every premise of the question against the code before asking.
3. **Ask** exactly one question in its own message, headed "Question n of N" in the user's language. Then wait for the answer.
4. **Resolve**: verdict ✔ / ½ / ✗, what the code actually does with `file:line` references, and what the answer missed. Verify every fact in the resolution by reading the code. For exact values, run the function only when its purity and dependencies are evident from the code and it can be called without project imports that may have side effects. Do not run scripts, tests, or code that reads or writes data, files, or the network. If the value cannot be verified safely at runtime, say so instead of inventing it.
5. **Divergence**: when the user says how it *should* behave and the code behaves otherwise, mark the resolution as a **divergence** on top of the verdict, then carry on.
6. **Own errors**: when a question or an earlier resolution of yours was wrong, say so plainly and give the correct fact.

After the user answers, put the resolution and the next question in the same message. That message contains exactly one new question. After the last resolution, do not ask another question; continue with the wrap-up.

The round is done when all N questions are resolved.

## Wrap-up

1. A table: number, topic, verdict with a one-line note.
2. Two sentences on the pattern: where the user's knowledge is solid and where the gaps cluster.
3. For each divergence, locate the applicable `AGENTS.md` or `CLAUDE.md`. If it defines an issue tracker, ask once whether to record the divergence there and record it only on a yes. If no local instruction defines a tracker, report that no record was made.
4. Offer another round; it quizzes areas this session has not covered.
5. End with one line, in the user's language, reminding them to turn the prompt suggestions back on in `/config` if they want them. Leave it out if another round starts right away, and give it at the end of that round instead.
