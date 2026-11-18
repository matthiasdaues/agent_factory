# Design Position After The First Round

This note records the design the stakeholder and the parent session reached after `synthesis.md`, in the session of 2026-11-17 (Claude Code session `60f0dc5d`). It replaces the synthesis where the two differ. The synthesis recommended markdown records in git. The briefs of that round had set "markdown in git" as a constraint, so the investigators' agreement on it was weak evidence. The stakeholder then set the bar: "We're talking about a knowledge graph. Not some rickety thing cobbled together quickly."

On 2026-11-17 and 2026-11-18 the stakeholder widened the scope and settled three points. The second survey, [knowledge-across-sources](../knowledge-across-sources/survey-report.md), researched the wider scope.

## The wider scope

The system manages knowledge from news, email, chat, and conversation transcripts, on any topic, far beyond the factory's own documents. The Agent Factory plays two parts. It is the first tenant, whose sessions and decisions fill the store first. It is also the method that builds and runs the system: records, quoted anchors, deterministic checks, and human decisions.

## The propagation model

A wire report and fifty outlets that repeat it are 51 sources. The wire report is the primary source of the factual claim, and repetition adds no support to it. Each outlet is a downstream consumer and multiplier, and a source of what it did with the report. It reuses the report verbatim, alters it, reframes it with its own claims, sentiment, or spin in the surrounding text, or reports independently, which makes it a new primary source. Spread and reach are knowledge in their own right.

## Out of scope for now

Copyright and data protection are not core functions. Every source document counts as storable. Rule-based exclusions can be built later.

## Why files in git do not hold the knowledge

When transcripts, email, and chat feed the graph, files in git fail in six places:

1. Volume. One meeting yields dozens of ideas, so one file per idea becomes thousands of files a month. Nobody reviews that in a pull request.
2. Queries. "Every idea that refines X, with its decisions, as of last March" is a graph query. "Has anyone said something like this before?" is a similarity query. Front matter answers neither without a hand-built database.
3. Forgetting. Git keeps every quote in every clone. Exclusions are out of scope for now, but a rule built later that removes a source would mean rewriting history on every machine.
4. Concurrent writes. A link is an edge between two ideas. Agents on parallel branches would edit the same files and conflict on every wave.
5. Scope. A chat thread is not about one repository. A graph inside one repository cuts every link that leaves it.
6. Structure in punctuation. A file marks a quote with quotation marks in prose, and a script finds it with a pattern. BUG-0129 shows where that breaks: a source with quotation marks of its own shifted the pairs, so real quotes failed and a note could pass as a quote. In a store, a quote is a span with a source, a start, and an end, and nothing can mistake a note for it.

The same reasons apply to decisions. A decision rests on conjectures, and a refutation must reopen it. If decisions lived in files and conjectures in the store, that link would cross two stores, which is where it is most likely to break.

## Three layers

| Layer      | Holds                                                                | Who writes it                  | Where it lives                                              |
| ---------- | -------------------------------------------------------------------- | ------------------------------ | ----------------------------------------------------------- |
| Provenance | Sources and the exact spans quoted from them                         | Import scripts, never edited   | A store outside git, where a record can be deleted for good |
| Knowledge  | Problems, conjectures, criticisms, tests, and their outcomes         | Agents propose, reviewers test | The same store, rebuildable from the sources                |
| Decisions  | Do, won't do, defer, accept, each naming the conjectures it rests on | A person, always               | The same store, as nodes linked to their conjectures        |

The ideas carry the volume, and the decisions carry the authority. A decision's authority comes from the person who records it and from its history, not from git. The store never overwrites a decision: a new decision replaces an old one and names it, so "what was decided as of date D" is a query. A rendered view in markdown can serve review, but it is a view of the store, never the record.

The stakeholder chose this on 2026-11-18. The first version of this note kept decisions as markdown in git, a constraint carried over from the first round's briefs.

## What stays a file

Documents written for people to read stay markdown: survey reports, validation passes, case documents, handoffs. Source records, quoted spans, concept histories, and decisions go into the store. The factory's existing ADRs and proposals stay files for now. The pilot imports them as sources, and the decisions in them become nodes anchored to their text.

## The store already half exists

The usage pipeline under `.agent-factory/usage/` already keeps full session transcripts (`control/config.json` sets `"transcript_retention": "full"`). On 2026-11-17 it held 44 sessions, 34 from Claude Code and 10 from Codex. Each message carries `uuid`, `parentUuid`, `timestamp`, `sessionId`, `gitBranch`, and `agentId`, so every idea can point to the exact message it came from. Each session is stored once per recording, so an import must remove repeated copies first. `.agent-factory/` is ignored by git, so material there can be deleted for good. `usage/analysis` already runs on DuckDB; the store itself is proposed below as PostgreSQL.

So the provenance layer exists for agent sessions. The knowledge layer becomes a second component beside `usage/analysis`: it reads the same transcripts and writes ideas and links into the store. Email, Slack, Teams, and the other three CLIs are not covered yet.

## The Popperian model

Every idea stays a conjecture. It earns standing only by surviving serious attempts to refute it. The factory already works this way in `research-topic`, whose claims are surviving, refuted, unresolved, or superseded, and never "proved".

1. The problem is a node type of its own. A session starts from a problem and generates competing conjectures against it. The Issue-Based Information System (IBIS) has the same shape: issue, position, argument.
2. Every conjecture states what would refute it. An idea without a refutation condition is marked "not testable yet", not discarded.
3. Statuses describe the history of tests, not truth: conjecture, corroborated (with the tests survived and their severity), refuted (with the test and evidence), unresolved, superseded, withdrawn. No status is "true" or "verified".
4. Repetition is not support. An idea that appears in twelve sessions is mentioned twelve times and has passed no test. Merging duplicates raises a mention count, never the corroboration.
5. A refutation is fallible too. It rests on accepted evidence, which here are the anchored source spans, so a refutation points to its spans and can be challenged.
6. Decisions depend on conjectures, and a refutation reopens them. Example from this repository: "Won't do: one Git ref per ID, because leased pushes on many refs are too slow." That decision rests on a conjecture about speed. When a test refutes the conjecture, the graph flags the decision for review. Today nothing does that.

A refutation is a statement about a statement, which needs provenance of its own. Both RDF and a property graph can hold it. The choice still depends on whether the graph spans projects.

## The proposed store

The stakeholder and the parent session proposed this sketch on 2026-11-18, after the [graph-and-embeddings](../graph-and-embeddings/survey-report.md) survey. That survey did not cover plain PostgreSQL with pgvector, so the sketch rests on the survey's store comparison and on the parent session's knowledge of PostgreSQL. Where it states how PostgreSQL behaves, the pilot must test it.

The store is one PostgreSQL server with one extension, pgvector. The graph lives in ordinary tables, and SQL is the only query language.

- `node`: one row per source, span, problem, conjecture, criticism, test, or decision, with its kind. Anything that can be criticised is a node. A claimed relation, such as "this outlet reframed that report", is a node with two plain edges, so a refutation always targets a node.
- `edge`: `id`, `source_id`, `target_id`, `type`, `status`, `asserted_by`, `evidence_span_id`, `valid_from`, `valid_to`, `recorded_at`, and `meta`. `type` is a foreign key to `edge_type`, which names the node kinds allowed at each end. `status` is candidate or confirmed; similarity writes candidates only, and a check or a person confirms them. Every value a query filters on or a rule checks is a column; `meta` as `jsonb` holds the rest.
- `embedding`: `node_id`, `model`, `model_version`, `vector`, with an HNSW index. A new model adds rows beside the old ones, and each vector carries the model version that produced it.

The database enforces the rules. A trigger rejects an edge whose ends have the wrong node kinds, which is shape validation done with plain constraints. Edges and decisions are append-only: a change ends the old row and writes a new one, so "as of date D" is a query. Indexes on `(source_id, type)` and `(target_id, type)` serve traversal in both directions.

The key query is one statement: a vector search, then a recursive traversal over `edge`, with the `CYCLE` clause against loops. SQL functions and procedures hold such queries, so callers name an operation, not a recursive query. A slim Python layer with asyncpg and aiosql runs the named queries. It also computes the embeddings, so the model stays outside the database, and writes text, vector, and edges in one transaction.

New ideas raise events. `NOTIFY` fires only when its transaction commits, so a listener never hears of an idea that was rolled back. A notification is lost when nobody listens, so an outbox table holds the events and the notification only wakes the reader. A relay such as pg_eventserv can carry them to WebSocket clients.

If PostgreSQL ships SQL/PGQ in a later release, the same tables can be declared as a property graph without moving data. Walks over many hops stay wordier in SQL than in Cypher; the functions hide that.

Tests for the pilot:

1. A vector search followed by a traversal runs as one statement in one transaction and sees that transaction's own writes.
2. The type trigger rejects every edge whose ends have the wrong node kinds.
3. No update or delete changes a confirmed edge or a decision; only a new row replaces it.
4. An event reaches a listener for every committed idea, and for none that was rolled back, including after a listener restart.

## Bolder options the stakeholder has not decided

- Turn the order around: the graph holds the ideas, and a proposal becomes a view, a bundle of ideas with one acceptance decision.
- One graph per person or team, not per repository. A project queries it and writes back only the decisions that concern it.

## The spike

Import a few sessions from `usage/transcripts/`, starting with the session behind the run-lifecycle handoff of 2026-11-16. Remove repeated copies, extract ideas and decisions with message anchors, and load them into a PostgreSQL database outside git, in the schema of "The proposed store". Ask: "What was decided about the run lifecycle?" The spike passes when the answer finds the twenty decisions of the handoff and each points to a message that exists. Nothing is committed except a short findings note. The stakeholder has not yet approved the spike.

## Costs

The factory's deterministic gates read files in git today. Checks on the store must run as queries: every quoted span resolves to its source, every decision names its conjectures, and every refutation points to its spans. Every CLI needs the same query command. The provenance and knowledge layers can be rebuilt from the sources. Decisions cannot, because a person made them, so the store needs a backup and an export of its decision history that nothing can rewrite. The factory rules ban a reference from a shipped agent to an unapproved store, so the store needs its own proposal.
