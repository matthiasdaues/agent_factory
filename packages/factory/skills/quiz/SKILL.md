---
name: quiz
category: onboarding
description: Quiz me about the current codebase, one open question at a time, graded against the actual code.
argument-hint: "[area...] [N] [with code] [quick]"
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
- Any expression equivalent to `quick` in the language of the conversation, such as `schnell` in German, selects the **quick round**. It combines with either quiz type.
- All remaining text names the area or areas; if it is absent, use the whole repo.
- Treat the repository as source files, tests, and in-repo documentation. Exclude dependencies, generated artifacts, build outputs, and external fixtures unless the selected area requires them.
- Ignore unrecognized tokens only when they are part of an area name; do not invent another setting from them.

If the current client exposes prompt suggestions in `/config`, the first message holds only the quiz type with its one-sentence explanation and one line, in the user's language: the prompt suggestions in the input box can give answers away, so turn them off and reply when done. Do not ask a question or give a hint about the questions to come. Wait for the reply, then ask question 1. Otherwise, the first message names the quiz type with its explanation and then asks question 1.

## Quiz type

The quiz has one of two types. Name it in the first message, in the user's language, with one sentence that explains it, so the user knows how to answer. If the user did not choose it, say that closed book is the default and that `with code` switches to open book.

- **Closed book**: the user answers from memory and does not read the code. Test the mental model: observable behaviour, responsibilities, rules, trade-offs and the reason behind a design. Every question must be answerable by someone who knows the system well without opening a file. Never ask for anything that can only be known by reading the code: exact numeric limits, constants, error-code names, message texts, field or function names, the order of internal steps, or the full list of cases in a validator. If a scenario needs such an edge value, build the question around the rule instead (for example "is an invalid draft stored?"), not around the value. Exact-value questions are not asked in this type.
- **Open book** ("with code", "mit Code"): the user may read the code before answering. Lean on why-is-it-built-this-way questions, and exact values and edge cases are allowed.

Before asking, apply this test to each closed-book question: "Could a developer who understands the design, but has not memorised the file, answer this correctly?" If not, rewrite the question or replace it.

Quiz questions test the user's understanding of the codebase. They do not ask the user to make a project decision, so the decision-question format does not apply.

## Quick round

The quick round asks short questions that have short answers. The question count, the area rules and the wrap-up stay as in a normal round. These rules replace the normal ones:

- **Question length.** A question has at most 12 words and asks one thing. It expects one of three answers: yes or no, a single word, or one sentence.
- **Question types.** Ask short forms of the normal types: a scenario as a yes/no question ("Is an invalid draft stored?"), a responsibility as a one-word question ("Which component calculates the tax?"), and, in open book only, one exact value. Ask no why-questions.
- **Grading.** A word with the same meaning counts as ✔. A different component or fact is ✗. A yes/no answer is ✔ or ✗. ½ is for an answer that is too coarse, such as "the billing module" where the question asked for one component.
- **Resolution.** One line: the verdict, the correct fact and one `file:line` reference. Verify the fact in the code as in a normal round. After ✗ and ½, offer to answer a follow-up question if the user wants one.
- **Message format.** The resolution and the next question stand in one message. The question heading is short, in the form `4/5`.

## Each question

1. **Pick** an area this session has not quizzed yet, where possible. An area is a cohesive module, component or subsystem, not a single file. Before question 1, survey the repo structure once and plan N questions across distinct areas within the selected scope, keeping them to yourself; if the arguments name areas, stay within those. Keep a running list of the areas already used and take the next planned one, even if another area is bigger or harder to read. A question belongs to the area it was picked for, even if resolving it leads into a neighbouring one. Use each available area once before repeating one. If the selected scope has fewer than N distinct areas, go deeper into the same areas with different questions after exhausting them; do not stop early or fail. Read the code for that area now, just enough to ask and resolve this one question.
2. **Write** the question for the chosen quiz type. Across a round, mostly scenarios ("What happens when …?") and flow or design questions ("How does X come about, why is it built so?"). In open book, add one exact value ("What does `f` return for …?"); in closed book, add none. The question is **spoiler-free**: open wording, no answer options, no hint at which case is special. Check every premise of the question against the code before asking.
3. **Ask** exactly one question in its own message, headed "Question n of N" in the user's language. Then wait for the answer.
4. **Resolve**: verdict ✔ / ½ / ✗, what the code actually does with `file:line` references, and what the answer missed. Verify every fact in the resolution by reading the code. For exact values, run the function only when its purity and dependencies are evident from the code and it can be called without project imports that may have side effects. Do not run scripts, tests, or code that reads or writes data, files, or the network. If the value cannot be verified safely at runtime, say so instead of inventing it.
   If a resolution needs tool calls, do them first and write the resolution and the next question together in the final message, never in text between tool calls, so the user always sees them. In closed book, grade the mental model: a code detail the question did not need is added as extra information, not counted as a miss.
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
