# A2-SR-15: DuckDB vss extension, README and DuckDB 2.0 documentation

```json
{
  "source_identity": "duckdb-vss README.md, main branch, https://github.com/duckdb/duckdb-vss; DuckDB documentation page 'Vector Similarity Search Extension', https://duckdb.org/docs/2.0/core_extensions/vss.html",
  "author_or_issuing_body": "DuckDB Labs (repository maintainers Max Gabrielsson and others); DuckDB Foundation documentation",
  "publisher": "GitHub, repository duckdb/duckdb-vss; duckdb.org",
  "publication_date": "2026-09-09T13:02:06Z",
  "relevant_event_date": "2026-09-03",
  "source_family": "Primary: project documentation and repository of the DuckDB vss extension.",
  "precise_evidence_location": "README opening paragraph and sections 'Pre-filtered searches', 'Inserts, Updates,  Deletes and Re-Compaction' and 'Limitations'; documentation page section 'Persistence'; README commit history; repository commit list; DuckDB release list",
  "method": "Project documentation read directly; history of the README and recent commits from the GitHub API.",
  "limitations": "publication_date is the last change of the README; relevant_event_date is the first commit of the pre-filter feature. The extension has no own tags or releases; it ships with DuckDB releases, so release activity is that of DuckDB. The documentation page for DuckDB 2.0 was read; the stable URL redirects to it. No source states whether the 2.0 page reflects the pre-filter change in the README.",
  "provenance": "README downloaded with curl from https://raw.githubusercontent.com/duckdb/duckdb-vss/main/README.md on 2026-11-18. Documentation page downloaded with curl on 2026-11-18 and converted to text. Commits read with gh api repos/duckdb/duckdb-vss/commits; the README of commit 58aa5df089b9 downloaded from raw.githubusercontent.com; DuckDB releases with gh api repos/duckdb/duckdb/releases. Repository metadata: archived false, last push 2026-11-12, licence MIT."
}
```

## Evidence

- README: "This is an experimental extension for DuckDB that adds indexing support to accelerate Vector Similarity Search using DuckDB's new fixed-size `ARRAY` type added in version v0.10.0."
- README: "This extension is based on the [usearch](https://github.com/unum-cloud/usearch) library and serves as a proof of concept for providing a custom index type, in this case a HNSW index, from within an extension and exposing it to DuckDB."
- README, pre-filtered searches: "Static `WHERE` filters that DuckDB can push into the table scan are applied before the HNSW search."
- README, pre-filtered searches: "This allows the index scan to return up to the requested number of qualifying nearest neighbors instead of finding the unfiltered top-k and discarding rows afterward."
- README, pre-filtered searches: "The current implementation builds a transaction-visible filter bitmap with an O(n) scan over the filter columns for each query."
- README: "Deletes are not immediately reflected in the index, but are instead"; the sentence goes on to say that deleted rows are marked and that the index can grow stale.
- README, limitations: "The index itself is not buffer managed and must be able to fit into RAM memory."
- README, limitations: "But there is no incremental updates, so every time DuckDB performs a checkpoint the entire index will be serialized to disk and overwrite its previous blocks."
- Documentation, persistence: "Due to some known issues related to persistence of custom extension indexes, the HNSW index can only be created on tables in in-memory databases by default, unless the SET hnsw_enable_experimental_persistence = bool configuration option is set to true."
- Documentation, persistence: "But we still recommend that you do not use this feature in production environments."
- README history: "First implementation for hsnw prefilter" (2026-09-03); before that the README last changed on 2024-09-05. The README of 2024-09-05 (commit 58aa5df089b9) has no section on filters; its sections are Usage, Inserts, Updates, Deletes and Re-Compaction, Limitations, and build notes.
- DuckDB releases between 2024-11-18 and 2026-11-18: 20, the latest v2.0.0 of 2026-10-21. The vss repository bumped its DuckDB reference to v2.0.1 on 2026-11-10.
- What the source shows: vss is an experimental HNSW index in DuckDB tables; the index lives in memory; persistence to a file is behind an experimental flag; filters are pushed before the search since September 2026.
- What the source does not show: any combination with DuckPGQ.
