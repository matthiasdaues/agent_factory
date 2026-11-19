# A1-SR-04: PostgreSQL commits for SEARCH and CYCLE and for enhanced cycle mark values, 2021

```json
{
  "source_identity": "PostgreSQL commits 3696a600e2292d43c00949ddf0352e4ebb487e5b 'SEARCH and CYCLE clauses' (2021-02-01) and f4adc41c4f92cc91d507b19e397140c35bb9fd71 'Enhanced cycle mark values' (2021-02-27); PostgreSQL 14 release notes, https://www.postgresql.org/docs/release/14.0/",
  "author_or_issuing_body": "Peter Eisentraut (author and committer); reviewed by Vik Fearing and Pavel Stehule",
  "publisher": "PostgreSQL Global Development Group (git repository, mirrored at github.com/postgres/postgres; postgresql.org)",
  "publication_date": "2021-02-01T12:54:59Z",
  "relevant_event_date": "2021-02-27",
  "source_family": "Primary: the PostgreSQL source repository and release notes. Same lineage as A1-SR-02 and A1-SR-03.",
  "precise_evidence_location": "Commit message of 3696a600e229; commit message of f4adc41c4f92; release notes 14.0, Release date line, Overview, and the item on SEARCH and CYCLE",
  "method": "Commit records read directly; release notes written by the developers.",
  "limitations": "The commits were read through the GitHub mirror, not git.postgresql.org. The draft SQL:202x text that f4adc41 cites was not read. relevant_event_date is the second commit. The release of the feature to users is 2021-09-30, from the release notes.",
  "provenance": "Commits read with gh api repos/postgres/postgres/commits/<sha> on 2026-11-18; found by listing commits on src/test/regress/sql/with.sql between 2020-06-01 and 2021-09-01. Release notes downloaded with curl on 2026-11-18. Re-verify with git show <sha> in a PostgreSQL clone."
}
```

## Evidence

- Commit 3696a600e229: "This adds the SQL standard feature that adds the SEARCH and CYCLE clauses to recursive queries to be able to do produce breadth- or depth-first search orders and detect cycles."
- Commit 3696a600e229: "These clauses can be rewritten into queries using existing syntax, and that is what this patch does in the rewriter."
- Commit f4adc41c4f92: "Per SQL:202x draft, in the CYCLE clause of a recursive query, the cycle mark values can be of type boolean and can be omitted, in which case they default to TRUE and FALSE."
- Release notes 14.0: "Release date: 2021-09-30"
- Release notes 14.0, Overview: "The SQL-standard SEARCH and CYCLE options for common table expressions have been implemented."
- Note: commit 3fb676504da9 of 2020-10-12 had already reordered the cycle and path columns in the manual examples, because the standard's CYCLE clause puts them in that order.
- What the source shows: PostgreSQL 14 added SEARCH and CYCLE as a rewrite into the hand-written form, and then followed a draft of the next standard to make the cycle mark values optional (feature T133 in the current manual, A1-SR-05).
- What the source does not show: who criticised the mandatory mark values of SQL:1999 (A1-SR-01), or why the draft changed them.
