# A2-SR-16: DuckPGQ README, conformance notes and community extension record

```json
{
  "source_identity": "DuckPGQ README.md and docs/SQLPGQ_CONFORMANCE.md, main branch, https://github.com/cwida/duckpgq-extension; DuckDB community extension descriptor extensions/duckpgq/description.yml, https://github.com/duckdb/community-extensions",
  "author_or_issuing_body": "Daniël ten Wolde (Dtenwolde) and contributors, CWI Database Architectures group",
  "publisher": "GitHub, repositories cwida/duckpgq-extension and duckdb/community-extensions",
  "publication_date": "2026-11-16T12:19:31Z",
  "relevant_event_date": "2026-10-27",
  "source_family": "Primary: project documentation and repository of DuckPGQ, and the DuckDB community extension registry.",
  "precise_evidence_location": "README sections 'Status', 'Installation' and 'Quick Example'; SQLPGQ_CONFORMANCE.md opening paragraph and tables 'Implementation-defined choices', 'Deviations and extensions' and 'Feature inventory'; description.yml fields version, license and maintainers; commit history of description.yml; contributors list",
  "method": "Project documentation read directly; registry history and contributors from the GitHub API.",
  "limitations": "publication_date is the latest commit on main; relevant_event_date is the latest registry update. The git tags stop at v0.10.1 of 2024-04-04, so release activity is read from the registry history. Contributor counts are commit counts from the GitHub API and include a bot account. The research papers behind DuckPGQ were not read. No source shows DuckPGQ and vss used in one query.",
  "provenance": "Files downloaded with curl from raw.githubusercontent.com on 2026-11-18. Commits, tags and contributors read with gh api on 2026-11-18. Repository metadata: archived false, last push 2026-11-18, 24 open issues and pull requests, licence MIT."
}
```

## Evidence

- README: "DuckPGQ is a DuckDB extension for graph workloads with support for SQL/PGQ."
- README, status: "DuckPGQ is a research project and a work in progress."
- README, status: "The SQL/PGQ syntax (`CREATE`, `DROP`, `DESCRIBE` and `SUMMARIZE PROPERTY GRAPH`, and `GRAPH_TABLE` queries) is provided through DuckDB's composable `GrammarExtension` API, so DuckPGQ needs no patched or vendored parser."
- README, quick example: `CREATE PROPERTY GRAPH social VERTEX TABLES (Person) EDGE TABLES (Person_knows_Person SOURCE KEY (person1id) REFERENCES Person (id) ...)` defines a graph over two ordinary tables that were created and filled with plain SQL first.
- Conformance notes: "Element identity | A graph element is a row of one vertex or edge table; `rowid` is its identity."
- Conformance notes: "`OPTIONAL MATCH`, `CHEAPEST` | Not in Part 16. Not implemented."
- Registry descriptor: version 1.0.0, licence MIT, one maintainer, Dtenwolde.
- Registry history: updates for DuckDB v1.2.0 (2025-02-05), v1.2.1, v1.2.2, v1.3.2, v1.4.1, v1.4.3, v1.4.4, v1.5.0, v1.5.1, v1.5.4, v1.5.6 and 2.0 (2026-10-14), and a last bump on 2026-10-27.
- Contributors by commits: Dtenwolde 1269, samansmink 196, carlopi 40, the next below 20.
- What the source shows: DuckPGQ defines a property graph as a view over DuckDB tables and queries it with SQL/PGQ `GRAPH_TABLE`; it follows each DuckDB release; one person does most of the work.
- What the source does not show: any vector feature, or a statement on maturity beyond the research-project status.
