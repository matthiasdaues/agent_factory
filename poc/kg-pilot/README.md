# Knowledge Graph Pilot

A technical proof of concept under the [technical-poc](../../packages/factory/playbooks/technical-poc.md) playbook. It tests the store settled in the [design position](../../docs/research/knowledge-graph-with-provenance/design-position.md#the-proposed-store) before the stakeholder decides on a proposal.

The stakeholder chose the scope on 2026-11-18: the store with its pilot tests, and the import of one real session. Extraction of ideas and decisions by a language model is out of scope; it belongs to the falsification study of the second survey's claim 6.

- [Story A: the store and its tests](story-a-store.md)
- [Story B: one session in the store](story-b-import.md)

The code here is not maintained or gated. Nothing carries over into the real codebase without a proposal.

## How to run

```sh
docker compose up -d
PGPASSWORD=owner psql -h 127.0.0.1 -p 55432 -U owner -d kg -v ON_ERROR_STOP=1 -f schema.sql
uv run --script checks.py
uv run --script import_session.py ~/.claude/projects/<project>/<session-id>.jsonl
uv run --script ask.py "What was decided about the run lifecycle?"
docker compose down -v
```

`checks.py` and the import share the database. Run the import on a fresh schema if the search should see only real vectors.

## Result

- [Notes on story A](notes-a.md): all nine pilot tests pass, twice on a fresh volume.
- [Notes on story B](notes-b.md): one real session imported, 1,966 spans, every anchor resolvable, the run-lifecycle question answered from 2026-11-16.

## Recommendation

Keep the store of the design position, with four changes the pilot found:

1. Import under `READ COMMITTED` and stop duplicates by a unique key or an advisory lock on the content hash. Under `SERIALIZABLE`, every vector reader conflicts with every concurrent writer.
2. Set `fastupdate = off` on the GIN index wherever `SERIALIZABLE` is used.
3. Filter the vector branch by model and version, with the iterative index scan.
4. Keep `pg_trgm` in the fused search for German compounds until Hunspell is decided.

The decision to build the store is deferred to a proposal. The pilot answers the technical risks; it does not settle the import from the usage pipeline, the import of written files such as handoffs, or the extraction of ideas and decisions.
