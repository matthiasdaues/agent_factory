# A2-SR-18: ParadeDB changelog entries 0.19.0 and 0.24.0 and release activity

```json
{
  "source_identity": "paradedb/paradedb, docs/project/changelog/0.19.0.mdx and 0.24.0.mdx at commit c0ffb135a234efc5e1cf67f68b9ca5c0e6a51723; GitHub releases v0.19.0 (2025-10-14) and v0.24.0 (2026-06-03); release list and repository metadata; https://github.com/paradedb/paradedb/releases",
  "author_or_issuing_body": "ParadeDB, Inc.",
  "publisher": "GitHub (changelog also published at paradedb.com/docs/project/changelog)",
  "publication_date": "2026-06-03T18:27:00Z",
  "relevant_event_date": "2025-10-14",
  "source_family": "Primary: vendor changelog, release metadata, and repository counts. Same lineage as A2-SR-03, A2-SR-04, A2-SR-05, A2-SR-07.",
  "precise_evidence_location": "0.19.0.mdx section Logical Replication Support; 0.24.0.mdx section Stability Improvements; GitHub API release list, commit list since 2024-11-18, contributor list, repository metadata",
  "method": "Vendor release notes; counts from the GitHub API.",
  "limitations": "Dates come from the GitHub releases because the changelog files carry none. publication_date is v0.24.0 and relevant_event_date is v0.19.0. Counts were taken on 2026-11-18 and change over time; the open-issue count from the repository metadata includes pull requests.",
  "provenance": "Sparse shallow clone of https://github.com/paradedb/paradedb on 2026-11-18; dates and counts from `gh api repos/paradedb/paradedb/releases`, `/commits?since=2024-11-18T00:00:00Z`, `/contributors`, and `gh api repos/paradedb/paradedb`. Re-verify at the URLs above."
}
```

## Evidence

- 0.19.0 (released 2025-10-14): "Previously, logical replication was an enterprise-only feature. We have made this feature available in ParadeDB Community, which means that ParadeDB Community can now run as a logical replica."
- 0.19.0: "Logical replication in ParadeDB is supported for PG17+ only."
- 0.24.0 (released 2026-06-03), Stability Improvements: "`pg_search` will now write WAL entries for its buffers, allowing for crash recovery."
- 0.24.0, same section: "Significantly improved test coverage via concurrent property testing."
- Release activity: 153 GitHub releases published between 2024-11-18 and 2026-11-18, 8 of them release candidates; latest v0.26.8 on 2026-11-18; 2,714 commits since 2024-11-18; 161 contributors; 261 open issues and pull requests; 9,540 stars; licence AGPL-3.0 (GitHub API, 2026-11-18).
- Not shown: whether Community physical standbys can replay the new WAL. A2-SR-06 reports that they stop.
