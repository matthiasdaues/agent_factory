# A2-SR-23: Tiger Data Docs tutorial "Hybrid search" with pg_textsearch and pgvectorscale

```json
{
  "source_identity": "Tiger Data Docs, hybrid search tutorial; source file src/content/docs/learn/tutorials/hybrid-search.mdx in timescale/Tiger-Data-Docs, last commit 938e195afcd787503d3dff16fa7b2e3ea3e68ff3",
  "author_or_issuing_body": "Tiger Data (formerly Timescale), documentation team",
  "publisher": "Tiger Data",
  "publication_date": "2026-10-28T08:55:57Z",
  "relevant_event_date": "2026-10-28",
  "source_family": "Primary: vendor tutorial. Same company and lineage as A2-SR-19 and A2-SR-20, so it does not corroborate them independently.",
  "precise_evidence_location": "hybrid-search.mdx: description (line 3), Create the extensions (lines 218 to 229 and 290 to 297), Create a StreamingDiskANN index for vector search (lines 701 to 716), fused statement (lines 815 to 846), Tune vector search accuracy (lines 931 to 943), large-table index statements (lines 955 to 964)",
  "method": "Vendor how-to page with SQL examples. It reports no test method.",
  "limitations": "Vendor material: it counts for syntax only. The claim that DiskANN does not need the whole index in RAM is a vendor statement without a measurement. The tutorial was read as its MDX source file, not as the rendered page. The rendered URL was not checked. It does not filter the vector branch and does not run the fused statement inside a writing transaction.",
  "provenance": "Fetched on 2026-11-19 with `gh api repos/timescale/Tiger-Data-Docs/contents/src/content/docs/learn/tutorials/hybrid-search.mdx` (sha256 53302f8c9aea845b21d18bab12b2bac9f8317609f6e23c18bb96b78944f30024); commit history from `gh api repos/timescale/Tiger-Data-Docs/commits?path=<source file>`. Found through a GitHub code search for 'pgvectorscale diskann' in that repository. Re-verify at the commit above."
}
```

## Evidence

The quotes are copied from the MDX source. Link markup is removed and the link text kept.

- Description: "Combine keyword search and semantic vector search in PostgreSQL using pg_textsearch and pgvectorscale, fused with Reciprocal Rank Fusion."
- Extensions: "CREATE EXTENSION pg_textsearch;" and "CREATE EXTENSION vectorscale CASCADE;", then "The `CASCADE` keyword in the second statement automatically installs pgvector as a dependency."
- Vector index: "CREATE INDEX episodes_embedding_idx ON episodes" with "USING diskann (embedding vector_cosine_ops);". Vendor statement: "Unlike pgvector's built-in HNSW index, DiskANN stores the graph on disk rather than requiring the entire index to fit in RAM".
- Fused statement: two common table expressions with `ROW_NUMBER()` and `LIMIT 20`, one ordered by "description \<@> 'mental health boundaries'" and one by "embedding \<=> $1", joined with `LEFT JOIN` and scored by "COALESCE(1.0 / (60 + b.rank), 0)" plus "COALESCE(1.0 / (60 + v.rank), 0) AS rrf_score". The page cites no fusion paper. The statement has the same form as the one in A2-SR-19; there the vector branch uses a pgvector HNSW index.
- Tuning: "SET LOCAL diskann.query_rescore = 150;".
- Not shown: a filter in the vector branch, a label column, WAL or replication behaviour, and any measurement.
