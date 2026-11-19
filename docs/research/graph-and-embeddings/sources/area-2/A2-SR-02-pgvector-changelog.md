# A2-SR-02: pgvector CHANGELOG and release tags

```json
{
  "source_identity": "pgvector CHANGELOG.md, master branch, https://github.com/pgvector/pgvector/blob/master/CHANGELOG.md; git tags v0.4.0 to v0.8.7",
  "author_or_issuing_body": "Andrew Kane (ankane) and pgvector contributors",
  "publisher": "GitHub, repository pgvector/pgvector",
  "publication_date": "2026-11-18T00:00:00Z",
  "relevant_event_date": "2021-04-20",
  "source_family": "Primary: release record of pgvector, written by its maintainer. Same lineage as A2-SR-01 and A2-SR-03.",
  "precise_evidence_location": "CHANGELOG entries 0.1.0, 0.5.0, 0.6.0, 0.7.0, 0.8.0, 0.8.1 to 0.8.7, and 0.9.0 (unreleased); commit dates of the tags from the GitHub API",
  "method": "Changelog kept by the maintainer; tag dates read from the commit each tag points to.",
  "limitations": "The changelog is a living file; the publication date is the retrieval date. relevant_event_date is the first release, 2021-04-20. The repository has no GitHub release objects, so release dates come from the changelog and from tag commit dates. The changelog lists changes but gives no reasons for them; reasons are in A2-SR-03.",
  "provenance": "CHANGELOG downloaded with curl from https://raw.githubusercontent.com/pgvector/pgvector/master/CHANGELOG.md on 2026-11-18. Tags and their commit dates read with gh api repos/pgvector/pgvector/tags and repos/pgvector/pgvector/commits/<tag> on 2026-11-18. Repository metadata from gh api repos/pgvector/pgvector: archived false, last push 2026-11-18."
}
```

## Evidence

- Entry 0.1.0 (2021-04-20): "First release"
- Entry 0.5.0 (2023-08-28): "Added HNSW index type"
- Entry 0.6.0 (2024-01-29): "Added support for parallel index builds for HNSW"
- Entry 0.7.0 (2024-04-29): "Added `halfvec` type" and "Added `sparsevec` type"
- Entry 0.8.0 (2024-10-30): "Added support for iterative index scans"
- Entry 0.8.3 (2026-06-17): "Fixed possible index corruption with HNSW vacuuming"
- Entry 0.8.4 (2026-06-30): "Fixed possible error with inserts during HNSW vacuuming"
- Entry 0.9.0: "## 0.9.0 (unreleased)"
- Tag commit dates: v0.8.1 2025-09-05, v0.8.2 2026-02-25, v0.8.3 2026-06-18, v0.8.4 2026-06-30, v0.8.5 2026-07-08, v0.8.6 2026-07-29, v0.8.7 2026-10-01. Seven releases fall between 2024-11-18 and 2026-11-18. All of them are patch releases of 0.8.
- Repository licence field from the GitHub API: NOASSERTION. The README calls pgvector "Open-source" (A2-SR-01).
- What the source shows: the order in which the index types and vector types arrived, the release dates, and that the latest release is 0.8.7 of 2026-10-01.
- What the source does not show: why each change was made, or how many maintainers are active.
