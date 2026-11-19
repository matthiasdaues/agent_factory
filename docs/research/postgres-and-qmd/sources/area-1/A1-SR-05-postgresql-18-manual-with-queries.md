# A1-SR-05: PostgreSQL 18 manual on WITH queries, SEARCH and CYCLE

```json
{
  "source_identity": "PostgreSQL 18 manual: section 7.8 WITH Queries (Common Table Expressions), https://www.postgresql.org/docs/current/queries-with.html; SELECT reference page, WITH clause, https://www.postgresql.org/docs/current/sql-select.html; Appendix D.1 Supported Features, https://www.postgresql.org/docs/current/features-sql-standard.html",
  "author_or_issuing_body": "PostgreSQL Global Development Group",
  "publisher": "PostgreSQL Global Development Group, postgresql.org",
  "publication_date": "2026-11-12T00:00:00Z",
  "relevant_event_date": "2025-09-25",
  "source_family": "Primary: the PostgreSQL manual for the current release. Same lineage as A1-SR-02, A1-SR-06, A1-SR-07 and A1-SR-08.",
  "precise_evidence_location": "Section 7.8.2 Recursive Queries; 7.8.2.1 Search Order; 7.8.2.2 Cycle Detection; 7.8.4 Data-Modifying Statements in WITH; SELECT page, paragraphs on RECURSIVE, SEARCH and CYCLE; Appendix D.1 rows T131, T132, T133",
  "method": "Project manual that states syntax and behaviour.",
  "limitations": "The manual is a living document. publication_date is the date of the latest minor release 18.7 (2026-11-12), from the postgresql.org front page; relevant_event_date is the release of PostgreSQL 18 (2025-09-25), from the versioning page. On 2026-11-18 postgresql.org marks 18 as current and 19 as release candidate 2. The manual does not combine a vector search and a recursive query in one example; that combination is inferred in A1-SR-10.",
  "provenance": "Pages downloaded with curl on 2026-11-18 and converted to text with pandoc; the page title reads 'Documentation: 18'. Re-verify at the URLs above or at /docs/18/."
}
```

## Evidence

- 7.8.2: "Using RECURSIVE, a WITH query can refer to its own output."
- 7.8.2: "While RECURSIVE allows queries to be specified recursively, internally such queries are evaluated iteratively."
- 7.8.2.2: "The standard method for handling such situations is to compute an array of the already-visited values."
- 7.8.2.2: "There is built-in syntax to simplify cycle detection."
- 7.8.2.2: "The CYCLE clause specifies first the list of columns to track for cycle detection, then a column name that will show whether a cycle has been detected, and finally the name of another column that will track the path."
- 7.8.2.1: "This syntax is internally expanded to something similar to the above hand-written forms."
- SELECT page: "Furthermore, processing of the recursive union will stop when a cycle has been detected."
- SELECT page: "When there are multiple queries in the WITH clause, RECURSIVE should be written only once, immediately after WITH. It applies to all queries in the WITH clause, though it has no effect on queries that do not use recursion or forward references."
- SELECT page: "Only one recursive self-reference is permitted per query."
- 7.8.4: "All the statements are executed with the same snapshot (see Chapter 13)". The sentence goes on to say that the sub-statements cannot see one another's effects on the target tables; this part is a paraphrase, because the source puts the word see in quotation marks.
- Appendix D.1 lists T131 Recursive query, T132 Recursive query in subquery, and T133 Enhanced cycle mark values as supported features.
- Statement S5: the manual allows several WITH queries in one statement, a non-recursive one beside a recursive one, so a vector search can sit in the first and the traversal with CYCLE in the second. This is inferred from the syntax; the manual shows no such example.
- What the source shows: current syntax and evaluation of recursive queries, the SEARCH and CYCLE clauses as a rewrite of the hand-written form, and the one-snapshot rule for data-modifying statements inside WITH.
- What the source does not show: the cost of CYCLE on large graphs, or any graph-specific index support. The path column is an array that grows with each hop; its cost is not stated.
