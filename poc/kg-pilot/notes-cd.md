# Notes On Stories C And D: Written Files And Extracted Decisions

Run on 2026-11-19 against the same store and session as story B. The session had grown to 6,045 records by then.

## Story C: written files as sources

| Item | Result |
| --- | --- |
| 1. Two runs, the second adds nothing | Met. The first run added 8,197 rows, among them 79 file versions; the second added 0. |
| 2. The recovered handoff is one source with all twenty decisions | Met. One source for message `ba9d6bda` of 2026-11-16T18:11:38Z, one `written_in` edge, three spans that hold all twenty decision texts. |
| 3. The answer key holds decisions 1 to 20 | Met. `answer-key.json`, recovered from the `Write` call in the session file. |
| 4. The run-lifecycle question finds the handoff | Not met. The best handoff span ranks 41st of 53 candidates. |
| 5. Every new source's message exists | Met. 1,003 span anchors, 0 not found. |

Item 4 fails because of the words, not the store. The decisions were settled before the topic had its name: the handoff calls it "Dispatch process", and the proposal was titled "Run Lifecycle" at 21:49 on 2026-11-15, after the last decision. The same search ranks a handoff span 7th for "What was decided about the dispatch process?" and 2nd for "decisions so far". A knowledge store needs a link between a topic's old and new names. An extracted decision linked to its topic node would give one.

The recovery itself is the stronger finding. The handoff on disk was overwritten, and the decisions note in the scratchpad is gone. The session file kept the tool call that wrote them, so the store could rebuild the file version and anchor it to the message that wrote it.

## Story D: two extractors on one day of chat

Input: 175 chat spans of 2026-11-15, 104,532 characters, with written files left out. Both extractors got `extract-prompt.md`. A fresh Claude subagent judged the 66 pooled statements against the answer key without knowing their authors.

| Measure | Claude subagent (`claude-opus-5-5`) | Local `qwen3:8b` through Ollama |
| --- | --- | --- |
| Decisions returned | 29 | 37 |
| Key decisions found | 20 of 20 | 17 of 20; missed 7, 17, 19 |
| Returned decisions that match a key decision | 24 of 29 | 17 of 37 |
| Quotes exact in the cited span | 29 of 29 | 28 of 37, 1 more after whitespace |
| Quotes not in the cited span | 0 | 8: 1 sits in the next span, 7 occur nowhere |
| Anchors that resolve to a session message | 29 of 29 | 37 of 37 |
| Statements that contradict a key decision | 0 | 4, by the judge's notes |
| Time | 63 seconds | 5,296 seconds; 34,353 prompt and 3,031 output tokens on a 4 GB GTX 1050 Ti, 54% on the GPU |

All 66 decisions are in the store as `decision` nodes with a `candidate` `quotes` edge to their span. A second load added nothing.

## What it says about the two claims

First-survey claim 8, verbatim quotes: the Claude extractor met it on this session. The local model did not; 7 of its 37 quotes occur nowhere in the input. So the quote check must be a gate in the import, not a hope. In the store it is one query against the span text.

Second-survey claim 6, decisions anchored to existing utterances: the Claude extractor found all twenty in one day of chat, each with an anchor that resolves. The local model found 17, and 4 of its statements say the opposite of a decision, such as "the guardrail asks rather than denies". A contradiction with a valid anchor is worse than a miss, because it looks like evidence. Extracted decisions should stay candidates until a person confirms them, as the design position already says for edges.

## Limits

- One session, one answer key, one judge, one run per extractor at temperature 0.
- The answer key was written by the assistant that took part in the conversation, and the judge is the same model family as one extractor. Both can favour Claude's phrasing; the judge saw no author names, but style can tell.
- The extractor and the judge were told to read only their input files. Nothing enforced it.
- Claude read the whole day in one context. The local model got twelve windows of about 10,000 characters, so a question and its answer can fall into different windows.
- Decisions 7, 17, and 18 in the key carry refinements from 2026-11-16 that the chat of 2026-11-15 does not hold. The judge counted a statement that states a central part.
- The judge's matches are one reading. `out/judgement.json` holds them with notes, for a person to check.

## Open points

1. Link a topic's old and new names, so a question in today's words finds decisions made in yesterday's.
2. Make the quote check a gate of the import, and keep extracted decisions as candidates until a person confirms them.
3. Repeat story D on a second session with an answer key written by a person, and with a judge from another model family.

## Decision

The stakeholder ruled out the local model as a feasible alternative for extraction on 2026-11-19. `extract_local.py` stays as the record of the comparison. The local embedding model of story B is not affected.
