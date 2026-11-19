# Story D: Decisions Extracted From The Chat, Two Extractors Compared

## Goal

Measure how many of the twenty run-lifecycle decisions a language model finds in the chat alone, each with a verbatim quote and an anchor to a message that exists. Compare a Claude subagent with a local open model on the same input and the same instructions.

## Why this is a candidate

The case names two candidate claims for the first falsification study. Second-survey claim 6: transcript decisions can be extracted, each anchored to an existing utterance. First-survey claim 8: extraction by a language model yields quotes that occur verbatim in the source. Story C gives a known answer, so both can be measured. The stakeholder chose on 2026-11-19 to run both extractors.

## What to build

- `export_spans.py`: writes the chat spans of one day, by default 2026-11-15, the day the decisions were settled, to a JSON Lines file: span id, timestamp, role, and text. Written files are excluded, so the answer is not in the input.
- `extract-prompt.md`: the one instruction both extractors get. Each decision comes back as a short statement, a quote copied from one span, and that span's id.
- `extract_local.py`: runs the prompt through Ollama on windows of spans, with a fixed JSON schema and temperature 0, and writes `out/extraction-local.json` with the model name and digest.
- The Claude extraction: a fresh subagent reads only the prompt and the spans file and writes `out/extraction-claude.json` in the same format.
- `load_extractions.py`: loads each extraction as `decision` nodes with a `quotes` edge of status `candidate` to the cited span, and checks each quote against the span's text.
- A blind judgement: a fresh subagent gets the answer key and the pooled extracted decisions under neutral ids, in random order, without knowing which extractor wrote which. For each of the twenty it lists the pool ids that state that decision. It writes `out/judgement.json`.
- `score.py`: per extractor, the share of the twenty found, the share of extracted decisions that match any of the twenty, the share of quotes found verbatim in their span, and the share of anchors that resolve to a message in the session file.

## Definition of done

1. Both extraction files exist, in the same format, from the same spans file and prompt.
2. Every extracted decision is a node in the store with a `candidate` edge to its span, or the load reports why not.
3. The judgement covers all twenty decisions and every pool id.
4. `score.py` prints the four shares for each extractor.
5. `notes-cd.md` records the scores, the run times, and what the scores say about claims 6 and 8, with their limits: one session, one answer key, one judge.
