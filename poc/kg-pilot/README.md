# Knowledge Graph Pilot

A technical proof of concept under the [technical-poc](../../packages/factory/playbooks/technical-poc.md) playbook. It tests the store settled in the [design position](../../docs/research/knowledge-graph-with-provenance/design-position.md#the-proposed-store) before the stakeholder decides on a proposal.

The stakeholder chose the scope on 2026-11-18: the store with its pilot tests, and the import of one real session. Extraction of ideas and decisions by a language model was out of scope then. On 2026-11-19 the stakeholder added stories C and D: written files as sources, and extraction by two models compared. Story E, the same day, makes the quote check a gate of the store, and story F links a topic's old and new names.

- [Story A: the store and its tests](story-a-store.md)
- [Story B: one session in the store](story-b-import.md)
- [Story C: written files as sources](story-c-written-files.md)
- [Story D: decisions extracted from the chat, two extractors compared](story-d-extraction.md)
- [Story E: the quote check as a gate](story-e-quote-gate.md)
- [Story F: a topic with its old and new name](story-f-topics.md)

The code here is not maintained or gated. Nothing carries over into the real codebase without a proposal.

## How to run

```sh
docker compose up -d
PGPASSWORD=owner psql -h 127.0.0.1 -p 55432 -U owner -d kg -v ON_ERROR_STOP=1 -f schema.sql
uv run --script checks.py
uv run --script import_session.py ~/.claude/projects/<project>/<session-id>.jsonl
uv run --script ask.py "What was decided about the run lifecycle?"
uv run --script make_answer_key.py ~/.claude/projects/<project>/<session-id>.jsonl
uv run --script export_spans.py 2026-11-15
uv run --script extract_local.py   # needs Ollama with qwen3:8b
# The Claude extraction and the judgement are subagent runs: see story D.
uv run --script make_pool.py
uv run --script load_extractions.py
uv run --script test_quote_gate.py
# A store loaded before story E: psql ... -f migrate-to-f.sql
uv run --script load_topic.py
uv run --script test_topics.py ~/.claude/projects/<project>/<session-id>.jsonl
uv run --script score.py ~/.claude/projects/<project>/<session-id>.jsonl
docker compose down -v
```

`checks.py` and the import share the database. Run the import on a fresh schema if the search should see only real vectors.

## Result

- [Notes on story A](notes-a.md): all nine pilot tests pass, twice on a fresh volume.
- [Notes on story B](notes-b.md): one real session imported, 1,966 spans, every anchor resolvable, the run-lifecycle question answered from 2026-11-16.
- [Notes on stories C and D](notes-cd.md): the overwritten handoff recovered from the session as a source; the Claude extractor found 20 of 20 decisions with exact quotes, the local `qwen3:8b` 17 of 20, with 8 of 37 quotes not in their span and 4 statements that contradict a decision.
- Story E: the store refuses the 8 quotes that are not in their span and loads the other 58 decisions; all six items pass on a throwaway database. See the [open points of the notes](notes-cd.md#open-points).
- [Notes on story F](notes-f.md): the run-lifecycle question now returns the 24 decisions that cover all twenty, through the topic's new name, and the old name returns the same; all six items pass. The route needs the name's words in order.

## Recommendation

Keep the store of the design position, with four changes the pilot found:

1. Import under `READ COMMITTED` and stop duplicates by a unique key or an advisory lock on the content hash. Under `SERIALIZABLE`, every vector reader conflicts with every concurrent writer.
2. Set `fastupdate = off` on the GIN index wherever `SERIALIZABLE` is used.
3. Filter the vector branch by model and version, with the iterative index scan.
4. Keep `pg_trgm` in the fused search for German compounds until Hunspell is decided.

The decision to build the store is deferred to a proposal. The pilot answers the technical risks; it does not settle the import from the usage pipeline. Stories C and D add two points: extracted decisions need a quote check as a gate and stay candidates until a person confirms them, and a topic needs a link between its old and new names.
