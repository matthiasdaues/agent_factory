# Story B: One Session In The Store

## Goal

Show that one real factory session can be imported as spans anchored to its messages, embedded by a local multilingual model, and searched with the fused search followed by a traversal.

## Why this is a candidate

The case names the factory's own sessions as the first source family. The design position assumes each message carries `uuid`, `parentUuid`, and `timestamp`, so every span can point to the exact message it came from. The pilot found that the copies under `.agent-factory/usage/transcripts/` do not show these fields in the form expected. Claude Code's own session file does. This story imports from that file and records the difference as an open point.

## What to build

- `import_session.py`: reads the session file of `9f81748e-d987-4164-8d2f-82836fdc0b2c`, the session that wrote the run-lifecycle handoff of 2026-11-16. It keeps user and assistant text blocks, removes repeated records by `uuid`, writes one `source` node for the session and one `span` node per text block with its message `uuid` and `timestamp`, links each span to the session and to its parent message's span, and embeds every span with a local multilingual model, recording the model name and version.
- `ask.py`: runs the fused search for a question, then follows edges from the best spans to their neighbours, and prints each hit with its message `uuid` and timestamp.

## Definition of done

1. The import runs twice without error; the second run adds no rows, because unchanged text is skipped by its content hash.
2. Every span's message `uuid` occurs in the session file.
3. `uv run --script ask.py "What was decided about the run lifecycle?"` prints at least five spans from 2026-11-16, each with a `uuid` that exists in the session file.
4. A German query and an English query each return spans.
5. The import reports how many records it read, how many it dropped as repeats, and how long embedding took.

Write a short comparison note, `notes-b.md`: what the import showed, how good the hits look by eye, and the open point about the usage pipeline's copies.
