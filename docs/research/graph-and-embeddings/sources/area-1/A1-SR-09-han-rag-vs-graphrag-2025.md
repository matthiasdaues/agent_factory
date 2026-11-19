# A1-SR-09: Han et al., RAG vs. GraphRAG: A Systematic Evaluation and Key Insights

```json
{
  "source_identity": "Haoyu Han, Li Ma, Yu Wang, et al., 'RAG vs. GraphRAG: A Systematic Evaluation and Key Insights', KDD 2026; arXiv:2502.11371v4; https://arxiv.org/abs/2502.11371",
  "author_or_issuing_body": "Haoyu Han, Li Ma, Yu Wang, and co-authors as listed on the arXiv record",
  "publisher": "arXiv (Cornell University); conference version in KDD 2026, ACM",
  "publication_date": "2025-02-17T00:00:00Z",
  "relevant_event_date": "2025-02-17",
  "source_family": "Primary. Independent benchmark study that criticises the evaluation and design of GraphRAG (A1-SR-02) and compares knowledge-graph and community-based designs with vector RAG. Cited by A1-SR-10.",
  "precise_evidence_location": "Abstract; Section 1 key findings; question-answering results, finding (4) on knowledge-graph coverage; hybrid strategies, paragraph Strategy 2: RAG and GraphRAG Integration; Section 5.3 Position Bias in Existing Evaluation",
  "method": "Benchmark study under one evaluation protocol for preprocessing, retrieval settings, and generation, on question answering and query-based summarisation datasets. Tests LLM-judge position bias by swapping the order of candidate answers.",
  "limitations": "Date is arXiv v1; the text read is v4 of 7 November 2026, which may differ from v1. Author affiliations were not recorded from the extracted text. The study re-implements the systems it compares. Shows: complementary strengths of vector and graph retrieval, coverage loss in extracted knowledge graphs, position bias in the LLM judge used by Edge et al., and concatenation as an integration strategy. Does not show: any update or consistency mechanism.",
  "provenance": "PDF downloaded with curl from arXiv on 2026-11-18 and extracted with pdftotext; quotes copied from the extracted text, with line breaks and hyphenation joined. Re-verify at the URL above."
}
```

## Evidence

- Section 1: "First, RAG and GraphRAG exhibit complementary behaviors rather than a consistent winner."
- Section 1: "Finally, GraphRAG is not free: it often incurs higher construction cost, retrieval latency, and storage footprint, and its performance can be sensitive to the quality (and cost) of graph construction."
- Question-answering results, finding (4): "KG-GraphRAG retrieves evidence primarily from extracted entities and relations, which can be incomplete and omit answer-critical information. In Appendix A, we show that only about 65.8% of answer entities appear in the constructed KG for HotPotQA and 65.5% for NQ, highlighting the sensitivity of KG-based retrieval to graph construction quality."
- Strategy 2 paragraph: "For each query, both methods retrieve relevant information in parallel, and the retrieved contexts are concatenated and fed into the generator to produce the final answer."
- Section 5.3: "Second, Edge et al. [6] evaluate performance using LLM-as-a-Judge without ground-truth references, while we evaluate generated summaries against human-written references using ROUGE and BERTScore."
- Section 5.3: "First, position bias [34, 40] is clearly present in LLM-as-a-Judge evaluations for summarization, as reversing the order of presented summaries leads to substantially different, and in some cases opposite, judgments."
