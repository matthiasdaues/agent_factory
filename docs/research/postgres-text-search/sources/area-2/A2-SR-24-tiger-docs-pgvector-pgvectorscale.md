# A2-SR-24: Tiger Data Docs page "Understand pgvector and pgvectorscale"

```json
{
  "source_identity": "Tiger Data Docs, 'Understand pgvector and pgvectorscale'; source file src/content/docs/learn/search/pgvector-pgvectorsearch.mdx in timescale/Tiger-Data-Docs, last commit 46c58b5e2662916a02b1966efbddcfc84ebd7436",
  "author_or_issuing_body": "Tiger Data (formerly Timescale), documentation team",
  "publisher": "Tiger Data",
  "publication_date": "2026-10-19T08:17:50Z",
  "relevant_event_date": "2026-10-19",
  "source_family": "Primary: vendor concept page. Same company and lineage as A2-SR-19, A2-SR-20, and A2-SR-23.",
  "precise_evidence_location": "pgvector-pgvectorsearch.mdx: title (line 2), opening paragraphs (lines 20 and 22), Next steps table (line 68)",
  "method": "Vendor overview page. It states features and points to the repository for details.",
  "limitations": "Vendor material: it counts for stated features only. The page is short and sends readers to the pgvectorscale repository for index details. It was read as its MDX source file; the rendered URL was not checked. `{C.PGVECTORSCALE}` and similar tokens are site constants whose rendered text was not checked.",
  "provenance": "Fetched on 2026-11-19 with `gh api repos/timescale/Tiger-Data-Docs/contents/src/content/docs/learn/search/pgvector-pgvectorsearch.mdx` (sha256 c5dc7c4af19fc20c4d486ed856f25d7662d796cab7f8a0dedec05147790bf244); commit history from `gh api repos/timescale/Tiger-Data-Docs/commits?path=<source file>`. Re-verify at the commit above."
}
```

## Evidence

The quotes are copied from the MDX source, with the site constants left as they stand.

- Roles of the two extensions: "**{C.PGVECTORSCALE}** builds on pgvector with indexing aimed at large-scale, high-performance workloads (including **StreamingDiskANN**, inspired by Microsoft’s DiskANN research)."
- HNSW belongs to pgvector: "You can rely on familiar pgvector capabilities (for example **HNSW** and **IVFFlat** indexes) and add **StreamingDiskANN** from {C.PGVECTORSCALE} when you want to optimize vector search further."
- Documentation home: the page points to the GitHub repository for "StreamingDiskANN, filtered vector search, index parameters".
- Not shown: WAL, replication, pg_dump, supported versions, or filter limits.
