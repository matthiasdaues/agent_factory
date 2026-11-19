# Notes On Story B: One Session In The Store

Run on 2026-11-19. Source: the Claude Code session file of `9f81748e-d987-4164-8d2f-82836fdc0b2c`, the session that wrote the run-lifecycle handoff of 2026-11-16. Model: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` through fastembed 0.9.1, on the CPU.

## Definition of done

| Item | Result |
| --- | --- |
| 1. Two runs, the second adds nothing | Met. The first run added 6,757 rows; the second added 0 in 1.8 seconds. |
| 2. Every anchor exists in the session file | Met. 865 message anchors, 0 not found. |
| 3. Five spans from 2026-11-16 with real anchors | Met. The English question returned hits and one-hop neighbours from 2026-11-16, among them the handoff summary, the "where things stand" message, and the message that read the handoff and named "the twenty design decisions". |
| 4. A German and an English query return spans | Met. The German question returned the same run-lifecycle spans, through the vector branch only. |
| 5. Counts and timing | 5,623 records with a `uuid`, 3,695 user and assistant messages kept, 1,966 spans, 0 repeats; embedding took 92 seconds, the whole import 95. |

## What the import showed

- The Claude Code session file has no repeated records. The repeats the design position warned about live in the usage pipeline: `.agent-factory/usage/transcripts/` held 523 copies of this session on 2026-11-19, and the copy inspected did not show `uuid` and `parentUuid` as top-level fields. The design position assumed it did. That is an open point for the import from the usage pipeline.
- The session is still in use, so the file grew by ten records between two runs. An import must expect a source that changes.
- Reply edges were built from `parentUuid`, skipping tool records, to the nearest imported message. The traversal follows them well.
- Every span also has a `part_of` edge to the session source, and the traversal follows it on every hit. That hop adds nothing. The traversal should take edge types as a parameter.

## How good the hits look

By eye, all ten English hits are about the run lifecycle: decisions, summaries, review findings, and resume points. None is the decision list itself. The decisions sit in the handoff file, not in the chat, and the pilot imports no files. Finding "the twenty decisions" needs either the handoff as a source or the extraction step of claim 6.

The German question worked across languages through the multilingual model. The keyword branch could not help, because the language heuristic tagged all 1,966 spans as English, correctly for this session. Cross-language search rests on the vector branch.

## Open points

1. Import from the usage pipeline: find where its copies keep `uuid`, `parentUuid`, and `timestamp`, or import from the CLIs' own session files.
2. Import the handoff and other written files as sources, so decisions written there can be found and anchored.
3. Give the traversal edge-type parameters.
4. The language heuristic is a stand-in; a real import needs language detection per span.
