# A1-SR-11: pgvector CHANGELOG, first README, and repository state

```json
{
  "source_identity": "pgvector CHANGELOG.md at commit 7c7345e0121d69f5a6e2a6a41357ad5a9a10156e; README.md at tag v0.1.0 (commit f2d881cc478fd90f6e4ab6e27cbc53033ed94e42); LICENSE; repository metadata of pgvector/pgvector, https://github.com/pgvector/pgvector",
  "author_or_issuing_body": "Andrew Kane (ankane) and pgvector contributors",
  "publisher": "GitHub, repository pgvector/pgvector",
  "publication_date": "2026-11-18T12:47:13Z",
  "relevant_event_date": "2021-04-20",
  "source_family": "Primary: release record and repository data of pgvector. Same lineage as A1-SR-10 and A1-SR-12 to A1-SR-15. The graph-and-embeddings survey record A2-SR-02 reads the same changelog for the store comparison.",
  "precise_evidence_location": "CHANGELOG entries 0.1.0, 0.5.0, 0.5.1, 0.8.0 to 0.8.7, and 0.9.0 (unreleased); v0.1.0 README, Indexing; LICENSE first lines; GitHub API repository and commit listings",
  "method": "Changelog kept by the maintainer; first README read at its tag; repository data counted from the GitHub API.",
  "limitations": "publication_date is the master commit read on 2026-11-18; relevant_event_date is the first release. The repository has no GitHub release objects, so release dates come from the changelog. Commit counts include merge and documentation commits and measure activity, not quality. The licence field of the GitHub API reads NOASSERTION; the LICENSE file holds a PostgreSQL-style permissive licence text.",
  "provenance": "Files downloaded with curl from raw.githubusercontent.com on 2026-11-18. Repository data from gh api repos/pgvector/pgvector and repos/pgvector/pgvector/commits?since=2024-11-18T00:00:00Z on 2026-11-18."
}
```

## Evidence

- CHANGELOG 0.1.0 (2021-04-20): "First release"
- README at v0.1.0, Indexing: "Speed up queries with an approximate index. Add an index for each distance function you want to use." The only index shown is `ivfflat`.
- README at v0.1.0: "Indexes should be created after the table has data for optimal clustering."
- CHANGELOG 0.5.0 (2023-08-28): "Added HNSW index type"
- CHANGELOG 0.5.1 (2023-10-10): "Added check for MVCC-compliant snapshot for index scans"
- CHANGELOG 0.8.0 (2024-10-30): "Added support for iterative index scans"
- CHANGELOG 0.8.0: "Improved cost estimation for better index selection when filtering"
- CHANGELOG 0.8.3 (2026-06-17): "Fixed possible index corruption with HNSW vacuuming"
- CHANGELOG 0.8.4 (2026-06-30): "Fixed possible error with inserts during HNSW vacuuming"
- CHANGELOG 0.9.0: "## 0.9.0 (unreleased)" and "Dropped support for Postgres 13 and 14"
- Release activity from 2024-11-18 to 2026-11-18: seven releases, 0.8.1 (2025-09-04), 0.8.2 (2026-02-25), 0.8.3 (2026-06-17), 0.8.4 (2026-06-30), 0.8.5 (2026-07-08), 0.8.6 (2026-07-29) and 0.8.7 (2026-10-01). All are patch releases of 0.8.
- Project health on 2026-11-18: not archived; last push 2026-11-18; 19 open issues and pull requests; 417 commits since 2024-11-18, of which Andrew Kane wrote 403. The project depends on one maintainer for most of its work.
- LICENSE: "Portions Copyright (c) 1996-2026, PostgreSQL Global Development Group". pgvector is open source.
- What the source shows: the order of the index types (IVFFlat in 2021, HNSW in 2023, iterative scans in 2024), the release rhythm, and the concentration of work on one maintainer.
- What the source does not show: the reasons for each change; those are in A1-SR-12 and A1-SR-13.
