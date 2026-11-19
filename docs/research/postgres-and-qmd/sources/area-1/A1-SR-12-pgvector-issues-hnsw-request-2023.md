# A1-SR-12: pgvector issues 10 and 181, from IVFFlat only to HNSW

```json
{
  "source_identity": "pgvector GitHub issues #10 'consider about add other based on graph method like hnsw?' (2021) and #181 'Add support for HNSW algo' (2023); https://github.com/pgvector/pgvector/issues/10 and /181",
  "author_or_issuing_body": "Issue authors alexw994 (#10) and vinodvarma24 (#181); replies by the maintainer Andrew Kane (ankane)",
  "publisher": "GitHub, repository pgvector/pgvector",
  "publication_date": "2023-07-07T15:46:45Z",
  "relevant_event_date": "2023-08-29",
  "source_family": "Primary: issue threads of the pgvector project with the maintainer's own replies. Same lineage as A1-SR-10, A1-SR-11 and A1-SR-13. The graph-and-embeddings survey record A2-SR-03 reads #10 and #181 as well.",
  "precise_evidence_location": "#10 maintainer reply of 2021-06-10T04:38:56Z; #181 issue body of 2023-07-07T15:46:45Z; #181 maintainer replies of 2023-07-12, 2023-07-21, 2023-08-08 and 2023-08-29T00:28:52Z",
  "method": "Discussion between users and the maintainer in the project issue tracker.",
  "limitations": "publication_date is the opening of #181; the reply in #10 is older and is context only. relevant_event_date is the maintainer's release reply; the changelog dates 0.5.0 one day earlier, 2023-08-28, in the maintainer's time zone. The user's statement on speed is an opinion, not a measurement. Only the maintainer's replies were read in full.",
  "provenance": "Read with gh api repos/pgvector/pgvector/issues/<n> and repos/pgvector/pgvector/issues/<n>/comments on 2026-11-18."
}
```

## Evidence

- #10, maintainer reply of 2021-06-10: "I currently think product quantization is a better fit for the library than graph-based methods"
- #181, issue body of 2023-07-07: "Currently, it's very slow, please add support for the HNSW algorithm to continue to use pg_vector."
- #181, issue body: "I recently came across, pg_embedding, please try to replicate it."
- #181, maintainer reply of 2023-07-12: "Hey all, this is in-progress and planned for 0.5.0."
- #181, maintainer reply of 2023-08-29: "Hey all, 0.5.0 is now released"
- What the source shows: the maintainer first preferred product quantization over graph indexes. Users then asked for HNSW because IVFFlat search was slow for them, and HNSW shipped in 0.5.0.
- What the source does not show: measured speed or recall for either index type.
