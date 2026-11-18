# A2-SR-05: Apache AGE and pgvector, issue 1121, pull requests 2088 and 2172, regression test

```json
{
  "source_identity": "Apache AGE issue #1121 'Proposal: Vector handling with extension(pgvector)'; pull requests #2088 'Add support for external extensions' and #2172 'Add support for operators in cypher query'; regression test regress/sql/pgvector.sql on the master branch; https://github.com/apache/age",
  "author_or_issuing_body": "Issue author iitaejeong; pull request author Muhammad Taha Naveed (AGE committer); replies by AGE committer John Gemignani (jrgemignani) and users",
  "publisher": "Apache Software Foundation, hosted on GitHub",
  "publication_date": "2023-08-02T02:12:38Z",
  "relevant_event_date": "2024-09-11",
  "source_family": "Primary: issue tracker, pull requests and test code of Apache AGE. Same lineage as A2-SR-04 and A2-SR-06.",
  "precise_evidence_location": "#1121 issue body (2023-08-02) and comments of 2025-05-11, 2025-12-19 and 2026-01-07; #2088 description, merged 2024-09-11; #2172 description, merged 2025-07-09; regress/sql/pgvector.sql, sections on similarity queries and 'Test vector index'",
  "method": "Feature request, the code changes that answered it, and a test file that runs Cypher queries against pgvector types and an HNSW index.",
  "limitations": "publication_date is the date of the issue; relevant_event_date is the merge of #2088. The regression test is an extra test that must be added to the test run explicitly (#2088 description); it shows syntax, not production behaviour. No AGE manual page on pgvector exists; a committer says so in #1121 on 2026-01-07. Issue #1121 is still open.",
  "provenance": "Read with gh api repos/apache/age/issues/1121, issues/1121/comments, pulls/2088 and pulls/2172 on 2026-11-18. Test file downloaded from https://raw.githubusercontent.com/apache/age/master/regress/sql/pgvector.sql on 2026-11-18; its change history read with gh api repos/apache/age/commits?path=regress/sql/pgvector.sql (commits of 2024-09-11, 2025-07-09 and 2026-06-01)."
}
```

## Evidence

- #1121 issue body (2023-08-02): "Apache age doesn't have the function for vector engineering."
- #2088 description: "This commit allows the functions from external extensions to be called from the Cypher queries, provided that typecast is available for args and return type of that function."
- #2088 description: "Added cypher typecast for vector, its not a direct cast. It casts agtype to text and then text to vector."
- #2172 description: "Added support for PG operators in cypher."
- #1121 comment of 2025-12-19 by jrgemignani: "Apache AGE supports the pgvector extension"
- #1121 comment of 2026-01-07 by jrgemignani: "AGE specific? Not that I'm aware."
- regress/sql/pgvector.sql ranks vertices by a pgvector distance inside one Cypher call. The query is `MATCH (m:Movie), (search:Movie {title: ...}) RETURN m.title ORDER BY m.embedding::vector(4) <=> search.embedding::vector(4) ASC LIMIT 4`, passed to `cypher('graph', $$ ... $$)`. The title literal is elided here.
- regress/sql/pgvector.sql, comment before the index: "The index expression below matches the expression seen in the EXPLAIN plan of above query". The test then creates an HNSW index on the label table `graph."Movie"` over the expression that casts the `embedding` property from agtype through text to `vector(4)`.
- What the source shows: one Cypher query can match a pattern and order by pgvector distance, and an HNSW index on the label table can serve it, because the vector sits in the vertex properties of the same PostgreSQL table.
- What the source does not show: a query that starts from a similarity search and then traverses, behaviour with real embedding sizes, or recall.
