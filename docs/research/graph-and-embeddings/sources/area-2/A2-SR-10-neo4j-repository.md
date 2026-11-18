# A2-SR-10: Neo4j repository, tags, branches and licence

```json
{
  "source_identity": "GitHub repository neo4j/neo4j, https://github.com/neo4j/neo4j: tags 2025.04.0 to 2026.10.2, branches 2025.01 to 2026.10 and release/5.26.x, repository metadata",
  "author_or_issuing_body": "Neo4j, Inc.",
  "publisher": "GitHub",
  "publication_date": "2026-10-29T14:16:29Z",
  "relevant_event_date": "2026-10-29",
  "source_family": "Primary: the public source repository of Neo4j Community Edition. Same vendor lineage as A2-SR-08 and A2-SR-09, but a release record, not documentation.",
  "precise_evidence_location": "gh api repos/neo4j/neo4j (licence, archived, default branch); repos/neo4j/neo4j/tags (all pages); repos/neo4j/neo4j/branches; commit dates of tags 2026.10.2, 2026.10.0 and 2025.04.0",
  "method": "Repository metadata and tag dates read from the GitHub API.",
  "limitations": "The repository holds Community Edition only; release dates of Enterprise Edition and Aura are not shown here. The GitHub release objects stop in 2017, so tags are the release record. Tag dates are commit dates, which can precede the public release by days. No changelog was read.",
  "provenance": "Read with gh api on 2026-11-18. publication_date is the commit date of tag 2026.10.2, the latest tag."
}
```

## Evidence

- Repository metadata: licence GPL-3.0, archived false, default branch 2026.10, last push 2026-11-06.
- The repository has one branch per calendar month from 2025.01 to 2026.10, and branches release/5.26.0 to release/5.26.24.
- 32 tags carry a calendar version that starts with 2025 or 2026. The latest is 2026.10.2, with commit date 2026-10-29.
- The latest 5.26 tags are 5.26.31, 5.26.32 and 5.26.33.
- What the source shows: Neo4j Community Edition is open source under GPL-3.0 and releases about once a month under calendar versions, with a parallel 5.26 line.
- What the source does not show: the number of maintainers, or the licence of Enterprise Edition.
