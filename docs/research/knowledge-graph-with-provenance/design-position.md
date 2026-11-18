# Design Position After The First Round

This note records the design the stakeholder and the parent session reached after `synthesis.md`, in the session of 2026-11-17 (Claude Code session `60f0dc5d`). It replaces the synthesis where the two differ. The synthesis recommended markdown records in git. The briefs of that round had set "markdown in git" as a constraint, so the investigators' agreement on it was weak evidence. The stakeholder then set the bar: "We're talking about a knowledge graph. Not some rickety thing cobbled together quickly."

On 2026-11-17 and 2026-11-18 the stakeholder widened the scope and settled three points. The second survey, [knowledge-across-sources](../knowledge-across-sources/survey-report.md), researched the wider scope.

## The wider scope

The system manages knowledge from news, email, chat, and conversation transcripts, on any topic, far beyond the factory's own documents. The Agent Factory plays two parts. It is the first tenant, whose sessions and decisions fill the store first. It is also the method that builds and runs the system: records, quoted anchors, deterministic checks, and human decisions.

## The propagation model

A wire report and fifty outlets that repeat it are 51 sources. The wire report is the primary source of the factual claim, and repetition adds no support to it. Each outlet is a downstream consumer and multiplier, and a source of what it did with the report. It reuses the report verbatim, alters it, reframes it with its own claims, sentiment, or spin in the surrounding text, or reports independently, which makes it a new primary source. Spread and reach are knowledge in their own right.

## Out of scope for now

Copyright and data protection are not core functions. Every source document counts as storable. Rule-based exclusions can be built later.

## Why markdown in git does not hold the ideas

When transcripts, email, and chat feed the graph, files in git fail in five places:

1. Volume. One meeting yields dozens of ideas, so one file per idea becomes thousands of files a month. Nobody reviews that in a pull request.
2. Queries. "Every idea that refines X, with its decisions, as of last March" is a graph query. "Has anyone said something like this before?" is a similarity query. Front matter answers neither without a hand-built database.
3. Forgetting. Git keeps every quote in every clone. Exclusions are out of scope for now, but a rule built later that removes a source would mean rewriting history on every machine.
4. Concurrent writes. A link is an edge between two ideas. Agents on parallel branches would edit the same files and conflict on every wave.
5. Scope. A chat thread is not about one repository. A graph inside one repository cuts every link that leaves it.

## Three layers

| Layer      | Holds                                                                | Who writes it                  | Where it lives                                              |
| ---------- | -------------------------------------------------------------------- | ------------------------------ | ----------------------------------------------------------- |
| Provenance | Sources and the exact spans quoted from them                         | Import scripts, never edited   | A store outside git, where a record can be deleted for good |
| Knowledge  | Problems, conjectures, criticisms, tests, and their outcomes         | Agents propose, reviewers test | The same store, rebuildable from the sources                |
| Decisions  | Do, won't do, defer, accept, each naming the conjectures it rests on | A person, always               | Markdown in git, behind review and gates                    |

The ideas carry the volume, and the decisions carry the authority. Only the decisions need git's history, review, and gates.

## The store already half exists

The usage pipeline under `.agent-factory/usage/` already keeps full session transcripts (`control/config.json` sets `"transcript_retention": "full"`). On 2026-11-17 it held 44 sessions, 34 from Claude Code and 10 from Codex. Each message carries `uuid`, `parentUuid`, `timestamp`, `sessionId`, `gitBranch`, and `agentId`, so every idea can point to the exact message it came from. Each session is stored once per recording, so an import must remove repeated copies first. `.agent-factory/` is ignored by git, so material there can be deleted for good. `usage/analysis` already runs on DuckDB.

So the provenance layer exists for agent sessions. The knowledge layer becomes a second component beside `usage/analysis`: it reads the same transcripts and writes ideas and links into DuckDB, so the factory runs one database engine. Email, Slack, Teams, and the other three CLIs are not covered yet.

## The Popperian model

Every idea stays a conjecture. It earns standing only by surviving serious attempts to refute it. The factory already works this way in `research-topic`, whose claims are surviving, refuted, unresolved, or superseded, and never "proved".

1. The problem is a node type of its own. A session starts from a problem and generates competing conjectures against it. The Issue-Based Information System (IBIS) has the same shape: issue, position, argument.
2. Every conjecture states what would refute it. An idea without a refutation condition is marked "not testable yet", not discarded.
3. Statuses describe the history of tests, not truth: conjecture, corroborated (with the tests survived and their severity), refuted (with the test and evidence), unresolved, superseded, withdrawn. No status is "true" or "verified".
4. Repetition is not support. An idea that appears in twelve sessions is mentioned twelve times and has passed no test. Merging duplicates raises a mention count, never the corroboration.
5. A refutation is fallible too. It rests on accepted evidence, which here are the anchored source spans, so a refutation points to its spans and can be challenged.
6. Decisions depend on conjectures, and a refutation reopens them. Example from this repository: "Won't do: one Git ref per ID, because leased pushes on many refs are too slow." That decision rests on a conjecture about speed. When a test refutes the conjecture, the graph flags the decision for review. Today nothing does that.

A refutation is a statement about a statement, which needs provenance of its own. Both RDF and a property graph can hold it. The choice still depends on whether the graph spans projects.

## Bolder options the stakeholder has not decided

- Turn the order around: the graph holds the ideas, and a proposal becomes a view, a bundle of ideas with one acceptance decision.
- One graph per person or team, not per repository. A project queries it and writes back only the decisions that concern it.

## The spike

Import a few sessions from `usage/transcripts/`, starting with the session behind the run-lifecycle handoff of 2026-11-16. Remove repeated copies, extract ideas and decisions with message anchors, and load them into a DuckDB file outside git. Ask: "What was decided about the run lifecycle?" The spike passes when the answer finds the twenty decisions of the handoff and each points to a message that exists. Nothing is committed except a short findings note. The stakeholder has not yet approved the spike.

## Costs

The store lives outside git, so the deterministic gates cannot see it. Every CLI needs the same query command. A lost store must be rebuildable from the sources. The factory rules ban a reference from a shipped agent to an unapproved store, so the store needs its own proposal.
