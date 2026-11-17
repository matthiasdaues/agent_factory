# Writing-rules spike: report

This spike asked two questions. Do sharper writing rules make agents write
clearer, more truthful text? And does the academic tone of the factory's
instruction texts carry over into what agents write? The spike ran on
2026-11-17 in session `46e1cd8c`. It answers both questions with "barely".
The faults that matter are faults of truth, and only checks against facts
catch them.

## What the spike did

The test case was the proposal `docs/proposals/run-lifecycle.md`. The input
was the conversation that led to it, cut to the turns that shaped the
current text (`input/`, 27,700 words).

1. **Rule rounds.** The writing instructions were split into 42 claims
   (`01-claims.md`). Demon agents tried to refute each claim against the
   proposal. Two rounds of rewrites followed (`03-rules-round1.md`,
   `07-rules-round2.md`).
2. **Passage test.** Three judges sorted 62 passages: 32 that the user had
   objected to in earlier sessions, and 30 that the user had accepted
   (`05-objections.md`, `08-blind-passages.md`).
3. **Reader test.** Writers wrote the proposal from the conversation under
   different instructions. A blind reader answered 40 questions on each
   version, and a scorer marked the answers against a key taken from the
   user's decisions (`06-reader-test.md`).
4. **Register test.** Two writers got the same task. One read the original
   instruction pack (`13-pack-original/`), and the other read a plain-language
   rewrite of it (`13-pack-plain/`).

## Results

The demons refuted or damaged every rule in both rounds: 65 verdicts, and no
rule survived. A demon told to refute finds an edge case on any rule, so the
verdicts did not separate good rules from bad ones.

No judge in the passage test did better than chance:

| Judge                      | Objections caught | Accepted passages flagged |
| -------------------------- | ----------------: | ------------------------: |
| Current `factory-voice.md` |    7 of 32 (22 %) |            11 of 30 (37 %) |
| Round-2 rules              |   22 of 32 (69 %) |            29 of 30 (97 %) |
| Reader judgment, no rules  |     2 of 32 (6 %) |              2 of 30 (7 %) |

The reader test gave all versions about the same score:

| Version | Written under                            | Body words | Right (of 40) | Invented |
| ------- | ---------------------------------------- | ---------: | ------------: | -------: |
| K       | the user's working copy, several passes  |      6,300 |            35 |        2 |
| T       | current `factory-voice.md`, one sitting  |      7,251 |            37 |        0 |
| M       | round-2 rules, one sitting               |      8,456 |            33 |        0 |
| R       | original instruction pack, one sitting   |      7,572 |            34 |        0 |
| S       | plain instruction pack, one sitting      |      6,047 |            35 |        0 |

The plain pack made the text 20 % shorter at the same accuracy. It did not
change the word choice: R has 18.0 abstract nouns per 1,000 words, and S has
19.0. The factory's instruction texts score 45 to 52 on the same measure.
All five proposal versions score between 16 and 21.

## Conclusions

1. **Rules change length, not quality.** With one text per condition, a gap
   of two to four right answers is noise.
2. **The faults that held up are faults of truth.** Each one was found by a
   check against something outside the text:
   - Real IDs in examples that contradict the backlog: the proposal says
     ST-0352 depends on ST-0351, and calls BUG-0090 open.
   - A "can" that the state machine forbids: line 188 lets a story that just
     started be returned.
   - A count that disagrees with its own list: "twelve" next to thirteen
     items.
   - Undecided points stated as decided: Q31 and Q39 in version K.
3. **The user's objections are about references and coined terms.** 20 of 36
   mined objections concern clarity. Most point at a reference without its
   target or a term the agent invented. Buzzwords appear in none of them, yet
   the voice file spends most of its words on buzzwords.
4. **The register of the instructions does not set the register of the
   output.** The conversation that both writers read is the more likely
   source. That is a hypothesis. The spike did not test it.
5. **Adversarial loops on style do not converge.** An agent judge finds
   whatever its instruction tells it to look for.

## Limits

- Each condition produced one text, so the scores show no small effects.
- The round-2 rules were fitted to the objections they were judged on.
- The passage test showed fragments without the turn before them, so a
  judge could not see context-dependent faults such as "which proposal?".
- The accepted passages are weak controls. The user accepted the decision,
  which does not prove the user accepted the prose.

## Next steps

1. **Rewrite `factory-voice.md` in plain language, and shorten it.** Use
   `13-pack-plain/factory-voice.md` as the draft. Keep the rules that the
   objections support: every reference shows its target, no coined terms, a
   decision question carries its case and outcomes, a sober tone, and no
   claim beyond what was decided. The plain pack renamed headings, so links
   from other files to the voice file must be fixed in the same change.
2. **Build two lints.** An ID lint compares every real ID in a document with
   the backlog and the findings. A count lint compares a stated count with
   the list next to it.
3. **Add the reader test as a step before a proposal goes to `open`.** The
   questions come from the conversation, a fresh reader answers them blind,
   and a scorer marks them against the key.
4. **Optional: run the plain-list test.** A writer gets the decisions as a
   plain list instead of the conversation. This tests conclusion 4. It costs
   one writer, one reader, and one scorer.

Steps 2 and 3 need a proposal before any work starts.

## Files

The files were written under `docs/spikes/writing-rules/` and moved here
later. Paths inside them still name the old folder. Links inside the copied
factory files and proposal versions point from their original folders and do
not resolve here. `scratch/README.md` describes the blind key, the scoring
script, the stripped versions, and the readers' answers.
