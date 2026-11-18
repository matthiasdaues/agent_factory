# A2-SR-09: pgx-bm25 (bm25_native) repository at commit 12055d2

```json
{
  "source_identity": "pgexperts/pgx-bm25, extension bm25_native: README.md at commit 12055d2b4e7a4de1e85af32275134e05d2e8f11c (2026-11-17); release v1.0.0 (2026-10-06); https://github.com/pgexperts/pgx-bm25",
  "author_or_issuing_body": "PGX, Inc. (pgexperts)",
  "publisher": "GitHub",
  "publication_date": "2026-11-17T18:49:53Z",
  "relevant_event_date": "2026-10-06",
  "source_family": "Primary: repository documentation and metadata of the extension. Found through a web search hit on a postgresql.org news item, which was not read.",
  "precise_evidence_location": "README.md opening paragraph, Requirements, Usage, ranking limits (around line 200 to 215), compatibility notes (around line 470 to 478), maintenance paragraph (line 578 onward), Repository and releases, License; repository metadata from the GitHub API",
  "method": "The maintainer describes the access method, its storage, and its limits; counts from the GitHub API.",
  "limitations": "The project is one release old. The public repository receives one squashed commit per release, so commit and contributor counts do not show development activity. The architecture files ARCHITECTURE.md and THEORY.md were not read. Rollback behaviour and the transaction semantics of the pending list are not stated in the README parts read.",
  "provenance": "Read with `gh api repos/pgexperts/pgx-bm25/readme`, `/releases`, `/commits`, `/contributors` on 2026-11-18. Re-verify at the commit above."
}
```

## Evidence

- Opening: "A native PostgreSQL **index access method** (`USING bm25_native`) for Okapi BM25 ranked full-text search. Pure C against stock PostgreSQL via PGXS — no external search engine, no separate runtime, no Rust. The whole index lives in the index relation's own pages, so it inherits WAL, crash recovery, and physical replication from core."
- Requirements: "**PostgreSQL 17, 18 or 19**" and "Minimum PostgreSQL 17 — PG16 is not supported".
- Usage: "CREATE INDEX docs_bm25 ON docs USING bm25_native (body);" with a match operator `@@@` and a rank operator `&@@` used in `ORDER BY ... LIMIT`.
- Ranking limits: a ranked scan read past `bm25_native.wand_top_k` rows re-ranks the match set. "If the index changed in between (rows inserted in the same transaction, or another session's commit, even under `REPEATABLE READ`), rows already returned are scored under the new corpus statistics". The corpus statistics are therefore not snapshot-bound (my reading).
- Compatibility notes, blockquote markers removed: "A logical dump/restore was never affected: `pg_dump` emits `CREATE INDEX`, so the restore rebuilds and re-stamps."
- Index options, around line 392: "`language` names a text-search dictionary as `<language>_stem`, so it is not limited to the Snowball set". The tokenizer therefore uses PostgreSQL text search dictionaries (my reading).
- Maintenance: "Inserts land in a WAL-logged pending list and are sealed into immutable segments automatically at a size threshold (the `bm25_native.seal_threshold` GUC, in KB) and during `VACUUM`".
- Repository and releases: "receives one squashed commit per release; development happens in a separate private repository". Issue numbers in the code refer to the private tracker.
- License: "The PostgreSQL License" (link text kept).
- Health: repository created 2026-10-06; one release, v1.0.0, on 2026-10-06; 14 stars; one contributor account (GitHub API, 2026-11-18).
- Not shown: independent tests, a hybrid statement, or adoption.
