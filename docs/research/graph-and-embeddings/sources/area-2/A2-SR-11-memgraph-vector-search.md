# A2-SR-11: Memgraph documentation, vector search and embeddings module

```json
{
  "source_identity": "Memgraph documentation, page 'Vector search', https://memgraph.com/docs/querying/vector-search; page 'embeddings', https://memgraph.com/docs/advanced-algorithms/available-algorithms/embeddings.md",
  "author_or_issuing_body": "Memgraph Ltd. (documentation team)",
  "publisher": "Memgraph Ltd., memgraph.com",
  "publication_date": "2026-11-18T00:00:00Z",
  "relevant_event_date": "2026-11-18",
  "source_family": "Primary: vendor documentation of Memgraph. Same lineage as A2-SR-12.",
  "precise_evidence_location": "Vector search page: introduction (isolation level and single-store pattern), sections 'Create vector index', 'Run vector search', 'Monitor vector index memory' and 'Drop vector index'. Embeddings page: introduction and procedure node_sentence().",
  "method": "Vendor documentation that states features, syntax and limits.",
  "limitations": "Living pages; the date is the retrieval date. Vendor documentation is used for stated features only. The vector search page shows the search procedure alone; it gives no example that combines the procedure with a graph pattern in one query. The page names an 'AI Platform license' but the licence terms were not read.",
  "provenance": "Downloaded with curl on 2026-11-18; the vector search page was converted from HTML to text with a local script, the embeddings page was fetched as Markdown. Re-verify at the URLs above."
}
```

## Evidence

- Introduction: "Memgraph implements a READ_UNCOMMITTED isolation level specifically for vector indices."
- Introduction: "While the main database can operate at any isolation level, the vector index specifically operates at READ_UNCOMMITTED."
- Introduction: "Both use the same single-store pattern: the vector value is stored only in the vector index backend (USearch), and the property store keeps only a reference (a vector index ID)."
- Create: the page creates an index with `CREATE VECTOR INDEX vector_index_name ON :Label(embedding) WITH CONFIG {...}`, where the configuration map sets the dimension and the capacity. The map is elided here.
- Search: the search runs as a procedure call, `CALL vector_search.search(<index name>, <k>, <query vector>) YIELD * RETURN *`. The argument values are elided here.
- Memory: "Deleting vertices or removing a vector property from nodes does not free vector_index_memory_tracked."
- Drop: "When you drop a vector index, Memgraph must move all vector data from USearch back into the property store."
- Embeddings page: "The embeddings module computes sentence embeddings for text — either for the string properties of nodes in the graph, or for an ad‑hoc list of strings."
- Embeddings page, node_sentence(): "Embeddings are created as a property of the nodes in the graph."
- What the source shows: one Memgraph instance holds the graph and an HNSW vector index from the USearch library; the vector index reads uncommitted data; a module can compute embeddings when it is called.
- What the source does not show: a trigger that recomputes an embedding when the text changes, or the HNSW name. The page names USearch; that USearch builds an HNSW graph is not stated on this page.
