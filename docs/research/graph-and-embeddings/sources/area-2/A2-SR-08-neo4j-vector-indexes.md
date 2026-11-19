# A2-SR-08: Neo4j Cypher Manual, vector indexes (current and version 5)

```json
{
  "source_identity": "Neo4j Cypher Manual, page 'Vector indexes', current version (Cypher 25), https://neo4j.com/docs/cypher-manual/current/indexes/semantic-indexes/vector-indexes/; same page for version 5, https://neo4j.com/docs/cypher-manual/5/indexes/semantic-indexes/vector-indexes/",
  "author_or_issuing_body": "Neo4j, Inc. (documentation team)",
  "publisher": "Neo4j, Inc., neo4j.com",
  "publication_date": "2026-11-18T00:00:00Z",
  "relevant_event_date": "2023-08-01",
  "source_family": "Primary: vendor documentation of Neo4j. Same lineage as A2-SR-09 and A2-SR-10.",
  "precise_evidence_location": "Current page: introduction; table 'Vector index capabilities per Neo4j version'; index configuration settings; section 'Limitations and known issues'; section on index providers. Version 5 page: introduction and procedure table.",
  "method": "Vendor documentation that states features, syntax and limits.",
  "limitations": "Living pages; the date is the retrieval date. relevant_event_date stands for the 5.11 public beta; the month is from the version 5 page, the day is set to the first of August 2023 and is not documented. Vendor documentation is used for stated features only. The page does not state whether index updates are applied at commit or later. Enterprise and Community features are named but the licence of Enterprise Edition is not described here.",
  "provenance": "Both pages downloaded with curl on 2026-11-18 and converted from HTML to text with a local script. Re-verify at the URLs above."
}
```

## Evidence

- Current page: "Neo4j vector indexes are powered by the Apache Lucene indexing and search library."
- Current page: "Vector indexes are available in both Neo4j Enterprise Edition and Community Edition."
- Current page: "Storing embeddings as native VECTOR properties requires block format, which is available in Enterprise Edition and Aura."
- Version 5 page: "Node vector indexes were released as a public beta in Neo4j 5.11 and general availability in Neo4j 5.13."
- Version 5 page: "Prior to Neo4j 5.15, node vector indexes were created using the db.index.vector.createNodeIndex() procedure."
- Current page, capability table: 5.13 "Supports single-label, single-property index for nodes or single-relationship-type, single-property index for relationships."; 2025.10 "Adds support for VECTOR value properties validated against index dimensions and the configured vector similarity function."; 2026.01 "Adds support for multi-label and multi-relationship-type vector indexes with additional properties used for filtering."; 2026.07 "Adds support for High Fidelity Quantized (HFQ) vector search, which can be enabled in the index configuration."
- Current page: "As of Neo4j 2026.01, the preferred way of querying vector indexes is by using the Cypher SEARCH clause."
- Current page, procedure signature: "Deprecated in Neo4j 2026.04"
- Current page, settings: "The M parameter controls the maximum number of connections each node has in the HNSW (Hierarchical Navigable Small Worlds) graph."
- Current page: "A newly created index is not immediately available but is created in the background."
- Limitations: "Changes made within the same transaction are not visible to the index."
- Limitations: "Only one vector index can be over a schema."
- Current page: "Vector index scores are meaningful within the result set from a vector query."
- What the source shows: the vector is a property of a node or relationship in the same database, indexed by Lucene HNSW, with a version history from a 5.11 beta to the 2026.01 SEARCH clause.
- What the source does not show: any feature in the vector index that recomputes an embedding when the text property changes.
