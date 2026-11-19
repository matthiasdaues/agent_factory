# A2-SR-13: FalkorDB documentation, vector index and concurrency model

```json
{
  "source_identity": "FalkorDB documentation, page 'Vector Indexing: Fast Similarity Search for GraphRAG', https://docs.falkordb.com/cypher/indexing/vector-index.html; page 'Atomicity and Concurrency Control in FalkorDB', https://docs.falkordb.com/design/concurrency.md",
  "author_or_issuing_body": "FalkorDB Ltd. (documentation team)",
  "publisher": "FalkorDB Ltd., docs.falkordb.com",
  "publication_date": "2026-11-18T00:00:00Z",
  "relevant_event_date": "2026-11-18",
  "source_family": "Primary: vendor documentation of FalkorDB. Same lineage as A2-SR-14.",
  "precise_evidence_location": "Vector index page: introduction, syntax, 'Query vector index', 'Performance Considerations'. Concurrency page: overview, 'Single Query Atomicity', 'Serialized Writers', 'When You Need External Coordination'.",
  "method": "Vendor documentation that states features, syntax and guarantees.",
  "limitations": "Living pages; the date is the retrieval date. The docs serve two engine lines, 4.x in C and 6.x in Rust (A2-SR-14); the pages do not say which line they describe. The memory figure on the vector page is a vendor estimate and is not used. Vendor documentation is used for stated features only.",
  "provenance": "Downloaded with curl on 2026-11-18. The vector page was converted from HTML to text; the concurrency page was fetched as Markdown. A web search first pointed to the concurrency page; its summary was not used, only the page itself."
}
```

## Evidence

- Vector page: "FalkorDB’s vector index uses the HNSW (Hierarchical Navigable Small World) algorithm with cosine similarity or Euclidean distance, supporting 1–4096-dimensional vectors."
- Vector page, syntax: `CREATE VECTOR INDEX FOR <entity_pattern> ON <entity_attribute> OPTIONS <options>`
- Vector page: "Always wrap the list in vecf32(). A plain list such as [2.1, 0.82, 1.3] is stored as a regular list property. The vector index skips it without an error, so the node never shows up in vector search results."
- Vector page: "To query the index use either db.idx.vector.queryNodes for node retrieval or db.idx.vector.queryRelationships for relationships."
- Vector page, costs: "No support for filtering: Vector queries don’t combine well with property filters"
- Concurrency page: "FalkorDB uses a per-graph reader-writer model: many read queries can run in parallel against the same graph, while write queries are serialized so that only one write executes at a time on a given graph."
- Concurrency page: "The entire query either succeeds completely or fails without applying any partial changes."
- Concurrency page: "FalkorDB does not natively support multi-query transactions."
- Concurrency page: "Note that `MULTI`/`EXEC` serializes all enclosed commands, so concurrent operations on other graphs will also be blocked for the duration of the transaction."
- What the source shows: the vector lives as a node or relationship property in the graph, searched through a procedure; a single write query is atomic; several queries need Redis MULTI/EXEC.
- What the source does not show: whether the vector index is updated inside the atomic write, and any feature that recomputes embeddings.
