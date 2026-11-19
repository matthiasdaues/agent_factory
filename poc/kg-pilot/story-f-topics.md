# Story F: A Topic With Its Old And New Name

## Goal

Show that a question in today's words finds the decisions made under an older name of the same topic.

## Why this is a candidate

In story C, "What was decided about the run lifecycle?" ranked the handoff 41st. The twenty decisions were made under the name "Dispatch process", and the proposal got the title "Run Lifecycle" at 21:49 on 2026-11-15, after the last decision ([notes on stories C and D](notes-cd.md), open point 1). The stakeholder chose a topic node over a synonym list on 2026-11-19, because a list records neither who renamed the topic nor when.

## What to build

- `schema.sql`: node kinds `topic` and `name`; edge types `names` (name to topic) and `about` (decision to topic); a `quotes` edge from a name to the span that first uses it, so the quote gate checks it; and a function `topic_route(question)` that finds the topics named in a question and returns their decisions.
- `migrate-to-f.sql`: the same changes, plus the quote gate of story E, for a store loaded before them, without dropping data.
- `load_topic.py`: one topic "Run lifecycle" with both names, and an `about` candidate edge from each Claude-extracted decision that the judge matched to a key decision.
- `ask.py`: prints the topic route before the fused search.
- `test_topics.py`: the items below, against the pilot store.

## Definition of done

1. "What was decided about the run lifecycle?" returns decisions that cover all twenty key decisions.
2. "What was decided about the dispatch process?" returns the same decisions.
3. A question that names neither, "What was decided about the release process?", returns no topic.
4. Every returned decision quotes a span of a message in the session file.
5. Each name has one `quotes` edge to the span that first uses it, and its quote is in that span.
6. A further load adds nothing.
