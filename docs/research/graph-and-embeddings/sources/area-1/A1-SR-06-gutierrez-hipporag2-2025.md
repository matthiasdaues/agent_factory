# A1-SR-06: Gutiérrez et al., From RAG to Memory: Non-Parametric Continual Learning for Large Language Models (HippoRAG 2)

```json
{
  "source_identity": "Bernal Jiménez Gutiérrez, Yiheng Shu, Weijian Qi, Sizhe Zhou, Yu Su, 'From RAG to Memory: Non-Parametric Continual Learning for Large Language Models', ICML 2025; arXiv:2502.14802v2; https://arxiv.org/abs/2502.14802",
  "author_or_issuing_body": "Gutiérrez, Shu, Qi, Zhou, Su (The Ohio State University; University of Illinois Urbana-Champaign)",
  "publisher": "arXiv (Cornell University); conference version at ICML 2025",
  "publication_date": "2025-02-20T00:00:00Z",
  "relevant_event_date": "2025-02-20",
  "source_family": "Primary. Successor to HippoRAG (A1-SR-05) by the same group. Criticises structure-augmented RAG designs, including GraphRAG (A1-SR-02), LightRAG (A1-SR-04), and HippoRAG, against a strong embedding-only baseline.",
  "precise_evidence_location": "Abstract; Section 1 Introduction (comparison with structure-augmented methods); Section 3.2 Dense-Sparse Integration; Section 3.5 Online Retrieval",
  "method": "Design description and experiments. Adds passage nodes to the HippoRAG graph, links each passage to its phrases, retrieves triples by embedding and filters them with an LLM, then runs Personalized PageRank seeded by phrase scores and passage embedding similarity. Baselines are re-run with the same extractor and retriever.",
  "limitations": "Date is arXiv v1; the text read is v2 of 19 June 2025. Authors evaluate their own design and re-implement the baselines. Shows: the design now embeds three kinds of unit, phrases, triples, and passages, and blends vector scores into the graph walk; the criticism that structure-augmented designs fall below embedding-only RAG on factual tasks. Does not show: how embeddings and graph are kept in step when a passage changes or is removed.",
  "provenance": "PDF downloaded with curl from arXiv on 2026-11-18 and extracted with pdftotext; quotes copied from the extracted text, with line breaks and hyphenation joined. Re-verify at the URL above."
}
```

## Evidence

- Abstract: "Recent RAG approaches augment vector embeddings with various structures like knowledge graphs to address some of these gaps, namely sense-making and associativity. However, their performance on more basic factual memory tasks drops considerably below standard RAG."
- Section 1: "As shown in Figure 1, our evaluation reveals that all previous structure-augmented methods underperform against the strongest embedding-based RAG methods available on all three benchmark types."
- Section 1: "For example, HippoRAG’s performance drops most on large-scale discourse understanding due to its lack of query-based contextualization, while RAPTOR’s performance deteriorates substantially on the simple and multi-hop QA tasks due to the noise introduced into the retrieval corpora by its LLM summarization mechanism."
- Section 3.2: "Unlike the document ensemble in HippoRAG, which simply aggregates scores from graph search and embedding matching, we enhance the KG by introducing passage nodes, enabling more seamless integration of contextual information."
- Section 3.5: "If no triples are available, it directly retrieves top-ranked passages using the embedding model."
- Section 3.5: "Reset probabilities are assigned based on ranking scores for phrase nodes, while passage nodes receive scores proportional to their embedding similarity, adjusted by a weight factor (§6.2) to balance the influence between phrase nodes and passage nodes."
- Not shown: any update or deletion procedure for passages.
