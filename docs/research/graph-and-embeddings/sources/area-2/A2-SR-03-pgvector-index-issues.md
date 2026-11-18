# A2-SR-03: pgvector issues 10, 181 and 259 on graph indexes and filtering

```json
{
  "source_identity": "pgvector GitHub issues #10 'consider about add other based on graph method like hnsw?', #181 'Add support for HNSW algo', #259 'Understanding HNSW + filtering'; https://github.com/pgvector/pgvector/issues/10, /181, /259",
  "author_or_issuing_body": "Issue authors alexw994 (#10), vinodvarma24 (#181), Palmik (#259); replies by the maintainer Andrew Kane (ankane)",
  "publisher": "GitHub, repository pgvector/pgvector",
  "publication_date": "2021-06-10T03:02:20Z",
  "relevant_event_date": "2021-06-10",
  "source_family": "Primary: issue threads of the pgvector project with the maintainer's own replies. Same lineage as A2-SR-01 and A2-SR-02.",
  "precise_evidence_location": "#10 maintainer reply of 2021-06-10; #181 issue body of 2023-07-07 and maintainer replies of 2023-07-12, 2023-07-21 and 2023-08-29; #259 maintainer replies of 2023-09-12 and 2024-09-20",
  "method": "Discussion between users and the maintainer in the project issue tracker.",
  "limitations": "publication_date is the date of the first thread (#10); the other threads run to 2024-09-20. Users' statements on speed are opinions, not measurements, and are not used as evidence of performance. Only the maintainer's replies were read in full in #259; comments by other users were skimmed.",
  "provenance": "Read with gh api repos/pgvector/pgvector/issues/<n> and repos/pgvector/pgvector/issues/<n>/comments on 2026-11-18."
}
```

## Evidence

- #10, maintainer reply of 2021-06-10: "Adding and supporting new index types is a good amount of work, so I'd like to be selective about it. I currently think product quantization is a better fit for the library than graph-based methods"
- #181, issue body of 2023-07-07: "Currently, it's very slow, please add support for the HNSW algorithm to continue to use pg_vector."
- #181, maintainer reply of 2023-07-21: "Note: HNSW indexes take significantly longer to build than IVFFlat"
- #181, maintainer reply of 2023-08-29: "Hey all, 0.5.0 is now released"
- #259, maintainer reply of 2023-09-12: "I think the decision to support it would come down to the complexity it adds."
- #259, maintainer reply of 2024-09-20: "If too few results from the initial index scan match the filters, the scan will continue until enough matching results are found."
- #259, same reply: "A drawback of this approach is results may not be returned in strict order"
- What the source shows: that the maintainer first preferred product quantization over graph indexes, that users then asked for HNSW, and that the iterative scan of 0.8.0 answered the complaint that filters return too few rows.
- What the source does not show: measured recall or speed. No benchmark from these threads is recorded.
