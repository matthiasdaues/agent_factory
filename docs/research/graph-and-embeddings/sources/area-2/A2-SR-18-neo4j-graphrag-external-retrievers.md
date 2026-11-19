# A2-SR-18: neo4j-graphrag-python user guide, external vector store retrievers

```json
{
  "source_identity": "neo4j-graphrag-python, docs/source/user_guide_rag.rst, main branch, sections on Weaviate, Pinecone and Qdrant retrievers, https://github.com/neo4j/neo4j-graphrag-python",
  "author_or_issuing_body": "Neo4j, Inc. and contributors",
  "publisher": "GitHub, repository neo4j/neo4j-graphrag-python",
  "publication_date": "2026-08-12T07:04:55Z",
  "relevant_event_date": "2026-08-12",
  "source_family": "Primary: vendor library documentation for a graph store paired with separate vector stores. Same vendor as A2-SR-08 to A2-SR-10, different product.",
  "precise_evidence_location": "Retriever table (lines 582 to 587 of the file at retrieval); section 'Weaviate Retrievers'; section 'Qdrant Retrievers'",
  "method": "Library documentation that states the retriever classes and their parameters.",
  "limitations": "publication_date is the last change of the file. The guide shows how a query joins the two stores by an identifier; it does not describe how writes reach both stores. It is one library; other designs of a graph beside a vector store were not read.",
  "provenance": "Downloaded with curl from https://raw.githubusercontent.com/neo4j/neo4j-graphrag-python/main/docs/source/user_guide_rag.rst on 2026-11-18. Last change date read with gh api repos/neo4j/neo4j-graphrag-python/commits?path=docs/source/user_guide_rag.rst."
}
```

## Evidence

- Retriever table: "Use this retriever when vectors are saved in a Qdrant vector database"
- Weaviate section: "Internally, this retriever performs the vector search in Weaviate, finds the corresponding node by matching the Weaviate metadata `id_property_external` with a Neo4j `node.id_property_neo4j`, and returns the matched node."
- Qdrant section, inline comment on a parameter: "The payload field that contains identifier to a corresponding Neo4j node id property"
- What the source shows: in the separate-store design, the vector store keeps a copy of the graph node identifier, and a query runs in two steps, first the vector search, then a lookup of the node in Neo4j.
- What the source does not show: any mechanism that keeps the identifiers or vectors in sync when nodes change.
