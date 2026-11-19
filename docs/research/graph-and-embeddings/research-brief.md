# Research Brief: Graph And Embeddings

This brief is the readable copy of [research-brief.json](research-brief.json).
The JSON file is authoritative and passes `research-brief.schema.json`.

The survey asks how current systems combine a graph data model with
embeddings, and which architectures do it with the fewest moving parts. The
technology of the knowledge graph with provenance is open. Candidates include
a graph database with a custom embedding layer, and PostgreSQL with Apache AGE
and pgvector. The earlier rounds are in
[knowledge-graph-with-provenance](../knowledge-graph-with-provenance/case-for-the-knowledge-graph.md),
[knowledge-graph-state-of-the-art](../knowledge-graph-state-of-the-art/survey-report.md),
and [knowledge-across-sources](../knowledge-across-sources/survey-report.md).

The survey covers four areas:

1. Architectures that combine graphs and embeddings, such as GraphRAG and
   hybrid retrieval, and how they keep graph and vectors consistent.
2. Stores that hold both, compared on components, query languages,
   consistency boundaries, and project health.
3. What embedding similarity can and cannot establish for paraphrase, claim
   matching, text reuse, and same-idea detection.
4. Nearest-neighbour indexes and queries that combine a similarity search with
   structured filters.

Simplicity and elegance guide the comparison: few components, one consistency
boundary, one query path, and derived data that can be rebuilt.

As before, the survey reports what sources document. A verdict that a concept
survived refutation belongs to a later falsification study.
