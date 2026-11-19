# A1-SR-02: PostgreSQL 8.4 release notes and manual on WITH RECURSIVE

```json
{
  "source_identity": "PostgreSQL 8.4 release notes, https://www.postgresql.org/docs/release/8.4.0/; PostgreSQL 8.4 manual, section 7.8 WITH Queries, https://www.postgresql.org/docs/8.4/queries-with.html",
  "author_or_issuing_body": "PostgreSQL Global Development Group; the release notes credit Yoshiyuki Asaba, Tatsuo Ishii and Tom Lane for the feature",
  "publisher": "PostgreSQL Global Development Group, postgresql.org",
  "publication_date": "2009-07-01T00:00:00Z",
  "relevant_event_date": "2009-07-01",
  "source_family": "Primary: project release notes and manual of PostgreSQL 8.4. Same lineage as A1-SR-04 and A1-SR-05.",
  "precise_evidence_location": "Release notes 8.4.0: Release Date line, Overview list, and the item on WITH clauses; manual 8.4 section 7.8, cycle detection paragraph",
  "method": "Release notes written by the developers; manual text of the release.",
  "limitations": "The 8.4 manual page is served from the archive of unsupported versions and may have been regenerated since 2009; its text was taken as the 8.4 text. The release notes do not say why SEARCH and CYCLE were left out. The original 2008 patch discussion was not read.",
  "provenance": "Both pages downloaded with curl on 2026-11-18 and converted to text with pandoc. Re-verify at the two URLs above."
}
```

## Evidence

- Release notes: "Release Date: 2009-07-01"
- Release notes, Overview: "Common Table Expressions and Recursive Queries"
- Release notes, item: "Add support for WITH clauses (CTEs), including WITH RECURSIVE (Yoshiyuki Asaba, Tatsuo Ishii, Tom)"
- Manual 8.4, section 7.8: "When working with recursive queries it is important to be sure that the recursive part of the query will eventually return no tuples, or else the query will loop indefinitely."
- Manual 8.4, section 7.8: "The standard method for handling such situations is to compute an array of the already-visited values."
- Note: the 8.4 manual shows cycle detection written by hand, with an array column `path` and a Boolean column `cycle`. It names no SEARCH or CYCLE clause.
- What the source shows: PostgreSQL implemented WITH RECURSIVE in 8.4 without the SEARCH and CYCLE clauses of SQL:1999 (A1-SR-01), and told users to detect cycles by hand with an array of visited values.
- What the source does not show: a stated reason for leaving out SEARCH and CYCLE. A1-SR-03 gives the only account found.
