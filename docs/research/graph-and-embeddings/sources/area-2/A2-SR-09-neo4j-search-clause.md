# A2-SR-09: Neo4j Cypher Manual, the SEARCH clause

```json
{
  "source_identity": "Neo4j Cypher Manual, page 'SEARCH', current version, https://neo4j.com/docs/cypher-manual/current/clauses/search/",
  "author_or_issuing_body": "Neo4j, Inc. (documentation team)",
  "publisher": "Neo4j, Inc., neo4j.com",
  "publication_date": "2026-11-18T00:00:00Z",
  "relevant_event_date": "2026-01-01",
  "source_family": "Primary: vendor documentation of Neo4j. Same lineage as A2-SR-08 and A2-SR-10.",
  "precise_evidence_location": "Page header; syntax section; section 'Vector search with filters'; section 'Limitations of the SEARCH clause', tables 'Limitations of the MATCH or OPTIONAL MATCH pattern' and 'Limitations of the WHERE predicate'",
  "method": "Vendor documentation that states syntax and limits of a Cypher clause.",
  "limitations": "Living page; the date is the retrieval date. relevant_event_date stands for Neo4j 2026.01, the version that introduced the clause; the day is not documented and is set to the first of the month. Example result rows on the page are illustrations, not measurements.",
  "provenance": "Downloaded with curl on 2026-11-18 and converted from HTML to text with a local script. Re-verify at the URL above."
}
```

## Evidence

- Header: "Cypher 25 onlyIntroduced in Neo4j 2026.01". The page text runs the two labels together.
- Syntax: "The optional WHERE subclause is only allowed in vector searches. It applies a filter to the vector index, and is a restricted version of the normal Cypher® WHERE clause."
- Filters: "Regardless of their order, the WHERE clause will act as a post-filtering step to the vector search, further filtering down the results."
- Filters: "Often, it is preferable to do the filtering while performing the vector search, so called in-index filtering, instead of as a post-filtering step."
- Filters: "When using vector search with filters, the vector search continues until it has found the requested number of result that also fulfills the other predicates."
- Filters: "By contrast, using a normal WHERE clause in the MATCH can lead to significantly fewer results."
- Pattern limits: "The pattern cannot have more than one bound variable." and "The pattern cannot have a length longer than one relationship hop."
- WHERE limits: "The predicate cannot include other boolean operators than AND." and "Before Neo4j 2026.06, the predicate cannot include the IN operator."
- A2-SR-08 shows a query that runs `MATCH (m:Movie {title: 'Godfather, The'})` and then `MATCH (movie: Movie) SEARCH movie IN ( VECTOR INDEX moviePlots FOR m.embedding LIMIT 5 ) SCORE AS score` in one Cypher statement.
- What the source shows: one Cypher statement can bind a node by a pattern, search the vector index, and filter in the index on properties stored in it. The pattern that encloses SEARCH is limited to one bound variable and at most one hop; further traversal needs a following clause.
- What the source does not show: recall or speed of in-index filtering.
