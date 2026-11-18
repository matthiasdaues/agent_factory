# A1-SR-13: pgvector issues 244 and 259, dead tuples and filtering with HNSW

```json
{
  "source_identity": "pgvector GitHub issues #244 'HNSW + dead tuples: recall loss/usability issues' (2023-08-29) and #259 'Understanding HNSW + filtering' (2023-09-11); https://github.com/pgvector/pgvector/issues/244 and /259",
  "author_or_issuing_body": "Issue authors alanwli (#244) and Palmik (#259); replies by the maintainer Andrew Kane (ankane)",
  "publisher": "GitHub, repository pgvector/pgvector",
  "publication_date": "2023-09-11T08:45:04Z",
  "relevant_event_date": "2024-09-20",
  "source_family": "Primary: issue threads of the pgvector project with the maintainer's own replies. Same lineage as A1-SR-10 to A1-SR-12 and A1-SR-14. The graph-and-embeddings survey record A2-SR-03 reads #259 as well.",
  "precise_evidence_location": "#244 issue body of 2023-08-29 and maintainer reply of 2023-09-02; #259 issue body of 2023-09-11T08:45:04Z; #259 maintainer replies of 2023-09-12, 2023-11-07, 2023-11-10, 2024-09-20T00:53:20Z and 2024-10-30",
  "method": "Discussion between users and the maintainer in the project issue tracker.",
  "limitations": "publication_date is the opening of #259; #244 is older by thirteen days and is context. relevant_event_date is the maintainer's plan for iterative scans. Comments by users other than the maintainer were skimmed, not read in full. The HQANN prototype was not traced beyond the two replies.",
  "provenance": "Read with gh api repos/pgvector/pgvector/issues/<n> and repos/pgvector/pgvector/issues/<n>/comments on 2026-11-18."
}
```

## Evidence

- #244, issue body: "But the top-10 results in the HNSW index happen to be dead tuples (due to updates & deletes), then the query will return 0 results."
- #244, maintainer reply of 2023-09-02: "As elements get updated/deleted, either speed or recall has to give until the graph can be repaired (which currently happens on vacuum, as it's expensive)."
- #259, issue body of 2023-09-11: "To do this efficiently is not straightforward"
- #259, maintainer reply of 2023-09-12: "I think the decision to support it would come down to the complexity it adds."
- #259, maintainer reply of 2023-11-07: "For the approach, I'm hoping we can avoid the complexity of multiple graphs by using HQANN."
- #259, maintainer reply of 2024-09-20: "If too few results from the initial index scan match the filters, the scan will continue until enough matching results are found."
- #259, same reply: "A drawback of this approach is results may not be returned in strict order"
- #259, same reply, proposed setting: `SET hnsw.iterative_scan = on;`
- #259, maintainer reply of 2024-10-30: "0.8.0 is now released with support for"; the sentence ends with a link to the README section on iterative index scans.
- What the source shows: two complaints against HNSW after 0.5.0, that dead tuples and filters return too few rows. The maintainer tried a filtered graph (HQANN) and then planned iterative scans, and named their drawback, that results may come out of order.
- What the source does not show: why HQANN was not shipped. No reply states it.
