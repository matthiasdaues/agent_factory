# A2-SR-01: pg_textsearch README and ARCHITECTURE.md at commit 18646d9

```json
{
  "source_identity": "timescale/pg_textsearch, README.md and ARCHITECTURE.md at commit 18646d9b64af54d1e83f046c01df7426ac44ec7e (main branch, 2026-11-18); https://github.com/timescale/pg_textsearch",
  "author_or_issuing_body": "Tiger Data (formerly Timescale), pg_textsearch maintainers",
  "publisher": "GitHub",
  "publication_date": "2026-11-18T00:00:00Z",
  "relevant_event_date": "2026-11-18",
  "source_family": "Primary: project documentation in the extension repository. Same lineage as the release notes in A2-SR-02.",
  "precise_evidence_location": "README.md sections PostgreSQL Version Compatibility, Getting Started, Querying, Boolean Filtering, Index Options, Compaction, Memtable Architecture, Limitations (Partitioned Tables, Two-Phase Commit); ARCHITECTURE.md opening paragraph, section Storage and WAL, Compaction phases (line 369 of the file at this commit)",
  "method": "The maintainers describe the access method, its storage layout, WAL use, query syntax, and limits.",
  "limitations": "Project documentation states intended behaviour; it is not an independent test. The commit date stands for the publication date because the files carry no date. The README does not mention pg_dump or logical replication behaviour. Rollback behaviour of ordinary inserts is not stated in either file; only compaction output is said to survive rollback.",
  "provenance": "Fetched with `gh api repos/timescale/pg_textsearch/readme` and `gh api repos/timescale/pg_textsearch/contents/ARCHITECTURE.md` on 2026-11-18; commit SHA from `gh api repos/timescale/pg_textsearch/commits/main`. Re-verify at the commit above."
}
```

## Evidence

- README, opening list: "Modern ranked text search for Postgres." and "BM25 ranking with configurable `k1` and `b`".
- README, PostgreSQL Version Compatibility: "pg_textsearch supports PostgreSQL 17, 18, and 19 RC2." and "Build from source for PG19; prebuilt packages target PG17 and PG18."
- README, Getting Started: the extension must be preloaded: "Add pg_textsearch to `shared_preload_libraries` in `postgresql.conf`, then restart the server".
- README, index and query syntax: "CREATE INDEX docs_idx ON documents USING bm25(content) WITH (text_config='english');" and "`<@>` returns negative BM25 scores for ascending index scans, so lower scores rank first."
- README, Boolean Filtering: "Use PostgreSQL's `@@` operator and `tsquery` syntax to filter through a BM25 index". The tokenizer is a PostgreSQL text search configuration, so the keyword side reuses the built-in configurations that area 1 records.
- ARCHITECTURE.md, opening: "It uses an LSM-like layout: an on-disk memtable receives writes and spills into immutable segments that are compacted across levels."
- ARCHITECTURE.md, Storage and WAL: "In-place and multi-page publication mutations use `GenericXLog`." and "pg_textsearch has no custom WAL resource manager. The on-disk chain is authoritative through crash recovery and physical replication."
- README, Memtable Architecture: "The L0 memtable is stored in the index as a WAL-logged chain of pages. It is the durable source of truth and can be restored by PostgreSQL without loading `pg_textsearch.so`." and "The cache is rebuilt from the chain when missing or stale, while standbys always read the chain directly."
- README, Compaction: "Long merge work checks for cancellation, but published replacements remain physical and are not undone by `ROLLBACK`." ARCHITECTURE.md line 369: "Published physical changes are not undone by transaction rollback."
- README, Compaction: "Hot standbys serving queries must set `hot_standby_feedback = on` so active snapshots delay physical page reuse on the primary."
- ARCHITECTURE.md, Storage and WAL: "These are physical index statistics, not MVCC-filtered corpus statistics." Corpus statistics for scoring therefore include rows a snapshot cannot see (my reading of the sentence).
- README, Query Performance: "Update-heavy workloads can fragment index pages. Use `REINDEX` during a low-traffic window if cold-cache latency degrades".
- README, Partitioned Tables: "BM25 statistics are local to each partition."
- README, Two-Phase Commit: "`PREPARE TRANSACTION` is not supported after creating a BM25 index or while BM25 index-drop cleanup is pending."
- README, Background Compaction: managed background mode depends on a second extension, pg_durable; the default `inline` mode needs no second extension.
- Licence: the GitHub API reports SPDX `PostgreSQL` for the repository.
- Not shown: pg_dump behaviour, logical replication, and whether a transaction sees its own uncommitted inserts through the index. The README does not show a hybrid keyword-and-vector statement.
