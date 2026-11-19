# Story C: Written Files As Sources

## Goal

Show that a file an agent wrote during a session can enter the store as a source, anchored to the message that wrote it, even when the file on disk has since changed.

## Why this is a candidate

Story B imported only text blocks. The twenty run-lifecycle decisions never appeared in them: they were written into `docs/handoffs/handoff-run-lifecycle-decisions-2026-11-16.md` by a `Write` call. That file is untracked, and a later session overwrote it with a nine-line resume point. The only surviving copy of the decisions is the `Write` call in the session file, in message `ba9d6bda-9d76-4e2a-869b-de65384fe6de` of 2026-11-16T18:11:38Z.

## What to build

- `schema.sql`: an edge type `written_in` from a `source` to the `span` of the message that wrote it.
- `import_session.py`: also reads `Write` and `Edit` calls to markdown files. Each call becomes one `source` node for that file version, anchored to the message `uuid`, the tool call, the timestamp, and the file path relative to the repository. Its text is cut into spans like a message. The source gets a `written_in` edge to the nearest imported span of the writing message or its ancestors.
- `make_answer_key.py`: reads the `Write` call of message `ba9d6bda` from the session file and writes `answer-key.json`, the twenty numbered decisions with their numbers and text.

## Definition of done

1. The import runs twice; the second run adds no rows.
2. The recovered handoff is one source in the store, with a `written_in` edge to a span of its session, and its spans hold all twenty decisions.
3. `answer-key.json` holds twenty decisions, numbered 1 to 20, and each text occurs in the recovered handoff.
4. `uv run --script ask.py "What was decided about the run lifecycle?"` returns at least one span of the recovered handoff among its hits.
5. Every new source's message `uuid` occurs in the session file.
