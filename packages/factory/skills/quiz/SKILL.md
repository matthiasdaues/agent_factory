---
name: quiz
description: Quiz me about the current codebase, one open question at a time, graded against the actual code.
argument-hint: "[area] [number of questions] [with code]"
disable-model-invocation: true
---

Quiz the user about the codebase in the working directory: its code, tests and in-repo docs (ADRs, glossary, specs). The point is to find where the user's mental model and the code part ways.

## Settings

Read them from the free-text arguments: $ARGUMENTS

Defaults for anything left out: areas across the whole repo, 5 questions, **closed book** (the user answers from memory). Start right away, without asking about settings.

The first message holds nothing but one line, in the user's language: the prompt suggestions in the input box can give answers away, please turn them off in `/config` ("Prompt suggestions") and reply when done. No question and no hint about the questions to come. Wait for the reply, then ask question 1.

- **Closed book**: lean on scenario questions; exact-value questions are guesswork here, keep them rare.
- **Open book** ("with code", "mit Code"): the user may read the code before answering; lean on why-is-it-built-this-way questions.

## Each question

1. **Pick** an area this session has not quizzed yet. Read the code for that area now, just enough to ask and resolve this one question.
2. **Write** the question. Across a round, mostly scenarios ("What happens when …?"), plus one exact value ("What does `f` return for …?") and one flow or design question ("How does X come about, why is it built so?"). The question is **spoiler-free**: open wording, no answer options, no hint at which case is special. Check every premise of the question against the code before asking.
3. **Ask** exactly one question in the message, headed "Question n of N" in the user's language. Then wait for the answer.
4. **Resolve**: verdict ✔ / ½ / ✗, what the code actually does with `file:line` references, and what the answer missed. Every fact in the resolution is verified: by reading the code, and for exact values by running the function. Run only pure functions, extracted and called in isolation with the inputs from the question; scripts, tests and anything that reads or writes data, files or the network stay unrun.
5. **Divergence**: when the user says how it *should* behave and the code behaves otherwise, mark the resolution as a **divergence** on top of the verdict, then carry on.
6. **Own errors**: when a question or an earlier resolution of yours was wrong, say so plainly and give the correct fact.

Put the next question in the same message, after the resolution.

The round is done when all N questions are resolved.

## Wrap-up

1. A table: number, topic, verdict with a one-line note.
2. Two sentences on the pattern: where the user's knowledge is solid and where the gaps cluster.
3. For each divergence, ask once whether to record it, in the project's issue tracker as its `AGENTS.md`/`CLAUDE.md` describes. Record only on a yes.
4. Offer another round; it quizzes areas this session has not covered.
5. End with one line, in the user's language, reminding them to turn the prompt suggestions back on in `/config` if they want them. Leave it out if another round starts right away, and give it at the end of that round instead.
