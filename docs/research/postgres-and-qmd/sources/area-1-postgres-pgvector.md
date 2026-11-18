# Area 1: Plain PostgreSQL With pgvector, Clients, and Events

This index covers assignment A1 of the [survey plan](../research-survey-plan.md). The records sit in [area-1/](area-1/) under the prefix `A1-SR-`. Twenty-one records were gathered on 2026-11-18. The graph-and-embeddings survey already compared stores and index algorithms; its records [A2-SR-01 to A2-SR-03](../../graph-and-embeddings/sources/area-2/) on pgvector and [A2-SR-07](../../graph-and-embeddings/sources/area-2/A2-SR-07-postgresql-sqlpgq-revert.md) on SQL/PGQ serve as context and are not repeated here.

## State of the Art

PostgreSQL 18 is the current release; 19 is at release candidate 2 (A1-SR-09). A graph fits in ordinary tables. Recursive queries with the `SEARCH` and `CYCLE` clauses walk it, and the clauses are a rewrite into hand-written SQL (A1-SR-04, A1-SR-05). A `CHECK` constraint may not read other rows, so the manual points to triggers for checks across rows (A1-SR-06). Privileges and triggers can block updates and deletes for ordinary roles, but not for the table owner or a superuser (A1-SR-06).

pgvector keeps vectors as columns and its indexes inside the server and its write-ahead log (A1-SR-10). HNSW and IVFFlat are approximate. Filters run after the index scan, and since 0.8.0 iterative scans fetch more candidates (A1-SR-10, A1-SR-14). The PostgreSQL core, not the index, decides which rows a snapshot sees (A1-SR-07). From that rule and the HNSW insert code it follows that a transaction can find its own new vectors through HNSW. No source states this directly (A1-SR-10, A1-SR-15).

`NOTIFY` delivers at commit, in commit order, with a payload under 8000 bytes. A notification reaches only sessions that listen at that moment (A1-SR-08). The transactional outbox keeps events in a table written in the same transaction (A1-SR-16). pg_eventserv relays `NOTIFY` to WebSocket clients, but nobody has changed its code since 2023 (A1-SR-19). asyncpg offers transactions and listeners (A1-SR-20). aiosql turns SQL files into named Python methods and leaves transactions to the caller (A1-SR-21).

### Statements S1 to S12

Each statement is listed with its records. "Inferred" means the records give the parts, and no source states the whole.

| No. | Finding                                                                                                                                                                                                                                               | Records                      |
| --- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------- |
| S1  | Supported. Vectors are table columns queried with SQL in the same server and write-ahead log. The embedding model runs outside the database.                                                                                                          | A1-SR-10, A1-SR-05           |
| S2  | Supported with a limit. The foreign key is a plain constraint; the node-kind check must be a trigger. It checks at insert time only, so a later change of a node's kind needs its own trigger on `node`.                                              | A1-SR-06                     |
| S3  | Supported with limits, inferred. Missing UPDATE, DELETE and TRUNCATE privileges or raising triggers block changes. Row triggers miss `TRUNCATE`; the owner and superusers keep full rights. No source was found for the "as of date D" query.         | A1-SR-06                     |
| S4  | Supported, inferred. A B-tree on `(source_id, type)` serves lookups on its leading column.                                                                                                                                                            | A1-SR-06                     |
| S5  | Inferred. Several WITH queries may share one statement, and pgvector search works inside a materialized CTE. No source shows the combined statement.                                                                                                  | A1-SR-05, A1-SR-10           |
| S6  | Supported. SQL functions can return tables and hold any SQL; procedures add transaction control.                                                                                                                                                      | A1-SR-07                     |
| S7  | Inferred, with two limits. Own writes are visible to later statements, and HNSW leaves visibility to the core. HNSW returns at most `hnsw.ef_search` candidates. HNSW and IVFFlat take no predicate locks, and a race under SERIALIZABLE is reported. | A1-SR-07, A1-SR-10, A1-SR-15 |
| S8  | Supported. Delivery happens only after commit; a failure to queue rolls the transaction back.                                                                                                                                                         | A1-SR-08                     |
| S9  | Supported. Loss without a listener and after a listener restart is inferred from `async.c`. The outbox keeps the events.                                                                                                                              | A1-SR-08, A1-SR-16           |
| S10 | Supported. pg_eventserv relays payloads to WebSockets. It does not buffer or replay, and nobody has changed its code since 2023.                                                                                                                      | A1-SR-19                     |
| S11 | The condition is not met. SQL/PGQ worked like a view over existing tables, then was reverted before release 19. No release is scheduled.                                                                                                              | A1-SR-09                     |
| S12 | Supported, with one condition. One asyncpg connection inside `connection.transaction()` holds the writes, aiosql names the queries, and asyncpg listens. A pool passed to aiosql gives each call its own transaction.                                 | A1-SR-20, A1-SR-21           |

### Simplicity Facts

| Fact                                       | Value                                                                                                                                                                                                                                                                   | Records                                  |
| ------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------- |
| Components                                 | One PostgreSQL server with the pgvector extension; the Python libraries asyncpg and aiosql; the embedding model in the caller; pg_eventserv as an optional relay.                                                                                                       | A1-SR-10, A1-SR-19 to A1-SR-21           |
| Query languages                            | SQL only, kept in `.sql` files by aiosql.                                                                                                                                                                                                                               | A1-SR-05, A1-SR-21                       |
| Consistency boundaries                     | One PostgreSQL transaction covers rows, vectors, index entries and `NOTIFY`. The model run, the relay and the listeners sit outside it, and notifications do not survive a server restart.                                                                              | A1-SR-07, A1-SR-08, A1-SR-10             |
| What must be kept in sync                  | Embeddings with their text and model version, because pgvector recomputes nothing. Outbox rows with the relay's read position.                                                                                                                                          | A1-SR-10, A1-SR-16                       |
| Rebuildable derived data                   | Vector indexes, with `REINDEX`. Embeddings can be recomputed from the text (inferred).                                                                                                                                                                                  | A1-SR-10                                 |
| Release activity, 2024-11-18 to 2026-11-18 | PostgreSQL: one major version a year and minor releases at least every three months. pgvector: seven patch releases. asyncpg: two. aiosql: ten. pg_eventserv: none.                                                                                                     | A1-SR-09, A1-SR-11, A1-SR-19 to A1-SR-21 |
| Project health                             | All four projects are open source and none is archived. pgvector and aiosql each have one maintainer who wrote over 95 percent of the commits since 2024-11-18. asyncpg has 290 open issues and pull requests. pg_eventserv has an open issue on archived dependencies. | A1-SR-11, A1-SR-19 to A1-SR-21           |

## Concept: Recursive Queries With Search and Cycle Detection

1. **SQL:1999 defines `WITH RECURSIVE` and the `SEARCH` and `CYCLE` clauses**, with mandatory cycle mark values (1999-09-01, A1-SR-01). Criticism leading to step 2: gap. No source says why PostgreSQL took only part of it.
2. **PostgreSQL 8.4 implements `WITH RECURSIVE` without `SEARCH` and `CYCLE`**. The manual tells users to detect cycles by hand with an array of visited values (2009-07-01, A1-SR-02). Criticism: Peter Eisentraut writes that the clauses were "never mentioned again" after the first discussion. The hand-written form is what the new syntax shortens (2020-05-20, A1-SR-03).
3. **PostgreSQL adds `SEARCH` and `CYCLE` as a rewrite into the hand-written form** (commit of 2021-02-01, released in 14 on 2021-09-30, A1-SR-04). Criticism leading to step 4: gap. The commit cites a draft of a later standard but no criticism of the mandatory mark values.
4. **The cycle mark values become optional and default to TRUE and FALSE** (2021-02-27, A1-SR-04). This is feature T133 in the current manual (A1-SR-05). No later criticism was found.

The concept has four formulations and one recorded criticism.

## Concept: Transactional Outbox

1. **Chris Richardson's pattern**: the service writes the message to an outbox table in the same transaction, and a relay sends it on by polling or by tailing the log. Its own listed drawbacks are duplicate sends, ordering problems with polling, and database-specific log tailing (2017-01-01, year only, A1-SR-16). Criticism: Gunnar Morling sets log-based change data capture against "any polling-based approach" (2019-02-19, A1-SR-17).
2. **The outbox through change data capture on the PostgreSQL write-ahead log**: the row is inserted and deleted in the same transaction, so the table stays empty and the broker keeps the history (2019-02-19, A1-SR-17). Criticism: the same author names the housekeeping of an outbox table and rows that can be changed by accident (2023-03-06, A1-SR-18).
3. **The outbox as logical decoding messages** written with `pg_logical_emit_message()`, without a table (2023-03-06, A1-SR-18). Criticism after this step: gap. The article only notes that the Debezium router did not yet support it.

The concept has three formulations and two recorded criticisms. For the sketch, step 1 is the relevant form, because the events must stay readable in the database.

## Concept: pgvector Index Types and Filtered Search

1. **IVFFlat is the only index**, to be built after the table has data (2021-04-20, A1-SR-11). Criticism: a user calls search "very slow" and asks for HNSW (2023-07-07, A1-SR-12).
2. **HNSW arrives in 0.5.0** (2023-08-29, A1-SR-12; the changelog says 2023-08-28, A1-SR-11). Criticism: filtered HNSW queries return too few rows, and doing it well "is not straightforward" (2023-09-11, A1-SR-13). Issue #244 on dead tuples, of 2023-08-29, makes the same complaint. The maintainer tried a filtered graph (HQANN) in 2023-11 and did not ship it; no record carries that date.
3. **The plan for iterative scans**: one switch, and the scan continues until enough rows match (2024-09-20, A1-SR-13). Criticism: the maintainer states in the same reply that results "may not be returned in strict order" (2024-09-20, A1-SR-13).
4. **0.8.0 ships iterative scans with two modes**, `strict_order` and `relaxed_order` (2024-10-30, A1-SR-14). No later criticism was recorded; the current README still describes both modes (A1-SR-10).

The concept has four formulations and three recorded criticisms. Steps 3 and 4 rest on one maintainer's statements.

## Gaps

- No source states that a transaction sees its own new vectors through HNSW. The finding is inferred from `hnswinsert.c`, `hnsw.c` and the index interface chapter. A GitHub issue search for "uncommitted" and "same transaction" found only #824 and #1055. Pilot test 1 must check it.
- No source shows a vector search and a recursive traversal with `CYCLE` in one statement (S5).
- No source was searched or found for the "as of date D" query pattern or for temporal constraints in PostgreSQL 18 (S3).
- The PostgreSQL manual states no cost for `CYCLE` path arrays on large graphs.
- The reasons behind SQL:1999 and behind the optional cycle mark values were not found. The 2020 to 2021 thread replies in A1-SR-03 were not read.
- The outbox page by Richardson carries only a year. Earlier uses of the pattern were not traced. The current Debezium outbox router documentation and the manual page for `pg_logical_emit_message` were not read.
- The reason pgvector dropped the HQANN prototype is not stated anywhere found.
- `async.c` of PostgreSQL 19 was not compared with release 18. The repository holds a tag `REL_19_0`, but postgresql.org has not announced 19.0.
- pg_eventserv has no tags or releases, so its release history is commit history only.
- The `gh search` subcommand was missing; searches went through the GitHub API instead.
- The plan excludes benchmarks and vendor performance claims, so no record holds speed, recall or build time figures.
