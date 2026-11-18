# A1-SR-03: Peter Eisentraut, SEARCH and CYCLE clauses, pgsql-hackers, 2020

```json
{
  "source_identity": "pgsql-hackers message 'SEARCH and CYCLE clauses', Message-ID db80ceee-6f97-9b4a-8ee8-3ba0c58e5be2@2ndquadrant.com, https://www.postgresql.org/message-id/db80ceee-6f97-9b4a-8ee8-3ba0c58e5be2@2ndquadrant.com",
  "author_or_issuing_body": "Peter Eisentraut (2ndQuadrant, PostgreSQL committer)",
  "publisher": "PostgreSQL Global Development Group, pgsql-hackers mailing list archive",
  "publication_date": "2020-05-20T11:46:18Z",
  "relevant_event_date": "2020-05-20",
  "source_family": "Primary: the developers' mailing list, first message of the thread that led to the commits in A1-SR-04.",
  "precise_evidence_location": "Message body of 2020-05-20 11:46:18; thread index on the same page",
  "method": "Patch proposal by the author of the feature, with a patch attached.",
  "limitations": "Only the first message was read in full. The thread holds about thirty replies from 2020-05-20 to 2021-02-27 by Vik Fearing, Pavel Stehule, Robert Haas, Anastasia Lubennikova and the author; their objections were not read. The archive time zone is not stated on the page; the time is recorded as given.",
  "provenance": "Downloaded with curl on 2026-11-18 and converted to text with pandoc. Re-verify at the URL above."
}
```

## Evidence

- Body: "I have implemented the SEARCH and CYCLE clauses."
- Body: "This is standard SQL syntax attached to a recursive CTE to compute a depth- or breadth-first ordering and cycle detection, respectively."
- Body: "This is just convenience syntax for what you can already do manually."
- Body: "The original discussion about recursive CTEs briefly mentioned these as something to do later but then it was never mentioned again."
- Body: "SQL specifies these in terms of syntactic transformations, and so that's how I have implemented them also, mainly in the rewriter."
- What the source shows: the reason for the change. Since 8.4 (A1-SR-02), users had to write cycle detection and search order by hand. The proposal adds the standard's shorter syntax and rewrites it into the hand-written form.
- What the source does not show: any measured cost of the hand-written form, or the review objections raised in the thread.
