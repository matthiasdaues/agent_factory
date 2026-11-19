# A2-SR-20: pgvectorscale README at commit 3ae6fcc

```json
{
  "source_identity": "timescale/pgvectorscale, README.md at commit 3ae6fccff8fe451f55825752e46a60b42dfdfa0d (2026-10-14); https://github.com/timescale/pgvectorscale",
  "author_or_issuing_body": "Tiger Data (formerly Timescale), pgvectorscale maintainers",
  "publisher": "GitHub",
  "publication_date": "2026-10-14T19:56:37Z",
  "relevant_event_date": "2026-10-14",
  "source_family": "Primary: repository documentation of the extension. Same company and lineage as A2-SR-19 and the pg_textsearch records A2-SR-01 and A2-SR-02, so it does not corroborate them independently.",
  "precise_evidence_location": "README.md: opening note (line 12), feature list and benchmark paragraph (lines 14 to 22), Installation (lines 44 to 148), Get started (lines 151 to 183), Filtered Vector Search (lines 185 to 305), Tuning (lines 307 to 406), Null Value Handling (line 408), ORDER BY vector distance (line 414), Index on an UNLOGGED table (line 433), Get involved (line 444)",
  "method": "The maintainers describe features, syntax, and parameters, with SQL examples. The benchmark figures point to a vendor blog post, which was not read.",
  "limitations": "Vendor material: it counts for features and syntax only. The benchmark against Pinecone is a vendor statement; its method was not read. The README says nothing on WAL, physical replication, rollback, MVCC, pg_dump, or supported PostgreSQL versions; those facts come from the code (A2-SR-21) and the release notes (A2-SR-22). The README describes the main branch, which is ahead of release 0.9.1 by one commit, the README change itself.",
  "provenance": "Fetched on 2026-11-19 with `gh api repos/timescale/pgvectorscale/readme` (sha256 7cc6d5787d27ab428242a7b529f15d5d0fc3bd233886c647ac81b4852605a097). Repository metadata from `gh api repos/timescale/pgvectorscale` on 2026-11-19: not archived, licence PostgreSQL, last push 2026-10-14. Re-verify at the commit above."
}
```

## Evidence

The quotes are copied from the raw README. They are the source's own words, not a fetch-tool summary. Link markup is removed and the link text kept.

- Relation to pgvector: "pgvectorscale complements pgvector, the open-source vector data extension for PostgreSQL, and introduces the following key innovations for pgvector data:" The three items are "A new index type called StreamingDiskANN, inspired by the DiskANN algorithm, based on research from Microsoft.", "Statistical Binary Quantization: developed by Timescale researchers, This compression method improves on standard Binary Quantization.", and "Label-based filtered vector search: based on Microsoft's Filtered DiskANN research". The research lineage is in A4-SR-05 (DiskANN), A4-SR-06 (FreshDiskANN, streaming updates), and A4-SR-10 (Filtered-DiskANN) of the graph-and-embeddings survey.
- Dependency: "CREATE EXTENSION IF NOT EXISTS vectorscale CASCADE;" followed by "The `CASCADE` automatically installs `pgvector`." The same statement appears for Docker, source builds, and Timescale Cloud.
- Outside the vendor cloud: "You can install pgvectorscale from source and install it in an existing PostgreSQL server". The build uses Rust and pgrx: "cargo pgrx init --pg18 pg_config". Building on macOS Intel "is currently not supported due to an open issue".
- Successor note, line 12: "We're building pg_vectorsearch, a next-generation PostgreSQL vector index that uses partitioning and compression instead of graph-based indexing". It is "available in early alpha and isn't yet production-ready."
- Vendor benchmark statement, without a method in the README: "achieves **28x lower p95 latency** and **16x higher query throughput** compared to Pinecone's storage optimized (s1) index". This counts as a vendor statement only.
- Index syntax: "USING diskann (embedding vector_cosine_ops);". Supported operators: "cosine distance (`<=>`) queries, for indices created with `vector_cosine_ops`; L2 distance (`<->`) queries, for indices created with `vector_l2_ops`; and inner product (`<#>`) queries". Also "(Note: inner product indices are not compatible with plain storage.)"
- Build parameters, from the table: `storage_layout` is "`memory_optimized` which uses SBQ to compress vector data or `plain` which stores data uncompressed", default memory_optimized. `num_neighbors` default 50, `search_list_size` default 100, `max_alpha` default 1.2, `num_dimensions` default "0 (all dimensions)", and `num_bits_per_dimension` default "2 for less than 900 dimensions, 1 otherwise".
- Query parameters: `diskann.query_search_list_size` default 100 and `diskann.query_rescore` default 50, settable per transaction with `SET LOCAL`.
- Two kinds of filtering: "**Label-based filtering with the diskann index**: This provides optimized performance for filtering by labels." and "**Arbitrary WHERE clause filtering**: This uses post-filtering after the vector search." The post-filter "is streaming and correct, ensuring accurate results without requiring the entire result set to be loaded into memory."
- Label index: "you must specify the label column directly in the index creation", with "labels SMALLINT[], -- Array of category labels" and "CREATE INDEX ON documents USING diskann (embedding vector_cosine_ops, labels);".
- Label limits: "Label values must be within the PostgreSQL `smallint` range (-32768 to 32767)." and "pgvectorscale includes an implementation of the `&&` overlap operator for `smallint[]` arrays, which is used for efficient label-based filtering." The example query comments "WHERE labels && ARRAY[1, 3] -- Documents with label 1 OR 3".
- Parallel build and labels: parallel building is enabled only when "The table has no labels (label-based filtering not yet supported in parallel)".
- Nulls: "Null vectors are not indexed", "Null labels are treated as empty arrays", and "Null values in label arrays are ignored".
- Ordering: "pgvectorscale's diskann index uses relaxed ordering which allows results to be slightly out of order by distance. This is analogous to using `iterative scan with relaxed ordering` with pgvector's ivfflat or hnsw indexes." Strict order needs a `MATERIALIZED` common table expression.
- Unlogged tables: "Creating an index on an UNLOGGED table is currently not supported." The error is `ERROR:  ambuildempty: not yet implemented`.
- Maturity, in the maintainers' words: "pgvectorscale is still at an early stage."
- Not shown: WAL, physical or logical replication, rollback, MVCC, pg_dump, supported PostgreSQL versions, and partial indexes with a `WHERE` clause. The README gives no example that combines a label filter and a fused keyword branch.
