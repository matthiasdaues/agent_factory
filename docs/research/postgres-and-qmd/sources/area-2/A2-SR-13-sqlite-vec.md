# A2-SR-13: sqlite-vec repository and documentation

```json
{
  "source_identity": "GitHub repository asg017/sqlite-vec, README.md at commit 04d28bd21773981e2d266bbf6aa4efbd011eb4f6, release list; documentation page https://alexgarcia.xyz/sqlite-vec/features/knn.html",
  "author_or_issuing_body": "Alex Garcia (asg017) and contributors",
  "publisher": "GitHub; alexgarcia.xyz",
  "publication_date": "2026-05-18T06:50:43Z",
  "relevant_event_date": "2026-03-31",
  "source_family": "Primary: repository, README, and release metadata of sqlite-vec, a dependency of qmd. Independent of the tobi/qmd lineage. The KNN page was read through a summarising fetch tool and is recorded as paraphrase except one quoted phrase.",
  "precise_evidence_location": "README.md lines 1-18; GitHub API repos/asg017/sqlite-vec fields license, pushed_at, open_issues_count; releases list; contributors count",
  "method": "Read the README through gh api repos/asg017/sqlite-vec/readme and the API metadata on 2026-11-18. Fetched the KNN page with a summarising web tool.",
  "limitations": "The README does not state whether vec0 KNN search is exhaustive. The KNN page was read through a summarising tool, which reported no statement either way. relevant_event_date is the v0.1.9 release that qmd pins. No commits since 2026-06-01 were returned by the API on 2026-11-18.",
  "provenance": "gh api calls on 2026-11-18. Re-verify at https://github.com/asg017/sqlite-vec/blob/04d28bd21773981e2d266bbf6aa4efbd011eb4f6/README.md."
}
```

## Evidence

- README lines 5-6, whole sentence: "An extremely small, "fast enough" vector search SQLite extension that runs anywhere!"
- README line 11: "_`sqlite-vec` is a pre-v1, so expect breaking changes!_"
- README lines 15-18: vec0 virtual tables store float, int8, and binary vectors; "Written in pure C, no dependencies, runs anywhere SQLite runs"; non-vector data goes into "metadata, auxiliary, or partition key columns".
- API: license Apache-2.0; archived false; pushed_at 2026-05-18; 252 open issues; 18 contributors on the first API page. Releases: v0.1.8 on 2026-03-30, v0.1.9 on 2026-03-31, then v0.1.10-alpha.1 to alpha.4, the last on 2026-05-18. qmd pins 0.1.9 (A2-SR-12).
- KNN page, paraphrase: the page does not say whether vec0 KNN queries are exhaustive or approximate. Its only use of the term is for plain tables: "and an `ORDER BY` clause to perform a brute-force KNN query."
- Shows: licence, release state, and stated scope of the vector extension. Does not show: index type, recall, or behaviour under concurrent writers. The graph-and-embeddings survey (docs/research/graph-and-embeddings/sources/area-4-nearest-neighbour-indexes.md) covers index algorithms and has no record on sqlite-vec.
