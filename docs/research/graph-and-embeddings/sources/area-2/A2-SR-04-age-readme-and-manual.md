# A2-SR-04: Apache AGE README and manual pages

```json
{
  "source_identity": "Apache AGE README.md, master branch, https://github.com/apache/age/blob/master/README.md; AGE manual sources docs/intro/cypher.md, docs/intro/graphs.md and docs/advanced/sql_in_cypher.md in https://github.com/apache/age-website",
  "author_or_issuing_body": "Apache AGE project (Project Management Committee and contributors)",
  "publisher": "Apache Software Foundation, hosted on GitHub",
  "publication_date": "2026-11-18T00:00:00Z",
  "relevant_event_date": "2026-11-18",
  "source_family": "Primary: project documentation of Apache AGE. Same lineage as A2-SR-05 and A2-SR-06.",
  "precise_evidence_location": "README section introducing AGE; README section 'What is and isn't transactional'; manual page 'The AGE Cypher Query Format'; manual page on graphs (label tables); manual page 'SQL In Cypher' (last changed 2023-12-01)",
  "method": "Project documentation that states the data model, the query interface and the transaction behaviour.",
  "limitations": "The README is a living document; the date is the retrieval date. The manual page 'SQL In Cypher' was last changed on 2023-12-01 and may predate the extension support of A2-SR-05. The README does not say how much of openCypher AGE supports; no conformance list or openCypher TCK result was found (see the area index). Vendor documentation is used for stated features only.",
  "provenance": "README downloaded with curl from https://raw.githubusercontent.com/apache/age/master/README.md on 2026-11-18. Manual pages downloaded from https://raw.githubusercontent.com/apache/age-website/master/docs/... on 2026-11-18; last-change date of sql_in_cypher.md read with gh api repos/apache/age-website/commits."
}
```

## Evidence

- README: "The basic principle of the project is to create a single storage that handles both the relational and graph data model so that the users can use the standard ANSI SQL along with openCypher, one of the most popular graph query languages today."
- README feature list: "**Hybrid Querying**: enables SQL and/or Cypher"
- README: "Currently, only PostgreSQL versions 11, 12, 13, 14, 15, 16, 17 & 18 are supported."
- README, transaction section: "AGE's DDL-like functions write to the catalog, and catalog writes only become visible to other sessions after the enclosing transaction is committed."
- README, transaction table: a Cypher `CREATE` called through `cypher('g', $$ ... $$)` is listed as a write that needs a commit to be visible elsewhere.
- Manual, Cypher query format: "Cypher queries are constructed using a function called cypher in ag_catalog which returns a Postgres SETOF". The sentence ends with a link named records.
- Manual, graphs page: "After creating the graph, two tables are going to be created under the graph's namespace to store vertices and edges: `_ag_label_vertex` and `_ag_label_edge`."
- Manual, SQL In Cypher: "AGE does not support SQL being directly written in Cypher. However with user defined functions you can write SQL queries and call them in a cypher command." The manual links "user defined functions" to its page on user functions; the link is dropped here because it is relative to the manual.
- Manual, SQL In Cypher, developer's note: "Void and Scalar-Value functions only. Set returning functions are not currently supported."
- What the source shows: AGE stores vertices and edges in PostgreSQL tables per label, runs Cypher inside a SQL function call, and follows PostgreSQL transaction rules.
- What the source does not show: which openCypher clauses AGE lacks, and anything about vectors.
