# Area 2: Ranking Extensions and Hybrid Search

This index covers BM25 extensions for PostgreSQL and the SQL statements that fuse keyword and vector results. It holds 24 source records in `sources/area-2/`. The brief asked for 10 to 15. The extra records give each concept-history step a record with a matching date. Records A2-SR-20 to A2-SR-24 cover pgvectorscale, which A2-SR-19 installs. Records from the postgres-and-qmd survey are cited with the prefix "postgres-and-qmd", so that their IDs do not clash with this folder.

## State of the Art

Four BM25 extensions have public repositories with commits in 2026 (A2-SR-02, A2-SR-08, A2-SR-09, A2-SR-18). All four add an index access method and a scoring operator, and none needs a server outside PostgreSQL.

| Fact                              | pg_search (ParadeDB)                                                                     | pg_textsearch                                                                              | VectorChord-bm25                                          | pgx-bm25 (bm25_native)                                     |
| --------------------------------- | ---------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------ | --------------------------------------------------------- | ---------------------------------------------------------- |
| Index layout                      | LSM segments built with Tantivy, in PostgreSQL block storage (A2-SR-03, A2-SR-04)        | LSM memtable and segments in index pages (A2-SR-01)                                        | Block-WeakAnd index on a bm25vector column (A2-SR-08)     | Pending list and sealed segments in index pages (A2-SR-09) |
| Tokenizer                         | Its own tokenizers (A2-SR-03)                                                            | PostgreSQL text search configurations; one partial index per language (A2-SR-01, A2-SR-19) | Second extension pg_tokenizer (A2-SR-08)                  | PostgreSQL text search dictionaries (A2-SR-09)             |
| WAL                               | Custom resource manager (A2-SR-06); Community writes WAL since 0.24.0 (A2-SR-18)         | Generic WAL, no custom resource manager (A2-SR-01)                                         | Generic WAL in the page writer, read from code (A2-SR-08) | Stated: inherits WAL from core (A2-SR-09)                  |
| Physical replication              | Enterprise only (A2-SR-03); in Community, creating an index stops the standby (A2-SR-06) | Supported since v1.2.0, needs `hot_standby_feedback` (A2-SR-01, A2-SR-02)                  | Not found                                                 | Stated as inherited from core (A2-SR-09)                   |
| PostgreSQL versions               | 15 to 18 (A2-SR-03)                                                                      | 17, 18, 19 RC (A2-SR-01); the Tiger Cloud page for v1.1.0 states 17 and 18 (A2-SR-19)      | 14 to 18 (A2-SR-08)                                       | 17, 18, 19 (A2-SR-09)                                      |
| Licence                           | AGPL-3.0; Enterprise is commercial (A2-SR-03)                                            | PostgreSQL (A2-SR-01)                                                                      | AGPLv3 or Elastic License v2 (A2-SR-08)                   | PostgreSQL (A2-SR-09)                                      |
| Releases 2024-11-18 to 2026-11-18 | 153 (A2-SR-18)                                                                           | 23, first on 2025-10-14 (A2-SR-02)                                                         | 6, last on 2025-12-15 (A2-SR-08)                          | 1, on 2026-10-06 (A2-SR-09)                                |
| Contributors                      | 161 (A2-SR-18)                                                                           | 17 (A2-SR-02)                                                                              | 9 (A2-SR-08)                                              | 1 public account; development is private (A2-SR-09)        |
| Extra parts                       | pgvector for vectors (A2-SR-07)                                                          | Preload; pg_durable for background compaction only (A2-SR-01)                              | pg_tokenizer and a derived token column (A2-SR-08)        | None stated (A2-SR-09)                                     |

**Transaction boundary.** ParadeDB states that index changes are atomic and follow MVCC (A2-SR-03). Issue #7093 reports index documents without heap rows after crash recovery (A2-SR-06). pg_textsearch has a rollback test suite (A2-SR-02). Its compaction output survives `ROLLBACK`, and its corpus statistics are not filtered by MVCC (A2-SR-01). The Tiger Cloud page for v1.1.0 states that an insert fails with an error when memtable memory exceeds `pg_textsearch.memory_limit` (A2-SR-19). pgx-bm25 states that a ranked scan can rescore rows under new corpus statistics within one statement (A2-SR-09). For VectorChord-bm25 the sources show no statement on rollback or visibility. The token column is derived data that a trigger or an `UPDATE` must keep in sync (A2-SR-08).

**Dump and rebuild.** pgx-bm25 states that `pg_dump` emits `CREATE INDEX`, so a restore rebuilds the index (A2-SR-09). ParadeDB recommends `pg_dump` and `pg_restore` to load data (A2-SR-03). For pg_textsearch and ParadeDB the sources name `REINDEX` as the way to rebuild the index (A2-SR-01, A2-SR-06).

**One statement for keyword and vector.** Three records show the full statement. The pgvector example ranks with built-in `ts_rank_cd` and a pgvector distance, then fuses with reciprocal rank fusion (RRF), using `FULL OUTER JOIN` and k = 60 (A2-SR-10). ParadeDB fuses its BM25 branch and a vector branch with `UNION ALL`, `GROUP BY`, and per-branch weights (A2-SR-07). The Tiger Cloud page fuses a pg_textsearch BM25 branch and a pgvector HNSW branch with RRF, k = 60, `LEFT JOIN` to the base table, and optional weights of 0.7 and 0.3 (A2-SR-19). Both are plain SQL with common table expressions. Neither needs a fusion function from an extension. qmd fuses outside the database (postgres-and-qmd A2-SR-02, A2-SR-09). No record shows a score-based fusion, such as a convex combination, in SQL.

**pgvectorscale.** pgvectorscale is a vector index extension, not a BM25 extension. It adds the `diskann` index type, a compression method called Statistical Binary Quantization (SBQ), and label filters, and it requires pgvector (A2-SR-20, A2-SR-21). The graph-and-embeddings survey records its research background (A4-SR-05, A4-SR-06, A4-SR-10). The A2-SR-19 statement uses `USING hnsw` and `<=>`, which pgvector provides, so it needs `CREATE EXTENSION vector` and not `vectorscale` (inferred, A2-SR-20, A2-SR-24). The vendor tutorial runs the same fused statement on a `diskann` index (A2-SR-23).

- Index writes go through generic WAL, read from code; no document states replication, rollback, or `pg_dump` behaviour (A2-SR-21, A2-SR-22).
- It supports PostgreSQL 14 to 18. Support for 19 exists only as an open user issue (A2-SR-21, A2-SR-22).
- The licence is PostgreSQL. The control file sets `superuser = true`. It builds from source outside Tiger Cloud (A2-SR-20, A2-SR-21).
- Seven releases fall between 2024-11-18 and 2026-11-18, and the API counts 15 contributors. The README calls the project "still at an early stage" and announces pg_vectorsearch, in early alpha, as a new approach (A2-SR-20, A2-SR-22).
- Labels are `smallint` values in a `smallint[]` column named in the index. The index matches one `&&` overlap condition, that is, a logical OR. A second condition is checked after the scan, and conjunctive label filters are not planned (A2-SR-20, A2-SR-21, A2-SR-22). Other `WHERE` conditions are applied after the scan, which streams like pgvector's iterative scan (A2-SR-20).
- A filter by embedding model works if each row carries a label number for its model. That column is derived data to keep in sync (inferred, A2-SR-20). Since 0.9.1 the column needs a `vector(N)` type, so models with different dimensions need separate columns (inferred, A2-SR-22). The pilot's `hnsw.iterative_scan` filter serves the same case without a second extension (inferred, A2-SR-20).

## Concept: BM25 Term Weighting

1. **Robertson-Sparck Jones weight without term frequency or document length (BM1), TREC-1, 1992.** The record dates are 1993-11-01 (A2-SR-16) and 1994-11-02 (A2-SR-14); no record of the TREC-1 paper itself exists. Criticism: the scheme favours long documents (A2-SR-14, footnote 1), and TREC-2 added term frequency and length components (A2-SR-16).
2. **BM11 and BM15 from the 2-Poisson model, 1993-11-01 (A2-SR-16).** Criticism: the authors call the 2-Poisson argument weak and leave k1 undetermined (A2-SR-16). BM11 rests on the verbosity hypothesis, which "might be expected to exaggerate the document length effect" (A2-SR-14, 1994-11-02).
3. **BM25, which mixes BM11 and BM15 through the parameter b, 1994-11-02 (A2-SR-14).** Criticism: the model gives no guidance on k1 and b, and it treats a document as one stream of text (A2-SR-15, 2009).
4. **BM25F for documents with several fields, recorded 2009 (A2-SR-15).** The 2004 paper that introduced BM25F was not read (gap). No later criticism is recorded.

The extensions take BM25 as given. pg_textsearch exposes k1 and b (A2-SR-01). VectorChord-bm25 criticises built-in `ts_rank` as inefficient (A2-SR-08), without a measurement.

## Concept: Rank Fusion

1. **Score fusion: CombSUM and CombMNZ, TREC-2 (A2-SR-12, event 1993-08-31, published 1994-03-01).** The method adds the similarity values of several runs. Criticism: CombMNZ uses "uncalibrated scores" and its results have higher variance (A2-SR-11, 2009-07-19).
2. **Reciprocal rank fusion with k = 60, 2009-07-19 (A2-SR-11).** The method combines ranks "without regard to the arbitrary scores". Criticism: RRF is "sensitive to its parameters" and "discards useful information" about the score distribution (A2-SR-13, 2023-05-04). An intermediate step is a gap: Chen et al. 2022 used RRF for zero-shot hybrid retrieval and argued against convex combination. That paper is known only from A2-SR-13 and was not read.
3. **Convex combination of normalized lexical and semantic scores, 2023-05-04 (A2-SR-13).** No criticism of this step is recorded.
4. **RRF in SQL without weights, pgvector example, 2024-08-28 (A2-SR-10).** No recorded criticism drove this step. It follows the 2009 form.
5. **RRF in SQL with per-branch weights, ParadeDB, 2026-11-18 (A2-SR-07).** The page cites no paper. No record links the weights to the criticism in step 2.

## Concept: pg_textsearch Durability and Replication

1. **Index buffers written without WAL, as of 2026-03-21 (A2-SR-17).** The v0.0.4 note of 2025-11-20 describes a shared-memory memtable (A2-SR-02). Criticism: no crash atomicity and "No physical replication" of index changes (A2-SR-17, 2026-03-21).
2. **Custom WAL entries to keep the replica memtable in sync, v1.2.0, 2026-05-12 (A2-SR-02).** Criticism: the custom entries "are not compatible with the stateless WAL redo" of disaggregated storage systems (A2-SR-02, 2026-05-29).
3. **Paged memtable with a shared-memory cache, generic WAL, no custom resource manager, v1.3.0, 2026-05-29 (A2-SR-02).** The current files describe this design (A2-SR-01). The sources record limits but no criticism yet: compaction output survives rollback, and standbys need `hot_standby_feedback` (A2-SR-01). The Tiger Cloud page, last changed on 2026-06-30, still describes v1.1.0: memtables in dynamic shared memory, rebuilt from the heap after a crash, and no background compaction (A2-SR-19). It is documentation lag, not a criticism, so it adds no step.

## Concept: ParadeDB Index Storage and WAL

1. **pg_bm25 renamed to pg_search with v0.6.0. The index is a PostgreSQL index type, 2023-11-15 (A2-SR-05).** The criticism that led to block storage is a gap. The 0.14.0 note implies that the index was not in block storage before (A2-SR-04).
2. **Index on PostgreSQL block storage, with WAL, replication, and recovery for Enterprise, 2025-01-12 (A2-SR-04).** Criticism: the PostgreSQL free space map is not WAL-logged, so free space is lost after a failover (A2-SR-04, 2025-07-17). The fix is an own WAL-logged free space map in 0.17.0 (A2-SR-04).
3. **Community writes WAL for its buffers for crash recovery, 0.24.0, 2026-06-03 (A2-SR-18).** Criticism: in Community, creating an index stops the physical standby for the whole cluster (A2-SR-06, 2026-08-20). Crash recovery can leave index documents without heap rows (A2-SR-06, 2026-10-29). Both issues were open on 2026-11-18.

The sources show no history for VectorChord-bm25 or pgx-bm25.

## Gaps

- Lv and Zhai 2011, on a lower bound for term-frequency normalization in BM25: the PDF at the CUHK address returned an HTML page, and the ACM copy is behind a paywall. No record exists.
- Robertson and Walker 1994 (SIGIR) on 2-Poisson approximations, the TREC-1 Okapi paper, and the 2004 BM25F paper were not read.
- Chen et al. 2022 and Montague and Aslam 2002 (Condorcet Fuse) were not read; both are known only through citations in A2-SR-13 and A2-SR-11.
- A web search summary said that Neon deprecated pg_search. Two Neon pages, fetched on 2026-11-18, do not mention it, so the statement is not recorded.
- The postgresql.org news items on pgx-bm25 and pg_textsearch 1.0, and a Google Cloud post on BM25 in AlloyDB, were seen as search hits and not read.
- ParadeDB: the record does not show where the index files lived before 0.14.0, or the WAL state of Community from 0.14.0 to 0.24.0. Issue #727, "Implement ROLLBACK", from 2024, has an empty template body. Issue #2195, a `pg_dump` error from 2025, was seen in search results and not read.
- pg_dump behaviour is not stated for pg_textsearch or VectorChord-bm25. The Tiger Cloud page on pg_textsearch says nothing on WAL, replication, rollback, or pg_dump either (A2-SR-19). Its sibling page for Tiger Cloud on Azure was not read.
- VectorChord-bm25: no document states its transaction, replication, or crash behaviour. The WAL fact comes from reading `storage.rs`. The files read do not give the reason for the move from tensorchord to supervc-stack.
- VectorChord-bm25 shows no hybrid keyword-and-vector statement in the files read. The pg_textsearch fused statement comes from vendor documentation and was not run (A2-SR-19). ParadeDB's hybrid page does not say whether the fused statement reads one snapshot.
- Issue searches used GitHub title keywords only, so reports with other titles may be missing.
- pgvectorscale: no record tests crash recovery, standby replay, `ROLLBACK`, or `pg_dump`, and no record states whether a partial `diskann` index with a `WHERE` clause works. Its benchmark figures are vendor statements; the method post was not read.
