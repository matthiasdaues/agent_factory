# Survey Report: Postgres And qmd

This report answers [research-brief.json](research-brief.json) in survey mode. It uses only the 36 source records under [sources/](sources/), cited by record ID: 21 records for area 1 with the prefix `A1-SR-`, and 15 records for area 2 with the prefix `A2-SR-`. It reports what the sources document and gives no verdict on whether a concept or design holds. That verdict belongs to a later falsification study. Sections 1 to 5 recommend nothing. Section 6 draws conclusions and is marked as interpretation.

The report compares two options. The first is plain PostgreSQL with pgvector, as sketched in [the proposed store](../knowledge-graph-with-provenance/design-position.md#the-proposed-store). The second is qmd, the local search tool for markdown at https://github.com/tobi/qmd, which the stakeholder confirmed (A2-SR-01, A2-SR-02). "Inferred" means that the records give the parts and no source states the whole.

## 1. Answer

The records support most of the PostgreSQL sketch, but not all of it. One PostgreSQL server with pgvector keeps rows, vectors, and index entries in one transaction and one write-ahead log, and SQL is its only query language (A1-SR-07, A1-SR-10). `NOTIFY` delivers only at commit, and a notification reaches only sessions that listen at that moment (A1-SR-08). An outbox table keeps the events (A1-SR-16). Five statements of the sketch rest on inference. The most important is that a transaction finds its own new vectors through HNSW (A1-SR-10, A1-SR-15). No source shows a vector search and a traversal with `CYCLE` in one statement (A1-SR-05). Append-only tables do not bind the table owner or a superuser (A1-SR-06). The condition for SQL/PGQ is not met, because it was reverted before release 19 (A1-SR-09).

qmd is a search index over markdown files: one SQLite file with full-text search, vectors, and a local model pipeline (A2-SR-02, A2-SR-03). Its schema has no edge table, no decision table, and no append-only log, and it deletes content that no document references (A2-SR-03, A2-SR-04). Its hybrid search pipeline has no counterpart in the sketch. That pipeline combines query expansion, weighted rank fusion, and a reranker (A2-SR-02, A2-SR-08).

On the simplicity facts, both options use one database file or server. The PostgreSQL sketch has one query language. qmd has a line-typed query format and a JSON filter, and its index lags the files until `qmd update` runs (A2-SR-04, A2-SR-08). Section 5 holds the full comparison.

## 2. State of the art by area

### 2.1 Plain PostgreSQL with pgvector, clients, and events

PostgreSQL 18 is the current release, at minor version 18.7 of 2026-11-12. Release 19 is at release candidate 2 (A1-SR-09). A graph fits in ordinary tables. A recursive common table expression walks it, and the `SEARCH` and `CYCLE` clauses add search order and cycle detection (A1-SR-05). Both clauses are a rewrite into the hand-written form with a path array (A1-SR-04, A1-SR-05). The manual states no cost for that path array on large graphs (A1-SR-05).

A `CHECK` constraint may not read other rows. So the manual points to triggers for a check across rows, and a trigger raises an exception to reject a row (A1-SR-06). Missing privileges or raising triggers can block updates and deletes. Row triggers do not fire on `TRUNCATE`, and the table owner and superusers keep their rights (A1-SR-06).

pgvector stores vectors as columns of ordinary tables, and its indexes sit in the same write-ahead log (A1-SR-10). HNSW and IVFFlat are approximate. A filter runs after the index scan, so a selective filter can leave few rows; since 0.8.0, an iterative scan fetches more candidates (A1-SR-10, A1-SR-14). The PostgreSQL core, not the index, decides which rows a snapshot sees (A1-SR-07). HNSW links a new element into its graph during the `INSERT` (A1-SR-10). From these two facts the records infer that a transaction finds its own new vectors through HNSW. No source states this directly (A1-SR-10, A1-SR-15). HNSW and IVFFlat take no predicate locks, and issue #1055 reports two check-then-insert transactions that both commit under `SERIALIZABLE` (A1-SR-10, A1-SR-15).

`NOTIFY` delivers at commit, in commit order, with a payload shorter than 8000 bytes in the default configuration (A1-SR-08). A notification reaches only sessions that listen at that moment, and the queue does not survive a server restart (A1-SR-08). The transactional outbox writes each event to a table in the same transaction, and a relay sends it on (A1-SR-16). pg_eventserv relays `NOTIFY` payloads to WebSocket clients. It keeps no buffer, and nobody has changed its code since 2023-07-14 (A1-SR-19). asyncpg runs a block of statements in one transaction and delivers notifications to a callback (A1-SR-20). aiosql turns SQL files into named Python methods and opens no transaction of its own (A1-SR-21).

### 2.2 qmd and its components

qmd is a command-line tool, a Node.js library, and an MCP server over one SQLite file (A2-SR-12). It indexes markdown files from folders that the user registers as collections, and it answers keyword, vector, and hybrid queries on the local machine (A2-SR-02). The repository is MIT-licensed and was created in December 2025 (A2-SR-01).

All index data sits in one SQLite database, by default `~/.cache/qmd/index.sqlite` (A2-SR-02). Table `content` keys each document body by its hash. Table `documents` maps a collection and a path to a hash and carries an `active` flag (A2-SR-03). An FTS5 table with the `porter unicode61` tokenizer holds the full-text index, and three SQLite triggers keep it in step with `documents` (A2-SR-03). The vectors sit in a sqlite-vec `vec0` table partitioned by collection. Table `vector_rows` maps each vector back to a content chunk (A2-SR-05).

`qmd update` scans the files and writes text and the full-text index. `qmd embed` is a separate step that writes the vectors (A2-SR-03). Each chunk holds about 900 tokens with 15 percent overlap and stores its character position (A2-SR-02). A plain query goes to a fine-tuned local model, which expands it into typed `lex`, `vec`, and `hyde` lines (A2-SR-08). `lex` lines go to BM25 and the other two to vector search. Reciprocal rank fusion (RRF) merges the ranked lists, a local reranker scores the top 30, and a blend by rank band mixes the two scores (A2-SR-02). The three default models run in-process through node-llama-cpp (A2-SR-02).

A re-index skips a file whose modification time and size match the last scan. It writes a new content row when the hash of a changed file differs (A2-SR-04). A vanished or emptied file gets `active = 0`, and a later cleanup hard-deletes such rows and the content that no row references (A2-SR-04). No code detects a rename. So a renamed file becomes a deactivated old path and a new path that reuses content and vectors through the hash (inferred, A2-SR-04). No file watcher exists, so the index changes only when `qmd update` runs (A2-SR-04).

Below the file level, qmd records the chunk sequence number and character position (A2-SR-03). No table records links between documents, citations, or anchors (A2-SR-03). Processors turn non-markdown input into index documents, and table `processor_outputs` records which source file produced which document (A2-SR-07). The five MCP tools only read the index (A2-SR-12).

## 3. Hardened concepts

A hardened concept went through several recorded rounds of formulation, criticism, and reformulation. The histories are in [histories/](histories/). The table below is the output of `concept-history-check --table`, copied unchanged. The script computes counts and ranks from the records.

| Rank | Concept                                  | Area                             | Rounds | Criticisms | Primary anchors | Criticism coverage | Records                                |
| ---- | ---------------------------------------- | -------------------------------- | ------ | ---------- | --------------- | ------------------ | -------------------------------------- |
| 1    | pgvector index types and filtered search | Area 1: PostgreSQL with pgvector | 4      | 3          | 100%            | 100%               | A1-SR-11, A1-SR-12, A1-SR-13, A1-SR-14 |
| 2    | qmd unit and layout of vector storage    | Area 2: qmd                      | 4      | 3          | 100%            | 100%               | A2-SR-11, A2-SR-09, A2-SR-10, A2-SR-02 |
| 3    | Transactional outbox                     | Area 1: PostgreSQL with pgvector | 3      | 2          | 100%            | 100%               | A1-SR-16, A1-SR-17, A1-SR-18           |
| 4    | qmd fusion of ranked lists               | Area 2: qmd                      | 3      | 2          | 100%            | 100%               | A2-SR-09, A2-SR-10                     |
| 5    | qmd query expansion                      | Area 2: qmd                      | 5      | 2          | 100%            | 25%                | A2-SR-09, A2-SR-08, A2-SR-10           |

Below the entry rule (at least 3 formulations and 2 recorded criticisms):

| Rank | Concept                                  | Area                             | Rounds | Criticisms | Primary anchors | Criticism coverage | Records                                |
| ---- | ---------------------------------------- | -------------------------------- | ------ | ---------- | --------------- | ------------------ | -------------------------------------- |
| -    | qmd model runtime                        | Area 2: qmd                      | 2      | 1          | 100%            | 100%               | A2-SR-11, A2-SR-09                     |
| -    | Recursive queries with SEARCH and CYCLE  | Area 1: PostgreSQL with pgvector | 4      | 1          | 100%            | 33%                | A1-SR-01, A1-SR-02, A1-SR-03, A1-SR-04 |
| -    | qmd location of collection configuration | Area 2: qmd                      | 2      | 0          | 100%            | 0%                 | A2-SR-09, A2-SR-03                     |

The histories follow the stakeholder's frame of conjecture and criticism only to sort the steps. Every step and criticism is anchored by a quote from its record. The script requires each date to equal a date of its record. For the qmd changelog records A2-SR-09 and A2-SR-10, that date is mostly 2026-11-17, the commit that was read. The formulation text in each history carries the date of its changelog section.

### 3.1 pgvector index types and filtered search

Release 0.1.0 of 2021 offered IVFFlat as the only approximate index (A1-SR-11). In issue #181, a user called search "very slow" and asked for HNSW. The maintainer announced release 0.5.0 with HNSW in the same thread (A1-SR-12). Issue #259 then reported that filtered HNSW queries return too few rows (A1-SR-13). In that thread, the maintainer planned iterative scans and named their drawback: results may come out of strict order (A1-SR-13). Release 0.8.0 shipped two modes, `strict_order` and `relaxed_order` (A1-SR-14). The drawback is not marked as driving the two modes, because A1-SR-14 does not link them. Steps 3 and 4 rest on one maintainer's statements.

### 3.2 qmd unit and layout of vector storage

The first commit stored one vector per document (A2-SR-11). The changelog then said that one embedding "averages everything together", and release 0.3.0 embedded chunks of about 900 tokens instead (A2-SR-09). Release 2.8.3 fixed small collections "crowded out of the global ANN candidate pool" with an exact scan for collections up to 20,000 rows (A2-SR-10). That fix has no quoted words of its own in the record, so the history does not count it as a step. Release 2.9.0 partitioned the vector table by collection. The same entry says deletes leave holes that every scan still reads, and `qmd cleanup` now repacks the table (A2-SR-02, A2-SR-10). All criticism comes from the project's own changelog.

### 3.3 Transactional outbox

Chris Richardson's pattern writes the event to an outbox table in the same transaction, and a relay polls the table or tails the log (A1-SR-16). Gunnar Morling set log-based change data capture against "any polling-based approach". In his design, the row is inserted and deleted in one transaction, and the broker keeps the history (A1-SR-17). In 2023 the same author named the housekeeping of an outbox table, and rows that can be changed by accident, as faults. He moved the events into logical decoding messages without a table (A1-SR-18). The sketch needs the events to stay readable in the database, so step 1 is the form it uses (A1-SR-16, A1-SR-18).

### 3.4 qmd fusion of ranked lists

Release 0.1.0 merged the BM25 and vector lists with plain RRF (A2-SR-09). Release 0.2.0 gave the original query double weight, because "the user's actual words are a more reliable signal" (A2-SR-09). Release 2.5.0 found that the weight had landed on the first lexical expansion. So it weights each list by query type (A2-SR-10). The README adds a bonus for top ranks and a blend with the reranker score (A2-SR-02). No record dates those two parts, so the history leaves them out. Every step and criticism comes from the project itself.

### 3.5 qmd query expansion

Release 0.6.0 typed the expansions, so each goes to its own backend "instead of sending everything everywhere" (A2-SR-09). Release 0.8.0 replaced the stock expansion model with one fine-tuned by GRPO (A2-SR-09). Release 0.9.0 kept the type on the way to the backends and said this "eliminates ~4 wasted backend calls per query" (A2-SR-09). Release 1.1.0 let the caller write the typed lines directly (A2-SR-08), and 1.1.5 added an intent line (A2-SR-09). In 2.9.0, one reported query ran 23 expansions where 9 were distinct (A2-SR-10). The record does not quote the fix for that, so the history ends at the intent line. The earlier untyped expansion through Ollama has no quoted anchor and is left out.

### 3.6 Concepts below the entry rule

- **qmd model runtime.** qmd first computed embeddings through Ollama and then moved all model work in-process to node-llama-cpp, because Ollama "adds convenience but also a running server dependency" (A2-SR-09, A2-SR-11). The 2.9.0 remote options have no quoted anchor in A2-SR-10, so the history stops at two steps.
- **Recursive queries with `SEARCH` and `CYCLE`.** SQL:1999 defined the clauses (A1-SR-01). PostgreSQL 8.4 left them out (A1-SR-02), and PostgreSQL 14 added them as a rewrite (A1-SR-03, A1-SR-04). Only one criticism is recorded: the clauses were "never mentioned again" after the first discussion (A1-SR-03). The reasons behind SQL:1999 and behind the optional cycle mark values were not found.
- **qmd location of collection configuration.** Configuration moved from SQLite tables into a YAML file, and later a table `store_collections` mirrored the YAML (A2-SR-03, A2-SR-09). The first SQLite form has no quoted anchor in A2-SR-11. The record of the 2.9.0 fix for concurrent config writes paraphrases it and quotes nothing (A2-SR-10). So the history holds two steps and no criticism.

## 4. The store sketch checked

The table checks the twelve statements S1 to S12 from the [survey plan](research-survey-plan.md). Each statement describes PostgreSQL behaviour in the sketch.

| No. | Statement                                                                     | Verdict                                          | Records                      |
| --- | ----------------------------------------------------------------------------- | ------------------------------------------------ | ---------------------------- |
| S1  | One server with pgvector holds graph and vectors; SQL is the only language.   | Supported                                        | A1-SR-05, A1-SR-10           |
| S2  | A trigger rejects an edge with the wrong node kinds, beside a foreign key.    | Inferred, with limits                            | A1-SR-06                     |
| S3  | Edges and decisions are append-only, and "as of date D" is a query.           | Inferred, with limits; no source for "as of"     | A1-SR-06                     |
| S4  | Indexes on `(source_id, type)` and `(target_id, type)` serve both directions. | Inferred                                         | A1-SR-06                     |
| S5  | One statement runs a filtered vector search, then a traversal with `CYCLE`.   | Inferred                                         | A1-SR-05, A1-SR-10           |
| S6  | SQL functions and procedures hold such queries.                               | Supported                                        | A1-SR-07                     |
| S7  | One transaction writes text, vector, and edges and sees its own writes.       | Inferred, with limits                            | A1-SR-07, A1-SR-10, A1-SR-15 |
| S8  | `NOTIFY` fires only when its transaction commits.                             | Supported                                        | A1-SR-08                     |
| S9  | A notification is lost without a listener; an outbox table keeps the events.  | Supported with limits; restart loss inferred     | A1-SR-08, A1-SR-16           |
| S10 | pg_eventserv carries notifications to WebSocket clients.                      | Supported with limits                            | A1-SR-19                     |
| S11 | If PostgreSQL ships SQL/PGQ, the same tables become a property graph.         | Not met                                          | A1-SR-09                     |
| S12 | asyncpg with aiosql runs named queries, one transaction, and listeners.       | Supported with limits; transaction part inferred | A1-SR-20, A1-SR-21           |

The records show these limits:

**The node-kind trigger checks at insert time only (S2).** The manual says a trigger gives "a one-time check against other rows at row insertion", not a lasting guarantee (A1-SR-06). A later change of a node's kind is not checked unless a second trigger on `node` checks it (A1-SR-06).

**Append-only does not bind the owner or a superuser (S3).** Row triggers do not fire on `TRUNCATE`, so a statement trigger or the missing privilege must cover it. The owner's right to change or drop a table cannot be revoked (A1-SR-06). The survey searched no source for the "as of date D" query or for temporal constraints in PostgreSQL 18.

**Own-write visibility through HNSW is inferred, and the result is approximate (S7).** HNSW returns at most `hnsw.ef_search` candidates, and dead or invisible rows use up candidates (A1-SR-10). So a search may miss a new vector even when the snapshot can see it (inferred, A1-SR-10). The maintainer adds that approximate results can differ between runs of the same query (A1-SR-15).

**`SERIALIZABLE` does not protect a check-then-insert on vectors (S7).** HNSW and IVFFlat take no predicate locks (A1-SR-10). Issue #1055 reports two such transactions that both commit, and the maintainer referred it to PostgreSQL core (A1-SR-15).

**A filter after the index scan can return too few rows (S5).** With HNSW and the default `hnsw.ef_search` of 40, a filter that matches 10 percent of rows returns about four rows (A1-SR-10). Iterative scans fetch more, and the relaxed mode gives up strict distance order (A1-SR-14).

**Notifications have no memory (S9, S10).** A new listener skips notifications that committed before it registered, and the queue does not survive a server restart (A1-SR-08). pg_eventserv starts to listen when the first WebSocket client opens a channel. It keeps no buffer, and its listen loop ends on a connection error with no reconnect in the code (inferred, A1-SR-19). Nobody has changed its code since 2023-07-14, and an open issue names archived dependencies (A1-SR-19).

**One transaction needs one connection (S12).** aiosql opens no transaction of its own (A1-SR-21). Given a pool, aiosql runs each call on its own connection and in its own transaction (inferred, A1-SR-21). A listener needs its own connection, because a connection that returns to the pool loses its listeners (A1-SR-20).

**SQL/PGQ is gone from release 19 (S11).** The March 2026 commit declared a property graph over existing tables, like a view. It was reverted on 2026-09-07, and no source gives a date for a new attempt (A1-SR-09).

## 5. The comparison

| Fact                      | PostgreSQL with pgvector (the sketch)                                                                                                                                                                | qmd                                                                                                                                                                                        |
| ------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Components                | One PostgreSQL server with pgvector; asyncpg and aiosql in Python; the embedding model in the caller; pg_eventserv as an optional relay (A1-SR-10, A1-SR-19 to A1-SR-21).                            | Node.js 22 or later; SQLite through better-sqlite3; FTS5; sqlite-vec 0.1.9; node-llama-cpp; three GGUF models; a YAML config file (A2-SR-02, A2-SR-03, A2-SR-12).                          |
| Query languages           | SQL only, kept in `.sql` files by aiosql (A1-SR-05, A1-SR-21).                                                                                                                                       | Line-typed query documents with `lex`, `vec`, `hyde`, and `intent`; a JSON filter tree for metadata; SQL only inside the SQLite file (A2-SR-08).                                           |
| Consistency boundaries    | One transaction covers rows, vectors, index entries, and `NOTIFY`. The model run, the relay, and the listeners sit outside it (A1-SR-07, A1-SR-08, A1-SR-10).                                        | Triggers keep the full-text index in step with `documents` inside SQLite. Vectors come from a separate `qmd embed` step. The index lags the files until `qmd update` (A2-SR-03, A2-SR-04). |
| What must be kept in sync | Embeddings with their text and model version, because pgvector recomputes nothing. Outbox rows with the relay's read position (A1-SR-10, A1-SR-16).                                                  | Files on disk with the index; the YAML config with `store_collections`; vectors with their model, which each vector row records (A2-SR-03, A2-SR-04, A2-SR-10).                            |
| Rebuildable derived data  | Vector indexes, with `REINDEX`. Embeddings from the text (inferred, A1-SR-10).                                                                                                                       | The index is derived from the files and the YAML config; a full rebuild is inferred, and no record names a rebuild command (A2-SR-03, A2-SR-04).                                           |
| Release activity          | PostgreSQL: a major version about once a year. 2024-11-18 to 2026-11-18: pgvector seven patch releases, asyncpg two, aiosql ten, pg_eventserv none (A1-SR-09, A1-SR-11, A1-SR-19 to A1-SR-21).       | 17 npm versions from 0.9.0 (2026-02-15) to 2.9.0 (2026-11-18), with a three-month gap before 2.9.0 (A2-SR-01).                                                                             |
| Project health            | All open source, none archived. pgvector and aiosql each have one maintainer with over 95 percent of recent commits. asyncpg has 290 open issues and pull requests (A1-SR-11, A1-SR-19 to A1-SR-21). | MIT licence; the owner holds 557 of 809 commits; 17 authors since 2026-08-18; 134 open issues and 130 open pull requests; sqlite-vec is pre-v1 (A2-SR-01, A2-SR-13).                       |

### 5.1 What qmd would need to hold the three layers

The design has three layers: provenance, knowledge, and decisions. No source states how qmd would hold any of them, so every statement here is inferred from its schema.

- **Provenance.** qmd keeps the chunk sequence and character position, and `qmd get` reads line ranges (A2-SR-02, A2-SR-03). It has no table for a quoted span with a source, a start, and an end. It deletes content rows once no document references them (A2-SR-04). So qmd would need a span table and a rule that keeps source content.
- **Knowledge.** The schema has no edge table (A2-SR-03). Frontmatter metadata accepts strings, numbers, booleans, and flat arrays, so a document can list target names under a key (A2-SR-02, A2-SR-06). qmd neither resolves such a value to a document nor checks that the target exists (inferred, A2-SR-06). Typed edges with a status, a source span, and validity dates would need a new table.
- **Decisions and history.** The schema has no decision table and no append-only log (A2-SR-03). A document update overwrites its `documents` row, and the metadata rows cascade-delete with their document (A2-SR-04, A2-SR-06). A new table would follow the numbered `PRAGMA user_version` migrations (A2-SR-05).
- **Writes.** The five MCP tools only read (A2-SR-12). Writes go through the files on disk and `qmd update`, or through the library (A2-SR-12). An agent that records an edge or a decision would need a new write path.

### 5.2 What qmd offers that the sketch lacks

The sketch, as written in the design position, names vector search and traversal. It names no keyword search, no query expansion, and no reranker. The area 1 records do not cover PostgreSQL full-text search, so this survey says nothing about it.

- **A hybrid search pipeline.** BM25 over FTS5, typed query expansion by a fine-tuned local model, RRF with weights by query type, a reranker over the top 30, and a blend by rank band (A2-SR-02, A2-SR-08, A2-SR-10).
- **A query format for agents.** A caller can write typed `lex`, `vec`, and `hyde` lines with phrases, negation, and an intent line (A2-SR-08, A2-SR-09).
- **Content addressing.** Vectors attach to the content hash, not the path, so an unchanged body is embedded once (A2-SR-03, A2-SR-04).
- **Change detection.** A re-index skips files by modification time and size and compares hashes (A2-SR-04).
- **Models in-process.** The three default models run inside the process through node-llama-cpp, with no model server (A2-SR-02, A2-SR-09).
- **An MCP server and an HTTP route** for agents (A2-SR-12).

## 6. What this means for the knowledge system

*This section is interpretation. Each point names the findings it rests on.*

**The PostgreSQL sketch fits the settled design. qmd does not, without a new data model.** The settled design keeps provenance, knowledge, and decisions in one store, with decisions as nodes linked to conjectures. An edge enters the graph only after a check or a person confirms it. The sketch has tables for all three and one transaction across them (section 4, S1, S7). qmd has none of the three tables. It has no write path through MCP, and it deletes content that nothing references (section 5.1). The missing parts are the core of the design. Adding them to qmd would turn it into a second store design inside SQLite. It would then face the same append-only and visibility questions as the sketch, on a pre-v1 vector extension (A2-SR-13).

**Parts of qmd's pipeline carry over as ideas, not as code.** The sketch has no answer for keyword queries or ranking. qmd's history records why each part exists: chunking because one vector per document matched poorly, and double weight for the user's own words. Weights by query type came after a weight landed on the wrong list (sections 3.2, 3.4). The query format with typed lines suits agents (A2-SR-08). Content addressing by hash would let the sketch skip re-embedding unchanged text (A2-SR-03). Two cautions apply. All of qmd's reasons come from its own changelog, and no record measures retrieval quality (A2-SR-09, A2-SR-10). The carry-over also needs PostgreSQL full-text search, which this survey did not read.

**Four pilot tests remain decisive, and one more check belongs beside them.**

1. Pilot test 1 rests on the inferred S5 and S7. It should test own-write visibility through HNSW. It should also test what happens when `hnsw.ef_search` or a filter leaves the new vector outside the candidates (A1-SR-10).
2. Pilot test 2 should test a change of a node's kind after the edge exists, not only the insert (A1-SR-06).
3. Pilot test 3 should run as an ordinary role and also try `TRUNCATE`. The owner's rights cannot be revoked, so the role design is part of the test (A1-SR-06).
4. Pilot test 4 should restart the listener and pg_eventserv and then read the outbox. `NOTIFY` keeps nothing for an absent listener (A1-SR-08, A1-SR-19).
5. The extra check: a check-then-insert of similar vectors under `SERIALIZABLE`, because issue #1055 reports that both transactions commit (A1-SR-15). Similarity proposes the candidate edges, so a duplicate candidate is the failure to look for.

**pg_eventserv is the weakest component.** It has had no code change since 2023, it has no releases, and its listen loop does not reconnect (A1-SR-19). asyncpg offers a listener and a callback for a lost connection inside the Python layer (A1-SR-20). Without pg_eventserv, the application would carry events to WebSocket clients itself.

**SQL/PGQ should not shape the schema now.** It was reverted, and no new date exists (A1-SR-09). The sketch's plain tables work without it.

## 7. Structured block

```json
{
  "findings": [
    {
      "title": "One server, one transaction, one query language",
      "summary": "pgvector stores vectors as columns of ordinary tables in the same write-ahead log, and SQL is the query language. One PostgreSQL transaction covers rows, vectors, index entries, and NOTIFY; the embedding model, the relay, and the listeners sit outside it.",
      "source_record_refs": ["A1-SR-05", "A1-SR-07", "A1-SR-08", "A1-SR-10"]
    },
    {
      "title": "Recursive traversal with SEARCH and CYCLE is a rewrite",
      "summary": "PostgreSQL 18 supports WITH RECURSIVE with SEARCH and CYCLE, rewritten into the hand-written form with a path array. The manual states no cost for the path array on large graphs. No source shows a vector search and a recursive traversal in one statement; S5 is inferred from the syntax.",
      "source_record_refs": ["A1-SR-04", "A1-SR-05", "A1-SR-10"]
    },
    {
      "title": "Edge validation and append-only tables need triggers and roles",
      "summary": "A CHECK constraint may not read other rows, so a node-kind check is a trigger, which checks at insert time only. Missing privileges or raising triggers block updates and deletes for ordinary roles, but row triggers miss TRUNCATE and the owner and superusers keep their rights. No source was found for the 'as of date D' query.",
      "source_record_refs": ["A1-SR-06"]
    },
    {
      "title": "Own-write visibility through HNSW is inferred, not stated",
      "summary": "The PostgreSQL core decides visibility, and HNSW links a new element during INSERT, so the records infer that a transaction finds its own new vectors through HNSW. No source states it. HNSW returns at most hnsw.ef_search candidates, and HNSW and IVFFlat take no predicate locks; issue #1055 reports a check-then-insert race under SERIALIZABLE.",
      "source_record_refs": ["A1-SR-07", "A1-SR-10", "A1-SR-15"]
    },
    {
      "title": "Filtered vector search and iterative scans",
      "summary": "With approximate indexes, pgvector filters after the index scan, so a selective filter can return few rows. Since 0.8.0, iterative scans fetch more candidates in a strict-order or a relaxed-order mode.",
      "source_record_refs": ["A1-SR-10", "A1-SR-13", "A1-SR-14"]
    },
    {
      "title": "NOTIFY delivers at commit and keeps nothing for an absent listener",
      "summary": "NOTIFY delivers only after commit, in commit order, with a payload under 8000 bytes by default. A new listener skips earlier notifications, and the queue does not survive a server restart; loss across a listener restart is inferred from async.c. The transactional outbox keeps events in a table written in the same transaction.",
      "source_record_refs": ["A1-SR-08", "A1-SR-16"]
    },
    {
      "title": "Relay and client layer",
      "summary": "pg_eventserv relays NOTIFY payloads to WebSocket clients, keeps no buffer, and has had no code change since 2023-07-14. asyncpg runs statements in one transaction and delivers notifications to a callback on its own connection. aiosql names SQL queries and opens no transaction of its own; given a pool, each call runs in its own transaction (inferred from the adapter).",
      "source_record_refs": ["A1-SR-19", "A1-SR-20", "A1-SR-21"]
    },
    {
      "title": "SQL/PGQ was reverted before PostgreSQL 19",
      "summary": "The March 2026 commit declared a property graph over existing tables like a view, and the revert of 2026-09-07 removed it. No source gives a date for a new attempt, so the condition of S11 is not met.",
      "source_record_refs": ["A1-SR-09"]
    },
    {
      "title": "qmd is a search index over markdown in one SQLite file",
      "summary": "qmd is a command-line tool, a library, and an MCP server over one SQLite file with content-addressed bodies, an FTS5 table kept in step by triggers, and a sqlite-vec vec0 table partitioned by collection.",
      "source_record_refs": ["A2-SR-02", "A2-SR-03", "A2-SR-05", "A2-SR-12"]
    },
    {
      "title": "qmd's hybrid search pipeline",
      "summary": "A fine-tuned local model expands a query into typed lex, vec, and hyde lines routed to BM25 or vector search. RRF with weights by query type merges the lists, a local reranker scores the top 30, and a blend by rank band mixes the scores. The models run in-process through node-llama-cpp.",
      "source_record_refs": ["A2-SR-02", "A2-SR-08", "A2-SR-09", "A2-SR-10"]
    },
    {
      "title": "qmd changes the index only on update and soft-deletes vanished files",
      "summary": "A re-index skips files by modification time and size, writes a new content row when the hash changes, and sets active = 0 for vanished files; a cleanup hard-deletes them and unreferenced content. No watcher and no rename detection exist; the rename outcome is inferred.",
      "source_record_refs": ["A2-SR-04", "A2-SR-10"]
    },
    {
      "title": "qmd holds no edges, decisions, or history",
      "summary": "The schema has no edge, decision, or append-only table, and no table for links between documents. Metadata can list target names as strings, which qmd neither resolves nor checks (inferred). The MCP tools only read. Every statement on what qmd would need is inferred from the schema.",
      "source_record_refs": ["A2-SR-03", "A2-SR-04", "A2-SR-06", "A2-SR-07", "A2-SR-12"]
    },
    {
      "title": "Release activity and project health",
      "summary": "PostgreSQL releases a major version about once a year. From 2024-11-18 to 2026-11-18, pgvector had seven patch releases, asyncpg two, aiosql ten, and pg_eventserv none; pgvector and aiosql each rest on one maintainer. qmd had 17 npm versions from 2026-02-15 to 2026-11-18, the owner holds 557 of 809 commits, and its vector extension sqlite-vec is pre-v1.",
      "source_record_refs": ["A1-SR-09", "A1-SR-11", "A1-SR-19", "A1-SR-20", "A1-SR-21", "A2-SR-01", "A2-SR-13"]
    },
    {
      "title": "Hardened concepts",
      "summary": "Five concepts meet the entry rule: pgvector index types and filtered search, qmd vector storage, the transactional outbox, qmd fusion of ranked lists, and qmd query expansion. concept-history-check computes their rank. All qmd criticism comes from the project's own changelog and README.",
      "source_record_refs": ["A1-SR-11", "A1-SR-12", "A1-SR-13", "A1-SR-14", "A1-SR-16", "A1-SR-17", "A1-SR-18", "A2-SR-02", "A2-SR-08", "A2-SR-09", "A2-SR-10", "A2-SR-11"]
    }
  ],
  "uncertainties": [
    "Statements S2, S3, S4, S5, and S7 are inferred from manual text and source code; no source states them whole.",
    "The loss of notifications across a listener restart, pg_eventserv's missing reconnect, and aiosql's transaction behaviour under a pool are inferred from source code.",
    "The sources conflict on whether sqlite-vec vec0 search is exhaustive: qmd's changelog says ANN candidate pool in 2.8.3 and brute-force scan in 2.9.0, and the sqlite-vec documentation says neither.",
    "The qmd README contradicts itself on the number of query expansions and lists two tables that the code drops.",
    "All design reasons for qmd come from the project's own changelog, README, and code comments; no independent review was found.",
    "Steps 3 and 4 of the pgvector history rest on one maintainer's statements.",
    "Contributor counts for qmd differ by method: 100 from the GitHub API and 105 author names from git log."
  ],
  "evidence_gaps": [
    "No source states that a transaction sees its own new vectors through HNSW.",
    "No source shows a vector search and a recursive traversal with CYCLE in one statement.",
    "No source was searched or found for the 'as of date D' query or for temporal constraints in PostgreSQL 18.",
    "The manual states no cost for CYCLE path arrays on large graphs.",
    "No record covers PostgreSQL full-text search, so the survey cannot say whether the sketch could run qmd's keyword stage.",
    "No source states how qmd would hold typed edges, decisions, or append-only history.",
    "The reasons behind SQL:1999 cycle clauses, the optional cycle mark values, and pgvector's dropped HQANN prototype were not found.",
    "The area 2 index names a per-index lock for qmd embed and a rebuild command qmd embed -f; no area 2 record holds either, so the report does not use them.",
    "No record quotes qmd's 2.9.0 deduplication of expansions, its 2.9.0 remote model options, or its serialised config publishing; these steps are paraphrased only.",
    "The licence status of EmbeddingGemma was not checked against the OSI list."
  ],
  "limitations": [
    "Survey mode: the report states what the sources document and gives no verdict on whether a design holds.",
    "No tool or store was installed, run, or benchmarked; no record holds speed, recall, or build time figures except qmd's own stated call counts.",
    "Source code was read, not run; every behaviour read from code is marked inferred where the record marks it.",
    "Release activity and project health are snapshots of 2026-11-18 from repository data and change with every day.",
    "The 2020 to 2021 thread replies on SEARCH and CYCLE were not read, and async.c of PostgreSQL 19 was not compared with release 18.",
    "concept-history-check requires each date to equal a record date, so most qmd changelog steps carry the commit date 2026-11-17; the formulation text gives the section date.",
    "The plan's survey covers only plain PostgreSQL with pgvector and qmd; the stores of the graph-and-embeddings survey serve as context only."
  ],
  "candidates_for_deeper_falsification_study": [
    "Pilot test 1: within one transaction, a vector search through HNSW followed by a recursive traversal with CYCLE in one statement finds the vector and edges the transaction wrote before. Refuted if the statement fails to find the new vector at default settings, or if the combined statement cannot be written.",
    "Pilot test 2: the node-kind trigger rejects every edge whose ends have the wrong node kinds, including after a node's kind changes. Refuted if any such edge is stored, at insert or after an update of a node.",
    "Pilot test 3: for the application role, no UPDATE, DELETE, or TRUNCATE changes a confirmed edge or a decision, and only a new row replaces it. Refuted if any of the three statements succeeds for that role, or if an as-of query returns a state that differs from the recorded history.",
    "Pilot test 4: a listener learns of every committed idea and of none that rolled back, including after the listener or pg_eventserv restarts, when it reads the outbox. Refuted if a committed event is missed after a restart, or if a rolled-back event is delivered.",
    "Under SERIALIZABLE, two concurrent transactions that check for a similar vector and then insert cannot both commit. Refuted by issue #1055's reported reproduction if it holds against the pilot schema.",
    "A filtered HNSW search with iterative scans returns the requested number of rows for the pilot's most selective filter. Refuted if it returns fewer rows than requested while matching rows exist."
  ]
}
```

## 8. Uncertainties, evidence gaps, and limitations

**Inferred statements.** Five statements of the sketch rest on inference: S2, S3, S4, S5, and S7 (section 4). The most important is S7. No pgvector document and no issue states that a transaction finds its own new vectors through HNSW. The records infer it from the PostgreSQL index interface and the HNSW insert code (A1-SR-07, A1-SR-10, A1-SR-15). Three more behaviours were read from code and are inferred. They are the loss of notifications across a listener restart (A1-SR-08), pg_eventserv's missing reconnect (A1-SR-19), and aiosql's transactions under a pool (A1-SR-21). On the qmd side, the rename outcome and everything qmd would need for the three layers are inferred from the schema (A2-SR-03, A2-SR-04, A2-SR-06).

**Sources that projects wrote about themselves.** All design reasons for qmd come from its own changelog, README, and code comments (A2-SR-09, A2-SR-10). No independent review of any qmd step was found. The pgvector README is the vendor's own text and serves for stated features only (A1-SR-10). Gunnar Morling led the tool he describes (A1-SR-17). The qmd README contradicts itself on the number of expansions and lists two tables that the code drops (A2-SR-02). The sources also conflict on whether sqlite-vec search is exhaustive, and the sqlite-vec documentation does not settle it (A2-SR-10, A2-SR-13).

**Claims of the area 2 index that no record holds.** The index names a per-index lock on `qmd embed`, the command `qmd embed -f`, and Bun as a runtime. No area 2 record holds these facts, so this report does not use them. The record of the 2.9.0 changes to expansion deduplication, remote models, and config publishing paraphrases them without a quote. So the histories leave those steps out.

**Unread material.** The 2020 to 2021 replies in the `SEARCH` and `CYCLE` thread were not read (A1-SR-03). The draft standard behind the optional cycle mark values was not read (A1-SR-04). The current Debezium outbox router documentation and the manual page for `pg_logical_emit_message` were not read (A1-SR-18). `async.c` of release 19 was not compared with release 18 (A1-SR-08). The reason pgvector dropped its HQANN prototype was not found (A1-SR-13). No source covers PostgreSQL full-text search or the "as of date D" query.

**Limits of method.** No tool was installed, run, or benchmarked, so no record holds speed or recall. The only figures are qmd's own call counts and timings (A2-SR-09). Release activity and project health are a snapshot of 2026-11-18 (A1-SR-11, A2-SR-01). The checker requires each history date to equal a record date. So most qmd changelog steps carry the commit date 2026-11-17, and the formulation text carries the section date.
