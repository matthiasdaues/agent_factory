# The Case For A Knowledge Graph With Provenance

This document joins the [design position](design-position.md) and five surveys: the [first](../knowledge-graph-state-of-the-art/survey-report.md) on graph models, the [second](../knowledge-across-sources/survey-report.md) on knowledge across sources, the [third](../graph-and-embeddings/survey-report.md) on graphs with embeddings, the [fourth](../postgres-and-qmd/survey-report.md) on PostgreSQL and the search tool qmd, and the [fifth](../postgres-text-search/survey-report.md) on text search in PostgreSQL. This document adds no research, and no survey gives a verdict on whether a design holds.

The surveys number their records the same way, so [A1-SR-10](../postgres-and-qmd/sources/area-1/A1-SR-10-pgvector-readme-and-source.md) and [A1-SR-10](../postgres-text-search/sources/area-1/A1-SR-10-fts-indexes-limits-generated-columns.md) are two different records. Every record identifier below is therefore a link to its file.

## 1. The decision in brief

People keep knowledge in news, email, chat, and conversation transcripts, where a claim loses its origin and an idea loses its link to the decisions that rest on it. The proposed system is a knowledge graph with provenance in three layers: sources and their quoted spans, conjectures and their tests, and human decisions linked to the conjectures they rest on. A refutation reopens the decisions that rest on the refuted conjecture.

The store is decided: one PostgreSQL server with the vector extension pgvector, the graph in ordinary tables, and the Structured Query Language (SQL) as the only query language (sections 3.5 to 3.7 and 7.1). The Agent Factory is the first tenant, and its own sessions are the pilot.

The stakeholder decides three questions, set out in section 7:

1. Whether one store serves one person or one team.
2. Which candidate design claim gets falsification research first.
3. Which identifier (ID) prefix the records use.

Section 8 describes the pilot that follows.

## 2. The problem

The first round's [internal inventory](sources/internal-inventory.md) shows the loss on the factory's own material. Only 19 of 83 proposals have a Decisions table, and each table numbers its own rows, so `DEC-01` exists 19 times. The twenty decisions on the run lifecycle sit in an untracked handoff, while the proposal says "Open Questions: None".

In one study, up to 75% of Dutch online news articles came from the news agency, much of it verbatim ([A4-SR-04](../knowledge-across-sources/sources/area-4/A4-SR-04-boumans-agency-copy-2018.md)). Without provenance, fifty copies of one report look like fifty sources that agree.

Files in git cannot hold this material ([design position](design-position.md#why-files-in-git-do-not-hold-the-knowledge)). One meeting yields too many ideas for review in a pull request, and graph and similarity queries need a database.

## 3. The proposed system

### 3.1 Three layers

| Layer      | Holds                                                                | Who writes it                  | Where it lives                                              |
| ---------- | -------------------------------------------------------------------- | ------------------------------ | ----------------------------------------------------------- |
| Provenance | Sources and the exact spans quoted from them                         | Import scripts, never edited   | A store outside git, where a record can be deleted for good |
| Knowledge  | Problems, conjectures, criticisms, tests, and their outcomes         | Agents propose, reviewers test | The same store, rebuildable from the sources                |
| Decisions  | Do, won't do, defer, accept, each naming the conjectures it rests on | A person, always               | The same store, as nodes linked to their conjectures        |

The ideas carry the volume, and the decisions carry the authority, which comes from the person who records a decision, not from git. The store never overwrites a decision; a new one replaces an old one and names it. A markdown view can serve review but is never the record ([design position](design-position.md#three-layers)). Copyright and data protection are out of scope.

### 3.2 Claims, ideas, and decisions

The system keeps three units as distinct records:

- A claim is a statement that a source makes about the world. Fact-checking research treats claims as units of their own ([A2-SR-12](../knowledge-across-sources/sources/area-2/A2-SR-12-schlichtkrull-averitec-2023.md)).
- An idea is a conjecture that a person or an agent proposes against a problem. The second survey found no record that treats an idea as a unit of its own ([§ 5](../knowledge-across-sources/survey-report.md#5-what-this-means-for-the-wider-knowledge-system)).
- A decision is a choice that a person makes. Meeting research labels a decision as roles of several utterances: an issue, a proposed resolution, and an agreement ([A3-SR-21](../knowledge-across-sources/sources/area-3/A3-SR-21-fernandez-decisions-multiparty-dialogue-2008.md)). So the system anchors each role to its own utterance.

Claims and ideas are conjectures in the knowledge layer. Every record points to at least one span, which names the source item, the exact quote, the speaker or author, and the time.

### 3.3 The Popperian model

The model uses Popper's terms: problem, conjecture, criticism, and error elimination. The design position sets six rules ([design position](design-position.md#the-popperian-model)):

1. The problem is a node type of its own.
2. Every conjecture states what would refute it. A conjecture without a refutation condition is marked "not testable yet", not discarded.
3. A status describes the history of tests, not truth: conjecture, corroborated, refuted, unresolved, superseded, or withdrawn.
4. Repetition is not support. Merging duplicates raises a mention count, never the corroboration.
5. A refutation is fallible too. It points to the spans it rests on, so anyone can challenge it.
6. A refutation reopens the decisions that rest on the refuted conjecture. This is the error elimination.

### 3.4 How a decision reopens

A decision in this repository reads: "Won't do: one Git ref per ID, because leased pushes on many refs are too slow." When a test refutes the conjecture about speed, the graph flags the decision for review. A person then writes a new decision that names the old one as replaced. The flag is one query from the refuted conjecture to every decision that names it.

### 3.5 The store

The store is one PostgreSQL server with pgvector and two modules that ship with PostgreSQL, `pg_trgm` and `unaccent` ([design position](design-position.md#the-proposed-store)). The graph lives in three ordinary tables:

- `node` holds one row per source, span, problem, conjecture, criticism, test, or decision, with its kind and its language. A claimed relation is a node with two plain edges, so a refutation always targets a node.
- `edge` holds the source, target, type, status, author, evidence span, validity dates, and the time recorded. The status is candidate or confirmed.
- `embedding` holds the node, the model, the model version, and the vector, with a hierarchical navigable small world (HNSW) index. HNSW is an approximate nearest-neighbour index that builds a layered graph ([A2-SR-01](../graph-and-embeddings/sources/area-2/A2-SR-01-pgvector-readme.md)).

The database enforces the rules. A trigger rejects an edge whose ends have the wrong node kinds. It is "a one-time check against other rows at row insertion", so a second trigger on `node` rejects a change of kind that would break an edge. Edges and decisions are append-only: a change ends the old row and writes a new one, so "as of date D" is a query. Withheld privileges and raising triggers enforce this for the application's role. The owner's right to change a table "cannot be granted or revoked", and `TRUNCATE` fires no delete triggers, so the role design is part of the store ([A1-SR-06](../postgres-and-qmd/sources/area-1/A1-SR-06-postgresql-18-manual-constraints-triggers-privileges.md)).

Embeddings only propose candidate edges, and a check or a person confirms them, for reasons the third survey records. Bi-encoders, which embed each text on its own, rank a document and its negation the same as or worse than random ([A3-SR-10](../graph-and-embeddings/sources/area-3/A3-SR-10-weller-nevir-2023.md)). Cosine similarity is symmetric, so it cannot express the direction of entailment ([A3-SR-11](../graph-and-embeddings/sources/area-3/A3-SR-11-vendrov-order-embeddings-2015.md)). A cosine threshold slides from duplicate to related ([A3-SR-19](../graph-and-embeddings/sources/area-3/A3-SR-19-abbas-semdedup-2023.md)). HippoRAG instead adds an edge whenever two vectors pass a threshold ([A1-SR-05](../graph-and-embeddings/sources/area-1/A1-SR-05-gutierrez-hipporag-2024.md)). The records offer two checks. A cross-encoder handled negation best among the tested models ([A3-SR-10](../graph-and-embeddings/sources/area-3/A3-SR-10-weller-nevir-2023.md)), and a natural language inference (NLI) model scores entailment with a direction, but degrades above 200 tokens ([A3-SR-13](../graph-and-embeddings/sources/area-3/A3-SR-13-honovich-true-2022.md)). No record tests either check on candidates from a vector search.

No store recomputes a vector when its text changes. The documentation of pgvector, Neo4j, and Memgraph names no such feature ([A2-SR-01](../graph-and-embeddings/sources/area-2/A2-SR-01-pgvector-readme.md), [A2-SR-08](../graph-and-embeddings/sources/area-2/A2-SR-08-neo4j-vector-indexes.md), [A2-SR-11](../graph-and-embeddings/sources/area-2/A2-SR-11-memgraph-vector-search.md)). So the application computes each vector. A new model's vectors need not compare with the old ones, so the options are one model for the life of the index or a full re-encode ([A3-SR-20](../graph-and-embeddings/sources/area-3/A3-SR-20-yang-murr-2025.md), [A3-SR-21](../graph-and-embeddings/sources/area-3/A3-SR-21-google-gemini-embedding-migration.md)). So each vector carries its model version, and a new model adds rows beside the old ones. The third survey found no record of that practice; qmd follows it ([A2-SR-03](../postgres-and-qmd/sources/area-2/A2-SR-03-qmd-store-schema.md)). A content hash, an idea taken from qmd, lets an import skip re-embedding unchanged text.

One transaction covers rows, vectors, and index entries, because pgvector writes into the same write-ahead log (WAL) as the tables. That a transaction finds its own new vector through HNSW is inferred from the code; no source states it. A filter runs after the index scan, so with the default `hnsw.ef_search` of 40, a filter that matches 10% of rows returns about four rows ([A1-SR-10](../postgres-and-qmd/sources/area-1/A1-SR-10-pgvector-readme-and-source.md)). HNSW takes no predicate locks, and issue #1055 reports two check-then-insert transactions that both commit under `SERIALIZABLE` ([A1-SR-15](../postgres-and-qmd/sources/area-1/A1-SR-15-pgvector-issues-transactions-2025.md)). Pilot tests 1 and 6 check these points.

### 3.6 Search

Search uses only what PostgreSQL ships, so the one transaction boundary holds ([design position](design-position.md#the-search-layer)):

- Full-text search runs over a stored generated `tsvector` column with a Generalized Inverted Index (GIN). A `tsvector` lists the normalised words of a text with their positions. The column picks the `german` or `english` configuration from the node's language.
- `pg_trgm` finds typos and partial names. A trigram is a group of three consecutive characters, and the trigram index also serves `LIKE` and regular expressions ([A1-SR-01](../postgres-text-search/sources/area-1/A1-SR-01-pg-trgm-manual.md)).
- `unaccent` removes diacritics, with a rules file on the server's disk ([A1-SR-05](../postgres-text-search/sources/area-1/A1-SR-05-unaccent-manual-and-sql.md)), and pgvector finds similar nodes.

One statement fuses the keyword ranking and the vector ranking by reciprocal rank fusion (RRF), as the pgvector example shows ([A2-SR-10](../postgres-text-search/sources/area-2/A2-SR-10-pgvector-hybrid-rrf-example.md)). The design weights the rankings by query type, an idea taken from qmd. No record covers reranking inside SQL, so a reranker would run in the Python layer.

With the default `fastupdate` setting, new GIN entries wait in a pending list that every search reads. Its pages go to the WAL, so they commit and roll back with the row. Under `SERIALIZABLE`, `fastupdate` makes every scan lock the whole index, so "you could get a lot of false positives" ([A1-SR-12](../postgres-text-search/sources/area-1/A1-SR-12-gin-pending-list-source-and-commits.md)). Pilot test 7 measures that.

The built-in ranking functions "do not use any global information" ([A1-SR-07](../postgres-text-search/sources/area-1/A1-SR-07-ts-rank-manual-and-source.md)). So `ts_rank` is not BM25 (Best Matching 25), which weighs how rare a term is across the collection. A BM25 extension enters only if the pilot shows that ranking is too weak. Each of the four that the fifth survey found breaks or leaves unstated part of the transaction boundary:

- ParadeDB `pg_search` states atomic writes ([A2-SR-03](../postgres-text-search/sources/area-2/A2-SR-03-paradedb-docs-guarantees-architecture.md)). In its free edition, creating an index stops a physical standby, and an open issue reports index entries without table rows after crash recovery ([A2-SR-06](../postgres-text-search/sources/area-2/A2-SR-06-paradedb-issues-replication-crash-recovery.md)).
- `pg_textsearch` keeps compaction output after a `ROLLBACK`. Multiversion concurrency control (MVCC) shows each transaction its own snapshot of the rows, but the extension's corpus statistics are "not MVCC-filtered" ([A2-SR-01](../postgres-text-search/sources/area-2/A2-SR-01-pg-textsearch-readme-architecture.md)).
- `pgx-bm25` has one release, and a ranked scan can score rows "under the new corpus statistics" within one statement ([A2-SR-09](../postgres-text-search/sources/area-2/A2-SR-09-pgx-bm25-repository.md)).
- VectorChord-bm25 states nothing about rollback or replication and has "only tested against English" ([A2-SR-08](../postgres-text-search/sources/area-2/A2-SR-08-vectorchord-bm25-repository.md)).

The German configuration stems words but does not split compounds: "To split up compound words cannot be done without a dictionary" ([A1-SR-09](../postgres-text-search/sources/area-1/A1-SR-09-snowball-german-and-english-stemmers.md)). Splitting needs Ispell or Hunspell dictionary files. PostgreSQL ships none, so the operator places them on the server's disk ([A1-SR-08](../postgres-text-search/sources/area-1/A1-SR-08-fts-dictionaries-and-configurations.md)). The fifth survey found no evaluation of a German Hunspell dictionary with PostgreSQL. PostgreSQL 19 changes German and English stems, and it changes character classification, for which its notes advise recomputing stored `tsvector` values after `pg_upgrade` ([A1-SR-14](../postgres-text-search/sources/area-1/A1-SR-14-release-notes-8-2-to-19.md)). Release 19 was a release candidate, so its notes may change.

### 3.7 Queries and events

The key query is one statement: a search, then a recursive traversal over `edge`, with the `CYCLE` clause against loops ([A1-SR-05](../postgres-and-qmd/sources/area-1/A1-SR-05-postgresql-18-manual-with-queries.md)). No source shows both in one statement; the fourth survey infers it from the syntax. SQL functions hold such queries, so callers name an operation. A slim Python layer runs them with asyncpg, a PostgreSQL client, and aiosql, which turns SQL files into named Python methods. Given a pool, aiosql would run each call in its own transaction (inferred, [A1-SR-21](../postgres-and-qmd/sources/area-1/A1-SR-21-aiosql-docs-and-repository.md)), so the layer holds one connection inside a transaction for writes. The layer also computes the embeddings.

New ideas raise events. `NOTIFY` delivers only when its transaction commits. A notification reaches only sessions that listen at that moment, and the queue does not survive a server restart ([A1-SR-08](../postgres-and-qmd/sources/area-1/A1-SR-08-postgresql-notify-manual-and-async-source.md)). So an outbox table, written in the same transaction, holds the events, and the notification only wakes the reader. The relay "might publish a message more than once", so readers ignore repeats ([A1-SR-16](../postgres-and-qmd/sources/area-1/A1-SR-16-richardson-transactional-outbox.md)). asyncpg reports a lost connection ([A1-SR-20](../postgres-and-qmd/sources/area-1/A1-SR-20-asyncpg-docs-and-repository.md)), and the layer then reconnects and reads the outbox.

pg_eventserv, a relay from `NOTIFY` to WebSocket clients, is ruled out. Its main branch has had no commit since 2023-07-14, and its code shows no reconnect after a connection error ([A1-SR-19](../postgres-and-qmd/sources/area-1/A1-SR-19-pg-eventserv-repository.md)).

## 4. Sources and their anchors

An anchor is the link from a record to the span it came from. Each source family offers an identifier with its own scope.

| Source family    | Identifier                                 | Unique within      | Thread structure                                           | Records                                                                                                                                                                                                          |
| ---------------- | ------------------------------------------ | ------------------ | ---------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Email            | `Message-ID`, new for each message version | The world, by rule | `In-Reply-To` names the parent, `References` the ancestors | [A3-SR-04](../knowledge-across-sources/sources/area-3/A3-SR-04-rfc2822-internet-message-format-2001.md), [A3-SR-05](../knowledge-across-sources/sources/area-3/A3-SR-05-rfc5322-internet-message-format-2008.md) |
| Slack            | `ts`, which looks like a time but is an ID | One channel        | One level, keyed by `thread_ts`                            | [A3-SR-14](../knowledge-across-sources/sources/area-3/A3-SR-14-slack-dev-retrieving-messages.md)                                                                                                                 |
| Factory sessions | `uuid` per message, with `sessionId`       | Not stated         | `parentUuid` names the parent message                      | [design position](design-position.md#the-store-already-half-exists)                                                                                                                                              |

One developer's survey of 22,950 messages found free text in `In-Reply-To` and contradictory `References` ([A3-SR-06](../knowledge-across-sources/sources/area-3/A3-SR-06-jwz-message-threading-1997-2002.md)). The threading standard of the Internet Message Access Protocol (IMAP) falls back on the first valid `Message-ID` in `In-Reply-To` ([A3-SR-07](../knowledge-across-sources/sources/area-3/A3-SR-07-rfc5256-imap-sort-thread-2008.md)). So an import must tolerate missing and contradictory parents. A chat anchor stores the identifier with its scope, and factory sessions need repeated copies removed first.

News has only an anchor in the text: a Text Quote Selector quotes the passage and the words around it ([A1-SR-18](../knowledge-across-sources/sources/area-1/A1-SR-18-w3c-web-annotation-data-model-2017.md)).

The second survey ranks concepts by how often each was formulated, criticized, and reformulated; a rank does not say whether a concept holds. In its [table](../knowledge-across-sources/survey-report.md#3-hardened-concepts), "In-Reply-To and References" ranks first with 3 rounds and 3 criticisms, and "The Message-ID rule" ranks fourth with 5 rounds and 2 criticisms.

## 5. Propagation

A wire report and fifty outlets that repeat it are 51 sources: the report is the primary source of the claim, and each outlet is a source of what it did with it ([design position](design-position.md#the-propagation-model)). No recorded source has one scheme with the four reuse classes below; the closest is a claim provenance graph whose authors state that they have not solved the problem ([A4-SR-15](../knowledge-across-sources/sources/area-4/A4-SR-15-zhang-claim-provenance-2020.md)).

| Class       | A recorded method shows                     | The second survey found no method that shows       | Who sets the edge                     |
| ----------- | ------------------------------------------- | -------------------------------------------------- | ------------------------------------- |
| Verbatim    | Shared wording and its share                | Who copied from whom, or a shared upstream source  | A script checks the overlap           |
| Altered     | Changed meaning, scored without a direction | An automatic score with the direction of change    | A script scores it, without direction |
| Reframed    | A frame or stance label for one text        | A frame change between a source and another outlet | A person, as an attributed judgement  |
| Independent | That no reuse was found                     | Independence from an undisclosed shared source     | A person or a disclosed source        |

A shared press release produces the same overlap as direct copying ([A4-SR-04](../knowledge-across-sources/sources/area-4/A4-SR-04-boumans-agency-copy-2018.md)). So the system records "no reuse found", and only a person or a disclosed source turns it into "independent". Every edge beyond a script's check is a judgement with its author, label scheme, and spans, and the store holds it as a node (section 3.5).

## 6. What the field has settled for the graph

The Resource Description Framework (RDF) is the data model of the World Wide Web Consortium (W3C) that describes data as triples. In the first survey's [table](../knowledge-graph-state-of-the-art/survey-report.md#3-hardened-concepts), "Nanopublication structure and identity" ranks first with 5 rounds and 3 criticisms.

A nanopublication splits one claim into its assertion, its provenance, and information about the publication, with no links between claims ([A3-SR-10](../knowledge-graph-state-of-the-art/sources/area-3/A3-SR-10-nanopublication-guidelines.md)). The Argument Interchange Format (AIF) supplies those links, with a conflict node for a criticism ([A3-SR-14](../knowledge-graph-state-of-the-art/sources/area-3/A3-SR-14-chesnevar-towards-an-argument-interchange-format.md)).

The Web Ontology Language (OWL) defines `owl:sameAs` as strict identity, and merging two profiles of one person let a reasoner infer a job the person never held ([A5-SR-03](../knowledge-graph-state-of-the-art/sources/area-5/A5-SR-03-ding-sameas-empirical-2010.md)). So a merge of two claims must not pass a status or a decision from one to the other.

A record check needs the closed-world assumption, so that a conjecture without a span fails. The Shapes Constraint Language (SHACL) treats the data as complete ([A4-SR-14](../knowledge-graph-state-of-the-art/sources/area-4/A4-SR-14-oudshoorn-shacl-ontologies-2026.md)) and became a W3C Recommendation in 2017 ([A4-SR-11](../knowledge-graph-state-of-the-art/sources/area-4/A4-SR-11-shacl-recommendation-2017.md)). It leaves the meaning of recursive shapes to each implementation ([A4-SR-16](../knowledge-graph-state-of-the-art/sources/area-4/A4-SR-16-shacl12-core-working-draft-2026.md)), so the record rules stay non-recursive. The W3C published the PROV family of provenance standards in 2013, with the PROV Ontology (PROV-O) among its Recommendations ([A3-SR-03](../knowledge-graph-state-of-the-art/sources/area-3/A3-SR-03-prov-overview.md)).

RDF needs an extra node or a named graph to annotate an edge, and a property graph carries key-value pairs on it. RDF 1.2 adds the triple term, a triple used inside another triple, and is still a draft ([A1-SR-01](../knowledge-graph-state-of-the-art/sources/area-1/A1-SR-01-rdf12-concepts.md)).

## 7. Decisions

### 7.1 The store: PostgreSQL with pgvector

This choice is settled (section 3.5). The third survey compared six designs that hold a graph and vectors; these columns come from its [table](../graph-and-embeddings/survey-report.md#4-the-store-comparison):

| Design                                  | Transaction boundary                                                 | A recorded risk                                                                                                                                       |
| --------------------------------------- | -------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| PostgreSQL with Apache AGE and pgvector | One, with two extensions and two query languages                     | No AGE manual page covers pgvector ([A2-SR-05](../graph-and-embeddings/sources/area-2/A2-SR-05-age-pgvector-interop.md))                              |
| Neo4j                                   | One, but the index does not see changes of the same transaction      | Native vector properties need Enterprise Edition or Aura ([A2-SR-08](../graph-and-embeddings/sources/area-2/A2-SR-08-neo4j-vector-indexes.md))        |
| Memgraph                                | The vector index reads uncommitted data                              | Deleting vertices does not free index memory ([A2-SR-11](../graph-and-embeddings/sources/area-2/A2-SR-11-memgraph-vector-search.md))                  |
| FalkorDB                                | One query is atomic; several need Redis `MULTI`/`EXEC`               | Vector queries have no filter support ([A2-SR-13](../graph-and-embeddings/sources/area-2/A2-SR-13-falkordb-vector-and-concurrency.md))                |
| DuckDB with DuckPGQ and vss             | Not found                                                            | The documentation advises against persistent vector indexes in production ([A2-SR-15](../graph-and-embeddings/sources/area-2/A2-SR-15-duckdb-vss.md)) |
| Neo4j beside Qdrant                     | Two; a Qdrant write is eventually consistent unless the client waits | The record shows no way to commit both writes together ([A2-SR-17](../graph-and-embeddings/sources/area-2/A2-SR-17-qdrant-consistency.md))            |

The third survey read Neo4j as the design with the fewest parts among those with one boundary ([§ 6](../graph-and-embeddings/survey-report.md#6-what-this-means-for-the-knowledge-system)). It did not compare PostgreSQL without AGE, and no survey compared that design with Neo4j directly. The fourth survey checked plain PostgreSQL in twelve statements and found five inferred, not stated ([§ 4](../postgres-and-qmd/survey-report.md#4-the-store-sketch-checked)).

Plain PostgreSQL with pgvector has the fewest moving parts for this design, for four reasons:

1. It has one server, one extension for vectors, and SQL as the only query language ([A1-SR-10](../postgres-and-qmd/sources/area-1/A1-SR-10-pgvector-readme-and-source.md)). AGE adds a second extension and a second language, and casts each vector through text ([A2-SR-05](../graph-and-embeddings/sources/area-2/A2-SR-05-age-pgvector-interop.md)).
2. One transaction covers rows, vectors, index entries, and `NOTIFY` (sections 3.5 and 3.7). Neo4j's index does not see changes of the same transaction ([A2-SR-08](../graph-and-embeddings/sources/area-2/A2-SR-08-neo4j-vector-indexes.md)), so a check inside the writing transaction cannot search the new vector.
3. Keyword, fuzzy, and vector search run in the same server (section 3.6).
4. The rules map onto triggers, privileges, and recursive queries that the PostgreSQL manual documents ([A1-SR-06](../postgres-and-qmd/sources/area-1/A1-SR-06-postgresql-18-manual-constraints-triggers-privileges.md)).

SQL Property Graph Queries (SQL/PGQ), the graph part of the SQL standard, does not shape the schema. PostgreSQL carried it on its development branch from March to September 2026 and reverted it before release 19. The Release Management Team named design issues that "can render the graph undumpable/unrestorable" ([A2-SR-07](../graph-and-embeddings/sources/area-2/A2-SR-07-postgresql-sqlpgq-revert.md)). No source gives a date for a new attempt ([A1-SR-09](../postgres-and-qmd/sources/area-1/A1-SR-09-postgresql-release-state-and-sqlpgq-2026.md)).

The fourth survey also compared qmd, a search index over markdown files in one SQLite file ([A2-SR-02](../postgres-and-qmd/sources/area-2/A2-SR-02-qmd-readme.md)). Its schema has no edge table, no decision table, and no append-only log ([A2-SR-03](../postgres-and-qmd/sources/area-2/A2-SR-03-qmd-store-schema.md)). It deletes content that no document references ([A2-SR-04](../postgres-and-qmd/sources/area-2/A2-SR-04-qmd-reindex.md)), and its agent tools only read ([A2-SR-12](../postgres-and-qmd/sources/area-2/A2-SR-12-qmd-mcp-server.md)). So qmd cannot hold the three layers without a new data model. The store takes two ideas from it: the content hash and weights by query type. No record measures its retrieval quality ([§ 6](../postgres-and-qmd/survey-report.md#6-what-this-means-for-the-knowledge-system)).

Each survey ranks the store's parts by the rule of section 4, and a rank holds only within its survey. These rows are copied from the [third](../graph-and-embeddings/survey-report.md#3-hardened-concepts), [fourth](../postgres-and-qmd/survey-report.md#3-hardened-concepts), and [fifth](../postgres-text-search/survey-report.md#3-hardened-concepts) tables:

| Survey | Rank | Concept                                  | Rounds | Criticisms |
| ------ | ---- | ---------------------------------------- | ------ | ---------- |
| Third  | 3    | Filtered vector search                   | 3      | 3          |
| Fourth | 1    | pgvector index types and filtered search | 4      | 3          |
| Fourth | 3    | Transactional outbox                     | 3      | 2          |
| Fifth  | 4    | GIN write path                           | 4      | 3          |
| Fifth  | 5    | Rank fusion                              | 4      | 2          |

What would change the choice:

- RDF stays the alternative where records must be exchanged with outside parties, because PROV-O and SHACL are W3C Recommendations built on RDF, or once RDF 1.2 becomes one.
- A failed pilot test on own-write visibility, rollback, the type trigger, or the role design (tests 1 to 4) reopens the store.
- A released SQL/PGQ would add a graph query language over the same tables. No source schedules one.

The choice fixes the schema and the import format of the pilot.

### 7.2 One store per person or per team

The wider scope rules out a store per repository, because a chat thread is not about one repository.

- Case: A Slack thread in the team channel discusses the counter rule of this repository. One team member's mailbox holds a newsletter on graph databases.
- Outcome with a store per person: Each member who imports the thread holds a copy, so joining copies needs entity resolution across stores. The newsletter raises no access question.
- Outcome with a store per team: The thread and its ideas exist once. Each record needs an owner and a read rule, because the newsletter came from one person's mailbox.
- Recommendation: Start the pilot with one store per person, and let each project write back only the decisions that concern it. The factory's transcripts already sit in each person's checkout, so the pilot needs no access rules.
- What would change it: If the pilot shows that most ideas come from team channels and team meetings, a team store avoids the copies. Its read rules would rest on row security, which `TRUNCATE` and superusers bypass ([A1-SR-06](../postgres-and-qmd/sources/area-1/A1-SR-06-postgresql-18-manual-constraints-triggers-privileges.md)), and which no survey tested for this use.
- What the answer settles: Where the server runs, and whether the proposal includes access rules.

### 7.3 Which candidate claim gets falsification research first

The first survey states nine candidate claims ([§ 7](../knowledge-graph-state-of-the-art/survey-report.md#7-structured-block)), and so does the second ([§ 6](../knowledge-across-sources/survey-report.md#6-structured-block)). These four bear most on the pilot:

| Survey | No. | Claim in short                                                                                                  |
| ------ | --- | --------------------------------------------------------------------------------------------------------------- |
| Second | 6   | Transcript decisions can be extracted as issue, proposal, and agreement, each anchored to an existing utterance |
| First  | 8   | Extraction by a large language model (LLM) yields quotes that occur verbatim in the source                      |
| Second | 4   | Email threads can be rebuilt from `Message-ID`, `In-Reply-To`, and `References` alone                           |
| Second | 1   | A script can record a verbatim reuse edge by text overlap alone, without human review                           |

The third survey adds a claim that bears on every candidate edge: a cross-encoder or NLI check rejects negated and reverse-entailment pairs that a cosine threshold accepts, on the system's own claim pairs ([§ 7](../graph-and-embeddings/survey-report.md#7-structured-block)).

- Case: The pilot imports the session behind the run-lifecycle handoff, whose twenty decisions are already listed.
- Outcomes: Second-survey claim 6 tests extraction against that known list and checks every anchor. First-survey claim 8 checks only the quotes. The third-survey check needs candidate pairs from the pilot. Claims 4 and 1 need email or news.
- Recommendation: Test second-survey claim 6 first, then first-survey claim 8, then the third-survey check. The handoff gives the first test a known answer.
- What would change it: If news becomes the second source family, second-survey claim 1 moves to second place.
- What the answer settles: The brief of the first falsification study.

### 7.4 The ID prefix for records

- Case: A record named `IDEA-0042` appears next to the architecture decision record (ADR) [ADR-0017](../../adr/0017-cycle-based-orchestration-supersedes-linear-playbook-fsm.md), which defines an IDEA delivery cycle.
- Outcomes: With `IDEA`, the reader cannot tell record from cycle. `CONCEPT` collides with the CONCEPT cycle of [ADR-0018](../../adr/0018-concept-internal-sequence-is-agent-owned.md). `NOTION` and `KI` (knowledge item) collide with neither ([synthesis](synthesis.md#decisions-for-the-stakeholder)).
- Recommendation: Decide after stage 1, which needs no production IDs. Then choose `NOTION`, because a reader understands it without looking it up. The proposal must also settle whether store IDs use the factory counter.
- What would change it: If claims and ideas get separate prefixes, a narrower name for each fits better.
- What the answer settles: The ID prefix registry entry, which changes together with the ID allocator ([process design](sources/codex-process-design.md#fit-with-factory-constraints)).

## 8. Next step: the pilot

The stakeholder has not yet approved the pilot ([design position](design-position.md#the-spike)). It runs in two stages.

### 8.1 Stage 1: factory sessions

- What it builds: An import of a few sessions from `usage/transcripts/`, starting with the session behind the run-lifecycle handoff of 2026-11-16. It removes repeated copies, extracts ideas and decisions with message anchors, and loads them into a PostgreSQL database outside git, in the schema of section 3.5.
- What it shows: A session asks "What was decided about the run lifecycle?" The answer finds the twenty decisions of the handoff, each with a message that exists.
- What counts as failure: A decision is missing, or an anchor points to no message.

The pilot also runs the nine tests of the [design position](design-position.md#tests-for-the-pilot).

1. A search followed by a traversal runs as one statement in one transaction. A row written earlier in that transaction is found through the HNSW index and through the GIN index. The test also covers a new vector that `hnsw.ef_search` or a filter leaves outside the candidates.
2. After `ROLLBACK`, no keyword or vector query finds the rolled-back row.
3. The type trigger rejects every edge whose ends have the wrong node kinds, also after a node's kind changes.
4. No update, delete, or `TRUNCATE` by the application's role changes a confirmed edge or a decision; only a new row replaces it.
5. An event reaches a listener for every committed idea and for none that was rolled back, also after the listener restarts and reads the outbox.
6. Two transactions that each check for a similar vector and then insert, under `SERIALIZABLE`, do not both commit a duplicate candidate.
7. Under `SERIALIZABLE`, serialization failures differ with the GIN `fastupdate` setting on and off, by an amount the test records.
8. A German sample corpus shows which compound queries miss without Hunspell.
9. A `pg_upgrade` from 18 to 19 shows which stored `tsvector` values change.

### 8.2 Stage 2: one email mailbox

Email is the recommended second family, because its anchors rank high in section 4. Slack exports lose thread structure ([A3-SR-13](../knowledge-across-sources/sources/area-3/A3-SR-13-slack-help-data-exports.md)), and news needs a person for most propagation edges.

- What it builds: An import of one mailbox that stores each message with its `Message-ID`, rebuilds threads from `In-Reply-To` and `References`, and anchors claims and decisions to quoted spans.
- What it shows: Whether second-survey claim 4 holds for the system's own mail.
- What counts as failure: More replies than a share set before the test lack a resolvable parent or carry contradictory `References`.

## 9. Limitations

- The factory's gates read files in git, so checks on the store must run as queries, with the same query command in every command-line interface (CLI) ([design position](design-position.md#costs)).
- Decisions cannot be rebuilt from the sources, so the store needs a backup and an export of its decision history that nothing can rewrite. It also needs its own approved proposal.
- No survey installed or ran a store. Own-write visibility through HNSW and through GIN is inferred from code.
- No record measures retrieval quality for `ts_rank`, BM25, or any fusion on a corpus like the store's, or how accurately a current LLM extracts ideas.
- The third survey failed its first validation pass on one blocking defect and passed the [second](../graph-and-embeddings/survey-validation-pass-2.md). The fourth and fifth passed at once, with minor corrections. The first and second surveys were accepted with open points from their last passes ([pass 5](../knowledge-graph-state-of-the-art/survey-validation-pass-5.md#notes-for-the-stakeholder), [pass 3](../knowledge-across-sources/survey-validation-pass-3.md)).

## 10. Glossary

- ADR (architecture decision record). A factory file that records one settled architecture choice. ADR-0017 and ADR-0018 matter for the ID prefix.
- AIF (Argument Interchange Format). A model of arguments with claim nodes and nodes for inference, preference, and conflict. It is the documented model for linking a criticism to a conjecture.
- aiosql. A Python library that turns SQL files into named Python methods. It opens no transaction of its own.
- Anchor. The link from a record to the span it came from. Each anchor stores the source's identifier together with its scope.
- Apache AGE. A PostgreSQL extension that stores a graph in tables and adds a second query language. The third survey records its health problems.
- Append-only. A table whose rows are never changed or deleted; a change ends the old row and writes a new one.
- asyncpg. A Python client for PostgreSQL. The store's Python layer uses it for transactions and for listening to `NOTIFY`.
- BM25 (Best Matching 25). A ranking formula that weighs how often a term occurs in a document, the document's length, and how rare the term is across the collection. PostgreSQL's built-in ranking does not compute it.
- Bi-encoder. A model that embeds each text on its own, so two texts are compared by the distance of their vectors.
- Claim. A statement that a source makes about the world, such as a figure in a wire report. The system stores it as a conjecture in the knowledge layer.
- CLI (command-line interface). One of the agent tools the factory runs in, such as Claude Code or Codex.
- Closed-world assumption. The reading that treats the data as complete, so a missing fact counts as false. A record check needs it, because a missing span must fail.
- Conjecture. A proposed answer to a problem, kept open to refutation. Every claim and idea in the graph stays one.
- Corroborated. The status of a conjecture that passed stated tests, recorded with their severity. It never means true.
- Cosine similarity. A measure of how close two vectors point. It is symmetric, so it cannot show which text entails which.
- Cross-encoder. A model that reads two texts together and scores their relation. It handled negation best in one benchmark.
- `CYCLE`. A clause of a recursive SQL query that stops the walk when it returns to a row it has visited.
- DuckDB. An embedded analytical database. One design the third survey compared combines it with the extensions DuckPGQ and vss.
- Embedding. A vector that a model computes from a text, so that similar texts lie close together.
- Entailment. A relation in which one statement supports another. A textual entailment model labels such relations between sentences automatically.
- Entity resolution. Deciding which records describe the same thing. Merging duplicate claims or ideas is a case of it.
- Error elimination. The step that removes a refuted conjecture from use. Here it marks the conjecture refuted and flags every decision that rests on it.
- Falsification research. Research that tries to refute a claim with tests defined in advance. The surveys' candidate claims are its input.
- `fastupdate`. The GIN setting that puts new entries in a pending list before they reach the main index. It is on by default.
- GIN (Generalized Inverted Index). The preferred PostgreSQL index for full-text search. It also serves trigram searches.
- HNSW (hierarchical navigable small world). An approximate nearest-neighbour index that builds a layered graph of vectors. pgvector offers it.
- Hunspell. A dictionary format that PostgreSQL can use to split compound words. PostgreSQL ships no such files.
- ID (identifier). A key that names one record.
- IMAP (Internet Message Access Protocol). The protocol mail clients use to read mail on a server. Its threading standard rebuilds email threads from headers.
- `In-Reply-To`. The email header that names the parent of a reply by its `Message-ID`. Mail software often filled it with free text.
- KI (knowledge item). A candidate ID prefix for records, beside `NOTION`.
- LLM (large language model). A model that generates text, as the factory's agents do. No record measures how accurately one extracts ideas.
- `Message-ID`. The email header that names one version of one message. It must be globally unique.
- MVCC (multiversion concurrency control). The way PostgreSQL shows each transaction its own snapshot of the rows.
- Nanopublication. A small published claim split into assertion, provenance, and publication information. It is the documented pattern for one claim per record.
- NLI (natural language inference). The task of deciding whether one text entails another. An NLI model gives the relation a direction.
- `NOTIFY`. The PostgreSQL command that sends a message to listening sessions when its transaction commits.
- Outbox. A table that a transaction writes its events into, so a reader can fetch them after the commit, also after a restart.
- OWL (Web Ontology Language). A W3C language for describing concepts and inferring facts. Its axioms do not act as record checks.
- `owl:sameAs`. The OWL property that states two names mean the same thing. Its misuse shows why "same claim" must not mean strict identity.
- pg_eventserv. A relay from `NOTIFY` to WebSocket clients. The store does not use it.
- `pg_trgm`. The PostgreSQL module for trigram similarity and its indexes.
- pgvector. The PostgreSQL extension that adds a vector column type and approximate indexes such as HNSW.
- Property graph. A graph model whose nodes and edges carry key-value pairs. The store holds one in ordinary tables.
- PROV. The W3C family of provenance standards from 2013. Its relations include `wasDerivedFrom` and `wasAttributedTo`.
- PROV-O (PROV Ontology). The PROV standard that maps PROV to RDF. It has been a Recommendation since 2013.
- Provenance. The link from a piece of information back to its source and how it came to be.
- qmd. A local search tool that indexes markdown files in one SQLite file. It holds no edges, decisions, or history.
- RDF (Resource Description Framework). The W3C data model that describes data as triples. It is the alternative where records must be exchanged with outside parties.
- Recursive shape. A shape that refers to itself through other shapes. SHACL leaves its meaning open, so record rules avoid it.
- `References`. The email header that lists the ancestors of a reply, oldest first.
- Refutation condition. The observation that would show a conjecture wrong. A conjecture without one is "not testable yet".
- RRF (reciprocal rank fusion). A way to merge rankings that scores each item by the sum of 1 / (60 + rank) over the rankings.
- `SERIALIZABLE`. The strictest PostgreSQL isolation level. It aborts transactions whose combined effect no serial order could produce.
- SHACL (Shapes Constraint Language). The W3C standard shape language from 2017. It is the documented way to check RDF data.
- Shape. A rule set that data must meet, such as "every conjecture has a span".
- Span. An exact passage of a source, with its item, speaker or author, and time. Every record points to at least one.
- SQL (Structured Query Language). The standard language for relational databases and the store's only query language.
- SQL/PGQ (SQL Property Graph Queries). The part of the SQL standard that queries property graphs. PostgreSQL reverted its implementation before release 19.
- Text Quote Selector. A W3C annotation part that points into a document by quoting the passage and the words around it.
- Trigger. A function that the database runs when a row is written. The store uses triggers to reject wrong edges and changes.
- Trigram. A group of three consecutive characters. `pg_trgm` compares strings by the trigrams they share.
- `ts`. The Slack message ID. It looks like a time but is unique only within one channel.
- `ts_rank`. PostgreSQL's built-in ranking function for full-text search. It reads one document's `tsvector` and no collection statistics.
- `tsvector`. The PostgreSQL type that lists the normalised words of a text with their positions.
- `unaccent`. The PostgreSQL module that removes diacritics from words.
- W3C (World Wide Web Consortium). The body that sets web standards. Its stages run from Working Draft to Candidate Recommendation Draft to Recommendation, the final standard.
- WAL (write-ahead log). The log in which PostgreSQL records every change before it applies it. Replication and crash recovery read it.
