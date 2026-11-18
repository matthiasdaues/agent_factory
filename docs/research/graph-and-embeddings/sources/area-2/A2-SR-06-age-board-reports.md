# A2-SR-06: Apache board reports and release tags of Apache AGE

```json
{
  "source_identity": "Apache AGE board reports and decisions, collected at https://whimsy.apache.org/board/minutes/AGE.html; release tags of https://github.com/apache/age",
  "author_or_issuing_body": "Apache AGE PMC chair Jeff Jirsa (reports 2024-08 to 2026-07); Apache Software Foundation board (decisions)",
  "publisher": "Apache Software Foundation (Whimsy board minutes); GitHub",
  "publication_date": "2026-09-16T00:00:00Z",
  "relevant_event_date": "2026-07-15",
  "source_family": "Primary: foundation governance records written by the project chair, and the project's own release tags. Same project lineage as A2-SR-04 and A2-SR-05, but a different author and purpose.",
  "precise_evidence_location": "Reports of 2024-08-21, 2025-05-21, 2025-11-19, 2026-03-18 and 2026-07-15; entries 'No report was submitted' for 2026-02-18, 2026-05-20, 2026-06-17 and 2026-08-19; decision of 2026-09-16 'New chair, Muhammad Shoaib'; GitHub release tags PG16/v1.6.0-rc0 to PG15/v1.8.0-rc0",
  "method": "Quarterly reports by the PMC chair to the foundation board; board decisions; tag dates from the GitHub API.",
  "limitations": "publication_date is the latest board decision shown; the page has no single publication date. The GitHub release objects are rc tags whose dates differ from the voted release dates in the board reports (for example PG17/v1.6.0-rc0 is tagged 2025-09-22, the report gives 2025-10-12 for the PG17-1.6.0 release). The chair's view of community health is a judgement, not a count. The report for 2026-10 was not on the page at retrieval.",
  "provenance": "Page downloaded with curl on 2026-11-18 and converted to text. Release tags read with gh api repos/apache/age/releases on 2026-11-18. Repository metadata: archived false, last push 2026-11-04, 269 open issues and pull requests, licence Apache-2.0."
}
```

## Evidence

- Report of 2024-08-21: "Acknowledging for the record that the PMC chair was changed by Board resolution in June 2024."
- Report of 2025-05-21: "The project continues to have very low organic activity and has not released software in over 12 months."
- Report of 2025-05-21: "Github user comments routinely ask for status updates and inquire about the life and activity of the project, but the number of non-committer / non-PMC code contributions is incredibly low."
- Report of 2025-11-19: "PG17-1.6.0 was released on 2025-10-12. PG16-1.6.0 was released on 2025-09-16."
- Report of 2025-11-19: "The last release before these was 2024-03-19."
- Report of 2026-03-18: "This quarter saw important releases, with 1.7.0 releases for both Postgres 17"
- Report of 2026-07-15: "Current project status: Ongoing, but low activity"
- Report of 2026-07-15: "The board appointed PMC chair has asked to be replaced."
- Report of 2026-07-15: "There are currently 20 committers and 13 PMC members in this project."
- Report of 2026-07-15: "Project interest appears to be growing, but organic contribution is low."
- The page lists "No report was submitted." for 2026-02-18, 2026-05-20, 2026-06-17 and 2026-08-19.
- Decision of 2026-09-16: "New chair, Muhammad Shoaib"
- GitHub release tags between 2024-11-18 and 2026-11-18: PG16/v1.6.0-rc0 (2025-09-04), PG17/v1.6.0-rc0 (2025-09-22), PG14 and PG15 v1.6.0-rc0 (2025-11-20), PG18/v1.7.0-rc0 (2026-01-21), PG17/v1.7.0-rc0 (2026-02-11), PG18/v1.8.0-rc0 (2026-07-09), PG15/v1.8.0-rc0 (2026-09-19). AGE releases one build per PostgreSQL major version.
- What the source shows: a gap with no release from 2024-03-19 to 2025-09-16, a return to releases from September 2025, a change of PMC chair in 2024 and again in 2026, and missing quarterly reports in 2026.
- What the source does not show: the number of active code contributors as a count, or who funds the work.
