# A2-SR-03: qmd store schema in src/store.ts

```json
{
  "source_identity": "src/store.ts of tobi/qmd at commit aa247d0ee2e5dc3b83e1270714c0f06ca94e2514, functions installFtsSyncTriggers and the schema initialisation block, https://github.com/tobi/qmd/blob/aa247d0ee2e5dc3b83e1270714c0f06ca94e2514/src/store.ts",
  "author_or_issuing_body": "Tobi Lütke and contributors",
  "publisher": "GitHub (tobi/qmd)",
  "publication_date": "2026-11-17T00:00:00Z",
  "relevant_event_date": "2026-11-17",
  "source_family": "Primary: source code of tobi/qmd. Same lineage as A2-SR-01, A2-SR-02 and A2-SR-04 to A2-SR-12.",
  "precise_evidence_location": "src/store.ts lines 977-1012 (FTS sync triggers), 1084-1093 (documents_fts DDL), 1380-1490 (tables content, documents, llm_cache, content_vectors, store_collections, store_config, file_sync_state)",
  "method": "Read the DDL statements in the clone at the stated commit.",
  "limitations": "The file has 7,667 lines; only the schema block and triggers were read in full. Tables created in other files are in A2-SR-05 and A2-SR-06. No database was created or inspected; the schema is read from code only. publication_date is the commit date.",
  "provenance": "Clone of https://github.com/tobi/qmd.git on 2026-11-18 at aa247d0ee2e5dc3b83e1270714c0f06ca94e2514. Re-verify with git show aa247d0ee2e5dc3b83e1270714c0f06ca94e2514:src/store.ts."
}
```

## Evidence

- Line 1380: "// Drop legacy tables that are now managed in YAML" followed by DROP TABLE for path_contexts and collections.
- Line 1384: "// Content-addressable storage - the source of truth for document content". Table content(hash TEXT PRIMARY KEY, doc TEXT NOT NULL, created_at TEXT NOT NULL).
- Line 1393: "// Documents table - file system layer mapping virtual paths to content hashes". Table documents(id, collection, path, title, hash, created_at, modified_at, active INTEGER NOT NULL DEFAULT 1, FOREIGN KEY (hash) REFERENCES content(hash) ON DELETE CASCADE, UNIQUE(collection, path)).
- Table content_vectors(hash, seq, pos, model, embed_fingerprint, total_chunks, embedded_at, PRIMARY KEY (hash, seq)). Vectors attach to content hashes, not to paths.
- Table llm_cache(hash TEXT PRIMARY KEY, result TEXT NOT NULL, created_at TEXT NOT NULL).
- Line 1446: "// Store collections — makes the DB self-contained (no external config needed)". Table store_collections(name, path, pattern, ignore_patterns, include_by_default, update_command, context).
- Table store_config(key TEXT PRIMARY KEY, value TEXT) and file_sync_state(collection, relative_path, mtime_ms, size, content_hash, document_id).
- Lines 1090-1092: documents_fts is an FTS5 virtual table over filepath, title, body with "tokenize='porter unicode61'".
- Lines 980-1012: three triggers on documents (documents_ai, documents_ad, documents_au) keep documents_fts in step with documents inside SQLite. The vector tables have no trigger; embedding is a separate step (A2-SR-02, qmd embed).
- Shows: the full relational shape of the index. Does not show: any table for links between documents, typed relations, decisions, or an append-only log. Inferred: holding typed edges would need a new table; no generic edge table exists to reuse.
