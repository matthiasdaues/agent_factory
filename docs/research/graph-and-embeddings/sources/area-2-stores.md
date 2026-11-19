# Area 2: Stores That Hold a Graph and Vectors

This index covers the stores in assignment A2 of the
[survey plan](../research-survey-plan.md). It reports what the 18 records in
[area-2/](area-2/) document, as of 2026-11-18. It forms no claims. The records
quote the sources; this index only points to them.

## State of the art

Six candidate designs exist. Five keep the graph and the vectors in one
database. The sixth puts a vector store beside a graph store. No further
store was added, because the candidates already cover every design the
assignment names.

The table below gives the simplicity facts for each design. A cell marked
"gap" has no record behind it; the section [Gaps](#gaps) says what was
searched.

| Design                                                             | Components                                                               | Query languages                                       | Consistency boundary                                                                                      | Kept in sync by hand                                                                             | Releases from 2024-11-18 to 2026-11-18                                                                                            | Health signs                                                                                                                 |
| ------------------------------------------------------------------ | ------------------------------------------------------------------------ | ----------------------------------------------------- | --------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| PostgreSQL with Apache AGE and pgvector                            | One server, two extensions (A2-SR-04, A2-SR-01)                          | SQL; openCypher inside a SQL function call (A2-SR-04) | One PostgreSQL transaction (A2-SR-04, A2-SR-01)                                                           | Vector against its source text; an index expression that matches the query expression (A2-SR-05) | AGE: 8 tags, one per PostgreSQL version and release (A2-SR-06). pgvector: 7 patch releases, latest 0.8.7 of 2026-10-01 (A2-SR-02) | AGE: no release from 2024-03-19 to 2025-09-16, four missing board reports in 2026, chair changes in 2024 and 2026 (A2-SR-06) |
| PostgreSQL with SQL/PGQ                                            | None released: the feature was reverted before PostgreSQL 19 (A2-SR-07)  | —                                                     | —                                                                                                         | —                                                                                                | —                                                                                                                                 | —                                                                                                                            |
| Neo4j with its vector index                                        | One server; Lucene inside (A2-SR-08)                                     | Cypher 5 and Cypher 25 (A2-SR-08, A2-SR-09)           | One transaction, but the index does not see changes made in the same transaction (A2-SR-08)               | Vector against its source text (gap for any sync feature)                                        | 32 calendar-version tags plus a 5.26 line, about monthly (A2-SR-10)                                                               | Community Edition under GPL-3.0, repository active (A2-SR-10)                                                                |
| Memgraph                                                           | One server; USearch inside (A2-SR-11)                                    | Cypher with procedures (A2-SR-11)                     | The vector index reads uncommitted data; the rest of the database keeps its isolation level (A2-SR-11)    | An embeddings module computes vectors when called (A2-SR-11)                                     | 29, latest v3.14.0 of 2026-10-21 (A2-SR-12)                                                                                       | Licence BSL 1.1 and Memgraph Enterprise License (A2-SR-12)                                                                   |
| FalkorDB                                                           | A Redis server with the FalkorDB module and a RediSearch fork (A2-SR-14) | openCypher with extensions (A2-SR-14)                 | One query is atomic; several queries need Redis MULTI/EXEC (A2-SR-13)                                     | A vector must be wrapped in vecf32() or the index skips it (A2-SR-13)                            | 78 on two lines, 4.x in C and 6.x in Rust (A2-SR-14)                                                                              | New engine in September 2026; successor of RedisGraph, which is no longer maintained (A2-SR-14); licence SSPL                |
| DuckDB with DuckPGQ and vss                                        | One embedded process, two extensions (A2-SR-15, A2-SR-16)                | SQL and SQL/PGQ GRAPH_TABLE (A2-SR-16)                | Gap: DuckDB's transaction model was not read; vss filters through a transaction-visible bitmap (A2-SR-15) | An in-memory HNSW index; persistence only behind an experimental flag (A2-SR-15)                 | DuckDB: 20 (A2-SR-15); DuckPGQ follows each DuckDB release (A2-SR-16)                                                             | vss is experimental (A2-SR-15); DuckPGQ is a research project with one main contributor (A2-SR-16)                           |
| Graph store beside a vector store, Neo4j and Qdrant as the example | Two servers (A2-SR-18)                                                   | Cypher and the Qdrant API (A2-SR-17, A2-SR-18)        | Two boundaries; a Qdrant write is eventually consistent unless the client waits (A2-SR-17)                | The node identifier copied into the vector payload (A2-SR-18)                                    | Qdrant: 34, latest v1.20.2 of 2026-11-16 (A2-SR-17)                                                                               | Qdrant under Apache-2.0, repository active (A2-SR-17)                                                                        |

Each design runs a traversal and a similarity search differently:

- AGE with pgvector runs one Cypher query that matches a pattern and orders by
  a pgvector distance. An HNSW index on the label table serves it when the
  index expression matches the cast in the query (A2-SR-05). No AGE manual
  page covers this (A2-SR-05).
- Neo4j binds nodes with `MATCH` and searches with `SEARCH` in one statement.
  The pattern around `SEARCH` allows one bound variable and at most one hop.
  Filters inside `SEARCH` run in the index; filters outside run afterwards
  (A2-SR-09).
- Memgraph and FalkorDB search through a procedure call (A2-SR-11,
  A2-SR-13). FalkorDB documents no filter support for vector queries
  (A2-SR-13).
- In the separate-store design, a query runs in two steps: first the vector
  search, then a lookup of the node by its copied identifier (A2-SR-18).

The vector indexes are HNSW in every store that names its algorithm:
pgvector also offers IVFFlat (A2-SR-01), Neo4j uses Lucene (A2-SR-08),
FalkorDB names HNSW (A2-SR-13), and vss uses the usearch library (A2-SR-15).
Memgraph names USearch but not the algorithm (A2-SR-11). The cost of keeping
an index current shows up as marked deletes that need compaction in vss
(A2-SR-15), memory not freed on delete in Memgraph (A2-SR-11), and HNSW
vacuum fixes in pgvector 0.8.3 and 0.8.4 (A2-SR-02).

No store documents a feature that recomputes a vector when its source text
changes. Memgraph's embeddings module comes closest, but it runs only when
a query calls it (A2-SR-11).

## Hardened concepts

Six concepts show a documented sequence of formulations.

### pgvector index design

1. **IVFFlat only, exact search by default.** Release 0.1.0, 2021-04-20
   (A2-SR-02). IVFFlat needs data before the index is built (A2-SR-01).
   Criticism: a user asked for a graph index in 2021; the maintainer then
   preferred product quantization (A2-SR-03, issue 10). In 2023, users called
   the search too slow and asked for HNSW (A2-SR-03, issue 181).
2. **HNSW index added.** Release 0.5.0, 2023-08-28 (A2-SR-02, A2-SR-03).
   HNSW needs no training step but builds more slowly (A2-SR-01).
   Criticism: a filter runs after the index scan, so a query can return too
   few rows (A2-SR-01; A2-SR-03, issue 259).
3. **Smaller vector types.** `halfvec` and `sparsevec`, release 0.7.0,
   2024-04-29 (A2-SR-02). Criticism: gap; no source for the reason was read.
4. **Iterative index scans.** Release 0.8.0, 2024-10-30 (A2-SR-02,
   A2-SR-03). The scan continues until enough rows match. Criticism: results
   may not come in strict order (A2-SR-03). The README now offers strict and
   relaxed ordering (A2-SR-01); the release that added the choice is a gap.

### Apache AGE and pgvector in one query

1. **SQL only through scalar user functions.** Manual page last changed
   2023-12-01 (A2-SR-04). Criticism: AGE had no vector handling, issue 1121,
   2023-08-02 (A2-SR-05).
2. **Functions of other extensions callable from Cypher, with a vector cast
   through text.** Pull request 2088, merged 2024-09-11 (A2-SR-05).
   Criticism: gap; the pull request that followed states what it adds, not
   what was missing.
3. **PostgreSQL operators in Cypher, with type modifiers.** Pull request
   2172, merged 2025-07-09 (A2-SR-05). Criticism: users still find no
   documentation, and a committer confirms none exists, 2026-01-07
   (A2-SR-05).

### Neo4j vector index

1. **Public beta, created by a procedure.** Neo4j 5.11, 2023 (A2-SR-08).
   Criticism: gap.
2. **General availability in 5.13; the `CREATE VECTOR INDEX` command
   replaces the procedure from 5.15** (A2-SR-08). Criticism: gap.
3. **Native VECTOR property type.** Neo4j 2025.10 (A2-SR-08). Criticism:
   gap.
4. **`SEARCH` clause with in-index filters.** Neo4j 2026.01 (A2-SR-08,
   A2-SR-09). The documented reason: a filter in `MATCH` after the search
   can return far fewer results (A2-SR-09). Remaining limits: one bound
   variable, one hop, AND-only predicates (A2-SR-09).
5. **Procedures deprecated.** Neo4j 2026.04 (A2-SR-08). The `IN` operator
   became allowed in filters in 2026.06 (A2-SR-09).

### Memgraph vector index

1. **Experimental, behind a flag.** v2.22.0, 2024-11-27 (A2-SR-12).
2. **Stable, with a changed API.** v3.0.0, 2025-01-29 (A2-SR-12).
   Criticism for the API change: gap.
3. **Vector stored only in the index.** v3.8.0, 2026-02-11 (A2-SR-12). The
   release note names the duplicated data in the property store as the
   problem it removes (A2-SR-12). The cost that remains: dropping the index
   moves every vector back (A2-SR-11).
4. **Multi-label and wildcard indexes.** v3.11.0, 2026-06-17 (A2-SR-12).

### SQL/PGQ in PostgreSQL

1. **Committed to the development branch.** 2026-03-16 (A2-SR-07).
   Criticism: the Release Management Team names unresolved design issues,
   such as orphaned graph metadata after `DROP ... CASCADE`, 2026-09-02
   (A2-SR-07).
2. **Reverted.** 2026-09-07; PostgreSQL 19 ships without it (A2-SR-07).
   The next attempt is a gap.

### Filtered search in DuckDB vss

1. **No pre-filtering.** The README of 2024-09-05 has no section on
   filters (A2-SR-15). Criticism: a top-k search followed by discarding rows
   returns fewer rows than asked; the pre-filter text states this (A2-SR-15).
2. **Pre-filtering of pushed-down filters.** First commit 2026-09-03
   (A2-SR-15). The remaining cost is an O(n) scan of the filter columns per
   query (A2-SR-15).

## Gaps

What could not be found or reached:

- **AGE openCypher support.** No list of supported clauses and no openCypher
  TCK result exists in the README or the manual. A GitHub search for "TCK"
  in apache/age returned zero issues. This concept therefore has no
  sequence here.
- **Neo4j.** No page states whether the vector index is updated at commit
  or later. The reasons for steps 1 to 3 of the Neo4j sequence were not
  found. The Neo4j GenAI documentation on creating embeddings was not read.
  The licence of Enterprise Edition and the number of maintainers were not
  recorded.
- **Memgraph.** No documented example combines `vector_search.search` with a
  graph pattern. The reason for the v3.0.0 API change was not found. The
  storage model, in memory or on disk, was not recorded.
- **FalkorDB.** No page states whether the vector index is updated inside
  the atomic write. No example combines a vector query with a traversal.
  The RedisGraph end-of-life blog post was not read.
- **DuckDB.** DuckDB's own transaction documentation was not read. No source
  shows DuckPGQ and vss in one query. The DuckPGQ research papers were not
  read.
- **Separate vector store.** Only Qdrant was read; Milvus and Weaviate were
  not. Qdrant's index types were not recorded. No Qdrant page on writes that
  span several requests was found. Only one library's join of the two
  stores was read (A2-SR-18).
- **Sync features.** No store documents automatic recomputation of vectors.
  Searches covered the pgvector README, the Neo4j and Memgraph vector pages,
  and the FalkorDB vector page.
- **pgvector.** The reason for `halfvec` and `sparsevec`, and the release
  that added strict and relaxed ordering, were not found.
- **AGE.** The board report for October 2026 was not on the board minutes
  page. The criticism that led to pull request 2172 was not found.
- **Licences.** The records name the licences of Memgraph (BSL 1.1, MEL)
  and FalkorDB (SSPL). Whether they count as open source was not assessed,
  as the assignment asks.
