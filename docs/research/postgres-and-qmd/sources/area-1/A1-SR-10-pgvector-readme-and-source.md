# A1-SR-10: pgvector README and index source code at commit 7c7345e

```json
{
  "source_identity": "pgvector README.md and source files src/hnsw.c, src/hnswinsert.c, src/hnswscan.c, src/hnswvacuum.c, src/ivfflat.c and src/ivfinsert.c at commit 7c7345e0121d69f5a6e2a6a41357ad5a9a10156e (head of master on 2026-11-18), https://github.com/pgvector/pgvector",
  "author_or_issuing_body": "Andrew Kane (ankane) and pgvector contributors",
  "publisher": "GitHub, repository pgvector/pgvector",
  "publication_date": "2026-11-18T12:47:13Z",
  "relevant_event_date": "2026-11-18",
  "source_family": "Primary: project documentation and source code of pgvector, written by its maintainer. Same lineage as A1-SR-11 to A1-SR-15. The graph-and-embeddings survey holds an earlier read of the same README as A2-SR-01; this record reads it again for transactions, MVCC, filtering and costs.",
  "precise_evidence_location": "README: opening section; Indexing; HNSW, Index Build Time; IVFFlat; Filtering; Iterative Index Scans; Vacuuming; FAQ 'Is replication supported?'; Troubleshooting 'Why are there less results for a query after adding an HNSW index?'. hnsw.c lines 489 to 582 (index access method routine: ampredlocks, aminsert, amcanreturn, amgettuple); hnswinsert.c lines 836 to 860 (hnswinsert); hnswscan.c lines 223 to 226 (MVCC snapshot check); hnswvacuum.c functions RepairGraphElement and RepairGraphEntryPoint; ivfflat.c line 470 (ampredlocks)",
  "method": "Project documentation that states features and syntax; source code read at a fixed commit.",
  "limitations": "The README is a living file and describes master, which holds unreleased 0.9.0 work; the latest release is 0.8.7 (A1-SR-11). The README is the vendor's own text, so it is used for stated features and syntax only, not for performance. The source was read, not compiled or run. Every statement about own-write visibility through HNSW is inferred from the code and from the PostgreSQL index interface (A1-SR-07); no pgvector document states it, and the record marks it as inferred.",
  "provenance": "Files downloaded with curl from https://raw.githubusercontent.com/pgvector/pgvector/7c7345e0121d69f5a6e2a6a41357ad5a9a10156e/<path> on 2026-11-18. Re-verify at that commit."
}
```

## Evidence

- README, opening: "Store your vectors with the rest of your data."
- README, Indexing: "By default, pgvector performs exact nearest neighbor search, which provides perfect recall."
- README, Indexing: "Unlike typical indexes, you will see different results for queries after adding an approximate index."
- README, HNSW: "It has better query performance than IVFFlat (in terms of speed-recall tradeoff), but has slower build times and uses more memory."
- README, HNSW, Index Build Time: "Indexes build significantly faster when the graph fits into `maintenance_work_mem`"
- README, IVFFlat: "Create the index *after* the table has some data"
- README, Filtering: "With approximate indexes, filtering is applied *after* the index is scanned."
- README, Filtering: "If a condition matches 10% of rows, with HNSW and the default `hnsw.ef_search` of 40, only 4 rows will match on average."
- README, Filtering: "For tenant isolation, use [list partitioning](https://www.postgresql.org/docs/current/ddl-partitioning.html) or separate tables."
- README, Iterative Index Scans: "Relaxed allows results to be slightly out of order by distance, but provides better recall"
- README, Vacuuming: "Vacuuming can take a while for HNSW indexes. Speed it up by reindexing first."
- README, FAQ: "Yes, pgvector uses the write-ahead log (WAL), which allows for replication and point-in-time recovery."
- README, Troubleshooting: "There may be even less results due to dead tuples or filtering conditions in the query."
- hnsw.c, lines 548, 564 and 570: `amroutine->ampredlocks = false;`, `amroutine->aminsert = hnswinsert;`, `amroutine->amcanreturn = NULL;`
- hnswinsert.c, function `hnswinsert`: each inserted row calls `HnswInsertTuple`, which links the new element into the on-disk graph during the INSERT statement.
- hnswscan.c, lines 223 to 226: "Requires MVCC-compliant snapshot as not able to maintain a pin"
- hnswvacuum.c: VACUUM removes deleted heap TIDs from the graph and repairs the neighbours of removed elements (functions `RepairGraphElement` and `RepairGraphEntryPoint`).
- ivfflat.c, line 470: `amroutine->ampredlocks = false;`
- Statement S1: supported. Vectors are columns of ordinary tables, written with INSERT and queried with SQL operators, in the same WAL as the other tables.
- Statement S7 (inferred): HNSW inserts the element at INSERT time, returns heap TIDs, and cannot return tuples itself, so the core checks every candidate against the snapshot (A1-SR-07). A later statement in the same transaction therefore can find the transaction's own new vector through HNSW. Two limits apply. First, HNSW returns at most `hnsw.ef_search` candidates, and dead or invisible rows use up candidates. Second, HNSW and IVFFlat take no predicate locks, so SERIALIZABLE checks fall back to a lock on the whole index (A1-SR-15).
- Statement S5 (inferred): the README shows vector search inside a materialized CTE with ORDER BY and LIMIT. That form can be the non-recursive part of a WITH RECURSIVE statement (A1-SR-05). No source shows the combined statement.
- Simplicity facts: one extension inside the PostgreSQL server, no separate process; SQL is the query language; the index is derived data and can be rebuilt with REINDEX; embeddings are written by the caller, and the README names no feature that recomputes a vector when its text changes.
- What the source does not show: measured recall, speed, or build time. None is recorded.
