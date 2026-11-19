# A2-SR-08: VectorChord-bm25 repository at commit 14fc2a3

```json
{
  "source_identity": "VectorChord-bm25 (extension vchord_bm25), repository supervc-stack/VectorChord-bm25, formerly tensorchord/VectorChord-bm25: README.md, LICENSE, Cargo.toml, src/index/storage.rs at commit 14fc2a332b665e1f38eb5d59bb85c8ac1a00490d (2026-04-28); releases 0.1.0 (2025-02-06) to 0.3.0 (2025-12-15); https://github.com/supervc-stack/VectorChord-bm25",
  "author_or_issuing_body": "TensorChord, VectorChord-bm25 maintainers",
  "publisher": "GitHub",
  "publication_date": "2026-04-28T09:17:34Z",
  "relevant_event_date": "2026-04-28",
  "source_family": "Primary: repository documentation, licence, build file, and source code of the extension.",
  "precise_evidence_location": "README.md sections Usage, Comparison to other solution in Postgres, Limitation; LICENSE first section; Cargo.toml [features] lines 18 to 22; src/index/storage.rs lines 227 to 236 and 312 to 318; repository and release metadata from the GitHub API",
  "method": "Repository files read at one commit; source code read for WAL behaviour that the README does not state; counts from the GitHub API.",
  "limitations": "The README may lag the code: commit #108 'refactor: new api' (2026-04-20) and #103 'add to_bm25query(regclass, int[])' came after the last release 0.3.0, and the README still shows the bm25query(index, vector) form. The WAL statement rests on reading storage.rs only; I did not trace every write path. The README says nothing about replication, rollback, or pg_dump. The repository moved from the tensorchord to the supervc-stack organisation; the GitHub API redirects the old name. The reason for the move is not stated in the files read.",
  "provenance": "Shallow clone (depth 50) of https://github.com/supervc-stack/VectorChord-bm25 on 2026-11-18; release list and counts from `gh api repos/supervc-stack/VectorChord-bm25/releases`, `/commits`, `/contributors`, `/issues`. Re-verify at the commit above."
}
```

## Evidence

- README, opening: "VectorChord-BM25 is a PostgreSQL extension for bm25 ranking algorithm. We implemented the Block-WeakAnd Algorithms for BM25 ranking inside PostgreSQL."
- README, Usage: "The extension is mainly composed by three parts, tokenizer, bm25vector and bm25vector index." The tokenizer is a second extension: "Tokenizer part is completed by a separate extension pg_tokenizer.rs" (link text kept).
- README, Usage: the user stores tokens in a separate column, for example "UPDATE documents SET embedding = tokenize(passage, 'bert');", and indexes that column with "CREATE INDEX documents_embedding_bm25 ON documents USING bm25 (embedding bm25_ops);". The README also shows a helper, `create_custom_model_tokenizer_and_trigger`, that fills the column by trigger. The bm25vector column is derived data that must be kept in sync with the text column.
- README, query: "SELECT id, passage, embedding \<&> bm25query('documents_embedding_bm25', tokenize('PostgreSQL', 'bert')) AS rank FROM documents ORDER BY rank LIMIT 10;" (line breaks removed).
- README, Comparison: "PostgreSQL lacks modern relevance scoring methods like BM25; it retrieves all matching documents and re-ranks them using ts_rank, which is inefficient and can obscure the most relevant results." This is the project's criticism of built-in ranking, not a measurement.
- README, Limitation: "The index will return up to `bm25_catalog.bm25_limit` results to PostgreSQL." and "We currently have only tested against English."
- src/index/storage.rs lines 227 to 236: the page write guard calls `GenericXLogAbort` when the thread panics and `GenericXLogFinish` otherwise; lines 312 to 318 start a write with `GenericXLogStart` and `GenericXLogRegisterBuffer`. Index pages are therefore WAL-logged through PostgreSQL's generic WAL (my reading of the code).
- LICENSE: "This software is licensed under a dual license model." The two licences are AGPLv3 and Elastic License v2.
- Cargo.toml lines 18 to 22: build features pg14, pg15, pg16, pg17, pg18.
- Release activity: six releases, 0.1.0 on 2025-02-06 to 0.3.0 on 2025-12-15; 88 commits since 2024-11-18; last commit on main 2026-04-28; 9 contributors; repository last pushed 2026-08-05 (GitHub API, 2026-11-18).
- Issue #124, opened 2026-08-23 and open: term searches fail under delete and rewrite churn, and the session then cannot REINDEX or DROP the index (title paraphrased).
- Not shown: tests of crash recovery or physical replication, rollback behaviour of the index, and a hybrid statement.
