# A1-SR-03: Edge, Trinh, Larson, LazyGraphRAG: Setting a new standard for quality and cost

```json
{
  "source_identity": "Darren Edge, Ha Trinh, Jonathan Larson, 'LazyGraphRAG: Setting a new standard for quality and cost', Microsoft Research Blog, 25 November 2024; https://www.microsoft.com/en-us/research/blog/lazygraphrag-setting-a-new-standard-for-quality-and-cost/",
  "author_or_issuing_body": "Darren Edge, Ha Trinh, Jonathan Larson (Microsoft Research)",
  "publisher": "Microsoft Research Blog",
  "publication_date": "2024-11-25T00:00:00Z",
  "relevant_event_date": "2024-11-25",
  "source_family": "Primary for the LazyGraphRAG design, written by the GraphRAG authors (A1-SR-02). Not peer reviewed. Self-revision within the GraphRAG lineage.",
  "precise_evidence_location": "Sections 'Affordable GraphRAG for every use case' and 'Blending vector RAG and Graph RAG with deferred LLM use'; Table 1 (GraphRAG compared with LazyGraphRAG by stage)",
  "method": "Design description by the design's authors, with an LLM-judged comparison on 5,590 news articles and 100 synthetic queries.",
  "limitations": "A blog post, not a paper. The authors compare their own designs. Cost and quality figures come from one dataset and LLM-judged win rates, and are not used here as evidence of performance. An editor's note of 6 June 2025 names products; those facts belong to area 2 and are not recorded. Shows: the design change from up-front LLM summarisation to query-time work, and that the query path uses text chunk embeddings together with a concept graph. Does not show: how the concept graph or the chunk embeddings are updated when a source changes.",
  "provenance": "Page fetched with curl on 2026-11-18 and stripped of HTML with a Python script; quotes copied from the extracted text. Re-verify at the URL above."
}
```

## Evidence

- Introduction: "In this blog post, we introduce a radically different approach to graph-enabled RAG that requires no prior summarization of the source data, avoiding the up-front indexing costs that may be prohibitive for some users and use cases."
- Blending section: "LazyGraphRAG aims to blend the advantages of vector RAG and Graph RAG while overcoming their respective limitations:"
- Blending section: "Vector RAG is a form of best-first search that uses the similarity with the query to select the best-matching source text chunks. However, it has no sense of the breadth of the dataset to consider for global queries."
- Blending section: "GraphRAG global search is a form of breadth-first search that uses the community structure of source text entities to ensure that queries are answered considering the full breadth of the dataset. However, it has no sense of the best communities to consider for local queries."
- Table 1, Build index, LazyGraphRAG column: "Uses NLP noun phrase extraction to extract concepts and their co-occurrences, b) uses graph statistics to optimize the concept graph and extract hierarchical community structure"
- Table 1, Match query, LazyGraphRAG column: "Uses text chunk embeddings and chunk-community relationships to first rank text chunks by similarity to the query, then rank communities by the rank of their top-k text chunks"
- Table 1, Summarize index, LazyGraphRAG column, paraphrase: no summary step; all LLM use is deferred until query time.
- Note: the design embeds text chunks, not graph elements. The graph supplies communities; the vectors rank chunks inside them.
- Not shown: any update or deletion procedure.
