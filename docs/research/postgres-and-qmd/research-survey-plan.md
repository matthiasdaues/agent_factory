# Research Survey Plan — Postgres And qmd

The plan follows [research-brief.json](research-brief.json). It splits the survey by the two scope areas of the brief, so no two assignments research the same component. Both assignments run in parallel as one wave.

## Research Questions

1. Area 1: How does plain PostgreSQL hold a graph in ordinary tables: adjacency tables, recursive common table expressions with the `SEARCH` and `CYCLE` clauses, constraints and triggers that validate edges, and append-only tables?
2. Area 1: How do the pgvector indexes HNSW and IVFFlat behave under PostgreSQL transactions and MVCC, does a transaction see its own new vectors, and how do filtered vector search and iterative index scans work?
3. Area 1: What do `LISTEN` and `NOTIFY` guarantee on delivery at commit, payload size, and loss without a listener, and how do the transactional outbox pattern, a relay such as pg_eventserv, and the client layer asyncpg with aiosql fit around them?
4. Area 1: Which statements of [the proposed store](../knowledge-graph-with-provenance/design-position.md#the-proposed-store) on PostgreSQL behaviour do the sources support, which do they contradict, and which do they leave open?
5. Area 2: Which tool does the stakeholder mean by qmd, and what are its purpose, data model, storage engine, indexing and search pipeline for full-text search, vector search, and reranking, and its interfaces?
6. Area 2: How does qmd handle changed and deleted files, does it record links, sources, or provenance below the file level, and what would it need to hold edges, decisions, and append-only history?
7. Both areas: How do PostgreSQL with pgvector and qmd compare on the simplicity facts of the graph-and-embeddings survey: components, query languages, consistency boundaries, what must be kept in sync, rebuildable derived data, release activity, and project health?
8. Both areas: Which concepts went through several documented rounds of formulation, criticism, and reformulation, and what criticism drove each change?

## Search Angles

- The PostgreSQL manual for the current release as of November 2026, for stated behaviour and syntax
- PostgreSQL source code, cited by file and commit, where the manual does not state a behaviour
- PostgreSQL mailing list threads and commitfest entries, for the history of a feature and for SQL/PGQ status
- The pgvector repository: README, changelog, source code, and issues on transactions, MVCC, and filtering
- Project repositories, release notes, and changelogs of pg_eventserv, asyncpg, aiosql, and qmd, for features, release activity, and project health
- The qmd repository and the repositories of every component qmd names as a dependency
- Descriptions of the transactional outbox pattern by the people who named it, and their later criticism
- The SQL:1999 standard and its secondary descriptions, only for the history of recursive queries

## Source Targets

- PostgreSQL manual chapters on `WITH` queries (including `SEARCH` and `CYCLE`), triggers, constraints, row-level security and privileges, MVCC and transaction isolation, `LISTEN` and `NOTIFY`, SQL functions and procedures, and `jsonb`
- PostgreSQL source files for `NOTIFY` delivery (`src/backend/commands/async.c`) and for any other behaviour the manual does not state
- PostgreSQL release notes and commitfest entries for `SEARCH` and `CYCLE` (release 14) and for SQL/PGQ
- The pgvector repository: README sections on HNSW, IVFFlat, filtering, and iterative index scans, `CHANGELOG.md`, and the index access method source
- The pg_eventserv repository and its release notes
- The asyncpg repository and documentation, including its listener API, and the aiosql repository and documentation
- Outbox pattern sources, such as the transactional outbox description by Chris Richardson and the Debezium outbox documentation
- The qmd repository the stakeholder means, its README, source code, release notes, and issues, and the repositories of the storage engine, search extensions, model runtime, and models it names

## Assignments

Each assignment declares agent, tier, independent session, a unique output, and a bounded task. The output is a record folder, an ID prefix, and one area index beside the folder, as [source-research](../../../packages/factory/skills/source-research/SKILL.md#record-file) defines. Every task carries the same six requirements:

- Aim for 10 to 15 records.
- Put the source's own words in straight double quotes in the Evidence section, because `concept-history-check` anchors only on quoted words. When the quoted words hold quotation marks of their own, quote the whole passage from its opening mark to its closing mark.
- Mark each source primary or secondary, and state what it shows and what it does not show.
- Cite source code by file and commit where the documentation is silent. Mark each behaviour that the record infers instead of reads.
- Take release activity and project health from repositories and release notes, never from vendor claims.
- Do not install, run, or benchmark any tool or store, and do not use vendor marketing as evidence of capability, performance, or adoption.

Three boundaries keep the areas apart:

- Area 1 owns PostgreSQL, pgvector, pg_eventserv, asyncpg, aiosql, and the outbox pattern. Area 2 owns qmd and every component qmd is built on, even where a component is also a database or a vector index.
- The graph-and-embeddings survey already covers nearest-neighbour index algorithms and the stores it compared. Both areas cite its records as context and record their own sources only for the questions above.
- Area 1 checks the statements of the store sketch. Area 2 records what qmd would need to hold the same three layers: edges, decisions, and append-only history.

Area 1 checks these statements of [the proposed store](../knowledge-graph-with-provenance/design-position.md#the-proposed-store). It records a source for or against each one, or a gap:

| No. | Statement of the sketch                                                                                                         |
| --- | ------------------------------------------------------------------------------------------------------------------------------- |
| S1  | One PostgreSQL server with one extension, pgvector, holds the graph tables and the vectors, and SQL is the only query language. |
| S2  | A trigger rejects an edge whose ends have the wrong node kinds, beside a foreign key from `edge.type` to `edge_type`.           |
| S3  | Edges and decisions can be made append-only, so no update or delete changes a confirmed row, and "as of date D" is a query.     |
| S4  | Indexes on `(source_id, type)` and `(target_id, type)` serve traversal in both directions.                                      |
| S5  | One statement runs a vector search, with a filter where needed, and then a recursive traversal over `edge` with `CYCLE`.        |
| S6  | SQL functions and procedures hold such queries, so a caller names an operation.                                                 |
| S7  | One transaction writes text, vector, and edges, and a vector search in that transaction sees its own writes through HNSW.       |
| S8  | `NOTIFY` fires only when its transaction commits, so a listener never hears of a rolled-back transaction.                       |
| S9  | A notification is lost when nobody listens, including during a listener restart, and an outbox table keeps the events.          |
| S10 | pg_eventserv carries notifications to WebSocket clients.                                                                        |
| S11 | If PostgreSQL ships SQL/PGQ, the same tables can be declared as a property graph without moving data.                           |
| S12 | asyncpg with aiosql runs named queries, writes in one transaction, and listens for notifications.                               |

S3, S7, S8, and S9 back the four pilot tests of the sketch.

| ID  | Agent      | Tier     | Area                                            | Output                                                                          | Independent Session |
| --- | ---------- | -------- | ----------------------------------------------- | ------------------------------------------------------------------------------- | ------------------- |
| A1  | researcher | standard | plain PostgreSQL with pgvector, clients, events | `sources/area-1/`, prefix `A1-SR-`, index `sources/area-1-postgres-pgvector.md` | false               |
| A2  | researcher | standard | qmd and its components                          | `sources/area-2/`, prefix `A2-SR-`, index `sources/area-2-qmd.md`               | false               |

## Stop Conditions

- Each assignment has recorded sources for the main concepts of its area, and `source-record-check` exits 0 on its folder.
- Area 1 has, for each statement S1 to S12, a record for or against it, or a recorded gap, and the area index lists the statements with their records.
- Area 2 has confirmed qmd from its repository, or has stopped and reported the candidates.
- Both areas have, for each simplicity fact, a record-backed value or a recorded gap.
- Each area index names the concepts with a recorded sequence of formulations, with the criticism and a source for each step, or states that it found none.
- A secondary source is marked as secondary and used only where no primary source is reachable.
- An assignment stops searching when further sources are unlikely to change its findings, and records its failed searches as gaps in its area index.

## Structured Block

The block below is the plan in the shape of `research-survey-plan.schema.json`. The tasks in `assignments` are the full text each researcher receives.

```json
{
  "research_questions": [
    "Area 1: How does plain PostgreSQL hold a graph in ordinary tables: adjacency tables, recursive common table expressions with the SEARCH and CYCLE clauses, constraints and triggers that validate edges, and append-only tables?",
    "Area 1: How do the pgvector indexes HNSW and IVFFlat behave under PostgreSQL transactions and MVCC, does a transaction see its own new vectors, and how do filtered vector search and iterative index scans work?",
    "Area 1: What do LISTEN and NOTIFY guarantee on delivery at commit, payload size, and loss without a listener, and how do the transactional outbox pattern, a relay such as pg_eventserv, and the client layer asyncpg with aiosql fit around them?",
    "Area 1: Which statements of the proposed store in docs/research/knowledge-graph-with-provenance/design-position.md on PostgreSQL behaviour do the sources support, which do they contradict, and which do they leave open?",
    "Area 2: Which tool does the stakeholder mean by qmd, and what are its purpose, data model, storage engine, indexing and search pipeline for full-text search, vector search, and reranking, and its interfaces?",
    "Area 2: How does qmd handle changed and deleted files, does it record links, sources, or provenance below the file level, and what would it need to hold edges, decisions, and append-only history?",
    "Both areas: How do PostgreSQL with pgvector and qmd compare on the simplicity facts of the graph-and-embeddings survey: components, query languages, consistency boundaries, what must be kept in sync, rebuildable derived data, release activity, and project health?",
    "Both areas: Which concepts went through several documented rounds of formulation, criticism, and reformulation, and what criticism drove each change?"
  ],
  "search_angles": [
    "The PostgreSQL manual for the current release as of November 2026, for stated behaviour and syntax",
    "PostgreSQL source code, cited by file and commit, where the manual does not state a behaviour",
    "PostgreSQL mailing list threads and commitfest entries, for the history of a feature and for SQL/PGQ status",
    "The pgvector repository: README, changelog, source code, and issues on transactions, MVCC, and filtering",
    "Project repositories, release notes, and changelogs of pg_eventserv, asyncpg, aiosql, and qmd, for features, release activity, and project health",
    "The qmd repository and the repositories of every component qmd names as a dependency",
    "Descriptions of the transactional outbox pattern by the people who named it, and their later criticism",
    "The SQL:1999 standard and its secondary descriptions, only for the history of recursive queries"
  ],
  "source_targets": [
    "PostgreSQL manual chapters on WITH queries (including SEARCH and CYCLE), triggers, constraints, row-level security and privileges, MVCC and transaction isolation, LISTEN and NOTIFY, SQL functions and procedures, and jsonb",
    "PostgreSQL source files for NOTIFY delivery (src/backend/commands/async.c) and for any other behaviour the manual does not state",
    "PostgreSQL release notes and commitfest entries for SEARCH and CYCLE (release 14) and for SQL/PGQ",
    "The pgvector repository: README sections on HNSW, IVFFlat, filtering, and iterative index scans, CHANGELOG.md, and the index access method source",
    "The pg_eventserv repository and its release notes",
    "The asyncpg repository and documentation, including its listener API, and the aiosql repository and documentation",
    "Outbox pattern sources, such as the transactional outbox description by Chris Richardson and the Debezium outbox documentation",
    "The qmd repository the stakeholder means, its README, source code, release notes, and issues, and the repositories of the storage engine, search extensions, model runtime, and models it names"
  ],
  "assignments": [
    "A1 | agent: researcher | tier: standard | independent_session: false | area: plain PostgreSQL with pgvector, clients, events | output: folder sources/area-1/, ID prefix A1-SR-, index sources/area-1-postgres-pgvector.md | task: Plain PostgreSQL with pgvector as a graph and vector store, and the client and event layer around it. Cover graphs in ordinary tables: adjacency tables, recursive common table expressions, and the SEARCH and CYCLE clauses; constraints and triggers that validate edges; and append-only tables enforced by triggers, rules, or privileges. Cover how the pgvector indexes HNSW and IVFFlat behave under PostgreSQL transactions and MVCC, including whether a transaction sees its own new vectors through the index, and filtered vector search with iterative index scans. Cover LISTEN and NOTIFY: delivery at commit, the payload limit, and loss without a listener. Cover the transactional outbox pattern, the relay pg_eventserv, and the client layer asyncpg with aiosql. Read the section The proposed store in docs/research/knowledge-graph-with-provenance/design-position.md. Record a source for or against each of its statements on PostgreSQL behaviour, S1 to S12 in the plan table: one server with pgvector and SQL only; a trigger that rejects edges with the wrong node kinds; append-only edges and decisions with as-of queries; indexes on (source_id, type) and (target_id, type) for traversal in both directions; one statement with a vector search, a filter, and a recursive traversal with CYCLE; SQL functions and procedures that hold such queries; one transaction that writes text, vector, and edges and sees its own writes through HNSW; NOTIFY only at commit; notifications lost without a listener and an outbox that keeps them; pg_eventserv to WebSocket clients; SQL/PGQ over the same tables; and asyncpg with aiosql for named queries, transactions, and listeners. Where no source settles a statement, record a gap for it in the area index. List S1 to S12 in the area index with their records. Record the simplicity facts for PostgreSQL with pgvector: components, query languages, consistency boundaries, what must be kept in sync, rebuildable derived data, release activity, and project health. Take release activity and project health from repositories and release notes, never from vendor claims. Use the documentation, source, and release state as of November 2026; use older sources only for the history of a concept, such as recursive queries in SQL:1999. Cite source code by file and commit where the documentation is silent. Mark each behaviour the record infers instead of reads. Cite the graph-and-embeddings survey records as context instead of repeating its store comparison or its index algorithms. Do not research qmd or the components it is built on; area 2 owns them. For each hardened concept in the area, such as recursive queries or the transactional outbox, record the sequence of formulations and the criticism that drove each change, with a source for each step. Aim for 10 to 15 records. Put the source's own words in straight double quotes in the Evidence section; when the quoted words hold quotation marks of their own, quote the whole passage from its opening mark to its closing mark. Mark each source primary or secondary. State for each source what it shows and what it does not show. Do not install, run, or benchmark any tool or store, and do not use vendor marketing as evidence of capability, performance, or adoption. Record only whether a component is open source. Record failed searches and gaps in the area index.",
    "A2 | agent: researcher | tier: standard | independent_session: false | area: qmd and its components | output: folder sources/area-2/, ID prefix A2-SR-, index sources/area-2-qmd.md | task: qmd, described in the brief as a local search tool for markdown documents, and every component qmd is built on. First confirm from its repository which tool the stakeholder means. If more than one candidate fits that description, or none does, record the candidates and the reason in the area index, then stop and report before you gather further records. Then record qmd's purpose, data model, storage engine, indexing and search pipeline for full-text search, vector search, and reranking, and its interfaces, such as a command line or an MCP server. Record how qmd handles changed and deleted files, and whether it records links, sources, or provenance below the file level. Record what qmd would need to hold edges, decisions, and append-only history, from its data model and source code; mark this as inferred where no source states it. Record each component qmd names as a dependency, such as its storage engine, its search extensions, its model runtime, and its models, with the facts the simplicity comparison needs. Record the simplicity facts for qmd: components, query languages, consistency boundaries, what must be kept in sync, rebuildable derived data, release activity, and project health. Take release activity and project health from repositories and release notes, never from vendor claims. Use the documentation, source, and release state as of November 2026. Cite source code by file and commit where the documentation is silent. Mark each behaviour the record infers instead of reads. Do not research PostgreSQL, pgvector, pg_eventserv, asyncpg, aiosql, or the outbox pattern; area 1 owns them. Cite the graph-and-embeddings survey records as context instead of repeating its index algorithms. For each hardened concept in the area, such as hybrid search with reranking, record the sequence of formulations and the criticism that drove each change, with a source for each step, or state in the area index that the sources show none. Aim for 10 to 15 records. Put the source's own words in straight double quotes in the Evidence section; when the quoted words hold quotation marks of their own, quote the whole passage from its opening mark to its closing mark. Mark each source primary or secondary. State for each source what it shows and what it does not show. Do not install, run, or benchmark any tool, and do not use vendor marketing as evidence of capability, performance, or adoption. Record only whether a component is open source. Record failed searches and gaps in the area index."
  ],
  "stop_conditions": [
    "Each assignment has recorded sources for the main concepts of its area, and source-record-check exits 0 on its folder.",
    "Area 1 has, for each statement S1 to S12 of the store sketch, a record for or against it, or a recorded gap, and the area index lists the statements with their records.",
    "Area 2 has confirmed qmd from its repository, or has stopped and reported the candidates.",
    "Both areas have, for each simplicity fact, a record-backed value or a recorded gap.",
    "Each area index names the concepts with a recorded sequence of formulations, with the criticism and a source for each step, or states that it found none.",
    "A secondary source is marked as secondary and used only where no primary source is reachable.",
    "An assignment stops searching when further sources are unlikely to change its findings, and records its failed searches as gaps in its area index."
  ]
}
```
