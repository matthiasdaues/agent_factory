# A2-SR-02: qmd README.md

```json
{
  "source_identity": "README.md of tobi/qmd at commit aa247d0ee2e5dc3b83e1270714c0f06ca94e2514, https://github.com/tobi/qmd/blob/aa247d0ee2e5dc3b83e1270714c0f06ca94e2514/README.md",
  "author_or_issuing_body": "Tobi Lütke and contributors",
  "publisher": "GitHub (tobi/qmd)",
  "publication_date": "2026-11-17T00:00:00Z",
  "relevant_event_date": "2026-11-17",
  "source_family": "Primary: project documentation of tobi/qmd. Same lineage as A2-SR-01 and A2-SR-03 to A2-SR-12.",
  "precise_evidence_location": "Lines 1-24 (intro and flowchart), 89-105 (MCP Server), 487-583 (Architecture, Score Normalization and Fusion), 596-606 (GGUF Models), 1060-1130 (Metadata Filtering), 1416-1462 (Index Maintenance), 1533-1549 (Data Storage, Schema), 1562-1673 (How It Works)",
  "method": "Read the file in the clone at the stated commit.",
  "limitations": "Documentation, not code; where it disagrees with source, the source in A2-SR-03 governs. The README contradicts itself on query expansion: line 505 shows 2 alternative queries, line 563 shows 1 LLM variation. Its schema list at lines 1539-1549 names collections and path_contexts tables that src/store.ts drops (A2-SR-03). Performance statements are the project's own and were not checked. publication_date is the commit date.",
  "provenance": "Clone of https://github.com/tobi/qmd.git on 2026-11-18 at aa247d0ee2e5dc3b83e1270714c0f06ca94e2514. Re-verify with git show aa247d0ee2e5dc3b83e1270714c0f06ca94e2514:README.md."
}
```

## Evidence

- Line 3: "An on-device search engine for everything you need to remember. Index your markdown notes, meeting transcripts, documentation, and knowledge bases. Search with keywords or natural language. Ideal for your agentic flows."
- Line 5: "QMD combines BM25 full-text search, vector semantic search, and LLM re-ranking—all running locally via node-llama-cpp with GGUF models."
- Line 24: the README routes lex expansions to BM25 and vec and hyde expansions to vector search: "The original query is sent to both backends, then fused with RRF and reranked."
- Lines 561-572 (Fusion Strategy): RRF with k=60, original query weight 2, top-rank bonus +0.05 for rank 1 and +0.02 for ranks 2-3, top 30 candidates to the reranker, then position-aware blending of 75/60/40 percent retrieval score by RRF rank band.
- Line 574: "**Why this approach**: Pure RRF can dilute exact matches when expanded queries don't match. The top-rank bonus preserves documents that score #1 for the original query. Position-aware blending prevents the reranker from destroying high-confidence retrieval results."
- Lines 598-606: three local GGUF models, embeddinggemma-300M-Q8_0 for embeddings, qwen3-reranker-0.6b-q8_0 for reranking, qmd-query-expansion-1.7B-q4_k_m for query expansion. "Models are downloaded from HuggingFace and cached in `~/.cache/qmd/models/`."
- Lines 91-99: MCP tools query, get, multi_get, status, metadata. Lines 133-160: an HTTP transport and a daemon mode.
- Line 1535: "Index stored in: `~/.cache/qmd/index.sqlite`"
- Lines 1581-1590: chunks of about 900 tokens with 15 percent overlap; each chunk stores hash, seq, and "pos: character position in original".
- Line 1442: "qmd get notes/meeting.md:120:40" reads a line range on retrieval.
- Line 1082: "Supported values are strings, numbers, booleans, and flat homogeneous arrays of one of those. Nested objects, nulls, empty arrays, and mixed-type arrays are rejected (the document still indexes; it is excluded from filtered search until corrected)."
- Line 1460: "# Drop caches and orphans; repack the vector table when it has holes"
- Shows: purpose, pipeline, models, interfaces, stated schema. Does not show: any link, edge, or citation table; any history table; how well the pipeline ranks.
