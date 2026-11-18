# A2-SR-01: pgvector README on the master branch

```json
{
  "source_identity": "pgvector README.md, master branch, https://github.com/pgvector/pgvector/blob/master/README.md",
  "author_or_issuing_body": "Andrew Kane (ankane) and pgvector contributors",
  "publisher": "GitHub, repository pgvector/pgvector",
  "publication_date": "2026-11-18T00:00:00Z",
  "relevant_event_date": "2026-11-18",
  "source_family": "Primary: project documentation of pgvector, written by its maintainer. Same lineage as A2-SR-02 and A2-SR-03.",
  "precise_evidence_location": "Opening section; section Indexing; sections HNSW and IVFFlat; section Filtering; section Iterative Index Scans",
  "method": "Project documentation that states features and syntax of the extension.",
  "limitations": "The README is a living document; the date is the retrieval date, not a release date. It describes the master branch, which holds unreleased 0.9.0 work (A2-SR-02). It is vendor documentation, so it is used for stated features and syntax only. Its statements on query performance are not used as evidence. It does not describe how pgvector behaves next to Apache AGE.",
  "provenance": "Downloaded with curl from https://raw.githubusercontent.com/pgvector/pgvector/master/README.md on 2026-11-18. Re-verify at that URL or at the tag v0.8.7."
}
```

## Evidence

- Opening section: "Store your vectors with the rest of your data."
- Opening section: "Plus [ACID](https://en.wikipedia.org/wiki/ACID) compliance, point-in-time recovery, JOINs, and all of the other [great features](https://www.postgresql.org/about/) of Postgres"
- Section Indexing: "By default, pgvector performs exact nearest neighbor search, which provides perfect recall."
- Section Indexing: "Unlike typical indexes, you will see different results for queries after adding an approximate index."
- Section Indexing lists two index types, HNSW and IVFFlat.
- Section HNSW: "An HNSW index creates a multilayer graph. It has better query performance than IVFFlat (in terms of speed-recall tradeoff), but has slower build times and uses more memory. Also, an index can be created without any data in the table since there isn’t a training step like IVFFlat."
- Section IVFFlat: "An IVFFlat index divides vectors into lists, and then searches a subset of those lists that are closest to the query vector."
- Section IVFFlat, first of three keys to good recall: "Create the index *after* the table has some data"
- Section Filtering: "With approximate indexes, filtering is applied *after* the index is scanned."
- Section Iterative Index Scans: "Starting with 0.8.0, you can enable iterative index scans, which will automatically scan more of the index until enough results are found (or it reaches `hnsw.max_scan_tuples` or `ivfflat.max_probes`)."
- Section Storing shows that a vector is a column of a table and is written with plain `INSERT` and `UPDATE`.
- What the source shows: the vector types, the two index types, the distance functions, and that filters run after the approximate index scan unless iterative scans are on.
- What the source does not show: any feature that recomputes a vector when its source text changes. The README names no such feature.
