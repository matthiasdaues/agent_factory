# A2-SR-11: qmd initial commit 39193ea

```json
{
  "source_identity": "Commit 39193ea252b1572f5d2d4c86a46ffaa184899df3 of tobi/qmd, file qmd.ts, https://github.com/tobi/qmd/commit/39193ea252b1572f5d2d4c86a46ffaa184899df3",
  "author_or_issuing_body": "Tobi Lutke",
  "publisher": "GitHub (tobi/qmd)",
  "publication_date": "2025-12-07T19:16:16-05:00",
  "relevant_event_date": "2025-12-07",
  "source_family": "Primary: source code of tobi/qmd at its first commit. Same lineage as A2-SR-01 to A2-SR-10 and A2-SR-12.",
  "precise_evidence_location": "Commit message; qmd.ts lines 116-196 (schema setup, vectors_vec DDL)",
  "method": "Read with git show 39193ea and git show 39193ea:qmd.ts in the clone.",
  "limitations": "Only the commit message and the schema part of qmd.ts were read. The record shows the first formulation; it does not show why each choice was made beyond the commit message.",
  "provenance": "Clone of https://github.com/tobi/qmd.git on 2026-11-18. Re-verify with git show 39193ea252b1572f5d2d4c86a46ffaa184899df3."
}
```

## Evidence

- Commit message: "A CLI tool for searching markdown knowledge bases using hybrid retrieval:" followed by "- BM25 full-text search via SQLite FTS5", "- Vector semantic search via sqlite-vec + Ollama embeddings", "- LLM re-ranking with qwen3-reranker (logprobs-based scoring)".
- qmd.ts: "// Content vectors keyed by hash (UNIQUE)" with content_vectors(hash TEXT PRIMARY KEY, model, embedded_at): one vector per document, no chunks.
- qmd.ts line 194: "CREATE VIRTUAL TABLE vectors_vec USING vec0(hash TEXT PRIMARY KEY, embedding float[${dimensions}])"
- The first schema already has tables collections and documents with an active flag, an FTS5 table, and three sync triggers.
- Shows: the first formulation of the storage and pipeline. Does not show: chunking (added 2025-12-08 in commit ceb534a, per git log -S), query expansion, or fusion weights.
