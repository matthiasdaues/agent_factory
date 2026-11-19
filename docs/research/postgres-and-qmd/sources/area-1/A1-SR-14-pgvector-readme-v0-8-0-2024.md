# A1-SR-14: pgvector README at tag v0.8.0, iterative index scans with strict and relaxed order

```json
{
  "source_identity": "pgvector README.md at tag v0.8.0 (commit 2627c5ff775ae6d7aef0c430121ccf857842d2f2), section Iterative Index Scans, https://github.com/pgvector/pgvector/blob/v0.8.0/README.md",
  "author_or_issuing_body": "Andrew Kane (ankane) and pgvector contributors",
  "publisher": "GitHub, repository pgvector/pgvector",
  "publication_date": "2024-10-30T20:06:34Z",
  "relevant_event_date": "2024-10-30",
  "source_family": "Primary: project documentation of pgvector at the release that added iterative scans. Same lineage as A1-SR-10 to A1-SR-13.",
  "precise_evidence_location": "README v0.8.0, section Iterative Index Scans, lines 478 to 500",
  "method": "Project documentation at a release tag.",
  "limitations": "The date is the commit date of the tag. The README is the vendor's text and is used for stated features only. It does not say that the strict and relaxed modes answer the drawback named in A1-SR-13; that link is inferred from the order of the two texts.",
  "provenance": "Downloaded with curl from https://raw.githubusercontent.com/pgvector/pgvector/v0.8.0/README.md on 2026-11-18. Tag commit and date from gh api repos/pgvector/pgvector/commits/v0.8.0."
}
```

## Evidence

- Section heading note: "*Added in 0.8.0*"
- "Starting with 0.8.0, you can enable iterative index scans, which will automatically scan more of the index until enough results are found (or it reaches `hnsw.max_scan_tuples` or `ivfflat.max_probes`)."
- "Iterative scans can use strict or relaxed ordering."
- "Strict ensures results are in the exact order by distance"
- "Relaxed allows results to be slightly out of order by distance, but provides better recall"
- Settings: `SET hnsw.iterative_scan = strict_order;` and `SET hnsw.iterative_scan = relaxed_order;`
- What the source shows: the released form of iterative scans. The single switch of the plan in A1-SR-13 became two modes, one that keeps strict distance order and one that gives it up for recall.
- What the source does not show: the cost of either mode.
