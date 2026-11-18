# A2-SR-05: qmd vector layout in src/vec-layout.ts and src/store-migrations.ts

```json
{
  "source_identity": "src/vec-layout.ts and src/store-migrations.ts of tobi/qmd at commit aa247d0ee2e5dc3b83e1270714c0f06ca94e2514",
  "author_or_issuing_body": "Tobi Lütke and contributors; layout commit 2e55927 by the qmd contributors",
  "publisher": "GitHub (tobi/qmd)",
  "publication_date": "2026-11-17T00:00:00Z",
  "relevant_event_date": "2026-09-24",
  "source_family": "Primary: source code of tobi/qmd. Same lineage as A2-SR-01 to A2-SR-04 and A2-SR-06 to A2-SR-12.",
  "precise_evidence_location": "src/vec-layout.ts lines 19-22 (table names), 102-124 (createVectorMetadataTables, createPartitionedVecTable); src/store-migrations.ts lines 1-15 (header comment)",
  "method": "Read both files in the clone at the stated commit. Found the first commit of vectors_by_collection with git log -S.",
  "limitations": "Whether vec0 queries scan exhaustively or use an approximate index is not stated here; A2-SR-10 and A2-SR-13 hold conflicting wording. relevant_event_date is the date of commit 2e55927 (2026-09-24), which introduced the layout. publication_date is the HEAD commit date.",
  "provenance": "Clone of https://github.com/tobi/qmd.git on 2026-11-18 at aa247d0ee2e5dc3b83e1270714c0f06ca94e2514. Re-verify with git show aa247d0ee2e5dc3b83e1270714c0f06ca94e2514:src/vec-layout.ts and git show 2e5592769b98a2b03b973a1071c8215892da3942."
}
```

## Evidence

- Lines 19-22: VEC_TABLE "vectors_by_collection", VEC_ROWS_TABLE "vector_rows", VEC_COLLECTION_IDS_TABLE "vector_collection_ids", LEGACY_VEC_TABLE "vectors_vec".
- Line 123: "CREATE VIRTUAL TABLE IF NOT EXISTS ${VEC_TABLE} USING vec0(collection_id INTEGER PARTITION KEY, embedding float[${dimensions}] distance_metric=cosine)"
- vector_rows(id, hash, seq, collection_id, UNIQUE(hash, seq, collection_id)) maps a vec0 rowid back to a content chunk.
- store-migrations.ts lines 3-7: "Version 1 installs the FTS sync triggers. Version 2 moves every vector out of the legacy `vectors_vec` table (one row per chunk, keyed by hash_seq) into the layout `vec-layout.ts` describes: one row per (chunk, active collection) in a vec0 table partitioned by collection id."
- Migrations are numbered by PRAGMA user_version and applied in IMMEDIATE transactions (header comment).
- Shows: the vector storage and its migration mechanism. Does not show: an approximate nearest-neighbour index; the brute-force question stays open here.
